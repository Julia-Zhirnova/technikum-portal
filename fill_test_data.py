#!/usr/bin/env python
"""
Скрипт заполнения красивых тестовых данных для студента Иванова И.И.
СНИЛС: 987-654-321 02

Скрипт идемпотентный — можно запускать многократно.
Перед запуском обязательно сделайте бэкап: ./backup_db.sh
"""
import os
import sys
import django
from datetime import date
from pathlib import Path

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from core.models import (
    User, Student, Group, Order,
    Passport, Health, Military, Family, FamilyMember,
    Profile, EducationInstitution
)

# Константы
STUDENT_SNILS = '987-654-321 02'
MEDIA_ROOT = Path(settings.MEDIA_ROOT)


def create_placeholder_pdf(filepath: Path, title: str = "Document"):
    """Создаёт минимальный валидный PDF-файл (только ASCII)."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # Минимальный валидный PDF 1.4 (только ASCII-символы)
    pdf_content = f"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< /Length 100 >>
stream
BT
/F1 18 Tf
50 750 Td
({title}) Tj
/F1 12 Tf
0 -30 Td
(Test document for portal) Tj
0 -20 Td
(Student: Ivanov Ivan) Tj
ET
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000266 00000 n 
0000000418 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
495
%%EOF"""
    filepath.write_text(pdf_content, encoding='latin-1')
    print(f"  ✅ Создан PDF: {filepath}")


def create_test_photo(filepath: Path):
    """Создаёт тестовое фото-заглушку."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # Пробуем использовать Pillow
    try:
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new('RGB', (400, 500), color=(200, 220, 255))
        draw = ImageDraw.Draw(img)
        
        # Рисуем круг (аватар)
        draw.ellipse([100, 50, 300, 250], fill=(100, 150, 200), outline=(50, 100, 150), width=3)
        
        # Добавляем текст
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except:
            font = ImageFont.load_default()
            small_font = font
        
        draw.text((140, 130), "ИИ", fill=(255, 255, 255), font=font)
        draw.text((90, 300), "Иванов Иван", fill=(30, 30, 30), font=small_font)
        draw.text((110, 330), "Студент ИС-24", fill=(80, 80, 80), font=small_font)
        
        img.save(filepath, 'JPEG', quality=90)
        print(f"  ✅ Создано фото через Pillow: {filepath}")
        return
    except ImportError:
        pass
    
    # Если Pillow нет — используем ImageMagick
    try:
        import subprocess
        subprocess.run([
            'convert', '-size', '400x500', 'xc:#C8DCFF',
            '-fill', '#6496C8', '-draw', 'circle 200,150 200,250',
            '-fill', 'white', '-pointsize', '48', '-gravity', 'Center',
            '-annotate', '+0-50', 'ИИ',
            '-fill', '#1E1E1E', '-pointsize', '20',
            '-annotate', '+0+80', 'Иванов Иван',
            str(filepath)
        ], check=True)
        print(f"  ✅ Создано фото через ImageMagick: {filepath}")
        return
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    
    # Фолбэк: создаём пустой файл (невалидный JPG, но путь будет работать)
    filepath.write_bytes(b'\xff\xd8\xff\xe0' + b'\x00' * 100)
    print(f"  ⚠️  Создан файл-заглушка (нет Pillow/ImageMagick): {filepath}")


def main():
    print("=" * 60)
    print("🚀 Заполнение тестовых данных для Иванова И.И.")
    print("=" * 60)
    
    # 1. Ищем студента
    print("\n📋 Поиск студента...")
    try:
        student = Student.objects.get(snils=STUDENT_SNILS)
        print(f"  ✅ Найден: {student}")
    except Student.DoesNotExist:
        print(f"  ❌ Студент со СНИЛС {STUDENT_SNILS} не найден!")
        print("  Проверьте, что база данных импортирована.")
        sys.exit(1)
    
    user = student.user
    if not user:
        print("  ❌ У студента нет связанного пользователя!")
        sys.exit(1)
    
    print(f"  👤 Пользователь: {user.get_full_name()} ({user.email})")
    
    # 2. Обновляем пользователя
    print("\n👤 Обновление пользователя...")
    user.last_name = 'Иванов'
    user.first_name = 'Иван'
    user.middle_name = 'Иванович'
    user.email = 'ivanov.ii@test.ru'
    user.requires_password_change = False
    user.save()
    print(f"  ✅ ФИО: {user.get_full_name()}")
    
    # 3. Обновляем паспорт
    print("\n📄 Обновление паспорта...")
    passport, _ = Passport.objects.get_or_create(
        id_passport=student.passport_id or 347,
        defaults={
            'is_foreign': False,
            'series_number': '4619 123456',
            'issue_date': date(2023, 3, 15),
            'issuer': 'ГУ МВД РОССИИ ПО МОСКОВСКОЙ ОБЛАСТИ',
            'unit_code': '502-011',
            'region_city': 'Московская область, г. Люберцы',
            'address_detail': 'обл. Московская, г. Люберцы, ул. Зеленая, д. 7, кв. 7',
            'fact_region': 'Московская область',
            'fact_detail': 'обл. Московская, г. Люберцы, ул. Зеленая, д. 7, кв. 7',
            'temp_reg': False,
            'file_path': 'docs/passports/ivanov_passport.pdf',
        }
    )
    if not student.passport:
        student.passport = passport
    print(f"  ✅ Паспорт: {passport.series_number}")
    
    # 4. Обновляем здоровье
    print("\n🏥 Обновление здоровья...")
    health, _ = Health.objects.get_or_create(
        id_health=student.health_id or 347,
        defaults={
            'status': 'здоров',
            'oms_number': '7712345678901234',
            'oms_date': date(2020, 6, 10),
            'oms_issuer': 'ООО "СК "БАСК-Мед"',
            'oms_scan': 'docs/health/ivanov_oms.pdf',
        }
    )
    if not student.health:
        student.health = health
    print(f"  ✅ Полис ОМС: {health.oms_number}")
    
    # 5. Обновляем воинский учёт
    print("\n🎖️  Обновление воинского учёта...")
    military, _ = Military.objects.get_or_create(
        id_military=student.military_id or 347,
        defaults={
            'registration_number': 'СА №1239900',
            'commissariat': 'Военный комиссариат городов Люберцы, Лыткарино, Дзержинский и Котельники Московской области',
            'issue_date': date(2024, 5, 20),
            'fitness_category': 'А',
            'file_path': 'docs/military/ivanov_military.pdf',
        }
    )
    if not student.military:
        student.military = military
    print(f"  ✅ Приписное: {military.registration_number}")
    
    # 6. Обновляем образование
    print("\n🎓 Обновление образования...")
    education, _ = EducationInstitution.objects.get_or_create(
        id_institution=student.education_id or 347,
        defaults={
            'name': 'МБОУ "Люберецкая СОШ №1"',
            'type': 'лицей',
            'profile': 'Информационно-технологический',
            'graduation_date': date(2025, 5, 30),
        }
    )
    if not student.education:
        student.education = education
    print(f"  ✅ Школа: {education.name}")
    
    # 7. Обновляем профиль
    print("\n💼 Обновление профиля...")
    profile, _ = Profile.objects.get_or_create(
        id_profile=student.profile_id or 347,
        defaults={
            'it_skills': ['программирование', 'создание сайтов'],
            'programming_langs': 'Python, JavaScript, HTML, CSS',
            'creative_skills': ['рисование', 'фотография'],
            'school_participation': ['олимпиады по математике', 'школьный актив'],
            'college_participation': ['IT-кружок'],
            'achievements': ['1 место в школьной олимпиаде по информатике'],
            'hobbies': 'Программирование, чтение, спорт',
            'extra_edu': 'Курсы веб-разработки на Stepik',
            'social_networks': [
                {'platform': 'ВКонтакте', 'link': 'https://vk.com/ivanov_ivan'},
                {'platform': 'Telegram', 'link': '@ivanov_ivan'},
            ],
            'motivation_college': ['по совету взрослых', 'близость к дому'],
            'motivation_specialty': ['считаю её перспективной и востребованной'],
            'desired_participation': ['работа студенческого актива'],
            'foreign_langs': [
                {'язык': 'английский', 'уровень': 'B1'},
                {'язык': 'немецкий', 'уровень': 'A1'},
            ],
            'drivers_license': ['B'],
            'sports_ranks': '3 юношеский разряд по плаванию',
            'character': 'Ответственный, исполнительный, легко находит общий язык с коллективом',
        }
    )
    if not student.profile:
        student.profile = profile
    print(f"  ✅ Профиль обновлён")
    
    # 8. Обновляем семью
    print("\n👨‍👩‍👧 Обновление семьи...")
    family, _ = Family.objects.get_or_create(
        id_family=student.family_id or 347,
        defaults={
            'minors_count': 1,
            'adults_count': 2,
            'status': 'полная',
            'housing_type': 'в_собственном_жилье_с_родителями',
        }
    )
    if not student.family:
        student.family = family
    
    # Создаём членов семьи
    family_members_data = [
        {
            'family': family,
            'relation': 'мать',
            'full_name': 'Иванова Мария Петровна',
            'birth_date': date(1980, 5, 15),
            'education': 'высшее: бакалавриат',
            'workplace': 'ООО "Транском"',
            'phone': '+79161234567',
            'is_pensioner': False,
            'is_svo': False,
            'is_priority_contact': True,
        },
        {
            'family': family,
            'relation': 'отец',
            'full_name': 'Иванов Пётр Сергеевич',
            'birth_date': date(1978, 11, 22),
            'education': 'высшее: специалитет',
            'workplace': 'ПАО "Газпром"',
            'phone': '+79261234567',
            'is_pensioner': False,
            'is_svo': False,
            'is_priority_contact': False,
        },
        {
            'family': family,
            'relation': 'брат',
            'full_name': 'Иванов Алексей Петрович',
            'birth_date': date(2012, 3, 10),
            'education': None,
            'workplace': 'Школа №5, 8 класс',
            'phone': None,
            'is_pensioner': False,
            'is_svo': False,
            'is_priority_contact': False,
        },
    ]
    
    # Удаляем старые члены семьи и создаём новые
    FamilyMember.objects.filter(family=family).delete()
    for member_data in family_members_data:
        FamilyMember.objects.create(**member_data)
    print(f"  ✅ Создано 3 члена семьи")
    
    # 9. Обновляем студента (связи и фото)
    print("\n📸 Обновление данных студента...")
    student.phone = '+79161234567'
    student.inn = '502712345678'
    student.birth_place = 'г. Люберцы, Московская область'
    student.pd_consent = True
    student.pd_consent_date = date(2025, 9, 1)
    student.photo_path = 'docs/students/photos/ivanov_photo.jpg'
    student.snils_file = 'docs/students/ivanov_snils.pdf'
    student.inn_file = 'docs/students/ivanov_inn.pdf'
    student.save()
    print(f"  ✅ Телефон: {student.phone}")
    print(f"  ✅ ИНН: {student.inn}")
    
    # 10. Создаём файлы-заглушки в media/
    print("\n📁 Создание файлов-заглушек...")
    
    # Фото
    photo_path = MEDIA_ROOT / 'docs/students/photos/ivanov_photo.jpg'
    create_test_photo(photo_path)
    
    # Сканы (используем только ASCII-символы для PDF)
    scans = [
        ('docs/students/ivanov_snils.pdf', 'SNILS'),
        ('docs/students/ivanov_inn.pdf', 'INN'),
        ('docs/passports/ivanov_passport.pdf', 'Passport'),
        ('docs/health/ivanov_oms.pdf', 'OMS_Policy'),
        ('docs/health/ivanov_diagnosis.pdf', 'Medical_Certificate'),
        ('docs/military/ivanov_military.pdf', 'Military_ID'),
    ]
    
    for scan_path, title in scans:
        create_placeholder_pdf(MEDIA_ROOT / scan_path, title)
    
    # Финальная проверка
    print("\n" + "=" * 60)
    print("✅ ТЕСТОВЫЕ ДАННЫЕ УСПЕШНО ЗАПОЛНЕНЫ!")
    print("=" * 60)
    print(f"\n📊 Итог:")
    print(f"  • Студент: {user.get_full_name()}")
    print(f"  • СНИЛС: {student.snils}")
    print(f"  • Группа: {student.group.id_group}")
    print(f"  • Паспорт: {passport.series_number}")
    print(f"  • ОМС: {health.oms_number}")
    print(f"  • Приписное: {military.registration_number}")
    print(f"  • Школа: {education.name}")
    print(f"  • Членов семьи: {FamilyMember.objects.filter(family=family).count()}")
    print(f"  • Фото: {student.photo_path}")
    print(f"\n🔗 Проверьте API:")
    print(f"  curl http://localhost:8000/api/student/profile/ \\")
    print(f"    -H 'Authorization: Bearer <ваш_токен>'")
    print("=" * 60)


if __name__ == '__main__':
    main()
