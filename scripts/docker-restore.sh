#!/bin/bash
set -e

if [ -z "$1" ]; then
    echo "Использование: $0 <backup_file.sql>"
    echo ""
    echo "Доступные бэкапы:"
    ls -lh backups/*.sql 2>/dev/null || echo "  (нет бэкапов)"
    exit 1
fi

BACKUP_FILE=$1

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Файл не найден: $BACKUP_FILE"
    exit 1
fi

echo "⚠️  ВНИМАНИЕ: Это удалит все текущие данные!"
read -p "Продолжить? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Отменено"
    exit 1
fi

echo "🔄 Восстановление из $BACKUP_FILE..."
docker-compose exec -T postgres psql -U technikum_user technikum_db < $BACKUP_FILE

if [ $? -eq 0 ]; then
    echo "✅ Восстановление завершено"
else
    echo "❌ Ошибка восстановления"
    exit 1
fi
