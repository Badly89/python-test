import requests
import json

API_TOKEN = "8ecc94c9432e9fb82b4b6b849ed050449277cbbc"
EMAIL = "malykhinal@mail.ru"
PASSWORD = "WgN-f8A-F7y-j78"
BASE_UUID = "3dfdd3a4-57a8-469d-9438-b51502b38d6f"

print("="*60)
print("ПРОВЕРКА: МОЖНО ЛИ КОНВЕРТИРОВАТЬ AUTH-TOKEN В BASE-TOKEN?")
print("="*60)

# Шаг 1: Получаем auth-token через логин/пароль
print("\n[1] Получаем auth-token...")
auth_response = requests.post(
    "https://cloud.seatable.io/api2/auth-token/",
    headers={
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded"
    },
    data={"username": EMAIL, "password": PASSWORD}
)

if auth_response.status_code != 200:
    print(f"❌ Ошибка: {auth_response.text}")
    exit()

auth_token = auth_response.json()['token']
print(f"✅ Auth-token: {auth_token[:30]}...")

# Шаг 2: Пробуем получить base-token используя auth-token
print("\n[2] Пробуем получить base-token через auth-token...")

# Вариант 1: Стандартный запрос
print("\n  Вариант 1: GET /api/v2.1/dtable/app-access-token/")
response = requests.get(
    "https://cloud.seatable.io/api/v2.1/dtable/app-access-token/",
    headers={
        "accept": "application/json",
        "authorization": f"Bearer {auth_token}"
    },
    params={"exp": "3d"}
)
print(f"  Статус: {response.status_code}")
if response.status_code == 200:
    base_token = response.json().get("access_token")
    print(f"  ✅ Base-token: {base_token[:30]}...")
else:
    print(f"  ❌ {response.text[:150]}")

# Вариант 2: Используем другой endpoint
print("\n  Вариант 2: GET /api/v2.1/dtable/app-access-token/ (без Bearer)")
response = requests.get(
    "https://cloud.seatable.io/api/v2.1/dtable/app-access-token/",
    headers={
        "accept": "application/json",
        "authorization": f"Token {auth_token}"  # Token вместо Bearer
    },
    params={"exp": "3d"}
)
print(f"  Статус: {response.status_code}")
if response.status_code == 200:
    base_token = response.json().get("access_token")
    print(f"  ✅ Base-token: {base_token[:30]}...")
else:
    print(f"  ❌ {response.text[:150]}")

# Вариант 3: Используем API Token для получения base-token (100% рабочий)
print("\n  Вариант 3: GET с API Token (контрольный)")
response = requests.get(
    "https://cloud.seatable.io/api/v2.1/dtable/app-access-token/",
    headers={
        "accept": "application/json",
        "authorization": f"Bearer {API_TOKEN}"
    },
    params={"exp": "3d"}
)
print(f"  Статус: {response.status_code}")
if response.status_code == 200:
    base_token_api = response.json().get("access_token")
    print(f"  ✅ Base-token: {base_token_api[:30]}...")
else:
    print(f"  ❌ {response.text[:150]}")

# Шаг 3: Проверяем, работает ли base-token полученный через auth-token
print("\n[3] Проверка работы base-token (если получен)...")
if 'base_token' in locals():
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {base_token}",
        "content-type": "application/json"
    }
    
    # Тест: получение строк
    response = requests.get(
        f"https://cloud.seatable.io/api-gateway/api/v2/dtables/{BASE_UUID}/rows/",
        headers=headers,
        params={"table_name": "Trapping", "limit": 1}
    )
    print(f"  GET rows: {response.status_code}")
    
    # Тест: создание строки
    test_row = {
        "table_name": "Trapping",
        "rows": [{"Текст сообщения": "Тест конвертации"}],
        "use_column_default": False
    }
    response = requests.post(
        f"https://cloud.seatable.io/api-gateway/api/v2/dtables/{BASE_UUID}/rows/",
        headers=headers,
        json=test_row
    )
    print(f"  POST rows: {response.status_code}")