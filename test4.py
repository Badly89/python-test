import requests
import json

API_TOKEN = "cff2f00dcfdd8931ab7e1d5a3ea8377f5e636dfa"
BASE_UUID = "65d08730-22fb-45db-b8be-19fb42cbafb2"

# 1. Получаем Base-Token
auth_response = requests.get(
    "https://ditable.yanao.ru/api/v2.1/dtable/app-access-token/",
    headers={"accept": "application/json", "authorization": f"Bearer {API_TOKEN}"},
    params={"exp": "3d"}
)
base_token = auth_response.json()["access_token"]
print("✅ Base token получен\n")

# 2. Явно указываем названия ваших 4 таблиц (ЗАМЕНИТЕ НА РЕАЛЬНЫЕ)
table_names = [
    "Заявки",  # эту вы уже использовали
    "Скворцова ОН",
    "Регистрация", 
    "Список рассылки",
    "Справочник вопросы",
    "Справочник подразделения"

]

# 3. Собираем по одной записи из каждой таблицы с convert_keys=true
result = {
    "base_uuid": BASE_UUID,
    "tables": {}
}

for table_name in table_names:
    print(f"📋 Загружаю из таблицы: {table_name}")
    
    response = requests.get(
        f"https://ditable.yanao.ru/api-gateway/api/v2/dtables/{BASE_UUID}/rows/",
        headers={"accept": "application/json", "authorization": f"Bearer {base_token}"},
        params={
            "table_name": table_name, 
            "limit": 1,
            "convert_keys": True   # ← КЛЮЧЕВОЙ ПАРАМЕТР!
        }
    )
    
    if response.status_code != 200:
        print(f"   ❌ Ошибка: {response.status_code}")
        result["tables"][table_name] = {"error": f"Ошибка {response.status_code}"}
        continue
    
    data = response.json()
    rows = data.get("rows", [])
    
    if not rows:
        print(f"   ⚠️ Таблица пуста")
        result["tables"][table_name] = {"status": "empty"}
    else:
        print(f"   ✅ Загружена 1 запись с человекочитаемыми названиями колонок")
        result["tables"][table_name] = {"first_row": rows[0]}

# 4. Выводим результат в JSON
print("\n" + "=" * 80)
print("РЕЗУЛЬТАТ (колонки с человекочитаемыми именами):")
print("=" * 80)
print(json.dumps(result, indent=2, ensure_ascii=False, default=str))

# 5. Сохраняем в файл
filename = "tables_with_readable_columns.json"
with open(filename, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False, default=str)

print("\n" + "=" * 80)
print(f"💾 Сохранено в файл: {filename}")
print("=" * 80)