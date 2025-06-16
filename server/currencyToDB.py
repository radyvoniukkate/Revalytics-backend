import csv
from pymongo import MongoClient
from collections import defaultdict
from datetime import datetime

# Параметри MongoDB
client = MongoClient("mongodb+srv://Cluster54986:UHVOSGFzdEd8@cluster54986.cr3raey.mongodb.net/?retryWrites=true&w=majority&appName=Cluster54986")
db = client["bkr"]
collection = db["usd_rates"]

# Очистка колекції (опціонально)
# collection.delete_many({})

# Шлях до CSV-файлу
csv_file = "./rate.csv"

# Словник для збереження всіх курсів за місяць
monthly_data = defaultdict(list)
threshold_date = datetime.strptime("28.12.2019", "%d.%m.%Y")

with open(csv_file, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)

    # Автоматичне визначення колонки з курсом
    rate_field = next((f for f in reader.fieldnames if "exchange" in f.lower() and "uah" in f.lower()), None)
    if not rate_field:
        raise ValueError("Не знайдено колонку з курсом UAH")

    for row in reader:
        try:
            date_str = row["Date"].strip()
            rate_raw = row[rate_field].strip().replace(",", ".")
            if not rate_raw:
                continue

            rate = float(rate_raw)
            date_obj = datetime.strptime(date_str, "%d.%m.%Y")
            year, month = date_obj.year, date_obj.month

            # Ділення на 100 лише до 28.12.2019
            if date_obj <= threshold_date:
                rate = rate / 100

            monthly_data[(year, month)].append(rate)

        except Exception as e:
            print(f"⚠️ Пропущено рядок: {row} — {e}")

# Агрегація середніх значень
docs = []
for (year, month), rates in monthly_data.items():
    avg_rate = sum(rates) / len(rates)
    docs.append({
        "year": year,
        "month": month,
        "usd": round(avg_rate, 4)
    })

# Запис у MongoDB
if docs:
    collection.insert_many(docs)
    print(f"✅ Імпортовано {len(docs)} записів")
else:
    print("⚠️ Жодного валідного запису не знайдено")