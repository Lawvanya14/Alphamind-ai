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

.sidebar-title {
    font-size: 24px;
    font-weight: 700;
}

.metric {
    text-align: center;
    padding: 12px;
    border-radius: 10px;
    background: rgba(30,41,59,0.5);
}

.card {
    background: rgba(30,41,59,0.6);
    padding: 18px;
    border-radius: 12px;
}

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

st.markdown("<h1 style='text-align:center;'>AlphaMind AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#94a3b8;'>AI-powered financial intelligence platform</p>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<div class='sidebar-title'>Control Panel</div>", unsafe_allow_html=True)

    assets = {

        "US Stocks": [
            "Apple (AAPL)","Microsoft (MSFT)","Google (GOOGL)","Amazon (AMZN)",
            "Meta (META)","Tesla (TSLA)","Nvidia (NVDA)","Netflix (NFLX)",
            "AMD (AMD)","Intel (INTC)","Oracle (ORCL)","IBM (IBM)",
            "Cisco (CSCO)","Adobe (ADBE)","Salesforce (CRM)",
            "Uber (UBER)","Lyft (LYFT)","PayPal (PYPL)",
            "Shopify (SHOP)","Snap (SNAP)"
        ],

        "Indian Stocks": [
            "Reliance (RELIANCE.NS)","TCS (TCS.NS)","Infosys (INFY.NS)",
            "HDFC Bank (HDFCBANK.NS)","ICICI Bank (ICICIBANK.NS)",
            "SBI (SBIN.NS)","L&T (LT.NS)","Axis Bank (AXISBANK.NS)",
            "Kotak Bank (KOTAKBANK.NS)","ITC (ITC.NS)",
            "Airtel (BHARTIARTL.NS)","Asian Paints (ASIANPAINT.NS)",
            "Maruti (MARUTI.NS)","Sun Pharma (SUNPHARMA.NS)","Wipro (WIPRO.NS)"
        ],

        "US ETFs": [
            "S&P 500 ETF (SPY)","Nasdaq ETF (QQQ)","Total Market ETF (VTI)",
            "Vanguard S&P ETF (VOO)","Dow Jones ETF (DIA)",
            "Russell 2000 ETF (IWM)","Tech ETF (XLK)",
            "Financial ETF (XLF)","ARK Innovation ETF (ARKK)",
            "Dividend ETF (SCHD)"
        ],

        "Indian ETFs": [
            "Nifty ETF (NIFTYBEES.NS)",
            "Bank ETF (BANKBEES.NS)",
            "Gold ETF (GOLDBEES.NS)",
            "Silver ETF (SILVERBEES.NS)",
            "IT ETF (ITBEES.NS)"
        ],

        "Crypto": [
            "Bitcoin (BTC-USD)","Ethereum (ETH-USD)",
            "Solana (SOL-USD)","BNB (BNB-USD)",
            "XRP (XRP-USD)"
        ],

        "Indices": [
            "S&P 500 (^GSPC)","Dow Jones (^DJI)",
            "Nasdaq (^IXIC)","Nifty 50 (^NSEI)",
            "Sensex (^BSESN)"
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
    st.info("Select asset and run analysis")

if analyze:

    query = custom.strip().upper() if custom else selected_asset.split("(")[-1].replace(")", "")

    with st.spinner("Running AI analysis..."):
        graph = build_graph()
        raw = graph.invoke({"query": query})
        result = format_output(raw)

    market = result["market"]

    st.subheader("Market Overview")
    c1, c2, c3, c4 = st.columns(4)

    def metric(title, val):
        st.markdown(f"<div class='metric'><div>{title}</div><b>{val}</b></div>", unsafe_allow_html=True)

    price = market.get("price", "N/A")

    metric_map = {
        ".NS": f"₹ {price}",
        "-USD": f"$ {price}",
        "^": f"{price}"
    }

    price_display = f"$ {price}"
    for k in metric_map:
        if k in query:
            price_display = metric_map[k]

    with c1: metric("Price", price_display)
    with c2: metric("Change", f"{market.get('change','N/A')}%")
    with c3: metric("Trend", market.get("trend","N/A"))
    with c4: metric("Signal", result["signal"])

    st.markdown("---")

    st.subheader("Price Chart")

    data = yf.download(query, period="3mo", interval="1d", progress=False)
    data = data.dropna()

    if len(data) < 5:
        data = yf.download(query, period="6mo", interval="1d", progress=False)
        data = data.dropna()

    if len(data) < 5:
        st.warning("Not enough data to render chart")
    else:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data["Close"],
            mode="lines",
            line=dict(width=3)
        ))
        fig.update_layout(template="plotly_dark", hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.subheader("Prediction")
    st.markdown(f"<div class='card'>{result['prediction']}</div>", unsafe_allow_html=True)

    st.markdown("---")

    st.subheader("Signal Reasoning")

    for i, r in enumerate(result["reasons"], 1):
        st.markdown(
            f"<div class='insight-box'><b>Insight {i}</b><br>{clean_output(r)}</div>",
            unsafe_allow_html=True
        )

    st.markdown("---")

    st.subheader("AI Insights")

    insight_text = clean_output(result["insight"])
    parts = insight_text.split(". ")

    financial = parts[0] if len(parts) > 0 else ""
    outlook = parts[1] if len(parts) > 1 else ""
    takeaway = ". ".join(parts[2:]) if len(parts) > 2 else ""

    if not financial.strip():
        financial = "Market trend suggests moderate movement based on current data."

    if not outlook.strip():
        outlook = "Short-term outlook remains stable with possible minor fluctuations."

    if not takeaway.strip():
        takeaway = "Investors should adopt a balanced strategy and monitor changes."

    with st.expander("Financial Interpretation"):
        st.write(financial)

    with st.expander("Short-term Outlook"):
        st.write(outlook)

    with st.expander("Investor Takeaway"):
        st.write(takeaway)

    st.caption("Source: Yahoo Finance | Prices may be delayed")
