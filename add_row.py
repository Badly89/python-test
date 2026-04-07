import requests
import json
from datetime import datetime

API_TOKEN = "8ecc94c9432e9fb82b4b6b849ed050449277cbbc"
BASE_UUID = "3dfdd3a4-57a8-469d-9438-b51502b38d6f"

def get_base_token():
    """Получает Base-Token"""
    auth_response = requests.get(
        "https://cloud.seatable.io/api/v2.1/dtable/app-access-token/",
        headers={"accept": "application/json", "authorization": f"Bearer {API_TOKEN}"},
        params={"exp": "3d"}
    )
    
    if auth_response.status_code != 200:
        print(f"Error: {auth_response.status_code}")
        print(auth_response.text)
        return None
    
    return auth_response.json()["access_token"]

def add_row(base_token, row_data):
    """Добавляет строку в таблицу"""
    url = f"https://cloud.seatable.io/api-gateway/api/v2/dtables/{BASE_UUID}/rows/"
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {base_token}",
        "content-type": "application/json"
    }
    
    payload = {
        "table_name": "Trapping",
        "rows": [row_data],
        "use_column_default": False
    }
    
    response = requests.post(url, headers=headers, json=payload)
    return response

def get_existing_rows(base_token, limit=10):
    """Получает существующие строки для примера"""
    url = f"https://cloud.seatable.io/api-gateway/api/v2/dtables/{BASE_UUID}/rows/"
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {base_token}"
    }
    params = {
        "table_name": "Trapping",
        "limit": limit
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    return None

def main():
    print("="*50)
    print("ДОБАВЛЕНИЕ СТРОКИ В ТАБЛИЦУ TRAPPING")
    print("="*50)
    
    # Получаем токен
    base_token = get_base_token()
    if not base_token:
        return
    
    print("[OK] Подключение установлено")
    
    # Показываем последние строки для примера
    print("\n--- Последние строки в таблице ---")
    rows_data = get_existing_rows(base_token, limit=3)
    if rows_data:
        rows = rows_data.get("rows", [])
        for i, row in enumerate(rows, 1):
            print(f"\nСтрока {i}:")
            print(f"  Текст сообщения: {row.get('Текст сообщения', '')[:50]}")
            print(f"  Имя пользователя: {row.get('Имя пользователя', '')}")
            print(f"  ID пользователя: {row.get('ID пользователя MAX', '')}")
            print(f"  Время получения: {row.get('Время получения', '')}")
    
    # Ввод новой строки
    print("\n" + "="*50)
    print("ВВОД НОВОЙ СТРОКИ")
    print("="*50)
    
    text_message = input("Текст сообщения: ").strip()
    user_id = input("ID пользователя MAX: ").strip()
    user_name = input("Имя пользователя: ").strip()
    
    # Автоматическая вставка текущего времени
    use_current_time = input("Использовать текущее время? (y/n): ").lower()
    if use_current_time == 'y':
        receive_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Время получения: {receive_time}")
    else:
        receive_time = input("Время получения (ГГГГ-ММ-ДД ЧЧ:ММ:СС): ").strip()
    
    # Формируем строку
    new_row = {
        "Текст сообщения": text_message,
        "ID пользователя MAX": user_id,
        "Имя пользователя": user_name,
        "Время получения": receive_time
    }
    
    print("\n--- Добавляемая строка ---")
    print(json.dumps(new_row, indent=2, ensure_ascii=False))
    
    confirm = input("\nДобавить строку? (y/n): ").lower()
    if confirm != 'y':
        print("Отменено")
        return
    
    # Добавляем строку
    response = add_row(base_token, new_row)
    
    if response.status_code == 201:
        print("\n[OK] Строка успешно добавлена!")
        result = response.json()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"\n[ERROR] {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    main()