import requests

# Ваши данные
API_TOKEN = "a30edef1455300afeac7f5b4d8a221483ea6682a"
BASE_UUID = "f3bf6ecc-cbb1-4da1-bfd4-82dd48137b96"

# 1. Получаем Base-Token (как у вас уже было)
auth_response = requests.get(
    "https://ditable.yanao.ru/api/v2.1/dtable/app-access-token/",
    headers={"accept": "application/json", "authorization": f"Bearer {API_TOKEN}"},
    params={"exp": "3d"}
)
# 1. Получаем Base-Token
auth_response = requests.get(
    "https://ditable.yanao.ru/api/v2.1/dtable/app-access-token/",
    headers={"accept": "application/json", "authorization": f"Bearer {API_TOKEN}"},
    params={"exp": "3d"}
)
base_token = auth_response.json()["access_token"]

# 2. Получаем данные из таблицы
response = requests.get(
    f"https://ditable.yanao.ru/api-gateway/api/v2/dtables/{BASE_UUID}/rows/",
    headers={"accept": "application/json", "authorization": f"Bearer {base_token}"},
    params={"table_name": "Почтовый адрес объекта", "limit": 200}
)

if response.status_code == 200:
    data = response.json()
    print(f"Получено строк: {len(data['rows'])}")
    
    for row in data['rows'][:15]:
        print(row)
else:
    print(f"Ошибка: {response.status_code}")
    print(response.text)