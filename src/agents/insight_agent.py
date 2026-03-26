import os
from groq import Groq

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

#  Financial knowledge (lightweight RAG)
FINANCIAL_KNOWLEDGE = """
Financial Interpretation Guide:
- Bearish trend → selling pressure, possible continuation or consolidation
- Bullish trend → buying momentum, potential upward continuation
- Mild trend → weak movement, often consolidation phase
- High volatility → uncertainty, sharp price swings (higher risk)
- Low volatility → stable movement, limited price swings
- Neutral sentiment → lack of strong conviction
- Bullish sentiment → positive investor outlook
- Bearish sentiment → negative investor outlook
"""


# Improved news filtering + context builder
def build_context(news, symbol):

    if not news:
        return "No major market-moving news available."

    symbol = symbol.lower()

    # Asset-specific keywords
    asset_keywords = {
        "nsei": ["nifty", "india", "market", "index"],
        "btc": ["bitcoin", "crypto", "btc"],
        "eth": ["ethereum", "crypto"],
        "gold": ["gold", "commodity"],
        "silver": ["silver", "commodity"]
    }

    base_keywords = ["market", "price", "stock", "economy", "crypto"]

    # pick relevant keywords
    matched_keywords = base_keywords
    for key in asset_keywords:
        if key in symbol:
            matched_keywords += asset_keywords[key]

    # filter news
    filtered = [
        n for n in news
        if any(k in n.lower() for k in matched_keywords)
    ]

    if not filtered:
        filtered = news[:2]  # fallback

    # concise context
    context = " | ".join(filtered[:3])

    return context


def generate_insight(market_data, sentiment, risk, news):

    context = build_context(news, market_data["symbol"])

    prompt = f"""
You are a professional financial analyst.

Use structured data, financial reasoning, and contextual information to generate a realistic market insight.

{FINANCIAL_KNOWLEDGE}

Market Data:
- Price: {market_data['price']}
- Daily Change: {market_data['change']}%
- Trend: {market_data['trend']}

Market Sentiment:
- {sentiment}

Risk Level:
- {risk}

Market Context:
- {context}

Instructions:
- Use financial reasoning (not generic statements)
- Interpret trend + sentiment + risk together
- Ignore irrelevant news
- Be concise and realistic (no exaggeration)

Output format:

1. Financial Interpretation  
2. Short-term Outlook  
3. Investor Takeaway  
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return response.choices[0].message.content