from transformers import pipeline

print("📦 Loading FinBERT sentiment model...")

# Load financial sentiment model once
sentiment_model = pipeline(
    "sentiment-analysis",
    model="ProsusAI/finbert"
)


def analyze_sentiment(news_articles):

    print("\n Analyzing market sentiment...\n")

    if not news_articles:
        return "Neutral sentiment"

    # Run FinBERT on each headline
    results = sentiment_model(news_articles)

    sentiment_count = {
        "positive": 0,
        "negative": 0,
        "neutral": 0
    }

    for r in results:
        label = r["label"].lower()
        sentiment_count[label] += 1

    # Determine dominant sentiment
    overall = max(sentiment_count, key=sentiment_count.get)

    sentiment_map = {
        "positive": "Bullish sentiment",
        "negative": "Bearish sentiment",
        "neutral": "Neutral sentiment"
    }

    return sentiment_map[overall]                                                                                              