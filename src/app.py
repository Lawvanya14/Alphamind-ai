import streamlit as st
from langgraph_flow import build_graph
import plotly.graph_objects as go
import yfinance as yf
import re

st.set_page_config(page_title="AlphaMind AI", layout="wide")

def clean_output(text):
    text = re.sub(r"\*\*\d+\.", "", text)
    text = re.sub(r"\*\*", "", text)  # remove stray **
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

.reason {
    padding: 10px;
    margin: 6px 0;
    border-radius: 8px;
    background: rgba(148,163,184,0.08);
    border-left: 3px solid #c084fc;
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

    st.subheader("Price Chart")
    data = yf.download(query, period="3mo")

    if not data.empty:
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=data.index,
            y=data["Close"],
            mode="lines",
            name="Price",
            line=dict(width=3),
            hovertemplate="Date: %{x}<br>Price: %{y}<extra></extra>"
        ))

        fig.update_layout(
            template="plotly_dark",
            hovermode="x unified",
            margin=dict(l=10, r=10, t=30, b=10),
            transition=dict(duration=400)
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available for this asset")

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

    st.subheader("Signal Reasoning")
    for i, r in enumerate(result["reasons"], 1):
        with st.expander(f"Insight {i}"):
            st.write(clean_output(r))

    st.markdown("---")

    st.subheader("AI Insights")

    insight_text = clean_output(result["insight"])
    sections = insight_text.split("\n\n")

    titles = [
        "Financial Interpretation",
        "Short-term Outlook",
        "Investor Takeaway"
    ]

    for i, section in enumerate(sections):
        title = titles[i] if i < len(titles) else f"Insight {i+1}"
        with st.expander(title):
            st.write(section.strip())

    st.caption("Source: Yahoo Finance | Prices may be delayed | For educational use only")
