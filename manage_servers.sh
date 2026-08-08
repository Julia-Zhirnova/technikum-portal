#!/bin/bash
# ============================================================================
# Управление серверами ТехноПортал (Django + Vite)
# ============================================================================

PROJECT_ROOT="/home/redoslek/projects/technikum-portal"
BACKEND_PID="$PROJECT_ROOT/.pids/django.pid"
FRONTEND_PID="$PROJECT_ROOT/.pids/vite.pid"
LOG_DIR="$PROJECT_ROOT/logs"

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Создаём директории
mkdir -p "$PROJECT_ROOT/.pids" "$LOG_DIR"

# Функция проверки процесса
is_running() {
    local pid_file=$1
    local process_name=$2
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        # Проверяем, жив ли процесс
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        fi
        # PID умер, но может быть живой дочерний процесс
        if [ -n "$process_name" ]; then
            if pgrep -f "$process_name" > /dev/null 2>&1; then
                # Обновляем PID на живой процесс
                pgrep -f "$process_name" | head -1 > "$pid_file"
                return 0
            fi
        fi
        rm -f "$pid_file"
    fi
    return 1
}

# Функция запуска
start_servers() {
    echo -e "${BLUE}🚀 Запуск серверов...${NC}"
    
    # Проверка: не запущены ли уже
    if is_running "$BACKEND_PID" "manage.py runserver"; then
        echo -e "${YELLOW}⚠️  Django уже запущен (PID: $(cat $BACKEND_PID))${NC}"
    else
        cd "$PROJECT_ROOT"
        source venv/bin/activate 2>/dev/null || true
        nohup python manage.py runserver 0.0.0.0:8000 > "$LOG_DIR/django.log" 2>&1 &
        echo $! > "$BACKEND_PID"
        echo -e "${GREEN}✅ Django запущен (PID: $(cat $BACKEND_PID))${NC}"
        echo -e "   ${BLUE}URL: http://localhost:8000${NC}"
        echo -e "   ${BLUE}Лог: $LOG_DIR/django.log${NC}"
    fi
    
    if is_running "$FRONTEND_PID" "vite"; then
        echo -e "${YELLOW}⚠️  Vite уже запущен (PID: $(cat $FRONTEND_PID))${NC}"
    else
        cd "$PROJECT_ROOT/frontend"
        nohup npm run dev > "$LOG_DIR/vite.log" 2>&1 &
        echo $! > "$FRONTEND_PID"
        echo -e "${GREEN}✅ Vite запущен (PID: $(cat $FRONTEND_PID))${NC}"
        echo -e "   ${BLUE}URL: http://localhost:5173${NC}"
        echo -e "   ${BLUE}Лог: $LOG_DIR/vite.log${NC}"
    fi
    
    # Ждём старта
    echo -e "\n${BLUE}⏳ Ожидание запуска (8 сек)...${NC}"
    sleep 8
    
    # Проверяем доступность (используем /admin/ для backend, т.к. /api/ может не существовать)
    if curl -s -o /dev/null http://localhost:8000/admin/ 2>/dev/null; then
        echo -e "${GREEN}✅ Backend доступен${NC}"
    else
        echo -e "${YELLOW}⚠️  Backend ещё не отвечает (проверьте $LOG_DIR/django.log)${NC}"
    fi
    
    if curl -s -o /dev/null http://localhost:5173/ 2>/dev/null; then
        echo -e "${GREEN}✅ Frontend доступен${NC}"
    else
        echo -e "${YELLOW}⚠️  Frontend ещё не отвечает (проверьте $LOG_DIR/vite.log)${NC}"
    fi
}

# Функция остановки
stop_servers() {
    echo -e "${BLUE}🛑 Остановка серверов...${NC}"
    
    if is_running "$BACKEND_PID" "manage.py runserver"; then
        kill $(cat "$BACKEND_PID") 2>/dev/null
        # Убиваем всех детей (runserver плодит процессы)
        pkill -P $(cat "$BACKEND_PID") 2>/dev/null
        pkill -f "manage.py runserver" 2>/dev/null
        rm -f "$BACKEND_PID"
        echo -e "${GREEN}✅ Django остановлен${NC}"
    else
        echo -e "${YELLOW}⚠️  Django не запущен${NC}"
    fi
    
    if is_running "$FRONTEND_PID" "vite"; then
        kill $(cat "$FRONTEND_PID") 2>/dev/null
        pkill -P $(cat "$FRONTEND_PID") 2>/dev/null
        pkill -f "vite" 2>/dev/null
        rm -f "$FRONTEND_PID"
        echo -e "${GREEN}✅ Vite остановлен${NC}"
    else
        echo -e "${YELLOW}⚠️  Vite не запущен${NC}"
    fi
}

# Функция статуса
show_status() {
    echo -e "${BLUE}📊 Статус серверов:${NC}"
    echo ""
    
    if is_running "$BACKEND_PID" "manage.py runserver"; then
        echo -e "  ${GREEN}●${NC} Django: ${GREEN}работает${NC} (PID: $(cat $BACKEND_PID))"
        # Проверяем доступность
        if curl -s -o /dev/null http://localhost:8000/api/ 2>/dev/null; then
            echo -e "       URL: ${GREEN}http://localhost:8000${NC} ✓"
        else
            echo -e "       URL: ${YELLOW}http://localhost:8000${NC} (запускается...)"
        fi
    else
        echo -e "  ${RED}●${NC} Django: ${RED}не запущен${NC}"
    fi
    
    if is_running "$FRONTEND_PID" "vite"; then
        echo -e "  ${GREEN}●${NC} Vite:   ${GREEN}работает${NC} (PID: $(cat $FRONTEND_PID))"
        if curl -s -o /dev/null http://localhost:5173/ 2>/dev/null; then
            echo -e "       URL: ${GREEN}http://localhost:5173${NC} ✓"
        else
            echo -e "       URL: ${YELLOW}http://localhost:5173${NC} (запускается...)"
        fi
    else
        echo -e "  ${RED}●${NC} Vite:   ${RED}не запущен${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}Логи:${NC}"
    echo -e "  Backend: $LOG_DIR/django.log"
    echo -e "  Frontend: $LOG_DIR/vite.log"
}

# Функция перезапуска
restart_servers() {
    stop_servers
    sleep 2
    start_servers
}

# Главное меню
show_menu() {
    echo ""
    echo -e "${BLUE}╔═══════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║   Управление серверами ТехноПортал    ║${NC}"
    echo -e "${BLUE}╠═══════════════════════════════════════╣${NC}"
    echo -e "${BLUE}║${NC} 1. 🚀 Запустить серверы              ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC} 2. 🛑 Остановить серверы             ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC} 3. 📊 Проверить статус               ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC} 4. 🔄 Перезапустить серверы          ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC} 5. 🚪 Выход                          ${BLUE}║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════╝${NC}"
    echo ""
}

# Обработка аргументов (для скриптов/CI)
case "${1:-}" in
    start)   start_servers; exit 0 ;;
    stop)    stop_servers; exit 0 ;;
    status)  show_status; exit 0 ;;
    restart) restart_servers; exit 0 ;;
esac

# Интерактивное меню
while true; do
    show_menu
    show_status
    read -p "Выберите действие (1-5): " choice
    case $choice in
        1) start_servers ;;
        2) stop_servers ;;
        3) show_status ;;
        4) restart_servers ;;
        5) echo -e "${BLUE}👋 До свидания!${NC}"; exit 0 ;;
        *) echo -e "${RED}❌ Неверный выбор${NC}" ;;
    esac
    echo ""
    read -p "Нажмите Enter для продолжения..."
done
