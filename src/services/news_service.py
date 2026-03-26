import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("NEWS_API_KEY")


def fetch_news(query):

    url = "https://newsapi.org/v2/everything"

    params = {
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "apiKey": API_KEY,
        "pageSize": 5
    }

    response = requests.get(url, params=params)

    data = response.json()

    articles = []

    if data.get("articles"):
        for article in data["articles"]:
            title = article["title"]
            articles.append(title)

    return articles