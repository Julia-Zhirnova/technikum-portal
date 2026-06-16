from django.http import JsonResponse, HttpResponse
from core.models import Campus


def hello(request):
    """Главная страница с данными из PostgreSQL"""
    campuses = Campus.objects.all()
    sp = ''.join([
        f'<li>'
        f'<b>🏢 {k.id_campus}</b><br>'
        f'<small>📍 {k.address}</small>'
        f'</li>'
        for k in campuses
    ])
    
    return HttpResponse(f"""
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Люберецкий техникум - Портал</title>
            <style>
                body {{ 
                    font-family: 'Segoe UI', Arial, sans-serif; 
                    max-width: 900px; 
                    margin: 40px auto; 
                    padding: 20px;
                    background: #f5f5f5;
                }}
                .container {{
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .ok {{ 
                    color: #28a745; 
                    font-size: 28px; 
                    font-weight: bold;
                    margin-bottom: 20px;
                }}
                .info {{ 
                    background: #e7f3ff; 
                    padding: 20px; 
                    border-radius: 8px; 
                    margin: 20px 0;
                    border-left: 4px solid #007bff;
                }}
                ul {{ 
                    line-height: 1.8; 
                    list-style: none;
                    padding: 0;
                }}
                li {{
                    background: #f8f9fa;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 5px;
                    border-left: 3px solid #28a745;
                }}
                .btn {{
                    display: inline-block;
                    margin-top: 20px;
                    margin-right: 10px;
                    padding: 12px 24px;
                    background: #007bff;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                }}
                .btn:hover {{ background: #0056b3; }}
                .btn-api {{ background: #28a745; }}
                .btn-api:hover {{ background: #1e7e34; }}
                small {{ color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="ok">✅ Django + PostgreSQL работает!</h1>
                <div class="info">
                    <p><b>🔌 Подключение к БД:</b> Успешно</p>
                    <p><b>📊 База данных:</b> PostgreSQL 16</p>
                    <p><b>🌐 Кодировка:</b> UTF-8</p>
                    <p><b>🕐 Часовой пояс:</b> Europe/Moscow</p>
                </div>
                <h2>🏢 Корпуса техникума ({campuses.count()} шт.):</h2>
                <ul>{sp}</ul>
                <p>
                    <a href="/admin/" class="btn">🔐 Войти в админку Django</a>
                    <a href="/api/campuses/" class="btn btn-api">📡 API: JSON с корпусами</a>
                </p>
            </div>
        </body>
        </html>
    """)


def api_campuses(request):
    """API эндпоинт для будущего React-фронтенда"""
    campuses = Campus.objects.values('id_campus', 'address')
    return JsonResponse({
        'success': True,
        'count': len(campuses),
        'data': list(campuses)
    }, json_dumps_params={'ensure_ascii': False})
