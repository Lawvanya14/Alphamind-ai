def analyze_risk(market_data):

    print("\n⚠ Assessing market risk...\n")

    change = market_data["change"]

    if abs(change) > 3:
        risk = "High volatility risk"
    elif abs(change) > 1:
        risk = "Moderate market volatility"
    else:
        risk = "Low volatility"

    print("Risk Level:", risk)

    return risk