#!/bin/bash

echo "=========================================="
echo "1. ТЕКУЩИЙ КОД КОМПОНЕНТА ProfilePage.tsx"
echo "=========================================="
echo ""

if [ -f "frontend/src/pages/ProfilePage.tsx" ]; then
    echo "Файл найден: frontend/src/pages/ProfilePage.tsx"
    echo "Размер файла: $(wc -c < frontend/src/pages/ProfilePage.tsx) байт"
    echo "Количество строк: $(wc -l < frontend/src/pages/ProfilePage.tsx)"
    echo ""
    echo "----------------------------------------"
    echo "СОДЕРЖИМОЕ ФАЙЛА:"
    echo "----------------------------------------"
    cat frontend/src/pages/ProfilePage.tsx
else
    echo "❌ Файл не найден: frontend/src/pages/ProfilePage.tsx"
fi

echo ""
echo ""
echo "=========================================="
echo "2. CURL ЗАПРОС ДЛЯ ТЕСТИРОВАНИЯ API"
echo "=========================================="
echo ""

# Получаем токен
echo "Получаем токен для пользователя..."
TOKEN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@yandex.ru", "password": "12345.Qwerty"}')

ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin).get('access', 'TOKEN_NOT_FOUND'))" 2>/dev/null)

if [ "$ACCESS_TOKEN" = "TOKEN_NOT_FOUND" ]; then
    echo "❌ Не удалось получить токен. Проверьте email и пароль."
    echo "Ответ сервера: $TOKEN_RESPONSE"
else
    echo "✅ Токен получен успешно"
    echo ""
    echo "----------------------------------------"
    echo "CURL ЗАПРОС ДЛЯ ПОЛУЧЕНИЯ ПРОФИЛЯ:"
    echo "----------------------------------------"
    echo ""
    echo "curl -X GET http://localhost:8000/api/student/profile/ \\"
    echo "  -H \"Authorization: Bearer $ACCESS_TOKEN\""
    echo ""
    echo ""
    echo "----------------------------------------"
    echo "CURL ЗАПРОС ДЛЯ ОБНОВЛЕНИЯ ПРОФИЛЯ (PATCH):"
    echo "----------------------------------------"
    echo ""
    echo "curl -X PATCH http://localhost:8000/api/student/profile/update/ \\"
    echo "  -H \"Authorization: Bearer $ACCESS_TOKEN\" \\"
    echo "  -H \"Content-Type: application/json\" \\"
    echo "  -d '{"
    echo "    \"phone\": \"+79991234567\","
    echo "    \"inn\": \"123456789012\","
    echo "    \"passport\": {"
    echo "      \"series_number\": \"4619 123456\","
    echo "      \"issue_date\": \"2024-01-15\","
    echo "      \"issuer\": \"ГУ МВД РОССИИ ПО МОСКОВСКОЙ ОБЛАСТИ\","
    echo "      \"unit_code\": \"500-066\","
    echo "      \"region_city\": \"Московская область, г. Люберцы\","
    echo "      \"address_detail\": \"ул. Зеленая, д. 7, кв. 7\","
    echo "      \"fact_region\": \"Московская область, г. Люберцы\","
    echo "      \"fact_detail\": \"ул. Зеленая, д. 7, кв. 7\","
    echo "      \"temp_reg\": false"
    echo "    },"
    echo "    \"health\": {"
    echo "      \"status\": \"здоров\","
    echo "      \"oms_number\": \"5091199794001932\","
    echo "      \"oms_date\": \"2024-01-15\","
    echo "      \"oms_issuer\": \"ЗАО МАКС-М МО\""
    echo "    },"
    echo "    \"military\": {"
    echo "      \"registration_number\": \"СА №1239900\","
    echo "      \"commissariat\": \"Военный комиссариат городов Люберцы\","
    echo "      \"issue_date\": \"2024-01-15\","
    echo "      \"fitness_category\": \"А\""
    echo "    },"
    echo "    \"family\": {"
    echo "      \"minors_count\": 2,"
    echo "      \"adults_count\": 1,"
    echo "      \"status\": \"полная\","
    echo "      \"housing_type\": \"в_собственном_жилье_с_родителями\","
    echo "      \"members\": ["
    echo "        {"
    echo "          \"relation\": \"мать\","
    echo "          \"full_name\": \"Иванова Анна Ивановна\","
    echo "          \"birth_date\": \"1977-07-07\","
    echo "          \"education\": \"высшее: бакалавриат\","
    echo "          \"workplace\": \"ООО Транском\","
    echo "          \"phone\": \"89991112233\","
    echo "          \"is_pensioner\": false,"
    echo "          \"is_svo\": false,"
    echo "          \"is_priority_contact\": true"
    echo "        }"
    echo "      ]"
    echo "    },"
    echo "    \"education\": {"
    echo "      \"name\": \"МБОУ Гимназия № 5\","
    echo "      \"type\": \"гимназия\","
    echo "      \"profile\": \"Физико-математический\","
    echo "      \"graduation_date\": \"2024-07-07\""
    echo "    },"
    echo "    \"profile\": {"
    echo "      \"it_skills\": [\"программирование\", \"создание_сайтов\"],"
    echo "      \"programming_langs\": \"Python, C++\","
    echo "      \"hobbies\": \"Футбол, программирование\","
    echo "      \"motivation_college\": [\"из-за_близости_к_дому\"],"
    echo "      \"motivation_specialty\": [\"считаю_ее_перспективной\"]"
    echo "    }"
    echo "  }'"
fi

echo ""
echo ""
echo "=========================================="
echo "3. ПРОВЕРКА ТЕКУЩИХ ДАННЫХ В БД"
echo "=========================================="
echo ""

if [ -f "manage.py" ]; then
    echo "Выполняем запрос к базе данных..."
    python3 manage.py shell << 'PYTHON_EOF'
from core.models import Student, Passport, Health, Military, Family, EducationInstitution, Profile

try:
    student = Student.objects.get(snils='111-333-999 22')
    print(f"✅ Студент найден: {student.user.get_full_name()}")
    print(f"   СНИЛС: {student.snils}")
    print(f"   Группа: {student.group.id_group}")
    print(f"   Телефон: {student.phone}")
    print(f"   ИНН: {student.inn}")
    print("")
    
    if student.passport:
        print("📄 Паспорт:")
        print(f"   Серия и номер: {student.passport.series_number}")
        print(f"   Дата выдачи: {student.passport.issue_date}")
        print(f"   Кем выдан: {student.passport.issuer}")
        print(f"   Код подразделения: {student.passport.unit_code}")
        print(f"   Регион: {student.passport.region_city}")
        print(f"   Адрес: {student.passport.address_detail}")
        print("")
    
    if student.health:
        print("🏥 Здоровье:")
        print(f"   Состояние: {student.health.status}")
        print(f"   Полис ОМС: {student.health.oms_number}")
        print(f"   Дата выдачи ОМС: {student.health.oms_date}")
        print(f"   Кем выдан ОМС: {student.health.oms_issuer}")
        print("")
    
    if student.military:
        print("🎖️ Воинский учет:")
        print(f"   Номер приписного: {student.military.registration_number}")
        print(f"   Военкомат: {student.military.commissariat}")
        print(f"   Дата выдачи: {student.military.issue_date}")
        print(f"   Категория годности: {student.military.fitness_category}")
        print("")
    
    if student.family:
        print("👨‍‍👧 Семья:")
        print(f"   Статус: {student.family.status}")
        print(f"   Тип жилья: {student.family.housing_type}")
        print(f"   Несовершеннолетних: {student.family.minors_count}")
        print(f"   Совершеннолетних: {student.family.adults_count}")
        print(f"   Членов семьи: {student.family.familymember_set.count()}")
        print("")
        
        for member in student.family.familymember_set.all():
            print(f"   - {member.full_name} ({member.relation})")
            print(f"     Дата рождения: {member.birth_date}")
            print(f"     Образование: {member.education}")
            print(f"     Место работы: {member.workplace}")
            print(f"     Телефон: {member.phone}")
            print(f"     Пенсионер: {member.is_pensioner}")
            print(f"     На СВО: {member.is_svo}")
            print(f"     Приоритетный контакт: {member.is_priority_contact}")
            print("")
    
    if student.education:
        print("🎓 Образование:")
        print(f"   Название: {student.education.name}")
        print(f"   Тип: {student.education.type}")
        print(f"   Профиль класса: {student.education.profile}")
        print(f"   Дата окончания: {student.education.graduation_date}")
        print("")
    
    if student.profile:
        print(" Профиль:")
        print(f"   IT навыки: {student.profile.it_skills}")
        print(f"   Языки программирования: {student.profile.programming_langs}")
        print(f"   Хобби: {student.profile.hobbies}")
        print(f"   Мотивация (техникум): {student.profile.motivation_college}")
        print(f"   Мотивация (специальность): {student.profile.motivation_specialty}")
        print("")
        
except Student.DoesNotExist:
    print("❌ Студент с СНИЛС 111-333-999 22 не найден")
except Exception as e:
    print(f"❌ Ошибка: {e}")
PYTHON_EOF
else
    echo "❌ Файл manage.py не найден. Убедитесь, что вы в корне проекта."
fi

echo ""
echo "=========================================="
echo "4. ПРОВЕРКА CHOICES В МОДЕЛЯХ"
echo "=========================================="
echo ""

python3 manage.py shell << 'PYTHON_EOF'
from core.models import Health, Family, EducationInstitution

print("📋 Доступные значения для Health.status:")
for choice in Health._meta.get_field('status').choices:
    print(f"   - {choice[0]}: {choice[1]}")
print("")

print("📋 Доступные значения для Family.status:")
for choice in Family._meta.get_field('status').choices:
    print(f"   - {choice[0]}: {choice[1]}")
print("")

print("📋 Доступные значения для Family.housing_type:")
for choice in Family._meta.get_field('housing_type').choices:
    print(f"   - {choice[0]}: {choice[1]}")
print("")

print("📋 Доступные значения для EducationInstitution.type:")
for choice in EducationInstitution._meta.get_field('type').choices:
    print(f"   - {choice[0]}: {choice[1]}")
print("")
PYTHON_EOF

echo ""
echo "=========================================="
echo "ГОТОВО!"
echo "=========================================="
