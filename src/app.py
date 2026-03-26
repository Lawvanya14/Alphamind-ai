import streamlit as st
from langgraph_flow import build_graph
import plotly.graph_objects as go
import yfinance as yf
import re

st.set_page_config(page_title="AlphaMind AI", layout="wide")

# CLEAN OUTPUT 
def clean_output(text):
    text = re.sub(r"\*\*\d+\.", "", text)
    return text.strip()

#  GLOBAL STYLES
st.markdown("""
<style>

/*  BASE*/
html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

/* MAIN BACKGROUND */
.main {
    background: linear-gradient(135deg, #020617, #0f172a);
    color: #e2e8f0;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020617, #0f172a);
    padding: 20px;
}

/* Sidebar Title */
.sidebar-title {
    font-size: 26px;
    font-weight: 700;
    background: linear-gradient(90deg, #a78bfa, #38bdf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 20px;
}

/* Labels */
label {
    color: #94a3b8 !important;
    font-size: 13px !important;
}

/* Inputs */
.stSelectbox div, .stTextInput input {
    background-color: #020617 !important;
    color: white !important;
    border-radius: 10px !important;
    border: 1px solid #334155 !important;
}

/* Button */
.stButton button {
    width: 100%;
    background: linear-gradient(90deg, #6366f1, #a855f7);
    color: white;
    border-radius: 10px;
    padding: 10px;
    border: none;
    font-weight: 600;
}

.stButton button:hover {
    background: linear-gradient(90deg, #4f46e5, #9333ea);
}

/*  HEADER */
.main-title {
    text-align:center;
    font-size:42px;
    font-weight:700;
    background: linear-gradient(90deg, #c084fc, #38bdf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.sub-title {
    text-align:center;
    color:#94a3b8;
    margin-bottom:25px;
}

/*  CARDS */
.glass {
    background: rgba(30,41,59,0.6);
    padding:20px;
    border-radius:16px;
    border:1px solid rgba(148,163,184,0.15);
}

/* METRICS */
.metric-box {
    text-align:center;
    padding:16px;
    border-radius:14px;
    background: rgba(30,41,59,0.5);
}

/* Signal Colors */
.buy { color:#22c55e; }
.sell { color:#ef4444; }
.hold { color:#facc15; }

/* REASONS */
.reason-box {
    padding:12px;
    margin:6px 0;
    border-radius:10px;
    background: rgba(148,163,184,0.08);
    border-left:3px solid #c084fc;
    transition:0.2s;
}

.reason-box:hover {
    transform: translateX(4px);
}

</style>
""", unsafe_allow_html=True)


st.markdown('<div class="main-title">AlphaMind AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Intelligent Financial Insight System</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="sidebar-title">Control Panel</div>', unsafe_allow_html=True)

    assets = {
        "Stocks": [
            "AAPL - Apple","TSLA - Tesla","NVDA - Nvidia","MSFT - Microsoft",
            "GOOGL - Google","AMZN - Amazon","META - Meta","NFLX - Netflix",
            "RELIANCE.NS - Reliance","TCS.NS - TCS","INFY.NS - Infosys"
        ],
        "Crypto": [
            "BTC-USD - Bitcoin","ETH-USD - Ethereum","SOL-USD - Solana",
            "XRP-USD - XRP","ADA-USD - Cardano"
        ],
        "Indices": [
            "^GSPC - S&P 500","^IXIC - Nasdaq","^DJI - Dow Jones",
            "^NSEI - Nifty 50","^BSESN - Sensex"
        ]
    }

    category = st.selectbox("Category", list(assets.keys()))
    selected_asset = st.selectbox("Asset", assets[category])
    custom = st.text_input("Custom Ticker")

    analyze = st.button("Analyze")


def extract(text, start, end=None):
    if end:
        pattern = rf"{start}\*\*(.*?){end}\*\*"
    else:
        pattern = rf"{start}\*\*(.*)"
    match = re.search(pattern, text, re.S)
    return match.group(1).strip() if match else ""

def format_output(result):
    text = str(result.get("insight", ""))

    return {
        "market": result.get("market_data", {}),
        "prediction": clean_output(result.get("prediction", "")),
        "signal": result.get("signal", "HOLD"),
        "confidence": int(result.get("confidence", 70)),
        "reasons": result.get("reasons", []),
        "insight": {
            "interpretation": clean_output(extract(text, "Financial Interpretation", "Short-term Outlook")),
            "outlook": clean_output(extract(text, "Short-term Outlook", "Investor Takeaway")),
            "takeaway": clean_output(extract(text, "Investor Takeaway"))
        }
    }


if not analyze:
    st.info("Select asset and analyze")

if analyze:

    query = custom.strip().upper() if custom else selected_asset.split(" - ")[0]

    with st.spinner("Running analysis..."):
        graph = build_graph()
        raw = graph.invoke({"query": query})
        result = format_output(raw)

    market = result["market"]

    #  METRICS 
    st.subheader("Market Overview")
    c1, c2, c3, c4 = st.columns(4)

    def metric(title, val, cls=""):
        st.markdown(f"<div class='metric-box'><div>{title}</div><div class='{cls}'>{val}</div></div>", unsafe_allow_html=True)

    price = market.get("price", 0)
    usd_to_inr = 83
    price_display = f"$ {price} | ₹ {round(price*usd_to_inr,2)}"

    with c1: metric("Price", price_display)
    with c2: metric("Change", f"{market.get('change','N/A')}%")
    with c3: metric("Trend", market.get("trend","N/A"))
    with c4:
        cls = "buy" if result["signal"]=="BUY" else "sell" if result["signal"]=="SELL" else "hold"
        metric("Signal", result["signal"], cls)

    st.divider()

    
    st.subheader("Price Chart")
    data = yf.download(query, period="3mo")

    if not data.empty:
        data['MA20'] = data['Close'].rolling(20).mean()

        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close']
        ))
        fig.add_trace(go.Scatter(x=data.index, y=data['MA20'], name="MA20"))
        fig.update_layout(template="plotly_dark", height=500)

        st.plotly_chart(fig, use_container_width=True)


    st.subheader("Prediction")
    col1, col2 = st.columns([2,1])

    with col1:
        st.markdown(f"<div class='glass'>{result['prediction']}</div>", unsafe_allow_html=True)

    with col2:
        conf = result['confidence']
        color = "#22c55e" if conf>75 else "#facc15" if conf>50 else "#ef4444"

        st.markdown(
            f"<div class='glass'><div>Confidence</div><div style='font-size:30px;color:{color}'>{conf}%</div></div>",
            unsafe_allow_html=True
        )
        st.progress(conf/100)

    st.subheader("Signal Reasoning")
    for r in result["reasons"]:
        st.markdown(f"<div class='reason-box'>{clean_output(r)}</div>", unsafe_allow_html=True)

    st.subheader("AI Insights")

    with st.expander("Interpretation", True):
        st.markdown(f"<div class='glass'>{result['insight']['interpretation']}</div>", unsafe_allow_html=True)

    with st.expander("Short-term Outlook"):
        st.markdown(f"<div class='glass'>{result['insight']['outlook']}</div>", unsafe_allow_html=True)

    with st.expander("Takeaway"):
        st.markdown(f"<div class='glass'>{result['insight']['takeaway']}</div>", unsafe_allow_html=True)
```
