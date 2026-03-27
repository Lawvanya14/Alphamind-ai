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
    transition: all 0.25s ease;
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
            "Vanguard ETF (VOO)","Dow ETF (DIA)",
            "Russell ETF (IWM)","Tech ETF (XLK)",
            "Finance ETF (XLF)","ARK ETF (ARKK)","Dividend ETF (SCHD)"
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
            "Solana (SOL-USD)","BNB (BNB-USD)","XRP (XRP-USD)"
        ],

        "Indices": [
            "S&P 500 (^GSPC)","Dow Jones (^DJI)",
            "Nasdaq (^IXIC)","Nifty 50 (^NSEI)","Sensex (^BSESN)"
        ]
    }

    category = st.selectbox("Category", list(assets.keys()))
    selected_asset = st.selectbox("Asset", assets[category])
    custom = st.text_input("Custom Ticker")
    analyze = st.button("Analyze")

def extract_ticker(asset):
    return asset.split("(")[-1].replace(")", "")

if not analyze:
    st.info("Select asset and run analysis")

if analyze:

    query = custom.strip().upper() if custom else extract_ticker(selected_asset)

    with st.spinner("Running AI analysis..."):
        graph = build_graph()
        raw = graph.invoke({"query": query})

    prediction = clean_output(raw.get("prediction",""))
    reasons = raw.get("reasons",[])
    insight = clean_output(raw.get("insight",""))

    st.subheader("Price Chart")

    data = yf.download(query, period="3mo", interval="1d", progress=False)
    data = data.dropna()

    if len(data) < 5:
        data = yf.download(query, period="6mo", interval="1d", progress=False)
        data = data.dropna()

    if len(data) < 5:
        st.error("Unable to fetch sufficient data")
    else:
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=data.index,
            y=data["Close"],
            mode="lines",
            line=dict(width=3)
        ))

        fig.update_layout(
            template="plotly_dark",
            hovermode="x unified"
        )

        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.subheader("Prediction")
    st.markdown(f"<div class='card'>{prediction}</div>", unsafe_allow_html=True)

    st.markdown("---")

    st.subheader("Signal Reasoning")

    for i, r in enumerate(reasons, 1):
        st.markdown(
            f"<div class='insight-box'><b>Insight {i}</b><br>{clean_output(r)}</div>",
            unsafe_allow_html=True
        )

    st.markdown("---")

    st.subheader("AI Insights")

    sentences = [s.strip() for s in insight.split(".") if s.strip()]

    financial = sentences[0] if len(sentences) > 0 else "Market shows directional movement."
    outlook = sentences[1] if len(sentences) > 1 else "Short-term trend likely to continue."
    takeaway = ". ".join(sentences[2:]) if len(sentences) > 2 else "Adopt a balanced strategy."

    with st.expander("Financial Interpretation"):
        st.write(financial)

    with st.expander("Short-term Outlook"):
        st.write(outlook)

    with st.expander("Investor Takeaway"):
        st.write(takeaway)

    st.caption("Source: Yahoo Finance | Prices may be delayed")
