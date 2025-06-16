import feedparser
from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb+srv://Cluster54986:UHVOSGFzdEd8@cluster54986.cr3raey.mongodb.net/?retryWrites=true&w=majority&appName=Cluster54986")
db = client["bkr"]
collection = db["google_news"]

def fetch_and_store_news(query: str):
    rss_url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=uk&gl=UA&ceid=UA:uk"

    feed = feedparser.parse(rss_url)

    for entry in feed.entries:
        news_item = {
            "title": entry.title,
            "link": entry.link,
            "published": entry.published,
            "summary": entry.summary,
            "query": query,
            "fetched_at": datetime.utcnow()
        }

        # уникаємо дублікатів
        collection.update_one({"link": news_item["link"]}, {"$set": news_item}, upsert=True)

    return len(feed.entries)
