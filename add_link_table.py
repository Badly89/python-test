import requests
import json
from datetime import datetime

API_TOKEN = "8ecc94c9432e9fb82b4b6b849ed050449277cbbc"
BASE_UUID = "3dfdd3a4-57a8-469d-9438-b51502b38d6f"

# Получаем токен
auth_response = requests.get(
    "https://cloud.seatable.io/api/v2.1/dtable/app-access-token/",
    headers={"accept": "application/json", "authorization": f"Bearer {API_TOKEN}"},
    params={"exp": "3d"}
)
base_token = auth_response.json()["access_token"]

headers = {
    "accept": "application/json",
    "authorization": f"Bearer {base_token}",
    "content-type": "application/json"
}

# 1. Получаем link_id
print("="*60)
print("1. ИНФОРМАЦИЯ О СВЯЗИ")
print("="*60)
metadata_response = requests.get(
    f"https://cloud.seatable.io/api-gateway/api/v2/dtables/{BASE_UUID}/metadata/",
    headers=headers
)
metadata = metadata_response.json()

for table in metadata['metadata']['tables']:
    if table['name'] == 'Trapping':
        for col in table['columns']:
            if col['type'] == 'link':
                link_id = col['data'].get('link_id')
                print(f"link_id: {link_id}")

# 2. Получаем ВСЕ строки из Table2
print("\n" + "="*60)
print("2. ВСЕ СТРОКИ В TABLE2")
print("="*60)
table2_response = requests.get(
    f"https://cloud.seatable.io/api-gateway/api/v2/dtables/{BASE_UUID}/rows/",
    headers=headers,
    params={"table_name": "Table2", "limit": 100}
)
table2_rows = table2_response.json()['rows']

print(f"Найдено строк: {len(table2_rows)}")
for i, row in enumerate(table2_rows, 1):
    print(f"  [{i}] Name: {row.get('0000', 'N/A')} | ID: {row['_id']}")

# 3. Выбираем строки для связи
print("\n" + "="*60)
print("3. ВЫБОР СТРОК ДЛЯ СВЯЗИ")
print("="*60)
print("Укажите номера строк через запятую (например: 1,3,5)")
print("Или нажмите Enter для выбора ВСЕХ строк")
choice = input("Ваш выбор: ").strip()

if choice:
    indices = [int(x.strip()) - 1 for x in choice.split(',')]
    selected_rows = [table2_rows[i] for i in indices if 0 <= i < len(table2_rows)]
else:
    selected_rows = table2_rows

linked_ids = [row['_id'] for row in selected_rows]

print(f"\nВыбрано строк для связи: {len(selected_rows)}")
for row in selected_rows:
    print(f"  - {row.get('0000', 'N/A')} (ID: {row['_id'][:16]}...)")

# 4. Создаём НОВУЮ тестовую строку
print("\n" + "="*60)
print("4. СОЗДАНИЕ НОВОЙ ТЕСТОВОЙ СТРОКИ")
print("="*60)

new_row = {
    "Текст сообщения": f"ТЕСТ СВЯЗЕЙ {datetime.now().strftime('%H:%M:%S')}",
    "ID пользователя MAX": "test_links",
    "Имя пользователя": "Тест Связей",
    "Время получения": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}

create_payload = {
    "table_name": "Trapping",
    "rows": [new_row],
    "use_column_default": False
}

create_response = requests.post(
    f"https://cloud.seatable.io/api-gateway/api/v2/dtables/{BASE_UUID}/rows/",
    headers=headers,
    json=create_payload
)

# ИСПРАВЛЕНО: проверяем и 200, и 201 статусы
if create_response.status_code in [200, 201]:
    result = create_response.json()
    
    # ИСПРАВЛЕНО: обрабатываем row_ids как список объектов
    if result.get('row_ids'):
        if isinstance(result['row_ids'][0], dict):
            # Формат: [{"_id": "..."}]
            new_row_id = result['row_ids'][0]['_id']
        else:
            # Формат: ["..."]
            new_row_id = result['row_ids'][0]
    elif result.get('first_row', {}).get('_id'):
        new_row_id = result['first_row']['_id']
    else:
        print(f"❌ Не удалось извлечь ID из ответа: {result}")
        exit()
    
    print(f"✅ Создана новая строка: {new_row_id}")
    print(f"   Статус ответа: {create_response.status_code}")
else:
    print(f"❌ Ошибка создания строки: {create_response.status_code}")
    print(create_response.text)
    exit()

# 5. Создаём связи
print("\n" + "="*60)
print("5. СОЗДАНИЕ СВЯЗЕЙ")
print("="*60)

link_payload = {
    "table_name": "Trapping",
    "other_table_name": "Table2",
    "link_id": link_id,
    "other_rows_ids_map": {
        new_row_id: linked_ids
    }
}

print(f"Payload: {json.dumps(link_payload, indent=2, ensure_ascii=False)}")

link_response = requests.post(
    f"https://cloud.seatable.io/api-gateway/api/v2/dtables/{BASE_UUID}/links/",
    headers=headers,
    json=link_payload
)

print(f"\nСтатус: {link_response.status_code}")
print(f"Ответ: {link_response.text}")

if link_response.status_code == 200:
    result = link_response.json()
    if result.get('success'):
        print("✅ СВЯЗИ УСПЕШНО СОЗДАНЫ!")
    else:
        print(f"⚠️ Ответ получен, но success != true: {result}")
else:
    print("❌ ОШИБКА СОЗДАНИЯ СВЯЗЕЙ")

# 6. ПРОВЕРЯЕМ РЕЗУЛЬТАТ
print("\n" + "="*60)
print("6. ПРОВЕРКА РЕЗУЛЬТАТА")
print("="*60)

# Получаем созданную строку через API (одиночная строка)
check_response = requests.get(
    f"https://cloud.seatable.io/api-gateway/api/v2/dtables/{BASE_UUID}/rows/{new_row_id}/",
    headers=headers,
    params={"table_name": "Trapping"}
)

if check_response.status_code == 200:
    row_data = check_response.json()
    print(f"Строка: {row_data.get('ExoQ', '')}")
    
    links = row_data.get('275x', [])
    print(f"Количество связей: {len(links)}")
    
    if links:
        print("\n✅ Связанные строки из Table2:")
        for link in links:
            print(f"  - ID: {link['row_id']}")
            print(f"    Display: {link['display_value']}")
    else:
        print("\n❌ СВЯЗЕЙ НЕТ!")
else:
    print(f"⚠️ Не удалось получить строку через GET /rows/{new_row_id}/")
    print(f"   Статус: {check_response.status_code}")
    # Альтернативная проверка через общий запрос
    print("\nПроверяем через общий запрос...")
    check_all = requests.get(
        f"https://cloud.seatable.io/api-gateway/api/v2/dtables/{BASE_UUID}/rows/",
        headers=headers,
        params={"table_name": "Trapping", "limit": 1000}
    )
    if check_all.status_code == 200:
        all_rows = check_all.json()['rows']
        for row in all_rows:
            if row['_id'] == new_row_id:
                print(f"\nНайдена строка: {row.get('ExoQ', '')}")
                links = row.get('275x', [])
                print(f"Связи: {json.dumps(links, indent=2, ensure_ascii=False)}")
                break

# 7. Проверяем обратную связь (Table2 -> Trapping)
print("\n" + "="*60)
print("7. ПРОВЕРКА ОБРАТНОЙ СВЯЗИ (Table2 -> Trapping)")
print("="*60)

for linked_id in linked_ids[:3]:
    check_linked = requests.get(
        f"https://cloud.seatable.io/api-gateway/api/v2/dtables/{BASE_UUID}/rows/{linked_id}/",
        headers=headers,
        params={"table_name": "Table2"}
    )
    
    if check_linked.status_code == 200:
        linked_row = check_linked.json()
        name = linked_row.get('0000', 'N/A')
        reverse_links = linked_row.get('zRa9', [])
        
        print(f"\nСтрока Table2: {name}")
        print(f"Обратных связей: {len(reverse_links)}")
        
        found = any(link.get('row_id') == new_row_id for link in reverse_links)
        if found:
            print(f"✅ Наша строка {new_row_id[:16]}... найдена в обратных связях!")
        else:
            print(f"❌ Наша строка НЕ найдена в обратных связях")
            print(f"   Обратные связи: {json.dumps(reverse_links, indent=2, ensure_ascii=False)}")
    else:
        print(f"⚠️ Ошибка проверки строки {linked_id}: {check_linked.status_code}")

print("\n" + "="*60)
print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
print("="*60)
print(f"\nID созданной строки: {new_row_id}")
print(f"Проверьте таблицу вручную по ссылке:")
print(f"https://cloud.seatable.io/workspace/{BASE_UUID}/")