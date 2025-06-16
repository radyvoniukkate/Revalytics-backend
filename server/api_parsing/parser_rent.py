import requests
import csv
import os

from datetime import datetime
from dateutil.relativedelta import relativedelta

API_KEY = 'TpV9fqm5heYjUZApsT83hDcLGtIaZOTSaV0u63JY'

cities = {
    1: "Vinnytsia",
    2: "Zhytomyr",
    3: "Ternopil",
    4: "Khmelnytskyi",
    5: "Lviv",
    6: "Chernihiv",
    7: "Kharkiv",
    8: "Sumy",
    9: "Rivne",
    10: "Kyiv",
    11: "Dnipro",
    12: "Odesa",
    14: "Zaporizhzhia",
    15: "Ivano-Frankivsk",
    16: "Kropyvnytskyi",
    18: "Lutsk",
    19: "Mykolaiv",
    20: "Poltava",
    22: "Uzhhorod",
    23: "Kherson",
    24: "Cherkasy",
    25: "Chernivtsi"
}


month_names_ukr = {
    1: "Січень",
    2: "Лютий",
    3: "Березень",
    4: "Квітень",
    5: "Травень",
    6: "Червень",
    7: "Липень",
    8: "Серпень",
    9: "Вересень",
    10: "Жовтень",
    11: "Листопад",
    12: "Грудень"
}

# Параметри для оренди приміщень
operation = 1        # оренда
category = 1           
sub_category = 2        # усі підкатегорії

# Папка для збереження CSV
output_folder = "./buy/regions/monthly_2018"
os.makedirs(output_folder, exist_ok=True)

# Період: з 2018-01 по 2018-12
start_date = datetime.strptime("2018-01", "%Y-%m")
end_date = datetime.strptime("2019-12", "%Y-%m")

for city_id, city_name in cities.items():
    filename = f"{output_folder}/rent_summary_{city_name}.csv"
    with open(filename, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Місяць", "Назва місяця", "Кількість об'єктів", "Середня ціна"])

        current_date = start_date
        while current_date <= end_date:
            month_str = current_date.strftime("%Y-%m")
            month_name = month_names_ukr[current_date.month]

            url = (
                f"https://developers.ria.com/dom/average_price"
                f"?category={category}&sub_category={sub_category}"
                f"&operation={operation}"
                f"&city_id={city_id}"
                f"&date_from={month_str}&date_to={month_str}"
                f"&api_key={API_KEY}"
            )

            try:
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()

                total = data.get("total", 0)
                average = data.get("arithmeticMean", 0)

                writer.writerow([month_str, month_name, total, round(average, 2)])
                print(f"✅ {city_name} - {month_name}: total={total}, avg={round(average, 2)}")

            except requests.exceptions.RequestException as e:
                print(f"❌ Помилка для {city_name}, {month_str}: {e}")

            current_date += relativedelta(months=1)