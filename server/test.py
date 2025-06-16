import requests
from pprint import pprint

# 🔑 Твій API ключ тут
API_KEY = 'TpV9fqm5heYjUZApsT83hDcLGtIaZOTSaV0u63JY'

# 📌 Параметри запиту
category = 1         # квартири/кімнати
operation = 1        # продаж
state_id = 10        # Київ (10 — ID для Києва на RIA)

# 🔗 Формування URL
url = (
    f"https://docs-developers.ria.com/dom/sell_apartments"
    f"?category={category}"
    f"&operation={operation}"
    f"&state_id={state_id}"
    f"&api_key={API_KEY}"
)

try:
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    pprint(data)
except requests.exceptions.RequestException as e:
    print(f"Помилка при запиті: {e}")
    print("Статус-код:", response.status_code)
    print("Raw відповідь сервера:")
    print(response.text)

