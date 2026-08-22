#!/bin/bash
set -e

BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.sql"

mkdir -p $BACKUP_DIR

echo "💾 Создание бэкапа базы данных..."
docker-compose exec -T postgres pg_dump -U technikum_user technikum_db > $BACKUP_FILE

if [ $? -eq 0 ]; then
    echo "✅ Бэкап создан: $BACKUP_FILE"
    echo "📦 Размер: $(du -h $BACKUP_FILE | cut -f1)"
else
    echo "❌ Ошибка создания бэкапа"
    exit 1
fi
