import requests
import json
from datetime import datetime
import random

API_TOKEN = "8ecc94c9432e9fb82b4b6b849ed050449277cbbc"
BASE_UUID = "3dfdd3a4-57a8-469d-9438-b51502b38d6f"

def get_base_token():
    """Получает Base-Token"""
    response = requests.get(
        "https://cloud.seatable.io/api/v2.1/dtable/app-access-token/",
        headers={"accept": "application/json", "authorization": f"Bearer {API_TOKEN}"},
        params={"exp": "3d"}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Ошибка получения токена: {response.status_code}")
        print(response.text)
        return None

def add_rows(base_token, table_name, rows):
    """Добавляет строки в таблицу"""
    url = f"https://cloud.seatable.io/api-gateway/api/v2/dtables/{BASE_UUID}/rows/"
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {base_token}",
        "content-type": "application/json"
    }
    
    payload = {
        "table_name": table_name,
        "rows": rows,
        "use_column_default": False
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    # SeaTable возвращает 200 при успешном добавлении
    if response.status_code in [200, 201]:
        return response.json()
    else:
        print(f"Ошибка добавления: {response.status_code}")
        print(response.text)
        return None

def get_columns(base_token, table_name):
    """Получает список колонок с их типами"""
    url = f"https://cloud.seatable.io/api-gateway/api/v2/dtables/{BASE_UUID}/columns/"
    headers = {"accept": "application/json", "authorization": f"Bearer {base_token}"}
    params = {"table_name": table_name}
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    return None

def add_demo_data_with_images():
    """Добавляет демо-данные с изображениями"""
    
    print("="*60)
    print("ДОБАВЛЕНИЕ ДЕМО-ДАННЫХ В ТАБЛИЦУ TRAPPING")
    print("="*60)
    
    # Получаем токен
    print("\n[1] Получение Base-Token...")
    base_token = get_base_token()
    if not base_token:
        return
    
    # Получаем структуру колонок
    print("\n[2] Получение структуры колонок...")
    columns_data = get_columns(base_token, "Trapping")
    
    if columns_data:
        columns = columns_data.get("columns", [])
        print(f"\nНайдено колонок: {len(columns)}")
        for col in columns:
            col_name = col.get("name")
            col_type = col.get("type")
            print(f"  - {col_name} ({col_type})")
    
    # Варианты изображений для демо
    image_urls = [
        "https://picsum.photos/id/1/200/150",   # Ноутбук
        "https://picsum.photos/id/10/200/150",  # Пейзаж
        "https://picsum.photos/id/20/200/150",  # Кофе
        "https://picsum.photos/id/26/200/150",  # Венеция
        "https://picsum.photos/id/42/200/150",  # Пианино
        "https://picsum.photos/id/60/200/150",  # Мужчина
        "https://picsum.photos/id/100/200/150", # Камера
    ]
    
    # Генерируем демо-строки
    print("\n[3] Генерация демо-строк...")
    demo_rows = []
    
    messages = [
        "Важное уведомление: обновление системы",
        "Привет! Как дела?",
        "Проверьте новый функционал",
        "Срочно: требуется подтверждение",
        "Спасибо за использование сервиса",
        "Новое сообщение от поддержки"
    ]
    
    users = [
        {"id": "user_anna", "name": "Анна Смирнова"},
        {"id": "user_petr", "name": "Петр Иванов"},
        {"id": "user_elena", "name": "Елена Петрова"},
        {"id": "user_dmitry", "name": "Дмитрий Сидоров"},
        {"id": "user_maria", "name": "Мария Кузнецова"}
    ]
    
    for i in range(1, 6):  # 5 демо-строк
        user = random.choice(users)
        row = {
            "Текст сообщения": random.choice(messages) + f" (id:{i})",
            "Изображение": random.choice(image_urls),
            "ID пользователя MAX": user["id"],
            "Имя пользователя": user["name"],
            "Время получения": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        demo_rows.append(row)
    
    # Показываем сгенерированные данные
    print(f"\nСгенерировано {len(demo_rows)} строк:")
    for i, row in enumerate(demo_rows, 1):
        print(f"\n--- Строка {i} ---")
        print(f"  Текст сообщения: {row['Текст сообщения']}")
        print(f"  Изображение: {row['Изображение']}")
        print(f"  ID пользователя: {row['ID пользователя MAX']}")
        print(f"  Имя пользователя: {row['Имя пользователя']}")
        print(f"  Время получения: {row['Время получения']}")
    
    # Подтверждение
    print("\n" + "="*60)
    confirm = input("Добавить эти строки в таблицу? (y/n): ").lower()
    
    if confirm != 'y':
        print("Операция отменена")
        return
    
    # Добавляем строки
    print("\n[4] Добавление строк в таблицу...")
    result = add_rows(base_token, "Trapping", demo_rows)
    
    if result:
        inserted_count = result.get("inserted_row_count", 0)
        print(f"\n[SUCCESS] Успешно добавлено {inserted_count} строк!")
        print(f"ID добавленных строк: {result.get('row_ids', [])}")
        
        # Показываем первую добавленную строку
        first_row = result.get("first_row", {})
        if first_row:
            print("\nПример добавленной строки:")
            for key, value in first_row.items():
                if not key.startswith('_') and value:
                    print(f"  {key}: {str(value)[:80]}")
    else:
        print("\n[ERROR] Не удалось добавить строки")

def get_all_rows():
    """Получает все строки из таблицы (для проверки)"""
    print("\n" + "="*60)
    print("ПРОВЕРКА ДОБАВЛЕННЫХ СТРОК")
    print("="*60)
    
    base_token = get_base_token()
    if not base_token:
        return
    
    url = f"https://cloud.seatable.io/api-gateway/api/v2/dtables/{BASE_UUID}/rows/"
    headers = {"accept": "application/json", "authorization": f"Bearer {base_token}"}
    params = {"table_name": "Trapping", "limit": 50}
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        rows = data.get("rows", [])
        print(f"\nВсего строк в таблице: {len(rows)}")
        
        for i, row in enumerate(rows[:10], 1):
            print(f"\n--- Строка {i} ---")
            print(f"  Текст сообщения: {row.get('Текст сообщения', '')[:50]}")
            print(f"  Изображение: {row.get('Изображение', '')[:60]}")
            print(f"  Имя пользователя: {row.get('Имя пользователя', '')}")
            print(f"  Время получения: {row.get('Время получения', '')}")
    else:
        print(f"Ошибка: {response.status_code}")

if __name__ == "__main__":
    # Добавляем демо-данные
    add_demo_data_with_images()
    
    # Проверяем результат
    check = input("\nПоказать все строки в таблице? (y/n): ").lower()
    if check == 'y':
        get_all_rows()