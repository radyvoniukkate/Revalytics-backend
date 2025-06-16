from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from pymongo import MongoClient
import time


def parse_apartments():
    # Підключення до MongoDB
    client = MongoClient("mongodb+srv://Cluster54986:UHVOSGFzdEd8@cluster54986.cr3raey.mongodb.net/?retryWrites=true&w=majority&appName=Cluster54986")
    db = client['bkr']
    collection = db['buy_apartments']

    # Налаштування драйвера
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")  # headless нової версії
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://dom.ria.com/uk/prodazha-kvartir/")

    # Очікуємо, поки оголошення завантажаться
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[data-testid="offer-card"]'))
        )
    except:
        print("⚠️ Не вдалося знайти оголошення. Можливо, сайт змінив структуру.")
        driver.quit()
        return

    # Зберігаємо HTML сторінки для перевірки
    with open("page_rendered.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    ads = soup.select('div[data-testid="offer-card"]')
    print(f"🔍 Знайдено оголошень: {len(ads)}")

    for ad in ads:
        title = ad.select_one('h2')
        price = ad.select_one('p.price')
        location = ad.select_one('p.address')
        link = ad.find('a', href=True)

        document = {
            "title": title.get_text(strip=True) if title else "—",
            "price": price.get_text(strip=True) if price else "—",
            "location": location.get_text(strip=True) if location else "—",
            "link": f"https://dom.ria.com{link['href']}" if link else "—",
        }

        collection.insert_one(document)
        print(f"✅ Збережено: {document['title']}")
