# Docker-развёртывание ТехноПортал

## Быстрый старт

### 1. Требования
- Docker 20.10+ или Podman 4.0+
- Docker Compose 2.0+
- RAM: 2 ГБ, Диск: 10 ГБ

### 2. Установка (РЕД ОС)
```
sudo dnf install -y docker docker-compose
sudo systemctl --user enable --now podman.socket
export DOCKER_HOST=unix:///run/user/$(id -u)/podman/podman.sock
echo 'export DOCKER_HOST=unix:///run/user/$(id -u)/podman/podman.sock' >> ~/.bashrc
```

### 3. Запуск
```
git clone <repo-url> && cd technikum-portal
cp .env.example .env && nano .env
docker-compose up -d --build
```

### 4. Доступ
- Frontend: http://localhost:5174
- Backend: http://localhost:8001
- API: http://localhost:8001/api/

## Полезные команды

| Команда | Описание |
|---------|----------|
| `docker-compose ps` | Статус |
| `docker-compose logs -f` | Логи |
| `docker-compose exec backend bash` | Shell |
| `docker-compose exec backend python manage.py migrate` | Миграции |
| `docker-compose exec backend pytest` | Тесты |
| `docker-compose down` | Остановка |
| `docker-compose down -v` | Остановка + удаление данных |

## Бэкапы
```
./scripts/docker-backup.sh
./scripts/docker-restore.sh backups/backup_XXX.sql
```

## Перенос на другой сервер
```
# Старый: ./scripts/docker-backup.sh && tar -czf media.tar.gz media/
# scp -r . user@new-server:/path/
# Новый: docker-compose up -d && ./scripts/docker-restore.sh backups/XXX.sql
```

## Порты (альтернативные, не конфликтуют с локальными)
- PostgreSQL: 5433 (внутри 5432)
- Redis: 6378 (внутри 6379)
- Backend: 8001 (внутри 8000)
- Frontend: 5174 (внутри 80)

## Устранение неполадок
```
docker-compose logs -f
docker-compose restart postgres
docker-compose down -v && docker-compose build --no-cache && docker-compose up -d
```
