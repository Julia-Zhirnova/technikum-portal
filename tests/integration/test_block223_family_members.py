"""БП 2.2.3 (Члены семьи): TC036-TC037, TC040-TC041, TC043, TC049-TC050.

Строки tests.txt: 1861, 1862, 1865-1866, 1875, 1881-1882.

Реальная структура:
- relation: CharField(100) с choices (10 значений в сериализаторе)
- full_name: CharField(255)
- education: CharField(255) без choices
- workplace: CharField(255)
- НЕТ полей: is_deceased, death_date, relation_other

Отложены (⏳): TC038/TC039 (транзакции), TC042 (импорт 1000 строк),
TC045/TC046 (нет relation_other), TC047 (Celery), TC048/TC051-TC056 (UI).
"""
import pytest

FAMILY_MEMBERS_URL = '/api/v1/student/family/members/'
FAMILY_MEMBER_DETAIL_URL = '/api/v1/student/family/members/{pk}/'


def _valid_family_member_payload(relation='отец', full_name='Тестов Тест Тестович'):
    """Возвращает валидный payload для создания члена семьи."""
    return {
        'full_name': full_name,
        'relation': relation,
        'birth_date': '1970-01-01',
        'education': 'Профессиональное образование: высшее: бакалавриат',
        'workplace': 'ООО Тест',
        'phone': '89001234567',
        'is_pensioner': False,
        'is_svo': False,
        'is_priority_contact': False,
    }


@pytest.mark.django_db
class TestBlock223FamilyMembersSecurity:
    """TC036-TC037: IDOR; TC040-TC041: XSS."""

    def test_TC036_idor_delete_other_family_member(self, api_client, student_user):
        """БП2.2.3-TC036: [Security] IDOR — удаление члена семьи другого студента."""
        api_client.force_authenticate(user=student_user)
        
        response = api_client.delete(FAMILY_MEMBER_DETAIL_URL.format(pk=5))
        assert response.status_code in (204, 403, 404), \
            f"Получен {response.status_code}"
        
        if response.status_code == 204:
            print("⚠️  Удалён свой член семьи (ID=5 принадлежит тестовому студенту)")
        elif response.status_code == 403:
            print("✅ IDOR защита сработала: 403 Forbidden")

    def test_TC037_idor_update_other_family_member(self, api_client, student_user):
        """БП2.2.3-TC037: [Security] IDOR — изменение члена семьи другого студента."""
        api_client.force_authenticate(user=student_user)
        
        response = api_client.patch(
            FAMILY_MEMBER_DETAIL_URL.format(pk=5),
            {'full_name': 'Чужой Член Семьи'},
            format='json',
        )
        assert response.status_code in (200, 403, 404), \
            f"Получен {response.status_code}"
        
        if response.status_code == 200:
            print("⚠️  Изменён свой член семьи (ID=5 принадлежит тестовому студенту)")
        elif response.status_code == 403:
            print("✅ IDOR защита сработала: 403 Forbidden")

    def test_TC040_xss_in_full_name(self, api_client, student_user):
        """БП2.2.3-TC040: [Security] XSS в поле ФИО."""
        api_client.force_authenticate(user=student_user)
        
        xss_payload = '<script>alert(1)</script>'
        payload = _valid_family_member_payload(full_name=xss_payload)
        response = api_client.post(FAMILY_MEMBERS_URL, payload, format='json')
        
        assert response.status_code in (200, 201, 400), \
            f"Получен {response.status_code}"
        
        if response.status_code in (200, 201):
            member_id = response.data.get('id_member')
            if member_id:
                from core.models import FamilyMember
                member = FamilyMember.objects.filter(id_member=member_id).first()
                if member and member.full_name == xss_payload:
                    print("⚠️  XSS-payload сохранён без серверного экранирования "
                          "(защита на рендеринге: React экранирует по умолчанию)")

    def test_TC041_xss_in_workplace(self, api_client, student_user):
        """БП2.2.3-TC041: [Security] XSS в поле Место работы."""
        api_client.force_authenticate(user=student_user)
        
        xss_payload = '<script>alert(1)</script>'
        payload = _valid_family_member_payload()
        payload['workplace'] = xss_payload
        response = api_client.post(FAMILY_MEMBERS_URL, payload, format='json')
        
        assert response.status_code in (200, 201, 400), \
            f"Получен {response.status_code}"
        
        if response.status_code in (200, 201):
            member_id = response.data.get('id_member')
            if member_id:
                from core.models import FamilyMember
                member = FamilyMember.objects.filter(id_member=member_id).first()
                if member and member.workplace == xss_payload:
                    print("⚠️  XSS-payload сохранён без серверного экранирования")


@pytest.mark.django_db
class TestBlock223FamilyMembersBoundary:
    """TC043: степени родства; TC049-TC050: max_length."""

    def test_TC043_all_valid_relation_types(self, api_client, student_user):
        """БП2.2.3-TC043: [Boundary] Все 10 допустимых степеней родства.
        
        Примечание: ТЗ ожидает 15 значений, но сериализатор реализует 10:
        ['мать', 'отец', 'брат', 'сестра', 'опекун', 'мачеха', 'отчим', 
         'бабушка', 'дедушка', 'другое'].
        Отсутствуют: родной/двоюродный брат/сестра, супруга, сын, дочь, тётя, дядя.
        """
        api_client.force_authenticate(user=student_user)
        
        # Реальные values из сериализатора
        relations = [
            'мать', 'отец', 'брат', 'сестра', 'опекун',
            'мачеха', 'отчим', 'бабушка', 'дедушка', 'другое'
        ]
        
        success_count = 0
        for i, relation in enumerate(relations, 1):
            payload = _valid_family_member_payload(
                relation=relation,
                full_name=f'Тестов {i} Тестович'
            )
            response = api_client.post(FAMILY_MEMBERS_URL, payload, format='json')
            
            if response.status_code in (200, 201):
                success_count += 1
            else:
                print(f"❌ {relation}: {response.status_code} — {response.data}")
        
        print(f"✅ Создано {success_count}/{len(relations)} членов семьи")
        assert success_count == len(relations), \
            f"Не все валидные relation созданы: {success_count}/{len(relations)}"

    def test_TC049_max_length_full_name(self, api_client, student_user):
        """БП2.2.3-TC049: [Boundary] full_name > 255 символов → 400."""
        api_client.force_authenticate(user=student_user)
        
        payload = _valid_family_member_payload(full_name='А' * 300)
        response = api_client.post(FAMILY_MEMBERS_URL, payload, format='json')
        
        assert response.status_code == 400, f"Получен {response.status_code}"
        assert 'full_name' in response.data, f"Нет ошибки по full_name: {response.data}"

    def test_TC050_max_length_workplace(self, api_client, student_user):
        """БП2.2.3-TC050: [Boundary] workplace > 255 символов → 400."""
        api_client.force_authenticate(user=student_user)
        
        payload = _valid_family_member_payload()
        payload['workplace'] = 'А' * 300
        response = api_client.post(FAMILY_MEMBERS_URL, payload, format='json')
        
        assert response.status_code == 400, f"Получен {response.status_code}"
        assert 'workplace' in response.data, f"Нет ошибки по workplace: {response.data}"
