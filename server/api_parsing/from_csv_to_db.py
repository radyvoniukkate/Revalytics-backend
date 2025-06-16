import os
import csv
from pymongo import MongoClient

# Параметри MongoDB
client = MongoClient("mongodb+srv://Cluster54986:UHVOSGFzdEd8@cluster54986.cr3raey.mongodb.net/?retryWrites=true&w=majority&appName=Cluster54986")
db = client["bkr"]
year = "2025"
collection = db[f"average_prices_{year}_rent"]

# Папка з CSV
csv_folder = f"./rent/"

# Очистка (опціонально)
# collection.delete_many({})

for filename in os.listdir(csv_folder):
    if filename.endswith(".csv") and filename.startswith("buying_region_"):
        # Отримати назву регіону з назви файлу
        region = filename.replace("buying_region_", "").replace(".csv", "")
        filepath = os.path.join(csv_folder, filename)

        with open(filepath, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            docs = []
            for row in reader:
                try:
                    doc = {
                        "price_uah": int(row["Ціна (грн)"]),
                        "object_count": int(row["Кількість об'єктів"]),
                        "region": region,
                        "type": "Квартира"
                    }
                    docs.append(doc)
                except Exception as e:
                    print(f"⚠️ Пропущено рядок у {region}: {row} — {e}")

            if docs:
                collection.insert_many(docs)
                print(f"✅ Імпортовано {len(docs)} рядків із {region}")
            else:
                print(f"⚠️ Порожній або некоректний файл: {filename}")
