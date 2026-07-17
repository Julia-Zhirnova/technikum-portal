from django.http import JsonResponse, HttpResponse
from core.models import Campus
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .serializers import ForceChangePasswordSerializer

def hello(request):
    campuses = Campus.objects.all()
    sp = ''.join([f'<li><b>🏢 {k.id_campus}</b><br><small>📍 {k.address}</small></li>' for k in campuses])
    return HttpResponse(f"<html><body><h1>✅ Django работает!</h1><ul>{sp}</ul></body></html>")

def api_campuses(request):
    campuses = Campus.objects.values('id_campus', 'address')
    return JsonResponse({'success': True, 'count': len(campuses), 'data': list(campuses)}, json_dumps_params={'ensure_ascii': False})

class ForceChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = ForceChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.requires_password_change = False
            user.save()
            return Response({"detail": "Пароль успешно изменен."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
