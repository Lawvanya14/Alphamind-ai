import streamlit as st
from langgraph_flow import build_graph
import plotly.graph_objects as go
import yfinance as yf
import re

st.set_page_config(page_title="AlphaMind AI", layout="wide")

def clean_output(text):
    text = re.sub(r"\*\*\d+\.", "", text)
    text = re.sub(r"\*\*", "", text)
    return text.strip()

st.markdown("""
<style>
html, body { font-family: 'Inter', sans-serif; }

.main {
    background: linear-gradient(135deg, #020617, #0f172a);
    color: #e2e8f0;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020617, #0f172a);
}

.sidebar-title {
    font-size: 24px;
    font-weight: 700;
    background: linear-gradient(90deg, #a78bfa, #38bdf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.stSelectbox > div > div,
.stTextInput > div > div > input {
    background-color: #020617 !important;
    color: white !important;
    border-radius: 10px !important;
    border: 1px solid #334155 !important;
}

.stButton button {
    width: 100%;
    background: linear-gradient(90deg, #6366f1, #a855f7);
    color: white;
    border-radius: 10px;
    border: none;
    font-weight: 600;
}

.title {
    text-align: center;
    font-size: 42px;
    font-weight: 700;
    background: linear-gradient(90deg, #c084fc, #38bdf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.subtitle {
    text-align: center;
    color: #94a3b8;
    margin-bottom: 25px;
}

.card {
    background: rgba(30,41,59,0.6);
    padding: 20px;
    border-radius: 14px;
}

.metric {
    text-align: center;
    padding: 14px;
    border-radius: 12px;
    background: rgba(30,41,59,0.5);
}

.buy { color:#22c55e; }
.sell { color:#ef4444; }
.hold { color:#facc15; }

.badge {
    padding: 6px 12px;
    border-radius: 20px;
    font-weight: 600;
    display: inline-block;
}

.badge-buy { background:#022c22; color:#22c55e; }
.badge-sell { background:#3f0f0f; color:#ef4444; }
.badge-hold { background:#3f3f0f; color:#facc15; }

.insight-box {
    padding: 14px;
    margin: 10px 0;
    border-radius: 10px;
    background: rgba(30,41,59,0.5);
    border: 1px solid #334155;
    transition: all 0.3s ease;
}

.insight-box:hover {
    background: rgba(99,102,241,0.15);
    border-color: #6366f1;
    transform: translateY(-2px);
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">AlphaMind AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-powered financial intelligence using market data, sentiment, and signals</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="sidebar-title">Control Panel</div>', unsafe_allow_html=True)

    assets = {
        "US Stocks": [
            "AAPL - Apple","MSFT - Microsoft","GOOGL - Google","AMZN - Amazon",
            "META - Meta","TSLA - Tesla","NVDA - Nvidia"
        ],
        "Indian Stocks": [
            "RELIANCE.NS - Reliance","TCS.NS - TCS","INFY.NS - Infosys",
            "HDFCBANK.NS - HDFC Bank","ICICIBANK.NS - ICICI Bank"
        ],
        "Indian ETFs": [
            "NIFTYBEES.NS - Nippon Nifty ETF",
            "BANKBEES.NS - Bank ETF",
            "GOLDBEES.NS - Gold ETF",
            "SILVERBEES.NS - Silver ETF",
            "ITBEES.NS - IT ETF"
        ],
        "Global ETFs": [
            "SPY - S&P 500 ETF","QQQ - Nasdaq ETF",
            "GLD - Gold ETF","SLV - Silver ETF"
        ],
        "Crypto": [
            "BTC-USD - Bitcoin","ETH-USD - Ethereum","SOL-USD - Solana"
        ],
        "Indices": [
            "^GSPC - S&P 500","^NSEI - Nifty 50"
        ]
    }

    category = st.selectbox("Category", list(assets.keys()))
    selected_asset = st.selectbox("Asset", assets[category])
    custom = st.text_input("Custom Ticker")

    analyze = st.button("Analyze")

def format_output(result):
    return {
        "market": result.get("market_data", {}),
        "prediction": clean_output(result.get("prediction", "")),
        "signal": result.get("signal", "HOLD"),
        "confidence": int(result.get("confidence", 70)),
        "reasons": result.get("reasons", []),
        "insight": result.get("insight", "")
    }

if not analyze:
    st.info("Select asset and analyze")

if analyze:

    query = custom.strip().upper() if custom else selected_asset.split(" - ")[0]

    with st.spinner("Analyzing market intelligence..."):
        graph = build_graph()
        raw = graph.invoke({"query": query})
        result = format_output(raw)

    market = result["market"]

    st.subheader("Market Overview")
    c1, c2, c3, c4 = st.columns(4)

    def metric(title, val, cls=""):
        st.markdown(f"<div class='metric'><div>{title}</div><div class='{cls}'>{val}</div></div>", unsafe_allow_html=True)

    price = market.get("price", 0)

    if ".NS" in query:
        price_display = f"₹ {price} per unit"
    elif "-USD" in query:
        price_display = f"$ {price} per coin"
    elif query.startswith("^"):
        price_display = f"{price} index value"
    else:
        price_display = f"$ {price} per share"

    with c1: metric("Price", price_display)
    with c2: metric("Change", f"{market.get('change','N/A')}%")
    with c3: metric("Trend", market.get("trend","N/A"))

    with c4:
        signal = result["signal"]
        cls = "buy" if signal=="BUY" else "sell" if signal=="SELL" else "hold"
        badge_class = f"badge-{cls}"
        st.markdown(f"<div class='metric'><div>Signal</div><div class='badge {badge_class}'>{signal}</div></div>", unsafe_allow_html=True)

    st.markdown("---")

    # FIXED GRAPH
    st.subheader("Price Chart")
    data = yf.download(query, period="3mo", interval="1d")

    if not data.empty:
        data = data.reset_index()
        data["Date"] = data["Date"].dt.strftime("%Y-%m-%d")

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=data["Date"],
            y=data["Close"],
            mode="lines+markers",
            line=dict(width=3),
            marker=dict(size=5),
            hovertemplate="Date: %{x}<br>Price: %{y}<extra></extra>"
        ))

        fig.update_layout(
            template="plotly_dark",
            hovermode="x unified",
            xaxis=dict(type="category"),
            margin=dict(l=10, r=10, t=30, b=10)
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available")

    st.markdown("---")

    st.subheader("Prediction")
    col1, col2 = st.columns([2,1])

    with col1:
        st.markdown(f"<div class='card'>{result['prediction']}</div>", unsafe_allow_html=True)

    with col2:
        conf = result['confidence']
        st.markdown(f"<div class='card'><b>Confidence</b><br><h2>{conf}%</h2></div>", unsafe_allow_html=True)
        st.progress(conf/100)

    st.markdown("---")

    # HOVER INSIGHTS
    st.subheader("Signal Reasoning")
    for i, r in enumerate(result["reasons"], 1):
        st.markdown(
            f"<div class='insight-box'><b>Insight {i}</b><br>{clean_output(r)}</div>",
            unsafe_allow_html=True
        )

    st.markdown("---")

    # CLEAN 3 DROPDOWNS
    st.subheader("AI Insights")

    insight_text = clean_output(result["insight"])

    financial, outlook, takeaway = "", "", ""
    lines = insight_text.split("\n")

    current = None
    for line in lines:
        l = line.lower()

        if "financial" in l:
            current = "f"; continue
        elif "short" in l:
            current = "o"; continue
        elif "takeaway" in l or "investor" in l:
            current = "t"; continue

        if current == "f": financial += line + " "
        elif current == "o": outlook += line + " "
        elif current == "t": takeaway += line + " "

    if not financial and not outlook and not takeaway:
        parts = insight_text.split(". ")
        if len(parts) > 0: financial = parts[0]
        if len(parts) > 1: outlook = parts[1]
        if len(parts) > 2: takeaway = parts[2]

    with st.expander("Financial Interpretation"):
        st.write(financial.strip())

    with st.expander("Short-term Outlook"):
        st.write(outlook.strip())

    with st.expander("Investor Takeaway"):
        st.write(takeaway.strip())

    st.caption("Source: Yahoo Finance | Prices may be delayed")
