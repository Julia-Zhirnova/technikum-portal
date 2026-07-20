import io
import zipfile
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from openpyxl import Workbook

from .services import reset_user_password

User = get_user_model()


class AdminResetAllPasswordsView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        users = User.objects.filter(is_active=True)
        reset_count = 0
        for user in users:
            reset_user_password(user)
            reset_count += 1
        return Response({"detail": f"Пароли сброшены у {reset_count} пользователей.", "count": reset_count}, status=status.HTTP_200_OK)


class AdminResetUserPasswordView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)
        new_password = reset_user_password(user)
        return Response({"detail": "Пароль сброшен.", "email": user.email, "temporary_password": new_password}, status=status.HTTP_200_OK)


class AdminResetMultiplePasswordsView(APIView):
    """Массовый сброс паролей для выбранных пользователей."""
    permission_classes = [IsAdminUser]

    def post(self, request):
        user_ids = request.data.get("user_ids", [])
        if not user_ids:
            return Response({"detail": "Не выбраны пользователи"}, status=status.HTTP_400_BAD_REQUEST)
        users = User.objects.filter(id__in=user_ids, is_active=True)
        results = []
        for user in users:
            new_password = reset_user_password(user)
            results.append({"id": user.id, "email": user.email, "temporary_password": new_password})
        return Response({"detail": f"Пароли сброшены у {len(results)} пользователей.", "results": results}, status=status.HTTP_200_OK)


class AdminExportPasswordsArchiveView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.filter(is_active=True).select_related("studentprofile__group")
        groups = {}
        employees = []
        for user in users:
            group_name = getattr(getattr(user, "studentprofile", None), "group", None)
            group_name = str(group_name) if group_name else None
            new_password = reset_user_password(user)
            full_name = f"{user.last_name} {user.first_name} {user.middle_name}".strip()
            row = [full_name, user.email, user.email, new_password, group_name or "—"]
            if group_name:
                groups.setdefault(group_name, []).append(row)
            else:
                employees.append(row)
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for group_name, users_data in groups.items():
                wb = Workbook()
                ws = wb.active
                ws.title = "Пользователи"
                ws.append(["ФИО", "Email", "Логин", "Временный пароль", "Группа"])
                for row in users_data:
                    ws.append(row)
                output = io.BytesIO()
                wb.save(output)
                output.seek(0)
                safe_name = "".join(c for c in group_name if c.isalnum() or c in (" ", "-", "_")).strip()
                zip_file.writestr(f"{safe_name}.xlsx", output.getvalue())
            if employees:
                wb = Workbook()
                ws = wb.active
                ws.title = "Сотрудники"
                ws.append(["ФИО", "Email", "Логин", "Временный пароль", "Группа"])
                for row in employees:
                    ws.append(row)
                output = io.BytesIO()
                wb.save(output)
                output.seek(0)
                zip_file.writestr("сотрудники.xlsx", output.getvalue())
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer.getvalue(), content_type="application/zip")
        response["Content-Disposition"] = "attachment; filename=\"passwords_archive.zip\""
        return response
