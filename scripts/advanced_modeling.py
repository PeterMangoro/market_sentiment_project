#!/usr/bin/env python3.11
import json
import os
import sys
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.api import VAR
import matplotlib.pyplot as plt

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

DATA_DIR = os.path.join(project_root, "data")
NEWS_SENTIMENT_FILE = os.path.join(DATA_DIR, "news_with_sentiment.json")
TWITTER_SENTIMENT_FILE = os.path.join(DATA_DIR, "twitter_with_sentiment.json")
STOCK_DATA_DIR = os.path.join(DATA_DIR, "stock_data")
MODELS_DIR = os.path.join(project_root, "models")
REPORTS_DIR = os.path.join(project_root, "reports", "modeling_results")

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# --- 1. Load Data ---
def load_json_data(filepath):
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Data file not found at {filepath}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {filepath}")
        return None

print("Loading data...")
news_sentiment_data = load_json_data(NEWS_SENTIMENT_FILE)
twitter_sentiment_data = load_json_data(TWITTER_SENTIMENT_FILE) # This is a list of query responses

stock_symbols = ["AAPL", "MSFT", "GOOGL"]
all_stock_data = {}
for symbol in stock_symbols:
    stock_file = os.path.join(STOCK_DATA_DIR, f"{symbol}_stock_data.json")
    data = load_json_data(stock_file)
    if data and data.get("chart") and data["chart"].get("result") and data["chart"]["result"][0].get("timestamp"):
        df = pd.DataFrame({
            "timestamp": data["chart"]["result"][0]["timestamp"],
            "close": data["chart"]["result"][0]["indicators"]["quote"][0]["close"],
            "volume": data["chart"]["result"][0]["indicators"]["quote"][0]["volume"]
        })
        df["date"] = pd.to_datetime(df["timestamp"], unit="s").dt.date
        df = df.dropna(subset=["close"])
        all_stock_data[symbol] = df.set_index("date")
    else:
        print(f"Could not load or parse stock data for {symbol}")

# --- 2. Preprocess and Merge Data (Example for AAPL) ---
# This part needs to be more robust and handle multiple stocks, aggregation of sentiment etc.
# For now, a simplified example for one stock (AAPL)

if not all_stock_data.get("AAPL") is not None or news_sentiment_data is None:
    print("Missing necessary data for AAPL or news sentiment. Exiting modeling script.")
    sys.exit(1)

# Process News Sentiment for AAPL
# Assuming news_sentiment_data is a list of articles, each with a sentiment dict and entities
aapl_news_sentiment_list = []
if news_sentiment_data:
    for article in news_sentiment_data:
        is_aapl = False
        if article.get("entities"):
            for entity in article.get("entities"):
                if entity.get("symbol") == "AAPL":
                    is_aapl = True
                    break
        if is_aapl and article.get("sentiment") and isinstance(article.get("published_at"), str):
            try:
                # Ensure published_at is valid and parseable
                date_str = article["published_at"].split("T")[0]
                article_date = pd.to_datetime(date_str).date()
                aapl_news_sentiment_list.append({
                    "date": article_date,
                    "news_sentiment_compound": article["sentiment"].get("compound", 0)
                })
            except Exception as e:
                print(f"Skipping article due to date parsing error: {e}, date: {article.get('published_at')}")

if not aapl_news_sentiment_list:
    print("No AAPL news sentiment data found or processed. Using zeros.")
    # Create a dummy entry to prevent crash if no news data, or handle this more gracefully
    # This is a placeholder, ideally, you'd ensure data exists or handle it in the model
    aapl_news_df = pd.DataFrame(columns=["date", "news_sentiment_compound"]).set_index("date")
else:
    aapl_news_df = pd.DataFrame(aapl_news_sentiment_list)
    aapl_news_df["date"] = pd.to_datetime(aapl_news_df["date"])
    # Aggregate sentiment per day (e.g., mean)
    aapl_news_df = aapl_news_df.groupby("date")["news_sentiment_compound"].mean().reset_index()
    aapl_news_df = aapl_news_df.set_index("date")

# Combine with stock data
aapl_stock_df = all_stock_data.get("AAPL")
if aapl_stock_df is None:
    print("AAPL stock data not loaded. Exiting.")
    sys.exit(1)

# Ensure index is datetime for proper merging
aapl_stock_df.index = pd.to_datetime(aapl_stock_df.index)
aapl_news_df.index = pd.to_datetime(aapl_news_df.index)

merged_aapl_df = aapl_stock_df.join(aapl_news_df, how="left").fillna(0) # Fill missing sentiment with 0 (neutral)

# --- 3. Feature Engineering ---
merged_aapl_df["target_close_next_day"] = merged_aapl_df["close"].shift(-1)
merged_aapl_df["sentiment_lag1"] = merged_aapl_df["news_sentiment_compound"].shift(1)
merged_aapl_df = merged_aapl_df.dropna() # Drop rows with NaN (last row for target, first for lag)

if merged_aapl_df.empty:
    print("Merged AAPL dataframe is empty after feature engineering. Cannot proceed with modeling.")
    sys.exit(1)

print("Sample of merged_aapl_df for modeling:")
print(merged_aapl_df.head())

# --- 4. Model 1: Random Forest Regressor for Price Prediction ---
print("\nTraining Random Forest Regressor for AAPL...")
features = ["close", "volume", "news_sentiment_compound", "sentiment_lag1"]
X = merged_aapl_df[features]
y = merged_aapl_df["target_close_next_day"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False) # Time series data, so no shuffle

rf_model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
rf_model.fit(X_train, y_train)
y_pred_rf = rf_model.predict(X_test)

mse_rf = mean_squared_error(y_test, y_pred_rf)
print(f"Random Forest MSE for AAPL: {mse_rf}")

# Plot RF predictions
plt.figure(figsize=(12, 6))
plt.plot(y_test.index, y_test.values, label="Actual Next Day Close")
plt.plot(y_test.index, y_pred_rf, label="Predicted Next Day Close (RF)", linestyle="--")
plt.title("AAPL Next Day Close Price Prediction (Random Forest)")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.savefig(os.path.join(REPORTS_DIR, "aapl_rf_prediction.png"))
print(f"Saved RF prediction plot to {os.path.join(REPORTS_DIR, 'aapl_rf_prediction.png')}")
plt.close()

# --- 5. Model 2: VAR Model for Multivariate Time Series Analysis ---
# This is a more complex model and requires careful stationarity checks and parameter tuning.
# Simplified VAR example:
print("\nTraining VAR Model for AAPL...")
var_data = merged_aapl_df[["close", "news_sentiment_compound"]].copy()
# Ensure data is stationary (e.g., by differencing) - SKIPPING for this basic example, but crucial in practice
# var_data_diff = var_data.diff().dropna()

if len(var_data) < 10: # VAR needs sufficient data points
    print("Not enough data points for VAR model after processing.")
else:
    try:
        var_model = VAR(var_data)
        # lag_order = var_model.select_lags(maxlags=10)
        # print(f"Selected VAR lag order: {lag_order.selected_lags}")
        # results_var = var_model.fit(lag_order.selected_lags) # Use selected lags
        results_var = var_model.fit(maxlags=5, ic='aic') # Or fit with a fixed number or AIC selection
        print(results_var.summary())
        # results_var.plot_forecast(steps=5)
        # plt.savefig(os.path.join(REPORTS_DIR, "aapl_var_forecast.png"))
        # print(f"Saved VAR forecast plot to {os.path.join(REPORTS_DIR, 'aapl_var_forecast.png')}")
        # plt.close()
    except Exception as e:
        print(f"Error training VAR model: {e}")

print("\nAdvanced modeling script finished.")

