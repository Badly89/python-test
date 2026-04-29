import requests
import json

# Ваши данные
API_TOKEN = "8ecc94c9432e9fb82b4b6b849ed050449277cbbc"
BASE_UUID = "3dfdd3a4-57a8-469d-9438-b51502b38d6f"

# 1. Получаем Base-Token
auth_response = requests.get(
    "https://cloud.seatable.io/api/v2.1/dtable/app-access-token/",
    headers={"accept": "application/json", "authorization": f"Bearer {API_TOKEN}"},
    params={"exp": "3d"}
)
base_token = auth_response.json()["access_token"]

# 2. Получаем метаданные базы (структуру всех таблиц)
metadata_response = requests.get(
    f"https://cloud.seatable.io/api-gateway/api/v2/dtables/{BASE_UUID}/metadata/",
    headers={"accept": "application/json", "authorization": f"Bearer {base_token}"}
)

if metadata_response.status_code == 200:
    metadata = metadata_response.json()
    print("=== СТРУКТУРА БАЗЫ ДАННЫХ ===")
    print(json.dumps(metadata, indent=2, ensure_ascii=False))
    
    # Показываем таблицы и их колонки
    for table in metadata.get('tables', []):
        print(f"\nТаблица: {table['name']}")
        for column in table.get('columns', []):
            print(f"  - {column['name']} ({column['type']})")
            if column['type'] == 'link':
                print(f"    Связь с таблицей: {column.get('data', {}).get('table_id', 'N/A')}")
                print(f"    Тип связи: {column.get('data', {}).get('link_type', 'N/A')}")

# 3. Получаем данные из таблицы "Trapping" для просмотра
response = requests.get(
    f"https://cloud.seatable.io/api-gateway/api/v2/dtables/{BASE_UUID}/rows/",
    headers={"accept": "application/json", "authorization": f"Bearer {base_token}"},
    params={"table_name": "Trapping", "limit": 5}
)

if response.status_code == 200:
    data = response.json()
    print(f"\n=== ДАННЫЕ ТАБЛИЦЫ TRAPPING ===")
    for row in data['rows'][:2]:
        print(json.dumps(row, indent=2, ensure_ascii=False))