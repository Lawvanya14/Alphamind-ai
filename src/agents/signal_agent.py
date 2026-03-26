def generate_signal(prediction, sentiment, risk):

    score = 0
    reasons = []

    # ML Prediction
    if "Bullish" in prediction:
        score += 1
        reasons.append("ML indicates upward trend")
    else:
        score -= 1
        reasons.append("ML indicates downward trend")

    # Sentiment
    if "Bullish" in sentiment:
        score += 1
        reasons.append("Positive market sentiment")
    elif "Bearish" in sentiment:
        score -= 1
        reasons.append("Negative market sentiment")
    else:
        reasons.append("Neutral sentiment")

    # Risk
    if "Low" in risk:
        score += 1
        reasons.append("Low volatility")
    elif "High" in risk:
        score -= 1
        reasons.append("High volatility risk")
    else:
        reasons.append("Moderate risk")

    # Final Decision
    if score >= 2:
        signal = "BUY"
    elif score >= 0:
        signal = "HOLD"
    else:
        signal = "SELL"

    confidence = abs(score) / 3 * 100

    return signal, round(confidence, 2), reasons