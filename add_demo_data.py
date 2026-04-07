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
        print(f"Ошибка: {response.status_code}")
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
    return response

# Проверенные рабочие URL изображений (все доступны)
IMAGE_URLS = [
    # Природа и пейзажи
    "https://picsum.photos/id/10/300/200",   # Туманный лес
    "https://picsum.photos/id/15/300/200",   # Водопад
    "https://picsum.photos/id/26/300/200",   # Венеция
    "https://picsum.photos/id/29/300/200",   # Горы
    "https://picsum.photos/id/96/300/200",   # Горы и облака
    
    # Города и архитектура
    "https://picsum.photos/id/1/300/200",    # Ноутбук
    "https://picsum.photos/id/20/300/200",   # Кофе
    "https://picsum.photos/id/42/300/200",   # Пианино
    "https://picsum.photos/id/91/300/200",   # Железная дорога
    
    # Животные
    "https://picsum.photos/id/100/300/200",  # Камера (можно)
    "https://picsum.photos/id/102/300/200",  # Собака
    "https://picsum.photos/id/107/300/200",  # Кошка
    
    # Абстракции
    "https://picsum.photos/300/200?grayscale",
    "https://picsum.photos/300/200?random=1",
]

def main():
    print("="*60)
    print("ДОБАВЛЕНИЕ СТРОК С ИЗОБРАЖЕНИЯМИ")
    print("="*60)
    
    # Получаем токен
    print("\n[1] Получение токена...")
    base_token = get_base_token()
    if not base_token:
        return
    
    # Тексты сообщений
    messages = [
        "Добро пожаловать в наш сервис!",
        "Новое обновление доступно",
        "Пожалуйста, проверьте уведомления",
        "Ваш заказ обработан",
        "Тестовое сообщение из API",
        "Системное уведомление"
    ]
    
    users = [
        {"id": "user_001", "name": "Анна Смирнова"},
        {"id": "user_002", "name": "Петр Иванов"},
        {"id": "user_003", "name": "Елена Петрова"},
        {"id": "user_004", "name": "Дмитрий Сидоров"},
        {"id": "user_005", "name": "Мария Кузнецова"}
    ]
    
    # Генерируем 5 строк
    print("\n[2] Генерация строк...")
    rows_to_add = []
    
    for i in range(1, 6):
        user = random.choice(users)
        row = {
            "Текст сообщения": f"{random.choice(messages)} (тест #{i})",
            "Изображение": random.choice(IMAGE_URLS),
            "ID пользователя MAX": user["id"],
            "Имя пользователя": user["name"],
            "Время получения": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        rows_to_add.append(row)
    
    # Показываем что будет добавлено
    print("\n[3] Данные для добавления:")
    for i, row in enumerate(rows_to_add, 1):
        print(f"\n--- Строка {i} ---")
        print(f"  Текст: {row['Текст сообщения']}")
        print(f"  Изображение: {row['Изображение']}")
        print(f"  Пользователь: {row['Имя пользователя']} ({row['ID пользователя MAX']})")
        print(f"  Время: {row['Время получения']}")
    
    # Подтверждение
    print("\n" + "="*60)
    confirm = input("Добавить эти строки? (y/n): ").lower()
    
    if confirm != 'y':
        print("Отменено")
        return
    
    # Добавляем
    print("\n[4] Добавление в таблицу...")
    response = add_rows(base_token, "Trapping", rows_to_add)
    
    if response.status_code in [200, 201]:
        result = response.json()
        print(f"\n[SUCCESS] Добавлено {result.get('inserted_row_count', 0)} строк!")
        print(f"ID строк: {result.get('row_ids', [])}")
    else:
        print(f"\n[ERROR] {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    main()