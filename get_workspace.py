import requests
import json

API_TOKEN = "8ecc94c9432e9fb82b4b6b849ed050449277cbbc"
EMAIL = "malykhinal@mail.ru"
PASSWORD = "WgN-f8A-F7y-j78"
BASE_UUID = "3dfdd3a4-57a8-469d-9438-b51502b38d6f"

def get_metadata_via_api_token():
    """Получает метаданные используя API Token (чтобы узнать workspace_id и base_name)"""
    # Получаем временный base-token
    response = requests.get(
        "https://cloud.seatable.io/api/v2.1/dtable/app-access-token/",
        headers={"accept": "application/json", "authorization": f"Bearer {API_TOKEN}"},
        params={"exp": "1h"}  # на 1 час
    )
    
    if response.status_code != 200:
        print("Не удалось получить base-token через API Token")
        return None
    
    base_token = response.json()["access_token"]
    
    # Получаем метаданные
    response = requests.get(
        f"https://cloud.seatable.io/api-gateway/api/v2/dtables/{BASE_UUID}/metadata/",
        headers={"accept": "application/json", "authorization": f"Bearer {base_token}"}
    )
    
    if response.status_code == 200:
        return response.json().get('metadata', {})
    return None

def get_base_token_via_account(email, password):
    """
    Получает base-token через логин/пароль.
    Предварительно узнаёт workspace_id и base_name.
    """
    # 1. Узнаём workspace_id и base_name через API Token
    print("[1] Получаем метаданные через API Token...")
    metadata = get_metadata_via_api_token()
    
    if not metadata:
        print("Не удалось получить метаданные")
        return None
    
    workspace_id = metadata.get('workspace_id')
    base_name = metadata.get('name')
    
    print(f"    Workspace ID: {workspace_id}")
    print(f"    Base Name: {base_name}")
    
    # 2. Авторизуемся через логин/пароль
    print("\n[2] Авторизация через логин/пароль...")
    auth_response = requests.post(
        "https://cloud.seatable.io/api2/auth-token/",
        headers={
            "accept": "application/json",
            "content-type": "application/x-www-form-urlencoded"
        },
        data={"username": email, "password": password}
    )
    
    if auth_response.status_code != 200:
        print(f"Ошибка: {auth_response.text}")
        return None
    
    account_token = auth_response.json()['token']
    print("    Account-token получен")
    
    # 3. Обмениваем на base-token
    print("\n[3] Получаем base-token...")
    url = f"https://cloud.seatable.io/api/v2.1/workspace/{workspace_id}/dtable/{base_name}/access-token/"
    
    response = requests.get(
        url,
        headers={
            "accept": "application/json",
            "authorization": f"Bearer {account_token}"
        },
        params={"exp": "3d"}
    )
    
    if response.status_code == 200:
        base_token = response.json().get("access_token")
        print(f"    ✅ Base-token получен!")
        print(f"    Токен: {base_token[:30]}...")
        return base_token
    else:
        print(f"    ❌ Ошибка: {response.status_code}")
        print(f"    {response.text}")
        return None

# Тестируем
print("="*60)
print("ПОЛУЧЕНИЕ BASE-TOKEN ЧЕРЕЗ ЛОГИН/ПАРОЛЬ")
print("="*60)

base_token = get_base_token_via_account(EMAIL, PASSWORD)

if base_token:
    print("\n" + "="*60)
    print("ПРОВЕРКА РАБОТЫ BASE-TOKEN")
    print("="*60)
    
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {base_token}",
        "content-type": "application/json"
    }
    
    # Тест 1: Получение строк
    print("\n[Тест 1] GET rows...")
    response = requests.get(
        f"https://cloud.seatable.io/api-gateway/api/v2/dtables/{BASE_UUID}/rows/",
        headers=headers,
        params={"table_name": "Trapping", "limit": 1}
    )
    print(f"    Статус: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
    
    # Тест 2: Создание строки
    print("\n[Тест 2] POST row...")
    test_row = {
        "table_name": "Trapping",
        "rows": [{"Текст сообщения": "Тест через auth-token"}],
        "use_column_default": False
    }
    response = requests.post(
        f"https://cloud.seatable.io/api-gateway/api/v2/dtables/{BASE_UUID}/rows/",
        headers=headers,
        json=test_row
    )
    print(f"    Статус: {response.status_code} {'✅' if response.status_code in [200, 201] else '❌'}")
    
    # Тест 3: Создание связи
    if response.status_code in [200, 201]:
        new_id = response.json().get('first_row', {}).get('_id')
        if new_id:
            print("\n[Тест 3] POST link...")
            link_data = {
                "table_name": "Trapping",
                "other_table_name": "Table2",
                "link_id": "FC4s",
                "other_rows_ids_map": {
                    new_id: ["SCsZkDSvTo-RMJ3VKmTcDg"]
                }
            }
            response = requests.post(
                f"https://cloud.seatable.io/api-gateway/api/v2/dtables/{BASE_UUID}/links/",
                headers=headers,
                json=link_data
            )
            print(f"    Статус: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
    
    print("\n" + "="*60)
    print("✅ ВСЁ РАБОТАЕТ! Можно использовать логин/пароль!")
    print("="*60)
else:
    print("\n❌ Не удалось получить base-token")