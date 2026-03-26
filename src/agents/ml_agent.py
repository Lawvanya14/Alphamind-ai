import yfinance as yf
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier


def calculate_rsi(series, window=14):

    delta = series.diff()

    gain = (delta.where(delta > 0, 0)).rolling(window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def predict_price_movement(symbol):

    # Fetch historical data
    data = yf.download(symbol, period="3mo", interval="1d")

    if data.empty:
        return "Prediction unavailable"

    df = data.copy()

    # Feature engineering
    df["return"] = df["Close"].pct_change()
    df["ma5"] = df["Close"].rolling(5).mean()
    df["ma10"] = df["Close"].rolling(10).mean()
    df["volatility"] = df["return"].rolling(5).std()

    # NEW FEATURES
    df["momentum"] = df["Close"] - df["Close"].shift(5)
    df["rsi"] = calculate_rsi(df["Close"])

    # Target variable
    df["target"] = (df["Close"].shift(-1) > df["Close"]).astype(int)

    df.dropna(inplace=True)

    features = ["return", "ma5", "ma10", "volatility", "momentum", "rsi"]

    X = df[features]
    y = df["target"]

    # Train models
    lr_model = LogisticRegression(max_iter=500)
    rf_model = RandomForestClassifier(n_estimators=120, random_state=42)

    lr_model.fit(X, y)
    rf_model.fit(X, y)

    # Latest data for prediction
    latest_data = pd.DataFrame([df[features].iloc[-1]])

    lr_pred = lr_model.predict(latest_data)[0]
    rf_pred = rf_model.predict(latest_data)[0]

    # Ensemble vote
    prediction = round((lr_pred + rf_pred) / 2)

    if prediction == 1:
        return "Bullish probability higher (price may increase)"
    else:
        return "Bearish probability higher (price may decrease)"