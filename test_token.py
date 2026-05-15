import requests
import json

API_TOKEN = "8ecc94c9432e9fb82b4b6b849ed050449277cbbc"
EMAIL = "malykhinal@mail.ru"
PASSWORD = "WgN-f8A-F7y-j78"
BASE_UUID = "3dfdd3a4-57a8-469d-9438-b51502b38d6f"

def test_token(token_name, token):
    """Тестирует токен на разных операциях"""
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {token}",
        "content-type": "application/json"
    }
    
    results = {}
    
    # Тест 1: Получение строк (GET)
    print(f"\n  [Тест 1] GET /rows/")
    response = requests.get(
        f"https://cloud.seatable.io/api-gateway/api/v2/dtables/{BASE_UUID}/rows/",
        headers=headers,
        params={"table_name": "Trapping", "limit": 1}
    )
    results['GET rows'] = response.status_code
    print(f"    Статус: {response.status_code}")
    
    # Тест 2: Создание строки (POST)
    print(f"  [Тест 2] POST /rows/")
    test_row = {
        "table_name": "Trapping",
        "rows": [{
            "Текст сообщения": f"Тест токена {token_name}",
            "ID пользователя MAX": "test",
            "Имя пользователя": "Тест",
            "Время получения": "2026-04-29 12:00:00"
        }],
        "use_column_default": False
    }
    response = requests.post(
        f"https://cloud.seatable.io/api-gateway/api/v2/dtables/{BASE_UUID}/rows/",
        headers=headers,
        json=test_row
    )
    results['POST rows'] = response.status_code
    
    if response.status_code in [200, 201]:
        result = response.json()
        if result.get('row_ids'):
            new_id = result['row_ids'][0] if isinstance(result['row_ids'][0], str) else result['row_ids'][0]['_id']
        else:
            new_id = result.get('first_row', {}).get('_id')
        print(f"    Статус: {response.status_code} ✅ (ID: {new_id})")
        results['new_row_id'] = new_id
    else:
        print(f"    Статус: {response.status_code} ❌")
        print(f"    Ответ: {response.text[:100]}")
    
    # Тест 3: Создание связи (POST /links/)
    if 'new_row_id' in results:
        print(f"  [Тест 3] POST /links/")
        
        # Получаем ID строки из Table2
        response = requests.get(
            f"https://cloud.seatable.io/api-gateway/api/v2/dtables/{BASE_UUID}/rows/",
            headers=headers,
            params={"table_name": "Table2", "limit": 1}
        )
        
        if response.status_code == 200 and response.json().get('rows'):
            linked_id = response.json()['rows'][0]['_id']
            
            link_data = {
                "table_name": "Trapping",
                "other_table_name": "Table2",
                "link_id": "FC4s",
                "other_rows_ids_map": {
                    results['new_row_id']: [linked_id]
                }
            }
            
            response = requests.post(
                f"https://cloud.seatable.io/api-gateway/api/v2/dtables/{BASE_UUID}/links/",
                headers=headers,
                json=link_data
            )
            results['POST links'] = response.status_code
            
            if response.status_code == 200:
                print(f"    Статус: {response.status_code} ✅")
            else:
                print(f"    Статус: {response.status_code} ❌")
                print(f"    Ответ: {response.text[:100]}")
    
    # Тест 4: Получение метаданных
    print(f"  [Тест 4] GET /metadata/")
    response = requests.get(
        f"https://cloud.seatable.io/api-gateway/api/v2/dtables/{BASE_UUID}/metadata/",
        headers=headers
    )
    results['GET metadata'] = response.status_code
    print(f"    Статус: {response.status_code}")
    
    return results

# ============================================
print("="*60)
print("СРАВНЕНИЕ ТОКЕНОВ")
print("="*60)

# 1. Получаем base-token (старый способ через API Token)
print("\n[1] BASE-TOKEN (через API Token)")
print("-"*40)
response = requests.get(
    "https://cloud.seatable.io/api/v2.1/dtable/app-access-token/",
    headers={
        "accept": "application/json",
        "authorization": f"Bearer {API_TOKEN}"
    },
    params={"exp": "3d"}
)

if response.status_code == 200:
    base_token = response.json()["access_token"]
    print(f"Токен получен: {base_token[:20]}...")
    base_results = test_token("base-token", base_token)
else:
    print(f"❌ Не удалось получить: {response.status_code}")
    base_token = None

# 2. Получаем auth-token (через логин/пароль)
print("\n\n[2] AUTH-TOKEN (через логин/пароль)")
print("-"*40)
response = requests.post(
    "https://cloud.seatable.io/api2/auth-token/",
    headers={
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded"
    },
    data={"username": EMAIL, "password": PASSWORD}
)

if response.status_code == 200:
    auth_token = response.json()['token']
    print(f"Токен получен: {auth_token[:20]}...")
    auth_results = test_token("auth-token", auth_token)
else:
    print(f"❌ Не удалось получить: {response.status_code}")
    auth_token = None
    auth_results = None

# 3. Пробуем получить base-token используя auth-token
print("\n\n[3] BASE-TOKEN (полученный через auth-token)")
print("-"*40)
if auth_token:
    response = requests.get(
        "https://cloud.seatable.io/api/v2.1/dtable/app-access-token/",
        headers={
            "accept": "application/json",
            "authorization": f"Bearer {auth_token}"
        },
        params={"exp": "3d"}
    )
    
    if response.status_code == 200:
        combined_token = response.json()["access_token"]
        print(f"Токен получен: {combined_token[:20]}...")
        combined_results = test_token("combined", combined_token)
    else:
        print(f"❌ Не удалось: {response.status_code}")
        combined_token = None
        combined_results = None

# 4. ИТОГОВАЯ ТАБЛИЦА
print("\n\n" + "="*60)
print("ИТОГОВОЕ СРАВНЕНИЕ")
print("="*60)

print(f"\n{'Операция':<30} {'Base-token':<15} {'Auth-token':<15} {'Комбинированный':<15}")
print("-"*75)

if base_results:
    print(f"{'GET rows':<30} {base_results.get('GET rows', 'N/A'):<15}", end="")
else:
    print(f"{'GET rows':<30} {'N/A':<15}", end="")

if auth_results:
    print(f"{auth_results.get('GET rows', 'N/A'):<15}", end="")
else:
    print(f"{'N/A':<15}", end="")

if combined_results:
    print(f"{combined_results.get('GET rows', 'N/A'):<15}")
else:
    print(f"{'N/A':<15}")

# POST rows
if base_results:
    print(f"{'POST rows':<30} {base_results.get('POST rows', 'N/A'):<15}", end="")
else:
    print(f"{'POST rows':<30} {'N/A':<15}", end="")

if auth_results:
    print(f"{auth_results.get('POST rows', 'N/A'):<15}", end="")
else:
    print(f"{'N/A':<15}", end="")

if combined_results:
    print(f"{combined_results.get('POST rows', 'N/A'):<15}")
else:
    print(f"{'N/A':<15}")

# POST links
if base_results:
    print(f"{'POST links':<30} {base_results.get('POST links', 'N/A'):<15}", end="")
else:
    print(f"{'POST links':<30} {'N/A':<15}", end="")

if auth_results:
    print(f"{auth_results.get('POST links', 'N/A'):<15}", end="")
else:
    print(f"{'N/A':<15}", end="")

if combined_results:
    print(f"{combined_results.get('POST links', 'N/A'):<15}")
else:
    print(f"{'N/A':<15}")

# GET metadata
if base_results:
    print(f"{'GET metadata':<30} {base_results.get('GET metadata', 'N/A'):<15}", end="")
else:
    print(f"{'GET metadata':<30} {'N/A':<15}", end="")

if auth_results:
    print(f"{auth_results.get('GET metadata', 'N/A'):<15}", end="")
else:
    print(f"{'N/A':<15}", end="")

if combined_results:
    print(f"{combined_results.get('GET metadata', 'N/A'):<15}")
else:
    print(f"{'N/A':<15}")

print("\n" + "="*60)
print("ВЫВОД:")
print("="*60)

if base_results and all(v in [200, 201] for v in base_results.values() if isinstance(v, int)):
    print("✅ Base-token (API Token) - ПОЛНОСТЬЮ РАБОТАЕТ")

if auth_results and all(v in [200, 201] for v in auth_results.values() if isinstance(v, int)):
    print("✅ Auth-token (логин/пароль) - ПОЛНОСТЬЮ РАБОТАЕТ")
elif auth_results:
    print("⚠️ Auth-token - работает ЧАСТИЧНО")
    failed = [k for k, v in auth_results.items() if isinstance(v, int) and v not in [200, 201]]
    print(f"   Не работают: {', '.join(failed)}")

if combined_results and all(v in [200, 201] for v in combined_results.values() if isinstance(v, int)):
    print("✅ Комбинированный - ПОЛНОСТЬЮ РАБОТАЕТ")