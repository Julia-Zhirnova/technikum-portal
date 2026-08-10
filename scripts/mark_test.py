#!/usr/bin/env python3
"""Пометить статус теста в Тестовые сценарии.csv (устойчив к многострочным полям).

Использование: python scripts/mark_test.py 1.1-001 ["✅ Есть"]
"""
import sys
from pathlib import Path

CSV = Path('/home/redoslek/projects/technikum-portal/Тестовые сценарии.csv')
STATUSES = ['🔴 Новый', '🟡 Новый', '🟢 Новый', '⏳ В работе', '✅ Исправлен', '✅ Есть']

def mark(test_id: str, status: str = '✅ Есть') -> int:
    raw = CSV.read_text(encoding='utf-8')
    pos = raw.find(test_id)
    if pos == -1:
        print(f"❌ {test_id}: не найден в CSV")
        return 0
    # Ищем ближайший статус в окне после ID (покрывает многострочные поля)
    window = raw[pos:pos + 3000]
    for old in STATUSES:
        p = window.find(old)
        if p != -1:
            if old == status:
                print(f"ℹ️  {test_id}: уже помечен '{status}'")
                return 0
            abs_p = pos + p
            CSV.write_text(raw[:abs_p] + status + raw[abs_p + len(old):], encoding='utf-8')
            print(f"✅ {test_id}: '{old}' → '{status}'")
            return 1
    print(f"⚠️  {test_id}: строка найдена, но статус в окне не найден")
    return 0

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    mark(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else '✅ Есть')
