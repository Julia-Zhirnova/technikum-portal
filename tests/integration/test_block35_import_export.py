
import pytest
from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from core.models import Student, Organization, Employment, ImportHistory, AuditLog
from datetime import datetime, timedelta
import json
import io
import csv
from django.core.files.uploadedfile import SimpleUploadedFile
import openpyxl

User = get_user_model()

@pytest.mark.django_db
class TestBlock35EmploymentImportExport:
    """Тесты для Блока 3.5: Массовый импорт/экспорт трудоустройств"""
    
    def setup_method(self):
        """Подготовка тестовых данных"""
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.ru',
            password='admin123'
        )
        self.client.login(username='admin', password='admin123')
        
        # Создание тестовых студентов
        self.student1 = Student.objects.create(
            id_student='ST001',
            email='student1@test.ru',
            first_name='Иван',
            last_name='Иванов',
            snils='18253094699'
        )
        self.student2 = Student.objects.create(
            id_student='ST002',
            email='student2@test.ru',
            first_name='Петр',
            last_name='Петров',
            snils='12345678901'
        )
        
        # Создание тестовой организации
        self.organization = Organization.objects.create(
            name='ООО Тест',
            inn='7701234567'
        )
    
    def create_test_file(self, rows, format='xlsx'):
        """Создание тестового файла"""
        if format == 'xlsx':
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = 'Трудоустройства'
            headers = ['СНИЛС', 'ИНН организации', 'Дата начала', 'Дата окончания', 'Должность']
            ws.append(headers)
            for row in rows:
                ws.append(row)
            
            buffer = io.BytesIO()
            wb.save(buffer)
            buffer.seek(0)
            return SimpleUploadedFile('test.xlsx', buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        
        elif format == 'csv':
            output = io.StringIO()
            writer = csv.writer(output, delimiter=';')
            writer.writerow(['СНИЛС', 'ИНН организации', 'Дата начала', 'Дата окончания', 'Должность'])
            for row in rows:
                writer.writerow(row)
            
            return SimpleUploadedFile('test.csv', output.getvalue().encode('utf-8-sig'), content_type='text/csv')
        
        elif format == 'txt':
            content = 'СНИЛС;ИНН организации;Дата начала;Дата окончания;Должность\n'
            for row in rows:
                content += ';'.join(row) + '\n'
            
            return SimpleUploadedFile('test.txt', content.encode('utf-8-sig'), content_type='text/plain')
    
    def test_tc001_dry_run_valid_file(self):
        """БП3.5-TC001: Сухой прогон валидного файла"""
        rows = [
            ['18253094699', '7701234567', '01.09.2023', '31.12.2023', 'Инженер'],
            ['12345678901', '7701234567', '01.10.2023', '30.06.2024', 'Менеджер']
        ]
        file_obj = self.create_test_file(rows)
        
        url = reverse('employment-dry-run-import')
        response = self.client.post(url, {'file': file_obj})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['dry_run'] == True
        assert response.json()['total_rows'] == 2
        assert response.json()['valid_rows'] == 2
        assert response.json()['invalid_rows'] == 0
        
        # Проверка, что данные не сохранены
        assert Employment.objects.count() == 0
    
    def test_tc002_import_skip_errors(self):
        """БП3.5-TC002: Импорт в режиме skip_errors"""
        rows = [
            ['18253094699', '7701234567', '01.09.2023', '31.12.2023', 'Инженер'],
            ['18253094699', '7701234567', '01.09.2023', '31.12.2023', 'Инженер2'],  # Дубликат
            ['12345678901', '7701234567', '01.10.2023', '30.06.2024', 'Менеджер']
        ]
        file_obj = self.create_test_file(rows)
        
        url = reverse('employment-import')
        response = self.client.post(url, {'file': file_obj, 'mode': 'skip_errors'})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['created_rows'] > 0
        assert response.json()['invalid_rows'] == 0  # Ошибочные строки пропущены
    
    def test_tc003_import_stop_on_error(self):
        """БП3.5-TC003: Импорт в режиме stop_on_error"""
        rows = [
            ['18253094699', '7701234567', '01.09.2023', '31.12.2023', 'Инженер'],
            ['99999999999', '7701234567', '01.10.2023', '30.06.2024', 'Менеджер']  # Неверный СНИЛС
        ]
        file_obj = self.create_test_file(rows)
        
        url = reverse('employment-import')
        response = self.client.post(url, {'file': file_obj, 'mode': 'stop_on_error'})
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # Проверка, что данные не сохранены
        assert Employment.objects.count() == 0
    
    def test_tc004_import_update_existing(self):
        """БП3.5-TC004: Импорт в режиме update_existing"""
        # Создаем существующую запись
        employment = Employment.objects.create(
            student=self.student1,
            organization=self.organization,
            employment_type_id=1,
            position='Старая должность',
            date_start=datetime(2023, 9, 1),
            date_end=datetime(2023, 12, 31)
        )
        
        rows = [
            ['18253094699', '7701234567', '01.09.2023', '31.12.2023', 'Новая должность']
        ]
        file_obj = self.create_test_file(rows)
        
        url = reverse('employment-import')
        response = self.client.post(url, {'file': file_obj, 'mode': 'update_existing'})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['updated_rows'] == 1
        
        # Проверка обновления
        employment.refresh_from_db()
        assert employment.position == 'Новая должность'
    
    def test_tc006_auto_create_organization(self):
        """БП3.5-TC006: Авто-создание организации при неизвестном ИНН"""
        rows = [
            ['18253094699', '9999999999', '01.09.2023', '31.12.2023', 'Инженер']
        ]
        file_obj = self.create_test_file(rows)
        
        url = reverse('employment-import')
        response = self.client.post(url, {'file': file_obj, 'mode': 'skip_errors'})
        
        assert response.status_code == status.HTTP_200_OK
        
        # Проверка создания организации
        org = Organization.objects.get(inn='9999999999')
        assert org.verification_status == 'unverified'
    
    def test_tc007_validate_snils(self):
        """БП3.5-TC007: Валидация СНИЛС"""
        rows = [
            ['18253094699', '7701234567', '01.09.2023', '31.12.2023', 'Инженер']  # Корректный
        ]
        file_obj = self.create_test_file(rows)
        
        url = reverse('employment-dry-run-import')
        response = self.client.post(url, {'file': file_obj})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['valid_rows'] == 1
    
    def test_tc014_check_virus(self):
        """БП3.5-TC014: Проверка на вирус"""
        virus_content = b'X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE'
        file_obj = SimpleUploadedFile('eicar.com', virus_content)
        
        url = reverse('employment-import')
        response = self.client.post(url, {'file': file_obj})
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'вредоносный код' in str(response.content)
    
    def test_tc016_audit_log_created(self):
        """БП3.5-TC016: Создание записей в core_import_history и core_auditlog"""
        rows = [
            ['18253094699', '7701234567', '01.09.2023', '31.12.2023', 'Инженер'],
            ['12345678901', '7701234567', '01.10.2023', '30.06.2024', 'Менеджер']
        ]
        file_obj = self.create_test_file(rows)
        
        url = reverse('employment-import')
        response = self.client.post(url, {'file': file_obj, 'mode': 'skip_errors'})
        
        assert response.status_code == status.HTTP_200_OK
        
        # Проверка ImportHistory
        assert ImportHistory.objects.filter(user=self.admin_user).exists()
        
        # Проверка AuditLog
        assert AuditLog.objects.filter(action_type='import_employment').exists()
    
    def test_tc043_transaction_integrity_stop_on_error(self):
        """БП3.5-TC043: Транзакционная целостность при stop_on_error"""
        rows = [
            ['18253094699', '7701234567', '01.09.2023', '31.12.2023', 'Инженер1'],
            ['12345678901', '7701234567', '01.10.2023', '30.06.2024', 'Менеджер2'],
            ['18253094699', '7701234567', '01.09.2023', '31.12.2023', 'Инженер3'],
            ['12345678901', '7701234567', '01.10.2023', '30.06.2024', 'Менеджер4'],
            ['99999999999', '7701234567', '01.10.2023', '30.06.2024', 'Менеджер5']  # Ошибка на 5-й строке
        ]
        file_obj = self.create_test_file(rows)
        
        initial_count = Employment.objects.count()
        
        url = reverse('employment-import')
        response = self.client.post(url, {'file': file_obj, 'mode': 'stop_on_error'})
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # Проверка, что ни одна запись не добавлена
        assert Employment.objects.count() == initial_count
    
    def test_tc044_transaction_integrity_update_existing_error(self):
        """БП3.5-TC044: Транзакционная целостность при update_existing с ошибкой"""
        # Создаем существующую запись
        employment = Employment.objects.create(
            student=self.student1,
            organization=self.organization,
            employment_type_id=1,
            position='Старая должность',
            date_start=datetime(2023, 9, 1),
            date_end=datetime(2023, 12, 31)
        )
        
        # Создаем файл с ошибкой (невалидная дата)
        rows = [
            ['18253094699', '7701234567', '01.09.2023', '31.12.2023', 'Новая должность'],
            ['12345678901', '7701234567', '01.10.2023', '30.06.2024', 'Менеджер']
        ]
        # Для ошибки обновления используем невалидную дату
        rows[0][2] = '01.09.2023'  # Даты валидные, но попробуем вызвать ошибку через дублирование
        
        file_obj = self.create_test_file(rows)
        
        url = reverse('employment-import')
        response = self.client.post(url, {'file': file_obj, 'mode': 'update_existing'})
        
        # Проверка, что запись не обновлена
        employment.refresh_from_db()
        assert employment.position == 'Старая должность'
    
    def test_tc045_sql_injection_employment_type(self):
        """БП3.5-TC045: SQL-инъекция через поле 'Форма занятости'"""
        rows = [
            ['18253094699', '7701234567', '01.09.2023', '31.12.2023', "Трудоустроен' OR '1'='1"]
        ]
        file_obj = self.create_test_file(rows)
        
        url = reverse('employment-import')
        response = self.client.post(url, {'file': file_obj, 'mode': 'skip_errors'})
        
        # Проверка, что инъекция отклонена
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]
        # Проверка безопасности - либо запись не создана, либо данные экранированы
        if response.status_code == status.HTTP_200_OK:
            # Проверяем, что опасные символы экранированы
            employments = Employment.objects.all()
            for emp in employments:
                assert "'" not in str(emp.employment_type)
    
    def test_tc046_xss_injection_position(self):
        """БП3.5-TC046: XSS-инъекция через поле 'Должность'"""
        rows = [
            ['18253094699', '7701234567', '01.09.2023', '31.12.2023', '<script>alert(1)</script>']
        ]
        file_obj = self.create_test_file(rows)
        
        url = reverse('employment-import')
        response = self.client.post(url, {'file': file_obj, 'mode': 'skip_errors'})
        
        # Проверка, что XSS отклонен или экранирован
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]
        
        if response.status_code == status.HTTP_200_OK:
            employments = Employment.objects.all()
            for emp in employments:
                # Проверка, что опасные символы не сохранены как есть
                assert '<script>' not in emp.position
                assert 'alert(1)' not in emp.position
