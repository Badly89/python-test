import requests

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

# 2. Получаем данные из таблицы
response = requests.get(
    f"https://cloud.seatable.io/api-gateway/api/v2/dtables/{BASE_UUID}/rows/",
    headers={"accept": "application/json", "authorization": f"Bearer {base_token}"},
    params={"table_name": "Trapping", "limit": 100}
)

if response.status_code == 200:
    data = response.json()
    print(f"Получено строк: {len(data['rows'])}")
    
    for row in data['rows'][:5]:
        print(row)
else:
    print(f"Ошибка: {response.status_code}")
    print(response.text)