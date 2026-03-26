def generate_signal(prediction, sentiment, risk):

    score = 0
    reasons = []

    # ML Prediction
    if "Bullish" in prediction:
        score += 1
        reasons.append("ML indicates upward trend")
        pred_strength = 1
    else:
        score -= 1
        reasons.append("ML indicates downward trend")
        pred_strength = 1

    # Sentiment
    if "Bullish" in sentiment:
        score += 1
        reasons.append("Positive market sentiment")
        sent_strength = 1
    elif "Bearish" in sentiment:
        score -= 1
        reasons.append("Negative market sentiment")
        sent_strength = 1
    else:
        reasons.append("Neutral sentiment")
        sent_strength = 0.5

    # Risk
    if "Low" in risk:
        score += 1
        reasons.append("Low volatility")
        risk_strength = 1
    elif "High" in risk:
        score -= 1
        reasons.append("High volatility risk")
        risk_strength = 1
    else:
        reasons.append("Moderate risk")
        risk_strength = 0.5

    # Final Decision
    if score >= 2:
        signal = "BUY"
    elif score >= 0:
        signal = "HOLD"
    else:
        signal = "SELL"

    # 🔥 IMPROVED CONFIDENCE CALCULATION
    agreement = abs(score) / 3   # how much signals agree
    strength = (pred_strength + sent_strength + risk_strength) / 3

    confidence = (0.7 * agreement + 0.3 * strength) * 100

    return signal, round(confidence, 2), reasons
