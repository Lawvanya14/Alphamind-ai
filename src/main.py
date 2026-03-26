from langgraph_flow import build_graph


def format_output(result):
    # ---- SAFE EXTRACTION ----
    market_data = result.get("market_data", {})

    prediction = result.get("prediction", "No prediction")
    sentiment = result.get("sentiment", "Neutral")
    risk = result.get("risk", "Medium")

    signal = str(result.get("signal", "HOLD")).upper()

    # ---- CONFIDENCE FIX ----
    confidence = result.get("confidence", 70)
    try:
        if isinstance(confidence, str):
            confidence = int(''.join(filter(str.isdigit, confidence)))
        confidence = int(confidence)
    except:
        confidence = 70

    # ---- REASONS FIX ----
    reasons = result.get("reasons", [])
    if isinstance(reasons, str):
        reasons = [reasons]

    # ---- INSIGHT FIX ----
    raw_insight = result.get("insight", "")

    if isinstance(raw_insight, dict):
        insight = raw_insight
    else:
        insight = {
            "interpretation": raw_insight,
            "outlook": "",
            "takeaway": ""
        }

    return {
        "market_data": market_data,
        "prediction": prediction,
        "sentiment": sentiment,
        "risk": risk,
        "signal": signal,
        "confidence": confidence,
        "reasons": reasons,
        "insight": insight
    }


def main():
    print("\n Financial AI Agent System Starting...\n")

    user_query = input("Ask about a stock / ETF / crypto: ").strip()

    if not user_query:
        print("⚠️ Please enter a valid asset name.")
        return

    try:
        graph = build_graph()

        print(" Running AI agent workflow...\n")

        raw_result = graph.invoke({"query": user_query})

        # FORMAT HERE
        result = format_output(raw_result)

        market_data = result["market_data"]

        print("\n========================================")
        print("        AI FINANCIAL ANALYSIS REPORT")
        print("========================================")

        print(f"\nAsset: {market_data.get('symbol', 'N/A')}")
        print(f"Price: ₹{market_data.get('price', 'N/A')}")
        print(f"Daily Change: {market_data.get('change', 'N/A')}%")
        print(f"Trend: {market_data.get('trend', 'N/A')}")

        print(f"\nML Prediction: {result['prediction']}")

        print(f"\nMarket Sentiment: {result['sentiment']}")
        print(f"Risk Level: {result['risk']}")

        print("\n📊 Trading Signal")
        print("----------------------------------------")
        print(f"Signal: {result['signal']}")
        print(f"Confidence: {result['confidence']}%")

        print("\nReasoning:")
        for r in result["reasons"]:
            print(f"• {r}")

        print("\n🔎 AI Insight")
        print("----------------------------------------")
        print(result["insight"]["interpretation"])

        print("\n========================================")
        print("          Analysis Completed")
        print("========================================\n")

    except Exception as e:
        print("❌ Unexpected error occurred:", str(e))


if __name__ == "__main__":
    main()