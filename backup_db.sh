#!/bin/bash
# backup_db.sh — универсальный скрипт бэкапа для Django

BACKUP_DIR="./backups"
DATE=$(date +"%Y-%m-%d_%H-%M-%S")
mkdir -p "$BACKUP_DIR"

# Определяем тип БД из settings.py
DB_ENGINE=$(grep -A 2 "DATABASES" config/settings.py | grep "ENGINE" | head -1 | sed "s/.*'\(.*\)'.*/\1/")

echo "🔍 Обнаружен движок БД: $DB_ENGINE"

if [[ "$DB_ENGINE" == *"sqlite3"* ]]; then
    # Бэкап SQLite — просто копируем файл
    FILENAME="backup_sqlite_${DATE}.sqlite3.gz"
    echo "🚀 Создаю бэкап SQLite..."
    gzip -c db.sqlite3 > "$BACKUP_DIR/$FILENAME"
elif [[ "$DB_ENGINE" == *"postgresql"* ]]; then
    # Бэкап PostgreSQL
    DB_NAME=$(grep -A 5 "DATABASES" config/settings.py | grep "NAME" | head -1 | sed "s/.*'\(.*\)'.*/\1/")
    DB_USER=$(grep -A 5 "DATABASES" config/settings.py | grep "USER" | head -1 | sed "s/.*'\(.*\)'.*/\1/")
    DB_HOST=$(grep -A 5 "DATABASES" config/settings.py | grep "HOST" | head -1 | sed "s/.*'\(.*\)'.*/\1/")
    FILENAME="backup_postgres_${DB_NAME}_${DATE}.sql.gz"
    echo "🚀 Создаю бэкап PostgreSQL: $DB_NAME..."
    pg_dump -U "$DB_USER" -h "${DB_HOST:-localhost}" -d "$DB_NAME" | gzip > "$BACKUP_DIR/$FILENAME"
else
    echo "❌ Неизвестный тип БД: $DB_ENGINE"
    exit 1
fi

if [ $? -eq 0 ]; then
    echo "✅ Бэкап создан: $BACKUP_DIR/$FILENAME"
else
    echo "❌ Ошибка при создании бэкапа!"
    exit 1
fi

# Очистка старых бэкапов (старше 7 дней)
find "$BACKUP_DIR" -type f -mtime +7 -delete
echo "🎉 Готово."
