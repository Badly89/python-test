import requests
import re
from docx import Document
import time

# --- Настройки ---
API_TOKEN = "0d587e5bfac8f558d0a908d871c50db1fee0d047"
BASE_UUID = "572d2646-73b9-4a2f-bd19-03ca42b4ceef"
TABLE_NAME = "ТЕСТ"  # Замените на "Справочник телефонов" для финальной загрузки

DEFAULT_LEGAL_ENTITY = "Администрация города Ноябрьска"

def clean_text(text):
    if not text: return ""
    text = re.sub(r'\[?\*+([^\*]+)\*+\]?', r'\1', text)
    text = re.sub(r'[\[\]]', '', text)
    text = re.sub(r'_{2,}', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def is_all_caps(text):
    """Проверяет, состоит ли текст в основном из заглавных букв"""
    if not text: return False
    # Убираем спецсимволы и цифры для проверки
    letters = re.sub(r'[^А-ЯЁA-Z]', '', text)
    if len(letters) < 3: return False
    return letters == letters.upper()

def is_legal_entity_header(text):
    """Юридическое лицо: заглавные буквы + ключевые слова"""
    if not is_all_caps(text): return False
    keywords = ["ДУМА", "СЧЁТНАЯ ПАЛАТА", "ИЗБИРАТЕЛЬНАЯ КОМИССИЯ", "АДМИНИСТРАЦИЯ"]
    return any(keyword in text.upper() for keyword in keywords)

def is_structure_header(text):
    """Структурное подразделение: заглавные буквы + УПРАВЛЕНИЕ или ДЕПАРТАМЕНТ"""
    if not is_all_caps(text): return False
    keywords = ["УПРАВЛЕНИЕ", "ДЕПАРТАМЕНТ"]
    return any(keyword in text.upper() for keyword in keywords)

def is_department_header(text):
    """Отдел/сектор: заглавные буквы + ОТДЕЛ, СЕКТОР, АРХИВ"""
    if not is_all_caps(text): return False
    keywords = ["ОТДЕЛ", "СЕКТОР", "АРХИВ"]
    return any(keyword in text.upper() for keyword in keywords)

def parse_docx_hierarchical(filepath):
    """Парсер с чёткой иерархией"""
    doc = Document(filepath)
    rows_data = []
    
    # Текущий контекст
    current_legal_entity = DEFAULT_LEGAL_ENTITY
    current_structure = ""
    current_department = ""
    
    print("📖 Иерархия документа:")
    
    for table in doc.tables:
        for row in table.rows:
            cells = row.cells
            row_text = " ".join([clean_text(cell.text) for cell in cells])
            
            if not row_text or row_text == "СПРАВОЧНИК":
                continue
            
            # Уровень 1: Юридическое лицо
            if is_legal_entity_header(row_text):
                current_legal_entity = row_text
                current_structure = ""
                current_department = ""
                print(f"\n🏢 {current_legal_entity}")
                continue
            
            # Уровень 2: Структурное подразделение
            if is_structure_header(row_text):
                current_structure = row_text
                current_department = ""
                print(f"  📂 {current_structure}")
                continue
            
            # Уровень 3: Отдел/сектор
            if is_department_header(row_text):
                current_department = row_text
                print(f"    📁 {current_department}")
                continue
            
            # Уровень 4: Сотрудники (обычные строки)
            if len(cells) >= 5:
                fio = clean_text(cells[0].text)
                position = clean_text(cells[1].text)
                kab = clean_text(cells[2].text)
                gorod_phone = clean_text(cells[3].text).replace('\n', ', ')
                vnutr_phone = clean_text(cells[4].text)
                
                # Пропускаем пустые строки и заголовки
                if not fio or fio in ["Фамилия Имя Отчество", "СПРАВОЧНИК", "ПОСТ ОХРАНЫ"]:
                    if "приёмная" in position.lower():
                        fio = f"Приёмная {current_structure}"
                    else:
                        continue
                
                # Пропускаем строки, которые на самом деле заголовки
                if is_all_caps(fio) and len(fio) > 10:
                    continue
                
                if fio and fio != "ПОСТ ОХРАНЫ":
                    row_dict = {
                        "ФИО сотрудника": fio,
                        "Должность": position,
                        "№ каб": kab,
                        "городской номер": gorod_phone,
                        "внутренний номер": vnutr_phone,
                        "отдел/сектор": current_department,
                        "Структурное подразделение": current_structure,
                        "Наименование юридического лица": current_legal_entity
                    }
                    rows_data.append(row_dict)
    
    return rows_data

def add_rows_batch(base_token, rows_batch):
    """Добавляет пакет строк в таблицу"""
    url = f"https://ditable.yanao.ru/api-gateway/api/v2/dtables/{BASE_UUID}/rows/"
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {base_token}",
        "content-type": "application/json"
    }
    
    payload = {
        "table_name": TABLE_NAME,
        "rows": rows_batch,
        "use_column_default": False
    }
    
    response = requests.post(url, headers=headers, json=payload)
    return response

def clear_table(base_token):
    """Очищает таблицу"""
    print("\n🧹 Очистка таблицы...")
    
    url = f"https://ditable.yanao.ru/api-gateway/api/v2/dtables/{BASE_UUID}/rows/"
    headers = {"authorization": f"Bearer {base_token}"}
    
    params = {"table_name": TABLE_NAME, "limit": 1000}
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        print(f"❌ Ошибка получения строк: {response.status_code}")
        return False
    
    data = response.json()
    rows = data.get('rows', [])
    
    if not rows:
        print("  ✅ Таблица уже пуста")
        return True
    
    print(f"  Найдено строк: {len(rows)}")
    
    headers_delete = {
        "accept": "application/json",
        "authorization": f"Bearer {base_token}",
        "content-type": "application/json"
    }
    
    deleted = 0
    for row in rows:
        response = requests.delete(
            f"{url}{row['_id']}/",
            headers=headers_delete,
            params={"table_name": TABLE_NAME}
        )
        if response.status_code in [200, 204]:
            deleted += 1
            if deleted % 50 == 0:
                print(f"  ✅ Удалено {deleted}/{len(rows)} строк")
    
    print(f"  ✅ Удалено {deleted} строк")
    return True

# ========== ОСНОВНОЙ КОД ==========

print("📖 Чтение DOCX файла...")
try:
    employees = parse_docx_hierarchical("СПРАВОЧНИК Адм.-2026.docx")
    print(f"\n✅ Найдено сотрудников: {len(employees)}")
    
    # Статистика
    print("\n📊 Статистика заполнения полей:")
    fields = ["Наименование юридического лица", "Структурное подразделение", "отдел/сектор"]
    for field in fields:
        filled = sum(1 for emp in employees if emp.get(field))
        pct = filled * 100 // len(employees) if employees else 0
        print(f"  {field}: {filled}/{len(employees)} ({pct}%)")
    
    # Группировка по юр. лицам и структурам
    print("\n📋 Структура организации:")
    legal_entities = {}
    for emp in employees:
        le = emp.get("Наименование юридического лица", "Не указано")
        struct = emp.get("Структурное подразделение", "Не указано")
        dept = emp.get("отдел/сектор", "")
        
        if le not in legal_entities:
            legal_entities[le] = {}
        if struct not in legal_entities[le]:
            legal_entities[le][struct] = set()
        if dept:
            legal_entities[le][struct].add(dept)
    
    for le, structures in legal_entities.items():
        print(f"\n🏢 {le}")
        for struct, depts in list(structures.items())[:3]:
            print(f"  📂 {struct} ({sum(1 for e in employees if e.get('Структурное подразделение') == struct)} сотр.)")
            for dept in list(depts)[:3]:
                print(f"    📁 {dept}")
    
    # Примеры записей
    print("\n📋 Примеры записей:")
    for i, emp in enumerate(employees[:5]):
        print(f"\n  {i+1}. {emp['ФИО сотрудника']}")
        print(f"     Должность: {emp['Должность']}")
        print(f"     Отдел: {emp['отдел/сектор']}")
        print(f"     Структура: {emp['Структурное подразделение']}")
        print(f"     Юр.лицо: {emp['Наименование юридического лица']}")
    
except Exception as e:
    print(f"❌ Ошибка чтения DOCX: {e}")
    import traceback
    traceback.print_exc()
    exit()

# Подтверждение
print(f"\n⚠️ Найдено {len(employees)} записей.")
proceed = input("Продолжить загрузку? (y/n): ")
if proceed.lower() != 'y':
    print("❌ Загрузка отменена")
    exit()

# Авторизация
print("\n🔑 Получение токена...")
try:
    auth_response = requests.get(
        "https://ditable.yanao.ru/api/v2.1/dtable/app-access-token/",
        headers={"accept": "application/json", "authorization": f"Bearer {API_TOKEN}"},
        params={"exp": "3d"}
    )
    base_token = auth_response.json()["access_token"]
    print("✅ Токен получен")
except Exception as e:
    print(f"❌ Ошибка API: {e}")
    exit()

# Очистка
response = input(f"\n🧹 Очистить таблицу '{TABLE_NAME}'? (y/n): ")
if response.lower() == 'y':
    clear_table(base_token)

# Загрузка
print(f"\n📤 Загрузка {len(employees)} записей...")

batch_size = 10
total_loaded = 0

for i in range(0, len(employees), batch_size):
    batch = employees[i:i+batch_size]
    
    response = add_rows_batch(base_token, batch)
    
    if response.status_code in [200, 201]:
        total_loaded += len(batch)
        print(f"  ✅ Батч {i//batch_size + 1}: +{len(batch)} (всего: {total_loaded}/{len(employees)})")
    else:
        print(f"  ❌ Ошибка в батче {i//batch_size + 1}: {response.status_code}")
        for emp in batch:
            single_response = add_rows_batch(base_token, [emp])
            if single_response.status_code in [200, 201]:
                total_loaded += 1
    
    time.sleep(0.5)

print(f"\n🎉 Загружено: {total_loaded} записей")