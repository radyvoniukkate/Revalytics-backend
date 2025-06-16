from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Завантаження змінних з .env
load_dotenv()

# === Параметри підключення ===
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb+srv://Cluster54986:UHVOSGFzdEd8@cluster54986.cr3raey.mongodb.net/?retryWrites=true&w=majority&appName=Cluster54986")
DB_NAME = os.getenv("MONGODB_DB", "bkr")

# Створення клієнта та бази
client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

# === Додаткові колекції ===
def get_news_collection():
    return db["google_news"]

def get_collection_by_type(purpose: str, level: str):
    """
    Повертає відповідну колекцію: purpose = 'buy'/'rent', level = 'cities'/'regions'
    """
    collection_name = f"avg_monthly_{purpose}_{level}"
    return db[collection_name]

def get_collection_by_year(year: int):
    return db[f"average_prices_{year}_buy"]

def get_usd_collection():
    return client["bkr"]["usd_rates"]