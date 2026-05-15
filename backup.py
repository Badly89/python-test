import requests
import json
from datetime import datetime
import os

API_TOKEN = "0d587e5bfac8f558d0a908d871c50db1fee0d047"
BASE_UUID = "572d2646-73b9-4a2f-bd19-03ca42b4ceef"
TABLE_NAME = "Справочник телефонов"

def backup_table_fast():
    try:
        print("🔄 Быстрое создание резервной копии...")
        
        # Получаем токен
        auth_response = requests.get(
            "https://ditable.yanao.ru/api/v2.1/dtable/app-access-token/",
            headers={"accept": "application/json", "authorization": f"Bearer {API_TOKEN}"},
            params={"exp": "3d"}
        )
        base_token = auth_response.json()["access_token"]
        
        # Загружаем данные с максимальным лимитом
        all_rows = []
        offset = 0
        limit = 1000  # Увеличиваем лимит для ускорения
        
        while True:
            response = requests.get(
                f"https://ditable.yanao.ru/api-gateway/api/v2/dtables/{BASE_UUID}/rows/",
                headers={"accept": "application/json", "authorization": f"Bearer {base_token}"},
                params={"table_name": TABLE_NAME, "limit": limit, "offset": offset},
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"⚠️ Ошибка на offset {offset}: {response.status_code}")
                break
                
            data = response.json()
            current_rows = data.get('rows', [])
            
            if not current_rows:
                break
                
            all_rows.extend(current_rows)
            offset += len(current_rows)
            
            print(f"📈 Загружено: {len(all_rows)} строк", end='\r')
            
            if len(current_rows) < limit:
                break
        
        print(f"\n✅ Загрузка завершена. Всего строк: {len(all_rows)}")
        
        # Сохраняем в файл
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backup_{TABLE_NAME.replace(' ', '_')}_{timestamp}.json"
        
        backup_data = {
            "metadata": {
                "backup_date": datetime.now().isoformat(),
                "table_name": TABLE_NAME,
                "total_rows": len(all_rows)
            },
            "data": all_rows
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        file_size = os.path.getsize(filename) / (1024 * 1024)  # Размер в МБ
        print(f"✅ Файл сохранен: {filename}")
        print(f"📦 Размер: {file_size:.2f} МБ")
        print(f"📍 Путь: {os.path.abspath(filename)}")
        
        return filename
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return None

# Запускаем
backup_table_fast()