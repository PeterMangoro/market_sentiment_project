#!/usr/bin/env python3.11
import json
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

DATA_DIR = os.path.join(project_root, "data")
REPORTS_DIR = os.path.join(project_root, "reports")
VISUALIZATIONS_DIR = os.path.join(REPORTS_DIR, "dashboard_visualizations") # Save plots here
TABLEAU_DATA_DIR = os.path.join(project_root, "visualizations_tableau") # Save CSVs for Tableau here

os.makedirs(VISUALIZATIONS_DIR, exist_ok=True)
os.makedirs(TABLEAU_DATA_DIR, exist_ok=True)

NEWS_SENTIMENT_FILE = os.path.join(DATA_DIR, "news_with_sentiment.json")
TWITTER_SENTIMENT_FILE = os.path.join(DATA_DIR, "twitter_with_sentiment.json") # Sample data
STOCK_DATA_DIR = os.path.join(DATA_DIR, "stock_data")

print("Starting dashboard visualization script...")

# --- 1. Load Data ---
def load_json_data(filepath):
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Data file not found at {filepath}")
        return []
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {filepath}")
        return []

news_data_raw = load_json_data(NEWS_SENTIMENT_FILE)
# twitter_data_raw = load_json_data(TWITTER_SENTIMENT_FILE) # Assuming this is a list of tweet objects with sentiment

stock_symbols = ["AAPL", "MSFT", "GOOGL"]
all_stock_dfs = {}
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
        df["symbol"] = symbol
        df = df.dropna(subset=["close"])
        all_stock_dfs[symbol] = df.set_index("date")
    else:
        print(f"Could not load or parse stock data for {symbol}")

if not all_stock_dfs:
    print("No stock data loaded. Exiting visualization script.")
    sys.exit(1)

# Combine all stock data into one DataFrame
combined_stock_df = pd.concat(all_stock_dfs.values())
combined_stock_df.index = pd.to_datetime(combined_stock_df.index)

# --- 2. Process News Sentiment Data ---
processed_news = []
for article in news_data_raw:
    # Determine relevant symbols for the article
    article_symbols = []
    if article.get("entities"):
        for entity in article.get("entities"):
            if entity.get("symbol") in stock_symbols:
                article_symbols.append(entity.get("symbol"))
    
    if not article_symbols: # If no target symbols, assign to all or skip
        # For simplicity, let's assume an article without specific entities might be general market news
        # or we could assign it to all symbols if it's broadly relevant.
        # Here, we'll just create an entry for each symbol if it's general, or skip if no entities.
        # This logic can be refined based on how general news should be treated.
        pass # Or assign to all: article_symbols = stock_symbols

    for symbol_in_article in article_symbols:
        if article.get("sentiment") and isinstance(article.get("published_at"), str):
            try:
                date_str = article["published_at"].split("T")[0]
                article_date = pd.to_datetime(date_str).date()
                processed_news.append({
                    "date": article_date,
                    "symbol": symbol_in_article,
                    "news_headline": article.get("title", "N/A"),
                    "news_sentiment_compound": article["sentiment"].get("compound", 0),
                    "news_sentiment_pos": article["sentiment"].get("pos", 0),
                    "news_sentiment_neg": article["sentiment"].get("neg", 0),
                    "news_sentiment_neu": article["sentiment"].get("neu", 0)
                })
            except Exception as e:
                print(f"Skipping news article due to processing error: {e}")

if not processed_news:
    print("No news sentiment data processed. Creating empty DataFrame.")
    news_sentiment_df = pd.DataFrame(columns=["date", "symbol", "news_headline", "news_sentiment_compound", "news_sentiment_pos", "news_sentiment_neg", "news_sentiment_neu"])
else:
    news_sentiment_df = pd.DataFrame(processed_news)
    news_sentiment_df["date"] = pd.to_datetime(news_sentiment_df["date"])

# Aggregate news sentiment per day per symbol (e.g., mean compound score)
daily_news_sentiment = news_sentiment_df.groupby(["date", "symbol"])["news_sentiment_compound"].mean().reset_index()
daily_news_sentiment = daily_news_sentiment.rename(columns={"news_sentiment_compound": "avg_daily_news_sentiment"})
daily_news_sentiment.set_index("date", inplace=True)

# --- 3. Merge Data for Tableau/Visualizations ---
# Merge stock data with daily news sentiment
master_df_list = []
for symbol in stock_symbols:
    if symbol in all_stock_dfs:
        stock_df_sym = all_stock_dfs[symbol].copy()
        stock_df_sym.index = pd.to_datetime(stock_df_sym.index)
        
        news_sentiment_sym = daily_news_sentiment[daily_news_sentiment["symbol"] == symbol][["avg_daily_news_sentiment"]]
        
        merged_sym = stock_df_sym.join(news_sentiment_sym, how="left")
        merged_sym["symbol"] = symbol # Ensure symbol column is present after join
        merged_sym.fillna({"avg_daily_news_sentiment": 0}, inplace=True) # Fill missing sentiment with 0
        master_df_list.append(merged_sym.reset_index()) # Reset index to have 'date' as a column

if not master_df_list:
    print("No data to merge for master DataFrame. Exiting.")
    sys.exit(1)

master_df = pd.concat(master_df_list)
master_df["date"] = pd.to_datetime(master_df["date"])

# Save master_df for Tableau
master_df_path = os.path.join(TABLEAU_DATA_DIR, "master_sentiment_stock_data.csv")
master_df.to_csv(master_df_path, index=False)
print(f"Saved master data for Tableau to {master_df_path}")

# --- 4. Generate Visualizations ---

# a. Stock Price Over Time (already done in modeling, but good for dashboard)
plt.figure(figsize=(14, 7))
sns.lineplot(data=master_df, x="date", y="close", hue="symbol")
plt.title("Stock Closing Prices Over Time")
plt.ylabel("Closing Price (USD)")
plt.xlabel("Date")
plt.legend(title="Symbol")
plt.tight_layout()
plt.savefig(os.path.join(VISUALIZATIONS_DIR, "stock_prices_over_time.png"))
plt.close()
print(f"Saved stock_prices_over_time.png to {VISUALIZATIONS_DIR}")

# b. Average Daily News Sentiment Over Time
plt.figure(figsize=(14, 7))
sns.lineplot(data=master_df, x="date", y="avg_daily_news_sentiment", hue="symbol")
plt.title("Average Daily News Sentiment (Compound Score) Over Time")
plt.ylabel("Average Compound Sentiment")
plt.xlabel("Date")
plt.axhline(0, color='grey', linestyle='--', linewidth=0.8)
plt.legend(title="Symbol")
plt.tight_layout()
plt.savefig(os.path.join(VISUALIZATIONS_DIR, "avg_news_sentiment_over_time.png"))
plt.close()
print(f"Saved avg_news_sentiment_over_time.png to {VISUALIZATIONS_DIR}")

# c. Sentiment Distribution by Stock
plt.figure(figsize=(10, 6))
sns.boxplot(data=news_sentiment_df, x="symbol", y="news_sentiment_compound", order=stock_symbols)
plt.title("Distribution of News Sentiment Scores by Stock")
plt.ylabel("Compound Sentiment Score")
plt.xlabel("Stock Symbol")
plt.axhline(0, color='grey', linestyle='--', linewidth=0.8)
plt.tight_layout()
plt.savefig(os.path.join(VISUALIZATIONS_DIR, "news_sentiment_distribution_boxplot.png"))
plt.close()
print(f"Saved news_sentiment_distribution_boxplot.png to {VISUALIZATIONS_DIR}")

# d. Correlation Heatmap (Sentiment vs. Price Change - requires price change calculation)
master_df["price_change_pct"] = master_df.groupby("symbol")["close"].pct_change() * 100
correlation_df = master_df.groupby("symbol")[["avg_daily_news_sentiment", "price_change_pct"]].corr().unstack().iloc[:,1]
correlation_df = correlation_df.reset_index(name="correlation_sentiment_vs_price_change")
correlation_pivot = correlation_df.pivot(index="symbol", columns=None, values="correlation_sentiment_vs_price_change")

if not correlation_pivot.empty:
    plt.figure(figsize=(8, 5))
    # sns.heatmap(correlation_pivot, annot=True, cmap="coolwarm", fmt=".2f", vmin=-1, vmax=1)
    # The above pivot might not be what we want for a heatmap directly. Let's try per-symbol correlation matrix
    # For simplicity, let's just print correlations for now, as a multi-stock heatmap needs careful setup.
    print("\nCorrelations between Avg Daily News Sentiment and Next Day Price Change Pct:")
    for symbol in stock_symbols:
        # Shift sentiment to predict next day's price change
        temp_df = master_df[master_df["symbol"] == symbol].copy()
        temp_df["avg_daily_news_sentiment_lag1"] = temp_df["avg_daily_news_sentiment"].shift(1)
        corr_val = temp_df[["avg_daily_news_sentiment_lag1", "price_change_pct"]].corr().iloc[0,1]
        print(f"  {symbol}: {corr_val:.4f}")
else:
    print("Could not compute correlation pivot for heatmap.")

# Example: Scatter plot of sentiment vs price change for one stock (AAPL)
aapl_data_for_scatter = master_df[master_df["symbol"] == "AAPL"].copy()
aapl_data_for_scatter["avg_daily_news_sentiment_lag1"] = aapl_data_for_scatter["avg_daily_news_sentiment"].shift(1)
aapl_data_for_scatter.dropna(subset=["avg_daily_news_sentiment_lag1", "price_change_pct"], inplace=True)

if not aapl_data_for_scatter.empty:
    plt.figure(figsize=(10,6))
    sns.scatterplot(data=aapl_data_for_scatter, x="avg_daily_news_sentiment_lag1", y="price_change_pct")
    plt.title("AAPL: Lagged News Sentiment vs. Daily Price Change (%)")
    plt.xlabel("Previous Day's Avg News Sentiment")
    plt.ylabel("Daily Stock Price Change (%)")
    plt.axhline(0, color='grey', linestyle='--', linewidth=0.8)
    plt.axvline(0, color='grey', linestyle='--', linewidth=0.8)
    plt.tight_layout()
    plt.savefig(os.path.join(VISUALIZATIONS_DIR, "aapl_lagged_sentiment_vs_price_change_scatter.png"))
    plt.close()
    print(f"Saved aapl_lagged_sentiment_vs_price_change_scatter.png to {VISUALIZATIONS_DIR}")
else:
    print("Not enough data for AAPL scatter plot.")

print("\nDashboard visualization script finished.")

