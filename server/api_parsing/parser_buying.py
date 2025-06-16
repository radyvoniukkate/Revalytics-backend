import requests
import csv
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta

API_KEY = 'TpV9fqm5heYjUZApsT83hDcLGtIaZOTSaV0u63JY'

regions = {
    1: 'Vinnytska',
    2: 'Zhytomyrska',
    3: 'Ternopilska',
    4: 'Khmelnytska',
    5: 'Lvivska',
    6: 'Chernihivska',
    7: 'Kharkivska',
    8: 'Sumska',
    9: 'Rivnenska',
    10: 'Kyivska',
    11: 'Dnipropetrovska',
    12: 'Odeska',
    13: 'Donetska',
    14: 'Zaporizka',
    15: 'Ivano-Frankivska',
    16: 'Kirovohradska',
    17: 'Luhanska',
    18: 'Volynska',
    19: 'Mykolaivska',
    20: 'Poltavska',
    22: 'Zakarpatska',
    23: 'Khersonska',
    24: 'Cherkaska',
    25: 'Chernivetska'
}

month_names_ukr = {
    1: "Січень", 2: "Лютий", 3: "Березень", 4: "Квітень",
    5: "Травень", 6: "Червень", 7: "Липень", 8: "Серпень",
    9: "Вересень", 10: "Жовтень", 11: "Листопад", 12: "Грудень"
}

# Фіксовані параметри
operation = 1      # продаж
category = 1
sub_category = 2

# Діапазон дат
start_date = datetime.strptime("2025-01", "%Y-%m")
end_date = datetime.strptime("2025-05", "%Y-%m")

# Створення папки для CSV
output_folder = "./buy/regions/monthly_2025"
os.makedirs(output_folder, exist_ok=True)

for state_id, region_name in regions.items():
    filename = f"{output_folder}/buying_summary_{region_name}.csv"
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
                f"&state_id={state_id}"
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
                print(f"✅ {region_name} - {month_name}: total={total}, avg={round(average, 2)}")

            except requests.exceptions.RequestException as e:
                print(f"❌ Помилка для {region_name}, {month_str}: {e}")

            current_date += relativedelta(months=1)
