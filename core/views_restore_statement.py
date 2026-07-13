from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from core.models import Statement
from django.shortcuts import get_object_or_404


class RestoreStatementView(APIView):
    """
    POST /api/teacher/statements/{id}/restore/
    Возвращает ведомость из архива в статус "в_работе"
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, statement_id):
        try:
            # Находим ведомость
            statement = get_object_or_404(Statement, id_statement=statement_id)
            
            # Проверяем, что пользователь - преподаватель этой ведомости
            if statement.teacher != request.user:
                return Response(
                    {'error': 'Вы не являетесь преподавателем этой ведомости'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Проверяем текущий статус
            if statement.status == 'в_работе':
                return Response(
                    {'error': 'Ведомость уже в работе'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Возвращаем ведомость в работу
            statement.status = 'в_работе'
            statement.save()
            
            return Response({
                'success': True,
                'message': f'Ведомость {statement.number} возвращена в работу',
                'statement_id': statement.id_statement,
                'status': statement.status
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
