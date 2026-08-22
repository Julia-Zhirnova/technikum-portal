#!/bin/bash
set -e

echo "🚀 Запуск Docker-окружения..."

# Проверка наличия .env
if [ ! -f .env ]; then
    echo "📝 Создание .env файла..."
    cat > .env <<'ENVEOF'
POSTGRES_DB=technikum_db
POSTGRES_USER=technikum_user
POSTGRES_PASSWORD=technikum_password
DJANGO_SECRET_KEY=django-insecure-dev-key-change-in-production-12345
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:80
ENVEOF
fi

# Сборка образов
echo "🔨 Сборка Docker-образов..."
docker-compose build

# Запуск сервисов
echo "⚡ Запуск сервисов..."
docker-compose up -d

# Ожидание готовности PostgreSQL
echo "⏳ Ожидание готовности PostgreSQL..."
sleep 5

# Применение миграций
echo "🗄️  Применение миграций..."
docker-compose exec backend python manage.py migrate --noinput

# Сборка статики
echo "📦 Сборка статики..."
docker-compose exec backend python manage.py collectstatic --noinput

echo ""
echo "✅ Сервисы запущены:"
echo "   Frontend:  http://localhost:5173"
echo "   Backend:   http://localhost:8000"
echo "   Admin:     http://localhost:8000/admin"
echo ""
echo "📋 Логи: docker-compose logs -f"
echo "🛑 Остановка: docker-compose down"
echo "💾 Бэкап БД: ./scripts/docker-backup.sh"
