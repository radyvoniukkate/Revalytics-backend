import requests
import csv
import os
import time

API_KEY = 'TpV9fqm5heYjUZApsT83hDcLGtIaZOTSaV0u63JY'

# Відсутні області
regions = {
    18: 'Rivne',
    23: 'Kherson'
}

output_folder = "buying_2024"
os.makedirs(output_folder, exist_ok=True)

category = 1
sub_category = 2
operation = 1
date_from = "2024-04"
date_to = "2024-08"

base_url = "https://developers.ria.com"

def get_cities(state_id):
    url = f"{base_url}/dom/cities/{state_id}?api_key={API_KEY}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            cities = response.json()
            # Фільтрація тільки валідних міст
            return [c for c in cities if c.get("city_id") and c.get("name")]
        else:
            print(f"❌ Не вдалося отримати міста (код {response.status_code})")
            return []
    except Exception as e:
        print(f"❌ Помилка при отриманні міст: {e}")
        return []

for state_id, region_name in regions.items():
    print(f"\n🔍 Обробка області: {region_name}")
    cities = get_cities(state_id)
    region_data = []

    for city in cities:
        city_id = city["city_id"]
        city_name = city["name"]

        url = (
            f"{base_url}/dom/average_price"
            f"?category={category}&sub_category={sub_category}"
            f"&operation={operation}"
            f"&state_id={state_id}&city_id={city_id}"
            f"&date_from={date_from}&date_to={date_to}"
            f"&api_key={API_KEY}"
        )

        try:
            response = requests.get(url)
            data = response.json()
            prices = data.get("prices", [])
            if prices:
                for item in prices:
                    region_data.append({
                        "price": item["value"],
                        "count": item["count"]
                    })
                print(f"✅ {city_name} — {len(prices)} записів")
            else:
                print(f"⚠️ {city_name} — немає цін")
        except Exception as e:
            print(f"❌ Помилка у місті {city_name}: {e}")

        time.sleep(0.4)  # м'якше до ліміту

    if region_data:
        filename = f"{output_folder}/buying_region_{region_name}.csv"
        with open(filename, "w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Ціна (грн)", "Кількість"])
            for row in region_data:
                writer.writerow([row["price"], row["count"]])
        print(f"💾 Збережено у {filename}")
    else:
        print(f"❗ Даних по містах у {region_name} не знайдено")
