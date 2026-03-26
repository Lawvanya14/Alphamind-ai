from src.agents.market_agent import analyze_market
from src.agents.news_agent import get_news


def run_pipeline(user_query):

    print("\n Running Financial AI Pipeline...\n")

    market_data = analyze_market(user_query)

    if not market_data:
        return None

    news = get_news(market_data["symbol"])

    return {
        "market_analysis": market_data,
        "news": news
    }