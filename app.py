from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import statistics

app = Flask(__name__)

def analyze_etsy(keyword):
    url = f"https://www.etsy.com/search?q={keyword}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    prices = []

    for price in soup.find_all("span", class_="currency-value"):
        try:
            value = float(price.text.replace(",", "."))
            prices.append(value)
        except:
            continue

    if not prices:
        return None

    avg_price = round(statistics.mean(prices), 2)
    median_price = round(statistics.median(prices), 2)

    prices_sorted = sorted(prices)
    lower_third = prices_sorted[len(prices)//3]
    upper_third = prices_sorted[(len(prices)//3)*2]

    competition = "Niedrig"
    if len(prices) > 40:
        competition = "Hoch"
    elif len(prices) > 20:
        competition = "Mittel"

    return {
        "count": len(prices),
        "average": avg_price,
        "median": median_price,
        "sweetspot_low": lower_third,
        "sweetspot_high": upper_third,
        "competition": competition
    }

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        keyword = request.form["keyword"]
        result = analyze_etsy(keyword)

    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run()
