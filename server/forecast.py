from pymongo import MongoClient
import pandas as pd
from prophet import Prophet
from fastapi import HTTPException

client = MongoClient("mongodb+srv://Cluster54986:UHVOSGFzdEd8@cluster54986.cr3raey.mongodb.net/?retryWrites=true&w=majority&appName=Cluster54986")
db = client["bkr"]

def get_collection_by_type(purpose: str, level: str):
    collection_name = f"avg_monthly_{purpose}_{level}"
    return db[collection_name]

def get_price_forecast(purpose: str, level: str, name: str):
    collection = get_collection_by_type(purpose, level)

    query = {"region": name}
    projection = {"year": 1, "month": 1, "average_price": 1, "_id": 0}

    cursor = list(collection.find(query, projection))
    if not cursor:
        raise HTTPException(status_code=404, detail="Дані не знайдено для вказаного місця")

    df = pd.DataFrame(cursor)
    df["date"] = pd.to_datetime(df[["year", "month"]].assign(day=1))
    df = df.dropna(subset=["date", "average_price"])

    monthly_prices = df[["date", "average_price"]].sort_values("date")
    monthly_prices.columns = ["ds", "y"]

    model = Prophet()
    model.fit(monthly_prices)

    future = model.make_future_dataframe(periods=6, freq="M")
    forecast = model.predict(future)

    result = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(6)
    return result.to_dict(orient="records")
