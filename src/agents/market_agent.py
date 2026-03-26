import yfinance as yf


def resolve_symbol(user_input):

    ASSET_MAP = {
        # 🇺🇸 Stocks
        "tesla": "TSLA",
        "apple": "AAPL",
        "nvidia": "NVDA",
        "microsoft": "MSFT",
        "amazon": "AMZN",
        "google": "GOOGL",
        "meta": "META",

        # 🇮🇳 Stocks
        "tcs": "TCS.NS",
        "infosys": "INFY.NS",
        "reliance": "RELIANCE.NS",
        "hdfc": "HDFCBANK.NS",
        "icici": "ICICIBANK.NS",

        # ETFs / Commodities
        "silver": "SILVERBEES.NS",
        "gold": "GOLDBEES.NS",
        "niftybees": "NIFTYBEES.NS",

        # Crypto
        "bitcoin": "BTC-USD",
        "ethereum": "ETH-USD",
        "btc": "BTC-USD",
        "eth": "ETH-USD",
        "solana": "SOL-USD",

        # Index
        "nifty50": "^NSEI",
        "nifty": "^NSEI",
        "sensex": "^BSESN"
    }

    query = user_input.strip().lower()

    # Exact match
    if query in ASSET_MAP:
        return ASSET_MAP[query]

    # Partial match
    for key in ASSET_MAP:
        if key in query:
            return ASSET_MAP[key]

    # Fallback (very important)
    return user_input.upper()


#  Fetch Market Data
def get_market_data(symbol):

    stock = yf.Ticker(symbol)
    data = stock.history(period="1d")

    if data.empty:
        print("⚠ Asset not found.")
        return None

    open_price = data["Open"].iloc[-1]
    close_price = data["Close"].iloc[-1]
    high = data["High"].iloc[-1]
    low = data["Low"].iloc[-1]

    change = ((close_price - open_price) / open_price) * 100

    return {
        "price": round(close_price, 2),
        "change": round(change, 2),
        "high": round(high, 2),
        "low": round(low, 2)
    }


#  Main Market Analysis
def analyze_market(user_query):

    symbol = resolve_symbol(user_query)

    print("\n Fetching market data...\n")

    data = get_market_data(symbol)

    if not data:
        return None

    print(" Financial AI Market Insight")
    print("Asset:", symbol)
    print(f"Current Price: {data['price']}")
    print(f"📈 Day Change: {data['change']}%")
    print(f"📉 Day Range: {data['low']} – {data['high']}")

    # Trend Logic (refined)
    if data["change"] > 2:
        trend = "Strong bullish momentum"
    elif data["change"] > 0:
        trend = "Mild bullish movement"
    elif data["change"] < -2:
        trend = "Strong bearish movement"
    elif data["change"] < 0:
        trend = "Mild bearish movement"
    else:
        trend = "Sideways / consolidation"

    print("\n Market Trend Analysis:", trend)

    return {
        "symbol": symbol,
        "price": float(data["price"]),
        "change": float(data["change"]),
        "trend": trend
    }