import json
from django.utils.deprecation import MiddlewareMixin

class DebugMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Отладка всех запросов к teacher API
        if '/api/teacher/' in request.path:
            print(f"🔍 DEBUG MIDDLEWARE - Request: {request.method} {request.path}")
            print(f"   User: {getattr(request, 'user', 'No user')}")
            print(f"   Headers: {dict(request.headers)}")
        
        if request.path == '/api/student/profile/' and request.method == 'PATCH':
            print("\n" + "="*80)
            print(f"🔍 PATCH запрос на {request.path}")
            print(f"📦 Тело запроса: {request.body.decode('utf-8')}")
            print("="*80 + "\n")
