import requests
import json

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

# 1. Получаем метаданные для проверки link_id
print("="*60)
print("1. ПРОВЕРКА МЕТАДАННЫХ (ищем link_id)")
print("="*60)
metadata_response = requests.get(
    f"https://cloud.seatable.io/api-gateway/api/v2/dtables/{BASE_UUID}/metadata/",
    headers=headers
)
metadata = metadata_response.json()

# Ищем колонку-связь в Trapping
for table in metadata['metadata']['tables']:
    if table['name'] == 'Trapping':
        for col in table['columns']:
            if col['type'] == 'link':
                print(f"\nКолонка связи: {col['name']} (key: {col['key']})")
                print(f"link_id: {col['data'].get('link_id')}")
                print(f"table_id: {col['data'].get('table_id')}")
                print(f"other_table_id: {col['data'].get('other_table_id')}")
                link_id = col['data'].get('link_id')
                other_table_id = col['data'].get('other_table_id')
                
                # Находим имя связанной таблицы
                for t in metadata['metadata']['tables']:
                    if t['_id'] == other_table_id:
                        other_table_name = t['name']
                        print(f"other_table_name: {other_table_name}")

# 2. Получаем последнюю созданную строку в Trapping
print("\n" + "="*60)
print("2. ПОСЛЕДНЯЯ СТРОКА В TRAPPING")
print("="*60)
rows_response = requests.get(
    f"https://cloud.seatable.io/api-gateway/api/v2/dtables/{BASE_UUID}/rows/",
    headers=headers,
    params={"table_name": "Trapping", "limit": 1, "direction": "desc"}
)
if rows_response.status_code == 200:
    last_row = rows_response.json()['rows'][0]
    print(f"ID строки: {last_row['_id']}")
    print(f"Текущие связи (275x): {last_row.get('275x', [])}")

# 3. Получаем строку из Table2
print("\n" + "="*60)
print("3. ПЕРВАЯ СТРОКА В TABLE2")
print("="*60)
table2_response = requests.get(
    f"https://cloud.seatable.io/api-gateway/api/v2/dtables/{BASE_UUID}/rows/",
    headers=headers,
    params={"table_name": "Table2", "limit": 1}
)
if table2_response.status_code == 200:
    first_row = table2_response.json()['rows'][0]
    print(f"ID строки: {first_row['_id']}")
    print(f"Name: {first_row.get('0000', 'N/A')}")

# 4. Пробуем создать связь разными способами
print("\n" + "="*60)
print("4. ТЕСТИРОВАНИЕ СОЗДАНИЯ СВЯЗИ")
print("="*60)

# Используем реальные ID
new_row_id = last_row['_id']
linked_row_id = first_row['_id']

# Вариант 1: Стандартный формат
print("\n--- Вариант 1: Стандартный формат ---")
payload1 = {
    "table_name": "Trapping",
    "other_table_name": "Table2",
    "link_id": link_id,
    "other_rows_ids_map": {
        new_row_id: [linked_row_id]
    }
}
print(f"Payload: {json.dumps(payload1, indent=2)}")

response1 = requests.post(
    f"https://cloud.seatable.io/api-gateway/api/v2/dtables/{BASE_UUID}/links/",
    headers=headers,
    json=payload1
)
print(f"Статус: {response1.status_code}")
print(f"Ответ: {response1.text}")

# Вариант 2: Используем table_id вместо имён
print("\n--- Вариант 2: Используем table_id ---")
payload2 = {
    "table_name": "Trapping",
    "other_table_name": "Table2",
    "link_id": link_id,
    "table_id": "0000",  # ID таблицы Trapping
    "other_table_id": other_table_id,  # ID таблицы Table2
    "other_rows_ids_map": {
        new_row_id: [linked_row_id]
    }
}
print(f"Payload: {json.dumps(payload2, indent=2)}")

response2 = requests.post(
    f"https://cloud.seatable.io/api-gateway/api/v2/dtables/{BASE_UUID}/links/",
    headers=headers,
    json=payload2
)
print(f"Статус: {response2.status_code}")
print(f"Ответ: {response2.text}")

# Вариант 3: Другой порядок (связанная таблица -> основная)
print("\n--- Вариант 3: Обратная связь ---")
payload3 = {
    "table_name": "Table2",
    "other_table_name": "Trapping",
    "link_id": link_id,
    "other_rows_ids_map": {
        linked_row_id: [new_row_id]
    }
}
print(f"Payload: {json.dumps(payload3, indent=2)}")

response3 = requests.post(
    f"https://cloud.seatable.io/api-gateway/api/v2/dtables/{BASE_UUID}/links/",
    headers=headers,
    json=payload3
)
print(f"Статус: {response3.status_code}")
print(f"Ответ: {response3.text}")

# Вариант 4: Используем ключ колонки "275x"
print("\n--- Вариант 4: Используем column_key ---")
payload4 = {
    "table_name": "Trapping",
    "other_table_name": "Table2",
    "link_id": link_id,
    "column_key": "275x",
    "other_rows_ids_map": {
        new_row_id: [linked_row_id]
    }
}
print(f"Payload: {json.dumps(payload4, indent=2)}")

response4 = requests.post(
    f"https://cloud.seatable.io/api-gateway/api/v2/dtables/{BASE_UUID}/links/",
    headers=headers,
    json=payload4
)
print(f"Статус: {response4.status_code}")
print(f"Ответ: {response4.text}")

# 5. Проверяем результат
print("\n" + "="*60)
print("5. ПРОВЕРКА РЕЗУЛЬТАТА")
print("="*60)
check_response = requests.get(
    f"https://cloud.seatable.io/api-gateway/api/v2/dtables/{BASE_UUID}/rows/",
    headers=headers,
    params={"table_name": "Trapping", "limit": 1, "direction": "desc"}
)
if check_response.status_code == 200:
    last_row = check_response.json()['rows'][0]
    print(f"Связи строки {last_row['_id']}:")
    print(json.dumps(last_row.get('275x', []), indent=2, ensure_ascii=False))