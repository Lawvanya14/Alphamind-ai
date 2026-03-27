import streamlit as st
from langgraph_flow import build_graph
import plotly.graph_objects as go
import yfinance as yf
import re


st.set_page_config(page_title="AlphaMind AI", layout="wide")


st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #020617, #0f172a);
    color: #e2e8f0;
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

.main-title {
    text-align:center;
    font-size:40px;
    font-weight:700;
    color:#c084fc;
}

.sub-title {
    text-align:center;
    color:#94a3b8;
    font-size:15px;
    margin-bottom:25px;
}

.glass {
    background: rgba(30,41,59,0.6);
    padding:20px;
    border-radius:16px;
    border:1px solid rgba(148,163,184,0.15);
}

.metric-box {
    text-align:center;
    padding:16px;
    border-radius:14px;
    background: rgba(30,41,59,0.5);
    transition:0.3s;
}

.metric-box:hover {
    transform: translateY(-4px);
}

.buy {
    color:#22c55e;
    text-shadow:0 0 8px #22c55e;
}
.sell {
    color:#ef4444;
    text-shadow:0 0 8px #ef4444;
}
.hold {
    color:#facc15;
    text-shadow:0 0 8px #facc15;
}

.reason-box {
    padding:12px;
    margin:6px 0;
    border-radius:10px;
    background: rgba(148,163,184,0.08);
    border-left:3px solid #c084fc;
    transition:0.3s;
}

.reason-box:hover {
    transform: translateX(6px);
    background: rgba(192,132,252,0.15);
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">AlphaMind AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Intelligent Financial Insight System</div>', unsafe_allow_html=True)

with st.sidebar:
    st.title("Control Panel")

    assets = {
        "Stocks": [
            "AAPL - Apple","TSLA - Tesla","NVDA - Nvidia","MSFT - Microsoft",
            "GOOGL - Google","AMZN - Amazon","META - Meta","NFLX - Netflix",
            "RELIANCE.NS - Reliance","TCS.NS - TCS","INFY.NS - Infosys",
            "HDFCBANK.NS - HDFC Bank","ICICIBANK.NS - ICICI Bank",
            "SBIN.NS - SBI","LT.NS - Larsen & Toubro"
        ],
        "Crypto": [
            "BTC-USD - Bitcoin","ETH-USD - Ethereum","SOL-USD - Solana",
            "XRP-USD - XRP","ADA-USD - Cardano"
        ],
        "Indices": [
            "^GSPC - S&P 500","^IXIC - Nasdaq","^DJI - Dow Jones",
            "^NSEI - Nifty 50","^BSESN - Sensex"
        ],
        "ETFs": [
            "SPY - S&P500 ETF","QQQ - Nasdaq ETF",
            "GOLDBEES.NS - Gold ETF","SILVERBEES.NS - Silver ETF",
            "NIFTYBEES.NS - Nifty ETF","BANKBEES.NS - Bank ETF",
            "ITBEES.NS - IT ETF"
        ]
    }

    category = st.selectbox("Category", list(assets.keys()))
    selected_asset = st.selectbox("Asset", assets[category])
    custom = st.text_input("Custom Ticker")
    analyze = st.button("Analyze")


def clean_text(text):
    text = re.sub(r"\*\*", "", text) 
    text = re.sub(r"\n?\s*\d+\.\s*$", "", text) 
    text = re.sub(r"\n\s*\d+\.\s*", "\n", text)  
    return text.strip()

def extract_section(text, start, end=None):
    try:
        if end:
            pattern = rf"{start}[:\-]?(.*?){end}"
        else:
            pattern = rf"{start}[:\-]?(.*)"
        match = re.search(pattern, text, re.S | re.I)
        return clean_text(match.group(1)) if match else "No data available"
    except:
        return "No data available"

def format_output(result):
    text = str(result.get("insight", ""))

    return {
        "market": result.get("market_data", {}),
        "prediction": result.get("prediction", ""),
        "signal": result.get("signal", "HOLD"),
        "confidence": int(result.get("confidence", 70)),
        "reasons": result.get("reasons", []),
        "insight": {
            "interpretation": extract_section(text, "Financial Interpretation", "Short-term Outlook"),
            "outlook": extract_section(text, "Short-term Outlook", "Investor Takeaway"),
            "takeaway": extract_section(text, "Investor Takeaway")
        }
    }

if not analyze:
    st.info("Select asset and analyze")

if analyze:

    query = custom if custom else selected_asset.split(" - ")[0]

    try:
        with st.spinner("Running AI..."):
            graph = build_graph()
            raw = graph.invoke({"query": query})
            result = format_output(raw)

        market = result["market"]

       
        st.subheader("Market Overview")
        c1, c2, c3, c4 = st.columns(4)

        def metric(title, val, cls=""):
            st.markdown(
                f"<div class='metric-box'><div>{title}</div><div class='{cls}'>{val}</div></div>",
                unsafe_allow_html=True
            )

        price = market.get("price", 0)
        usd_to_inr = 83
        price_display = f"$ {price} | ₹ {round(price*usd_to_inr,2)}"

        with c1: metric("Price", price_display)
        with c2: metric("Change", f"{market.get('change','N/A')}%")
        with c3: metric("Trend", market.get("trend","N/A"))
        with c4:
            cls = "buy" if result["signal"]=="BUY" else "sell" if result["signal"]=="SELL" else "hold"
            metric("Signal", result["signal"], cls)

        st.caption("Data Source: Yahoo Finance | Prices may be delayed")
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
        else:
            st.warning("No chart data available")

       
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
            icon = "📉" if "down" in r.lower() else "📈"
            st.markdown(f"<div class='reason-box'>{icon} {r}</div>", unsafe_allow_html=True)

        
        st.subheader("AI Insights")

        with st.expander("Financial Interpretation", True):
            st.markdown(f"<div class='glass'>{result['insight']['interpretation']}</div>", unsafe_allow_html=True)

        with st.expander("Short-term Outlook"):
            st.markdown(f"<div class='glass'>{result['insight']['outlook']}</div>", unsafe_allow_html=True)

        with st.expander("Investor Takeaway"):
            st.markdown(f"<div class='glass'>{result['insight']['takeaway']}</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Something went wrong: {str(e)}")
