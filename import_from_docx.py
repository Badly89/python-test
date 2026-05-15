import requests
import re
from docx import Document
import time

# --- Настройки ---
API_TOKEN = "a7bdd18d3f4065c922ecabb3c9109e7ee6a5e3db"
BASE_UUID = "f3bf6ecc-cbb1-4da1-bfd4-82dd48137b96"
TABLE_NAME = "ТЕСТ"  # Заменил с "Trapping" на вашу таблицу

DEFAULT_LEGAL_ENTITY = "Администрация города Ноябрьска"

def clean_text(text):
    if not text: return ""
    text = re.sub(r'\[?\*+([^\*]+)\*+\]?', r'\1', text)
    text = re.sub(r'[\[\]]', '', text)
    return text.strip()

def parse_docx_advanced(filepath):
    doc = Document(filepath)
    rows_data = []
    
    current_structure = ""
    current_department = ""
    
    for table in doc.tables:
        for row in table.rows:
            cells = row.cells
            
            if len(cells) < 5:
                cell_text = clean_text(cells[0].text)
                
                if "УПРАВЛЕНИЕ" in cell_text or "ДЕПАРТАМЕНТ" in cell_text or "ДУМА" in cell_text or "КОМИССИЯ" in cell_text or "ПАЛАТА" in cell_text:
                    current_structure = cell_text
                    current_department = ""
                elif "ОТДЕЛ" in cell_text or "Сектор" in cell_text or "Архивный сектор" in cell_text:
                    current_department = cell_text
                continue
            
            fio = clean_text(cells[0].text)
            dept_dolzhnost_raw = clean_text(cells[1].text)
            kab = clean_text(cells[2].text)
            gorod_phone = clean_text(cells[3].text).replace('\n', ', ')
            vnutr_phone = clean_text(cells[4].text)
            
            if not fio or fio in ["Фамилия Имя Отчество", "СПРАВОЧНИК"] or "ПОСТ ОХРАНЫ" in fio:
                continue
                
            row_dict = {
                "ФИО сотрудника": fio,
                "Должность": dept_dolzhnost_raw,
                "№ каб": kab,
                "городской номер": gorod_phone,
                "внутренний номер": vnutr_phone,
                "отдел/сектор": current_department,
                "Структурное подразделение": current_structure,
                "Наименование юридического лица": DEFAULT_LEGAL_ENTITY
            }
            rows_data.append(row_dict)
            
    return rows_data

def add_rows_batch(base_token, rows_batch):
    """Добавляет пакет строк в таблицу (правильный формат)"""
    url = f"https://ditable.yanao.ru/api-gateway/api/v2/dtables/{BASE_UUID}/rows/"
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {base_token}",
        "content-type": "application/json"
    }
    
    payload = {
        "table_name": TABLE_NAME,
        "rows": rows_batch,  # Важно: rows должен быть массивом
        "use_column_default": False
    }
    
    response = requests.post(url, headers=headers, json=payload)
    return response

# 1. Парсим файл
print("📖 Чтение DOCX файла...")
try:
    employees = parse_docx_advanced("СПРАВОЧНИК Адм.-2026.docx")
    print(f"✅ Найдено сотрудников: {len(employees)}")
except Exception as e:
    print(f"❌ Ошибка чтения DOCX: {e}")
    exit()

# 2. Авторизация в DTable
print("🔑 Получение токена...")
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

# 3. Тестовая отправка первых 3 записей
print("\n🧪 Тестовая отправка 3 записей...")
test_batch = employees[:3]

response = add_rows_batch(base_token, test_batch)

if response.status_code in [200, 201]:
    print(f"✅ Успех! Статус: {response.status_code}")
    result = response.json()
    print(f"📊 Добавлено записей: {len(result.get('rows', []))}")
    
    # 4. Загружаем остальные данные батчами по 50
    print(f"\n📤 Загрузка всех {len(employees)} записей...")
    
    batch_size = 50
    total_loaded = 3  # первые 3 уже загружены
    
    for i in range(3, len(employees), batch_size):
        batch = employees[i:i+batch_size]
        
        response = add_rows_batch(base_token, batch)
        
        if response.status_code in [200, 201]:
            total_loaded += len(batch)
            print(f"  ✅ Батч {i//batch_size + 1}: +{len(batch)} записей (всего: {total_loaded}/{len(employees)})")
        else:
            print(f"  ❌ Ошибка в батче {i//batch_size + 1}: {response.status_code}")
            print(f"     {response.text[:200]}")
            
            # Пробуем загрузить по одной записи из проблемного батча
            print(f"     🔄 Пробуем загрузить по одной...")
            for emp in batch:
                single_response = add_rows_batch(base_token, [emp])
                if single_response.status_code in [200, 201]:
                    total_loaded += 1
                    print(f"       ➕ {emp['ФИО сотрудника']}")
                else:
                    print(f"       ⚠️ {emp['ФИО сотрудника']}: {single_response.text[:100]}")
        
        time.sleep(0.5)  # Небольшая пауза между батчами
    
    print(f"\n🎉 Загрузка завершена! Всего загружено: {total_loaded} записей")
    
else:
    print(f"❌ Ошибка тестовой отправки: {response.status_code}")
    print(f"Ответ: {response.text}")
    
    # Пробуем отправить одну запись для диагностики
    print("\n🔍 Диагностика - отправка одной записи...")
    single_test = [employees[0]]
    print(f"Отправляемые данные: {single_test[0]}")
    
    response = add_rows_batch(base_token, single_test)
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.text}")