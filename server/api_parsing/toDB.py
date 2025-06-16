import os
import csv
from pymongo import MongoClient

# Параметри MongoDB
client = MongoClient("mongodb+srv://Cluster54986:UHVOSGFzdEd8@cluster54986.cr3raey.mongodb.net/?retryWrites=true&w=majority&appName=Cluster54986")
db = client["bkr"]
collection = db["avg_monthly_buy_regions"]  # Назва колекції універсальна

# Базова директорія
base_dir = "./buy/regions/"

# Очистка (опційно)
# collection.delete_many({})

# Рекурсивний пошук файлів
for root, dirs, files in os.walk(base_dir):
    for filename in files:
        if filename.startswith("buying_summary_") and filename.endswith(".csv"):
            region = filename.replace("buying_summary_", "").replace(".csv", "")
            filepath = os.path.join(root, filename)

            with open(filepath, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                docs = []
                for row in reader:
                    try:
                        year_month = row["Місяць"]
                        year, month = map(int, year_month.split("-"))
                        doc = {
                            "region": region,
                            "year": year,
                            "month": month,
                            "month_name_ua": row["Назва місяця"],
                            "object_count": int(row["Кількість об'єктів"]),
                            "average_price": float(row["Середня ціна"])
                        }
                        docs.append(doc)
                    except Exception as e:
                        print(f"⚠️ Пропущено рядок у {region}: {row} — {e}")

                if docs:
                    collection.insert_many(docs)
                    print(f"✅ Імпортовано {len(docs)} рядків із {region}")
                else:
                    print(f"⚠️ Порожній або некоректний файл: {filename}")
