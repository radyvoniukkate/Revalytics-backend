from fastapi import APIRouter
from bson import ObjectId
import hashlib
from typing import Optional
from typing import List
from server.database import get_collection_by_type
from server.database import get_collection_by_year
from fastapi import Query
import logging
logger = logging.getLogger("uvicorn")
from server.database import get_usd_collection
from fastapi import HTTPException
from server.models import Item
from server.parser_apartments import parse_apartments
from server.news import fetch_and_store_news
from server.database import get_news_collection
from server.forecast import get_price_forecast


router = APIRouter()


@router.get("/")
def root():
    return {"message": "MongoDB підключено!"}

@router.get("/parse")
def parse_data():
    return parse_apartments()

@router.get("/parse-news/")
def parse_news(query: str = "ринок нерухомості"):
    count = fetch_and_store_news(query)
    return {"message": f"{count} новин додано до бази"}


@router.get("/news")
def get_news():
    collection = get_news_collection()
    news_items = list(collection.find().sort("published", -1))  # сортовані за датою

    for item in news_items:
        item["_id"] = str(item["_id"])
    return news_items

@router.get("/locations/{purpose}/{level}", response_model=List[str])
def get_locations(purpose: str, level: str):
    """
    Отримати список унікальних назв регіонів або міст.
    - purpose: 'buy' або 'rent'
    - level: 'cities' або 'regions'
    """
    if purpose not in {"buy", "rent"}:
        raise HTTPException(status_code=400, detail="purpose має бути 'buy' або 'rent'")
    if level not in {"cities", "regions"}:
        raise HTTPException(status_code=400, detail="level має бути 'cities' або 'regions'")

    collection = get_collection_by_type(purpose, level)
    cursor = collection.find({}, {"region": 1, "_id": 0})
    locations = sorted({doc["region"] for doc in cursor if "region" in doc})
    return locations


# Отримання даних по місту/регіону
@router.get("/months/{purpose}/{level}", response_model=List[dict])
def get_available_months(purpose: str, level: str, year: int = Query(...)):
    """
    Отримати унікальні місяці (номер і назва українською) для конкретного року.
    """
    if purpose not in {"buy", "rent"} or level not in {"cities", "regions"}:
        raise HTTPException(status_code=400, detail="Невірні параметри")

    collection = get_collection_by_type(purpose, level)

    pipeline = [
        {"$match": {"year": year}},
        {"$group": {
            "_id": {"month": "$month", "name": "$month_name_ua"}
        }},
        {"$project": {
            "_id": 0,
            "month": "$_id.month",
            "name": "$_id.name"
        }},
        {"$sort": {"month": 1}}
    ]

    result = list(collection.aggregate(pipeline))
    return result

@router.get("/years/{purpose}/{level}", response_model=List[int])
def get_available_years(purpose: str, level: str):
    """
    Отримати список унікальних років для заданих purpose і level.
    - purpose: 'buy' або 'rent'
    - level: 'cities' або 'regions'
    """
    if purpose not in {"buy", "rent"} or level not in {"cities", "regions"}:
        raise HTTPException(status_code=400, detail="Невірні параметри")

    collection = get_collection_by_type(purpose, level)
    years = collection.distinct("year")
    return sorted(years)


@router.get("/analytics/regions/{year}")
def analytics_by_region(year: int):
    collection = get_collection_by_year(year)
    pipeline = [
        {"$group": {
            "_id": "$region",
            "avg_price": {"$avg": "$price_uah"},
            "total_objects": {"$sum": "$object_count"}
        }}
    ]
    raw_results = collection.aggregate(pipeline)

    results = []
    for item in raw_results:
        results.append({
            "_id": str(ObjectId()),                 # згенерований MongoDB ObjectId
            "region": item["_id"],                  # region окремо
            "avg_price": item["avg_price"],
            "total_objects": item["total_objects"]
        })

    return results

# Дані для конкретного регіону за рік
@router.get("/analytics/region/{region_name}/{year}")
def analytics_for_region(region_name: str, year: int):
    collection = get_collection_by_year(year)
    data = list(collection.find({"region": region_name}))

    # Перетворення ObjectId на рядок
    for item in data:
        item["_id"] = str(item["_id"])
    return data

# Додавання нового запису в колекцію відповідного року
@router.post("/items/{year}")
def create_item(item: Item, year: int):
    collection = get_collection_by_year(year)
    result = collection.insert_one(item.dict())
    return {"inserted_id": str(result.inserted_id)}

@router.get("/analytics/{purpose}/{level}/details")
def get_location_details_over_years(
    purpose: str,
    level: str,
    location_name: str = Query(...),
    years: List[int] = Query(...),
):
    """
    Отримати деталі по регіону/місту за кілька років.
    """
    if purpose not in {"buy", "rent"} or level not in {"cities", "regions"}:
        raise HTTPException(status_code=400, detail="Невірні параметри")

    collection = get_collection_by_type(purpose, level)

    results = []
    for year in years:
        match_stage = {
            "year": year,
            "average_price": {"$exists": True, "$ne": None},
            "object_count": {"$exists": True, "$ne": 0},
        }

        if level == "regions":
            match_stage["region"] = location_name
        elif level == "cities":
            match_stage["city"] = location_name

        pipeline = [
            {"$match": match_stage},
            {
                "$group": {
                    "_id": None,
                    "total_weighted_price": {"$sum": {"$multiply": ["$average_price", "$object_count"]}},
                    "total_objects": {"$sum": "$object_count"},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "year": year,
                    "avg_price": {
                        "$cond": [
                            {"$eq": ["$total_objects", 0]},
                            None,
                            {"$divide": ["$total_weighted_price", "$total_objects"]},
                        ]
                    },
                    "count": "$total_objects",
                }
            },
        ]

        year_result = list(collection.aggregate(pipeline))
        if year_result:
            item = year_result[0]
            item["avg_price"] = round(item["avg_price"], 2) if item["avg_price"] is not None else None
            results.append(item)
        else:
            results.append({"year": year, "avg_price": None, "count": 0})

    return results

@router.get("/analytics/{purpose}/{level}/{year}")
def get_analytics_by_year(purpose: str, level: str, year: int):
    if purpose not in {"buy", "rent"} or level not in {"cities", "regions"}:
        raise HTTPException(status_code=400, detail="Невірні параметри")

    collection = get_collection_by_type(purpose, level)

    pipeline = [
        {"$match": {"year": year, "average_price": {"$exists": True, "$ne": None}, "object_count": {"$exists": True, "$ne": 0}}},
        {
            "$group": {
                "_id": "$region",
                "total_weighted_price": {"$sum": {"$multiply": ["$average_price", "$object_count"]}},
                "total_objects": {"$sum": "$object_count"},
            }
        },
        {
            "$project": {
                "_id": 0,
                "region": "$_id",
                "avg_price": {
                    "$cond": [
                        {"$eq": ["$total_objects", 0]},
                        None,
                        {"$divide": ["$total_weighted_price", "$total_objects"]}
                    ]
                },
                "count": "$total_objects",
            }
        },
        {"$sort": {"region": 1}},
    ]

    result = list(collection.aggregate(pipeline))

    response = [
    {
        "region": item["region"],
        "avg_price": round(item["avg_price"], 2) if item["avg_price"] is not None else None,
        "count": item["count"]
    }
    for item in result
]

    return response

@router.get("/location/{purpose}/{level}/{year}")
def get_analytics_by_year_and_month(
    purpose: str,
    level: str,
    year: int,
    month: Optional[int] = Query(None, ge=1, le=12),
    city: Optional[str] = None,
    region: Optional[str] = None,
):
    # Валідація параметрів
    if purpose not in {"buy", "rent"} or level not in {"cities", "regions"}:
        raise HTTPException(status_code=400, detail="Невірні параметри purpose або level")

    # Отримуємо колекцію залежно від purpose і level
    collection = get_collection_by_type(purpose, level)

    # Формуємо match-умови
    match_stage = {
        "year": year,
        "average_price": {"$exists": True, "$ne": None},
        "object_count": {"$exists": True, "$ne": 0},
    }
    if month is not None:
        match_stage["month"] = month

    # Фільтрація по місту чи регіону залежно від level
    if level == "cities" and city:
        match_stage["city"] = city
    elif level == "regions" and region:
        match_stage["region"] = region

    # Групування по полю залежно від level
    group_field = "$region" 

    pipeline = [
        {"$match": match_stage},
        {
            "$group": {
                "_id": group_field,
                "total_weighted_price": {"$sum": {"$multiply": ["$average_price", "$object_count"]}},
                "total_objects": {"$sum": "$object_count"},
            }
        },
        {
            "$project": {
                "_id": 0,
                "location": "$_id",  # тут назва поля залежить від level
                "avg_price": {
                    "$cond": [
                        {"$eq": ["$total_objects", 0]},
                        None,
                        {"$divide": ["$total_weighted_price", "$total_objects"]},
                    ]
                },
                "count": "$total_objects",
            }
        },
        {"$sort": {"location": 1}},
    ]

    result = list(collection.aggregate(pipeline))

    # Формуємо відповідь, додаючи округлення avg_price
    return [
        {
            "location": item["location"],
            "avg_price": round(item["avg_price"], 2) if item["avg_price"] is not None else None,
            "count": item["count"],
        }
        for item in result
    ]

@router.get("/usd")
def get_usd_rates(year: Optional[int] = None, month: Optional[int] = None):
    """
    Отримати курси USD по місяцях. Можна вказати рік і/або місяць.
    """
    collection = get_usd_collection()

    query = {}
    if year is not None:
        query["year"] = year
    if month is not None:
        query["month"] = month

    data = list(collection.find(query, {"_id": 0}))
    if not data:
        raise HTTPException(status_code=404, detail="Дані не знайдено")

    return data

@router.get("/forecast")
def forecast(
    purpose: str = Query(..., enum=["buy", "rent"]),
    level: str = Query(..., enum=["cities", "regions"]),
    name: str = Query(...)
):
    return {"forecast": get_price_forecast(purpose, level, name)}

@router.get("/analytics/{purpose}/{level}/{region}/{year}/monthly")
def get_monthly_analytics_by_region(
    purpose: str,
    level: str,
    region: str,
    year: int
):
    if purpose not in {"buy", "rent"} or level not in {"cities", "regions"}:
        raise HTTPException(status_code=400, detail="Невірні параметри")

    collection = get_collection_by_type(purpose, level)

    # Для рівня 'regions' фільтруємо по region, для 'cities' — по city (тут поки тільки для регіону)
    match_stage = {
        "year": year,
        "region": region,
        "average_price": {"$exists": True, "$ne": None},
        "object_count": {"$exists": True, "$ne": 0}
    }

    pipeline = [
        {"$match": match_stage},
        {
            "$group": {
                "_id": "$month",
                "total_weighted_price": {"$sum": {"$multiply": ["$average_price", "$object_count"]}},
                "total_objects": {"$sum": "$object_count"},
            }
        },
        {
            "$project": {
                "_id": 0,
                "month": "$_id",
                "avg_price": {
                    "$cond": [
                        {"$eq": ["$total_objects", 0]},
                        None,
                        {"$divide": ["$total_weighted_price", "$total_objects"]}
                    ]
                },
                "count": "$total_objects",
            }
        },
        {"$sort": {"month": 1}}
    ]

    result = list(collection.aggregate(pipeline))

    return [
        {
            "month": item["month"],
            "avg_price": round(item["avg_price"], 2) if item["avg_price"] is not None else None,
            "count": item["count"]
        }
        for item in result
    ]
