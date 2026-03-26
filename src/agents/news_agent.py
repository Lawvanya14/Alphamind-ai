from services.news_service import fetch_news


def get_news(symbol):

    print("\n📰 Fetching related news...\n")

    # Smart keyword mapping
    keyword_map = {
        "SILVERBEES": "silver",
        "GOLDBEES": "gold",
        "NIFTYBEES": "nifty"
    }

    base_symbol = symbol.split(".")[0]

    query = keyword_map.get(base_symbol, base_symbol)

    articles = fetch_news(query)

    if not articles:
        print("No news found.")
        return []

    for article in articles:
        print("•", article)

    return articles