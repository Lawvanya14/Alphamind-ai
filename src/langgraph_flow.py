from langgraph.graph import StateGraph

from agents.market_agent import analyze_market
from agents.ml_agent import predict_price_movement
from agents.news_agent import get_news
from agents.sentiment_agent import analyze_sentiment
from agents.risk_agent import analyze_risk
from agents.signal_agent import generate_signal
from agents.insight_agent import generate_insight


# ------------------ NODES ------------------

def market_node(state):
    data = analyze_market(state["query"])
    state["market_data"] = data
    return state


def ml_node(state):
    pred = predict_price_movement(state["market_data"]["symbol"])
    state["prediction"] = pred
    return state


def news_node(state):
    news = get_news(state["market_data"]["symbol"])
    state["news"] = news
    return state


def sentiment_node(state):
    sentiment = analyze_sentiment(state["news"])
    state["sentiment"] = sentiment
    return state


def risk_node(state):
    risk = analyze_risk(state["market_data"])
    state["risk"] = risk
    return state


def signal_node(state):
    signal, confidence, reasons = generate_signal(
        state["prediction"], state["sentiment"], state["risk"]
    )
    state["signal"] = signal
    state["confidence"] = confidence
    state["reasons"] = reasons
    return state


def insight_node(state):
    insight = generate_insight(
        state["market_data"],
        state["sentiment"],
        state["risk"],
        state["news"]
    )
    state["insight"] = insight
    return state


# ------------------ GRAPH ------------------

def build_graph():

    graph = StateGraph(dict)

    graph.add_node("market", market_node)
    graph.add_node("ml", ml_node)
    graph.add_node("news", news_node)
    graph.add_node("sentiment", sentiment_node)
    graph.add_node("risk", risk_node)
    graph.add_node("signal", signal_node)
    graph.add_node("insight", insight_node)

    graph.set_entry_point("market")

    graph.add_edge("market", "ml")
    graph.add_edge("ml", "news")
    graph.add_edge("news", "sentiment")
    graph.add_edge("sentiment", "risk")
    graph.add_edge("risk", "signal")
    graph.add_edge("signal", "insight")

    graph.set_finish_point("insight")

    return graph.compile()