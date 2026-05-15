import requests
import json
from datetime import datetime

EMAIL = "malykhinal@mail.ru"
PASSWORD = "WgN-f8A-F7y-j78"
API_TOKEN = "8ecc94c9432e9fb82b4b6b849ed050449277cbbc"
BASE_UUID = "3dfdd3a4-57a8-469d-9438-b51502b38d6f"

def get_working_token():
    """
    Пробует разные методы авторизации и возвращает рабочий токен
    """
    headers = {"accept": "application/json"}
    
    # Метод 1: Старый API Token (получаем base-token)
    print("[1/3] Пробуем через API Token...")
    response = requests.get(
        "https://cloud.seatable.io/api/v2.1/dtable/app-access-token/",
        headers={**headers, "authorization": f"Bearer {API_TOKEN}"},
        params={"exp": "3d"}
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"✅ Работает! Base-token: {token[:20]}...")
        return token
    
    print(f"❌ Не работает: {response.status_code}")
    
    # Метод 2: Логин/пароль для получения auth-token
    print("\n[2/3] Пробуем через логин/пароль...")
    response = requests.post(
        "https://cloud.seatable.io/api2/auth-token/",
        headers={**headers, "content-type": "application/x-www-form-urlencoded"},
        data={"username": EMAIL, "password": PASSWORD}
    )
    
    if response.status_code == 200:
        auth_token = response.json()['token']
        print(f"✅ Auth-token получен: {auth_token[:20]}...")
        
        # Пробуем получить base-token через auth-token
        print("\n[2.1] Получаем base-token через auth-token...")
        response2 = requests.get(
            "https://cloud.seatable.io/api/v2.1/dtable/app-access-token/",
            headers={**headers, "authorization": f"Bearer {auth_token}"},
            params={"exp": "3d"}
        )
        
        if response2.status_code == 200:
            token = response2.json()["access_token"]
            print(f"✅ Base-token получен: {token[:20]}...")
            return token
        else:
            print(f"⚠️ Не удалось получить base-token, используем auth-token напрямую")
            return auth_token
    
    print("\n[3/3] Все методы не сработали")
    return None

def add_row(token, row_data):
    """Добавляет строку в Trapping"""
    url = f"https://cloud.seatable.io/api-gateway/api/v2/dtables/{BASE_UUID}/rows/"
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {token}",
        "content-type": "application/json"
    }
    
    payload = {
        "table_name": "Trapping",
        "rows": [row_data],
        "use_column_default": False
    }
    
    response = requests.post(url, headers=headers, json=payload)
    return response

def add_link(token, new_row_id, linked_row_ids, link_id="FC4s"):
    """Создаёт связь"""
    url = f"https://cloud.seatable.io/api-gateway/api/v2/dtables/{BASE_UUID}/links/"
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {token}",
        "content-type": "application/json"
    }
    
    payload = {
        "table_name": "Trapping",
        "other_table_name": "Table2",
        "link_id": link_id,
        "other_rows_ids_map": {
            new_row_id: linked_row_ids
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    return response

def get_table2_rows(token):
    """Получает строки из Table2"""
    url = f"https://cloud.seatable.io/api-gateway/api/v2/dtables/{BASE_UUID}/rows/"
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {token}"
    }
    params = {"table_name": "Table2", "limit": 100}
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get('rows', [])
    return []

def main():
    print("="*60)
    print("УМНАЯ АВТОРИЗАЦИЯ + ДОБАВЛЕНИЕ СТРОКИ СО СВЯЗЬЮ")
    print("="*60)
    
    # Получаем рабочий токен
    token = get_working_token()
    if not token:
        print("Не удалось авторизоваться!")
        return
    
    # Получаем строки Table2
    table2_rows = get_table2_rows(token)
    if table2_rows:
        print(f"\nДоступные строки в Table2:")
        for i, row in enumerate(table2_rows, 1):
            print(f"  [{i}] {row.get('0000', 'N/A')}")
        
        choice = input("\nВыберите номера для связи (через запятую): ").strip()
        if choice:
            indices = [int(x.strip()) - 1 for x in choice.split(',')]
            linked_ids = [table2_rows[i]['_id'] for i in indices if 0 <= i < len(table2_rows)]
        else:
            linked_ids = [row['_id'] for row in table2_rows]
    else:
        linked_ids = []
    
    # Создаём строку
    new_row = {
        "Текст сообщения": f"Тест {datetime.now().strftime('%H:%M:%S')}",
        "ID пользователя MAX": "test_user",
        "Имя пользователя": "Тест",
        "Время получения": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    print(f"\nДобавление строки...")
    response = add_row(token, new_row)
    
    if response.status_code in [200, 201]:
        result = response.json()
        if result.get('row_ids'):
            new_row_id = result['row_ids'][0] if isinstance(result['row_ids'][0], str) else result['row_ids'][0]['_id']
        else:
            new_row_id = result.get('first_row', {}).get('_id')
        
        print(f"✅ Строка создана: {new_row_id}")
        
        if linked_ids:
            print(f"Создание связей...")
            link_response = add_link(token, new_row_id, linked_ids)
            
            if link_response.status_code == 200 and link_response.json().get('success'):
                print(f"✅ Связи созданы!")
            else:
                print(f"❌ Ошибка связей: {link_response.text}")
    else:
        print(f"❌ Ошибка: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    main()