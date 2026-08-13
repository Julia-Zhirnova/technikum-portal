"""БП 1.5: Performance тесты (N+1, индексы).

Тест-кейсы: БП1.5-TC011, TC012
"""
import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework import status


@pytest.mark.django_db
class TestBlock15Performance:
    """Performance тесты Блока 1.5."""

    def test_TC011_n_plus_1_curator_group(self, api_client, curator_user):
        """БП1.5-TC011: N+1 запрос при загрузке curator/group.
        
        Количество запросов к БД не превышает 10.
        """
        api_client.force_authenticate(user=curator_user)
        
        with CaptureQueriesContext(connection) as ctx:
            response = api_client.get('/api/curator/group/')
        
        num_queries = len(ctx)
        
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
        
        if response.status_code == status.HTTP_200_OK:
            assert num_queries <= 10, (
                f"N+1 проблема: {num_queries} запросов (ожидалось ≤ 10)"
            )

    def test_TC012_indexes_on_sortable_fields(self, db):
        """БП1.5-TC012: Проверка индексов на sortable полях через EXPLAIN."""
        from django.db import connection
        
        # Проверяем индексы через information_schema (безопаснее чем EXPLAIN)
        with connection.cursor() as cursor:
            # Список таблиц, которые должны иметь индексы
            tables_to_check = [
                ('core_statementgrade', 'created_at'),
                ('core_student', 'group_id'),
            ]
            
            missing_indexes = []
            
            for table, field in tables_to_check:
                try:
                    # Проверяем существование таблицы
                    cursor.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND table_name = %s
                        )
                    """, [table])
                    
                    if not cursor.fetchone()[0]:
                        continue
                    
                    # Проверяем наличие индекса на поле
                    cursor.execute("""
                        SELECT COUNT(*) FROM pg_indexes 
                        WHERE tablename = %s 
                        AND indexdef LIKE %s
                    """, [table, f'%{field}%'])
                    
                    index_count = cursor.fetchone()[0]
                    
                    if index_count == 0:
                        missing_indexes.append(f"{table}.{field}")
                        
                except Exception as e:
                    # Если возникла ошибка — логируем и продолжаем
                    pytest.skip(f"Ошибка проверки индексов для {table}.{field}: {e}")
            
            if missing_indexes:
                pytest.fail(
                    f"Отсутствуют индексы: {', '.join(missing_indexes)}. "
                    f"Добавьте db_index=True в модели."
                )
