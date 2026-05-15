import requests

# Ваши данные
API_TOKEN = "a30edef1455300afeac7f5b4d8a221483ea6682a"
BASE_UUID = "f3bf6ecc-cbb1-4da1-bfd4-82dd48137b96"


print("=" * 60)
print("РАБОТА С SEA TABLE API - АЛЬТЕРНАТИВНЫЙ ПОДХОД")
print("=" * 60)

# 1. Авторизация и получение Base-Token
print("\n🔑 Шаг 1: Получение токена доступа...")
try:
    auth_response = requests.get(
        "https://ditable.yanao.ru/api/v2.1/dtable/app-access-token/",
        headers={"accept": "application/json", "authorization": f"Bearer {API_TOKEN}"},
        params={"exp": "3d"}
    )
    
    if auth_response.status_code != 200:
        print(f"❌ Ошибка авторизации! Статус: {auth_response.status_code}")
        print(f"Ответ сервера: {auth_response.text}")
        exit(1)
    
    base_token = auth_response.json()["access_token"]
    print("✅ Токен успешно получен")
    print(f"Токен: {base_token[:50]}...")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    exit(1)

# 2. Попробуем другие эндпоинты с правильной авторизацией
print("\n📋 Шаг 2: Поиск доступных эндпоинтов...")

# Вариант 1: Получить информацию о конкретной таблице через /rows/ (если знаем имя таблицы)
print("\n🔍 Вариант 1: Пробуем получить список доступных таблиц через информацию о workspace")

# Сначала получим список всех workspace (пространств) пользователя
try:
    workspaces_response = requests.get(
        "https://ditable.yanao.ru/api/v2.1/workspaces/",
        headers={
            "accept": "application/json",
            "authorization": f"Bearer {base_token}"
        }
    )
    
    if workspaces_response.status_code == 200:
        workspaces = workspaces_response.json()
        print(f"✅ Найдено workspace: {len(workspaces)}")
        print(f"Ответ: {workspaces}")
        
        # Ищем нашу базу в workspace
        for workspace in workspaces:
            print(f"\n📁 Workspace: {workspace.get('name')}")
            tables_in_ws = workspace.get('tables', [])
            if tables_in_ws:
                print(f"   Таблицы в этом workspace:")
                for table in tables_in_ws:
                    print(f"      - {table.get('name')} (ID: {table.get('id')})")
    else:
        print(f"❌ Ошибка получения workspace: {workspaces_response.status_code}")
        print(f"Ответ: {workspaces_response.text}")
        
except Exception as e:
    print(f"⚠️ Ошибка: {e}")

# Вариант 2: Попробуем другой метод авторизации - через API Token напрямую
print("\n🔍 Вариант 2: Прямой доступ к базе через API Token")

try:
    # Некоторые версии SeaTable используют другой формат авторизации
    direct_response = requests.get(
        f"https://ditable.yanao.ru/api/v2.1/dtable/{BASE_UUID}/",
        headers={
            "accept": "application/json",
            "authorization": f"Token {API_TOKEN}"  # Изменили Bearer на Token
        }
    )
    
    if direct_response.status_code == 200:
        print(f"✅ Доступ получен!")
        print(f"Информация о базе: {direct_response.json()}")
    else:
        print(f"❌ Ошибка: {direct_response.status_code}")
        print(f"Ответ: {direct_response.text}")
        
except Exception as e:
    print(f"⚠️ Ошибка: {e}")

# Вариант 3: Попробуем получить список всех доступных баз
print("\n🔍 Вариант 3: Получение списка всех баз пользователя")

try:
    dtables_response = requests.get(
        "https://ditable.yanao.ru/api/v2.1/dtables/",
        headers={
            "accept": "application/json",
            "authorization": f"Bearer {base_token}"
        }
    )
    
    if dtables_response.status_code == 200:
        dtables = dtables_response.json()
        print(f"✅ Найдено баз: {len(dtables)}")
        
        for dtable in dtables:
            print(f"\n📊 База: {dtable.get('name')}")
            print(f"   UUID: {dtable.get('uuid')}")
            
            # Пробуем получить таблицы для каждой найденной базы
            if dtable.get('uuid') == BASE_UUID:
                print(f"   👈 ЭТО НАША БАЗА!")
    else:
        print(f"❌ Ошибка: {dtables_response.status_code}")
        print(f"Ответ: {dtables_response.text}")
        
except Exception as e:
    print(f"⚠️ Ошибка: {e}")

# Вариант 4: Проверка прав доступа к конкретной базе
print("\n🔍 Вариант 4: Проверка прав доступа к базе")

try:
    # Пробуем получить информацию о базе через другой эндпоинт
    base_info_response = requests.get(
        f"https://ditable.yanao.ru/api/v2.1/share-links/",
        headers={
            "accept": "application/json",
            "authorization": f"Bearer {base_token}"
        },
        params={"dtable_uuid": BASE_UUID}
    )
    
    print(f"Статус проверки прав: {base_info_response.status_code}")
    if base_info_response.status_code == 200:
        print(f"✅ Доступ к базе есть")
        print(f"Ответ: {base_info_response.json()}")
    else:
        print(f"❌ Возможно, нет доступа к этой базе")
        
except Exception as e:
    print(f"⚠️ Ошибка: {e}")

# Вариант 5: Использование публичного API (если база опубликована)
print("\n🔍 Вариант 5: Проверка, опубликована ли база")

try:
    # Пробуем получить доступ через публичную ссылку
    # (Если база опубликована, можно получить API token для нее)
    publish_response = requests.get(
        f"https://ditable.yanao.ru/api/v2.1/dtable/{BASE_UUID}/publish-info/",
        headers={
            "accept": "application/json",
            "authorization": f"Bearer {base_token}"
        }
    )
    
    if publish_response.status_code == 200:
        publish_info = publish_response.json()
        if publish_info.get('is_published'):
            print(f"✅ База опубликована!")
            print(f"Публичный token: {publish_info.get('token')}")
        else:
            print(f"ℹ️ База не опубликована")
    else:
        print(f"❌ Не удалось проверить публикацию: {publish_response.status_code}")
        
except Exception as e:
    print(f"⚠️ Ошибка: {e}")

print("\n" + "=" * 60)
print("💡 РЕКОМЕНДАЦИИ:")
print("=" * 60)
print("""
1. Убедитесь, что API_TOKEN имеет доступ к базе с UUID: f3bf6ecc-cbb1-4da1-bfd4-82dd48137b96
2. Проверьте в веб-интерфейсе SeaTable, существует ли такая база
3. Убедитесь, что вы используете правильный API_TOKEN (не personal access token для аккаунта)
4. Возможно, база находится в другом workspace, и у токена нет к ней доступа

Как получить правильный API_TOKEN:
- Зайдите в веб-интерфейс SeaTable
- Перейдите в настройки аккаунта → API Token
- Создайте новый токен с доступом к нужным базам
""")