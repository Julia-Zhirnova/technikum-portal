from django.http import JsonResponse, HttpResponse
from core.models import Campus
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .serializers import ForceChangePasswordSerializer


def hello(request):
    """Главная страница портала."""
    campuses = Campus.objects.all()
    sp = ''.join([
        f'<li><b>🏢 {k.id_campus}</b><br><small>📍 {k.address}</small></li>'
        for k in campuses
    ])
    return HttpResponse(f"""
<html>
<head>
<meta charset="utf-8">
<title>ТехноПортал — Люберецкий техникум</title>
</head>
<body style="font-family: Arial; max-width: 900px; margin: 40px auto; padding: 20px;">
<h1>🚀 ТехноПортал работает!</h1>
<p><b>ГБПОУ МО «Люберецкий техникум имени Ю. А. Гагарина»</b></p>
<h2>🏢 Корпуса техникума ({campuses.count()} шт.):</h2>
<ul>{sp}</ul>
</body>
</html>
""")


def api_campuses(request):
    """API эндпоинт со списком корпусов."""
    campuses = Campus.objects.values('id_campus', 'address')
    return JsonResponse({
        'success': True,
        'count': len(campuses),
        'data': list(campuses)
    }, json_dumps_params={'ensure_ascii': False})


class ForceChangePasswordView(APIView):
    """Принудительная смена пароля (Функция 1.2)."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ForceChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.requires_password_change = False
            user.save()
            return Response(
                {"detail": "Пароль успешно изменен."},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
