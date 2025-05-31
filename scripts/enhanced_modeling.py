#!/usr/bin/env python3.11
import json
import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from statsmodels.tsa.api import VAR
import joblib
from xgboost import XGBRegressor
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.arima.model import ARIMA
import warnings
warnings.filterwarnings('ignore')

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
merged_aapl_df["close_lag1"] = merged_aapl_df["close"].shift(1)
merged_aapl_df["volume_lag1"] = merged_aapl_df["volume"].shift(1)
merged_aapl_df["close_pct_change"] = merged_aapl_df["close"].pct_change() * 100
merged_aapl_df = merged_aapl_df.dropna() # Drop rows with NaN (last row for target, first for lag)

if merged_aapl_df.empty:
    print("Merged AAPL dataframe is empty after feature engineering. Cannot proceed with modeling.")
    sys.exit(1)

print("Sample of merged_aapl_df for modeling:")
print(merged_aapl_df.head())

# --- 4. Model 1: Random Forest Regressor for Price Prediction ---
print("\nTraining Random Forest Regressor for AAPL...")
features = ["close", "volume", "news_sentiment_compound", "sentiment_lag1", "close_lag1", "volume_lag1"]
X = merged_aapl_df[features]
y = merged_aapl_df["target_close_next_day"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False) # Time series data, so no shuffle

# Scale features for better model performance
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Save the scaler for future use
joblib.dump(scaler, os.path.join(MODELS_DIR, "feature_scaler.joblib"))

# Train Random Forest model
rf_model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
rf_model.fit(X_train, y_train)
y_pred_rf = rf_model.predict(X_test)

# Evaluate Random Forest model
mse_rf = mean_squared_error(y_test, y_pred_rf)
mae_rf = mean_absolute_error(y_test, y_pred_rf)
r2_rf = r2_score(y_test, y_pred_rf)
print(f"Random Forest MSE for AAPL: {mse_rf}")
print(f"Random Forest MAE for AAPL: {mae_rf}")
print(f"Random Forest R² for AAPL: {r2_rf}")

# Save the Random Forest model
joblib.dump(rf_model, os.path.join(MODELS_DIR, "aapl_rf_model.joblib"))
print(f"Random Forest model saved to {os.path.join(MODELS_DIR, 'aapl_rf_model.joblib')}")

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

# --- 5. Model 2: XGBoost Regressor ---
print("\nTraining XGBoost Regressor for AAPL...")
xgb_model = XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
xgb_model.fit(X_train_scaled, y_train)
y_pred_xgb = xgb_model.predict(X_test_scaled)

# Evaluate XGBoost model
mse_xgb = mean_squared_error(y_test, y_pred_xgb)
mae_xgb = mean_absolute_error(y_test, y_pred_xgb)
r2_xgb = r2_score(y_test, y_pred_xgb)
print(f"XGBoost MSE for AAPL: {mse_xgb}")
print(f"XGBoost MAE for AAPL: {mae_xgb}")
print(f"XGBoost R² for AAPL: {r2_xgb}")

# Save the XGBoost model
joblib.dump(xgb_model, os.path.join(MODELS_DIR, "aapl_xgb_model.joblib"))
print(f"XGBoost model saved to {os.path.join(MODELS_DIR, 'aapl_xgb_model.joblib')}")

# Plot XGBoost predictions
plt.figure(figsize=(12, 6))
plt.plot(y_test.index, y_test.values, label="Actual Next Day Close")
plt.plot(y_test.index, y_pred_xgb, label="Predicted Next Day Close (XGBoost)", linestyle="--")
plt.title("AAPL Next Day Close Price Prediction (XGBoost)")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.savefig(os.path.join(REPORTS_DIR, "aapl_xgb_prediction.png"))
print(f"Saved XGBoost prediction plot to {os.path.join(REPORTS_DIR, 'aapl_xgb_prediction.png')}")
plt.close()

# --- 6. Model 3: ARIMA for Time Series Forecasting ---
print("\nTraining ARIMA Model for AAPL...")
# Prepare data for ARIMA (using only the close price)
arima_data = merged_aapl_df["close"].copy()

try:
    # Fit ARIMA model - using a simple (1,1,1) model for demonstration
    # In practice, you would use auto_arima or grid search to find optimal parameters
    arima_model = ARIMA(arima_data, order=(1, 1, 1))
    arima_results = arima_model.fit()
    
    # Make predictions for the test period
    arima_forecast = arima_results.forecast(steps=len(y_test))
    
    # Evaluate ARIMA model
    mse_arima = mean_squared_error(y_test, arima_forecast)
    mae_arima = mean_absolute_error(y_test, arima_forecast)
    r2_arima = r2_score(y_test, arima_forecast)
    print(f"ARIMA MSE for AAPL: {mse_arima}")
    print(f"ARIMA MAE for AAPL: {mae_arima}")
    print(f"ARIMA R² for AAPL: {r2_arima}")
    
    # Save the ARIMA model results
    joblib.dump(arima_results, os.path.join(MODELS_DIR, "aapl_arima_model.joblib"))
    print(f"ARIMA model saved to {os.path.join(MODELS_DIR, 'aapl_arima_model.joblib')}")
    
    # Plot ARIMA predictions
    plt.figure(figsize=(12, 6))
    plt.plot(y_test.index, y_test.values, label="Actual Next Day Close")
    plt.plot(y_test.index, arima_forecast, label="Predicted Next Day Close (ARIMA)", linestyle="--")
    plt.title("AAPL Next Day Close Price Prediction (ARIMA)")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.savefig(os.path.join(REPORTS_DIR, "aapl_arima_prediction.png"))
    print(f"Saved ARIMA prediction plot to {os.path.join(REPORTS_DIR, 'aapl_arima_prediction.png')}")
    plt.close()
    
except Exception as e:
    print(f"Error training ARIMA model: {e}")
    arima_forecast = None
    mse_arima = mae_arima = r2_arima = float('nan')

# --- 7. Model 4: VAR Model for Multivariate Time Series Analysis ---
# This is a more complex model and requires careful stationarity checks and parameter tuning.
# Simplified VAR example:
print("\nTraining VAR Model for AAPL...")
var_data = merged_aapl_df[["close", "news_sentiment_compound"]].copy()
# Ensure data is stationary (e.g., by differencing) - SKIPPING for this basic example, but crucial in practice
# var_data_diff = var_data.diff().dropna()

if len(var_data) < 10: # VAR needs sufficient data points
    print("Not enough data points for VAR model after processing.")
    mse_var = mae_var = r2_var = float('nan')
else:
    try:
        var_model = VAR(var_data)
        # lag_order = var_model.select_lags(maxlags=10)
        # print(f"Selected VAR lag order: {lag_order.selected_lags}")
        # results_var = var_model.fit(lag_order.selected_lags) # Use selected lags
        results_var = var_model.fit(maxlags=5, ic='aic') # Or fit with a fixed number or AIC selection
        print(results_var.summary())
        
        # Make predictions for the test period
        var_forecast = results_var.forecast(var_data.values[-results_var.k_ar:], steps=len(y_test))
        var_forecast_close = var_forecast[:, 0]  # Extract close price forecasts
        
        # Evaluate VAR model
        mse_var = mean_squared_error(y_test, var_forecast_close)
        mae_var = mean_absolute_error(y_test, var_forecast_close)
        r2_var = r2_score(y_test, var_forecast_close)
        print(f"VAR MSE for AAPL: {mse_var}")
        print(f"VAR MAE for AAPL: {mae_var}")
        print(f"VAR R² for AAPL: {r2_var}")
        
        # Save the VAR model
        joblib.dump(results_var, os.path.join(MODELS_DIR, "aapl_var_model.joblib"))
        print(f"VAR model saved to {os.path.join(MODELS_DIR, 'aapl_var_model.joblib')}")
        
        # Plot VAR predictions
        plt.figure(figsize=(12, 6))
        plt.plot(y_test.index, y_test.values, label="Actual Next Day Close")
        plt.plot(y_test.index, var_forecast_close, label="Predicted Next Day Close (VAR)", linestyle="--")
        plt.title("AAPL Next Day Close Price Prediction (VAR)")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.legend()
        plt.savefig(os.path.join(REPORTS_DIR, "aapl_var_prediction.png"))
        print(f"Saved VAR prediction plot to {os.path.join(REPORTS_DIR, 'aapl_var_prediction.png')}")
        plt.close()
        
    except Exception as e:
        print(f"Error training VAR model: {e}")
        mse_var = mae_var = r2_var = float('nan')

# --- 8. Model Comparison ---
# Create a DataFrame to compare model performance
models_comparison = pd.DataFrame({
    'Model': ['Random Forest', 'XGBoost', 'ARIMA', 'VAR'],
    'MSE': [mse_rf, mse_xgb, mse_arima, mse_var],
    'RMSE': [np.sqrt(mse_rf), np.sqrt(mse_xgb), np.sqrt(mse_arima) if not np.isnan(mse_arima) else float('nan'), np.sqrt(mse_var) if not np.isnan(mse_var) else float('nan')],
    'MAE': [mae_rf, mae_xgb, mae_arima, mae_var],
    'R²': [r2_rf, r2_xgb, r2_arima, r2_var]
})

# Save the comparison results
models_comparison.to_csv(os.path.join(REPORTS_DIR, "models_comparison.csv"), index=False)
print(f"\nModel comparison saved to {os.path.join(REPORTS_DIR, 'models_comparison.csv')}")

# Print the comparison table
print("\nModel Comparison:")
print(models_comparison)

# Create a bar chart to visualize model comparison (RMSE)
plt.figure(figsize=(10, 6))
plt.bar(models_comparison['Model'], models_comparison['RMSE'])
plt.title('Model Comparison - RMSE (Lower is Better)')
plt.ylabel('RMSE')
plt.xlabel('Model')
plt.savefig(os.path.join(REPORTS_DIR, "model_comparison_rmse.png"))
print(f"Saved model comparison plot to {os.path.join(REPORTS_DIR, 'model_comparison_rmse.png')}")
plt.close()

# Create a bar chart to visualize model comparison (R²)
plt.figure(figsize=(10, 6))
plt.bar(models_comparison['Model'], models_comparison['R²'])
plt.title('Model Comparison - R² (Higher is Better)')
plt.ylabel('R²')
plt.xlabel('Model')
plt.savefig(os.path.join(REPORTS_DIR, "model_comparison_r2.png"))
print(f"Saved model comparison plot to {os.path.join(REPORTS_DIR, 'model_comparison_r2.png')}")
plt.close()

print("\nAdvanced modeling script finished.")
