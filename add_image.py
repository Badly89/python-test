import requests
from datetime import datetime

API_TOKEN = "8ecc94c9432e9fb82b4b6b849ed050449277cbbc"
BASE_UUID = "3dfdd3a4-57a8-469d-9438-b51502b38d6f"
SERVER = "cloud.seatable.io"

# Просто добавляем строки с прямыми URL изображений
def add_rows_with_direct_urls():
    # Получаем токен
    resp = requests.get(
        f"https://{SERVER}/api/v2.1/dtable/app-access-token/",
        headers={"accept": "application/json", "authorization": f"Bearer {API_TOKEN}"},
        params={"exp": "3d"}
    )
    base_token = resp.json()["access_token"]
    
    # Прямые URL изображений (не требуют загрузки)
    rows = [
        {
            "Текст сообщения": "Тест с прямым URL",
            "Изображение": ["https://picsum.photos/id/1/300/200"],
            "ID пользователя MAX": "test_001",
            "Имя пользователя": "Тестовый Пользователь",
            "Время получения": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    ]
    
    url = f"https://{SERVER}/api-gateway/api/v2/dtables/{BASE_UUID}/rows/"
    headers = {"authorization": f"Bearer {base_token}", "content-type": "application/json"}
    payload = {"table_name": "Trapping", "rows": rows}
    
    response = requests.post(url, headers=headers, json=payload)
    print(response.status_code)
    print(response.json())

add_rows_with_direct_urls()