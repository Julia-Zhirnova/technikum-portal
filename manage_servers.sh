#!/bin/bash

# Скрипт для управления серверами Django и Vite

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PROJECT_DIR="/home/redoslek/projects/technikum-portal"

# Функция для запуска серверов
start_servers() {
    echo -e "${GREEN}🚀 Запуск серверов...${NC}"
    
    # Запуск Django в фоне
    cd "$PROJECT_DIR"
    nohup python manage.py runserver 0.0.0.0:8000 > django.log 2>&1 &
    DJANGO_PID=$!
    echo $DJANGO_PID > django.pid
    echo -e "${GREEN}✅ Django запущен (PID: $DJANGO_PID)${NC}"
    
    # Запуск Vite в фоне
    cd "$PROJECT_DIR/frontend"
    nohup npm run dev > vite.log 2>&1 &
    VITE_PID=$!
    echo $VITE_PID > vite.pid
    echo -e "${GREEN}✅ Vite запущен (PID: $VITE_PID)${NC}"
    
    echo -e "${GREEN}🌐 Доступно по адресу: http://localhost:5173${NC}"
}

# Функция для остановки серверов
stop_servers() {
    echo -e "${YELLOW}🛑 Остановка серверов...${NC}"
    
    # Остановка Django
    if [ -f "$PROJECT_DIR/django.pid" ]; then
        DJANGO_PID=$(cat "$PROJECT_DIR/django.pid")
        if ps -p $DJANGO_PID > /dev/null; then
            kill $DJANGO_PID
            echo -e "${YELLOW}✅ Django остановлен (PID: $DJANGO_PID)${NC}"
        fi
        rm "$PROJECT_DIR/django.pid"
    else
        echo -e "${RED}⚠️  Django PID файл не найден${NC}"
    fi
    
    # Остановка Vite
    if [ -f "$PROJECT_DIR/frontend/vite.pid" ]; then
        VITE_PID=$(cat "$PROJECT_DIR/frontend/vite.pid")
        if ps -p $VITE_PID > /dev/null; then
            kill $VITE_PID
            echo -e "${YELLOW}✅ Vite остановлен (PID: $VITE_PID)${NC}"
        fi
        rm "$PROJECT_DIR/frontend/vite.pid"
    else
        echo -e "${RED}⚠️  Vite PID файл не найден${NC}"
    fi
    
    # Дополнительная проверка процессов
    pkill -f "python manage.py runserver" 2>/dev/null
    pkill -f "npm run dev" 2>/dev/null
    
    echo -e "${YELLOW}✅ Все серверы остановлены${NC}"
}

# Функция для проверки статуса
check_status() {
    echo -e "${GREEN}📊 Статус серверов:${NC}"
    
    if pgrep -f "python manage.py runserver" > /dev/null; then
        echo -e "${GREEN}✅ Django работает${NC}"
    else
        echo -e "${RED}❌ Django не работает${NC}"
    fi
    
    if pgrep -f "npm run dev" > /dev/null; then
        echo -e "${GREEN}✅ Vite работает${NC}"
    else
        echo -e "${RED}❌ Vite не работает${NC}"
    fi
}

# Главное меню
while true; do
    echo ""
    echo "╔═══════════════════════════════════════╗"
    echo "║   Управление серверами техникум-портал ║"
    echo "╠═══════════════════════════════════════╣"
    echo "║ 1. 🚀 Запустить серверы               ║"
    echo "║ 2. 🛑 Остановить серверы              ║"
    echo "║ 3. 📊 Проверить статус                ║"
    echo "║ 4. 🔄 Перезапустить серверы           ║"
    echo "║ 5. 🚪 Выход                           ║"
    echo "╚═══════════════════════════════════════╝"
    echo ""
    read -p "Выберите действие (1-5): " choice
    
    case $choice in
        1)
            start_servers
            ;;
        2)
            stop_servers
            ;;
        3)
            check_status
            ;;
        4)
            echo -e "${YELLOW}🔄 Перезапуск серверов...${NC}"
            stop_servers
            sleep 2
            start_servers
            ;;
        5)
            echo -e "${GREEN}👋 До свидания!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Неверный выбор${NC}"
            ;;
    esac
done
