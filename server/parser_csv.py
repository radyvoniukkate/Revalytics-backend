import requests
import csv

API_KEY = 'TpV9fqm5heYjUZApsT83hDcLGtIaZOTSaV0u63JY'
operation = input("Тип операції (1 — Продаж, 2 — Оренда): ").strip()
city_id = input("ID міста (наприклад, 1 для Києва): ").strip()
date_from = input("Дата початку (YYYY-MM): ").strip()
date_to = input("Дата завершення (YYYY-MM): ").strip()

# Формування URL
url = (
    f"https://developers.ria.com/dom/average_price"
    f"?category=1&sub_category=2&operation={operation}"
    f"&state_id=1&city_id={city_id}"
    f"&date_from={date_from}&date_to={date_to}"
    f"&api_key={API_KEY}"
)

# Запит до API
response = requests.get(url)
data = response.json()

# Перевірка на наявність необхідних даних
if "prices" not in data or not data["prices"]:
    print("⚠️ Дані відсутні.")
    exit()

# Вивід результатів у консоль
print("\n📊 Розподіл цін:")
for entry in data["prices"]:
    print(f"{entry['value']} грн: {entry['count']} об'єктів")

# Збереження у CSV
with open("average_prices.csv", "w", newline='', encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Ціна (грн)", "Кількість об'єктів"])
    for entry in data["prices"]:
        writer.writerow([entry["value"], entry["count"]])

print("\n✅ CSV-файл 'average_prices.csv' успішно збережений.")