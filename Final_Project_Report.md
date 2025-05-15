# Market Sentiment Analysis for Financial Assets - Final Report

## 1. Introduction

This project aimed to investigate the potential relationship between public sentiment, derived from financial news articles and social media (conceptually, Twitter), and the stock price movements of major technology companies: Apple (AAPL), Microsoft (MSFT), and Google (GOOGL). The primary goal was to develop a data-driven approach to collect, analyze, and visualize sentiment data alongside historical stock performance, and to explore predictive modeling techniques. This project serves as a comprehensive demonstration of a data analytics workflow, from data acquisition to insight generation and model building, suitable for a professional portfolio.

## 2. Methodology

The project followed a structured methodology encompassing data collection, preprocessing, sentiment analysis, database storage, exploratory data analysis (EDA), and advanced modeling.

### 2.1. Data Sources

*   **Financial News:** News articles were sourced using the Marketaux API. This API provides access to a wide range of financial news publications.
*   **Historical Stock Prices:** Daily open, high, low, close (OHLC) prices, and volume data for AAPL, MSFT, and GOOGL were sourced using the YahooFinance API (via an internal sandbox tool, conceptually similar to using the `yfinance` library).
*   **Social Media (Conceptual):** Twitter data was conceptually included, with sample data processed. In a full local implementation, this would involve using the Twitter API (e.g., via Tweepy) to collect tweets related to the target stocks.

### 2.2. Data Collection

Python scripts were developed to interact with the respective APIs:
*   `fetch_marketaux_news.py`: Fetched news articles for AAPL, MSFT, and GOOGL using the Marketaux API key. Data was stored in `marketaux_news_data.json`.
*   `fetch_stock_data.py`: Fetched historical daily stock data for the specified symbols. Data for each stock was stored in separate JSON files (e.g., `AAPL_stock_data.json`).
*   `fetch_twitter_data.py`: (Conceptual for full local execution) A script was designed to fetch tweets using keywords related to the stocks. Sample Twitter data was used for processing in the sandbox, stored in `twitter_data.json`.

### 2.3. Data Preprocessing

Raw data from APIs required preprocessing:
*   **News Data:** Extracted relevant fields such as headline, summary, publication date, and associated entities (stock symbols).
*   **Stock Data:** Timestamps were converted to dates, and the data was structured into pandas DataFrames for easy manipulation.
*   **Twitter Data:** Tweet text, creation date, and user information were extracted.

### 2.4. Sentiment Analysis

Sentiment analysis was performed on the textual data (news headlines/summaries and tweet text) to quantify public opinion.
*   **Tool:** The NLTK library in Python, specifically the VADER (Valence Aware Dictionary and sEntiment Reasoner) sentiment intensity analyzer, was used. VADER is well-suited for social media text but also performs reasonably on news headlines.
*   **Process (`perform_sentiment_analysis.py`):**
    1.  The VADER lexicon was downloaded.
    2.  A function was created to calculate sentiment scores (positive, negative, neutral, and a compound score ranging from -1 to +1) for each piece of text.
    3.  This function was applied to the collected news articles and Twitter data.
    4.  The original data, augmented with sentiment scores, was saved to new JSON files (`news_with_sentiment.json`, `twitter_with_sentiment.json`).

### 2.5. Database Design and Population

A SQLite database (`market_sentiment.db`) was designed to store and manage the collected and processed data in a structured manner.
*   **Schema (`create_db.py`):**
    *   `news`: Stored news articles and their sentiment scores.
    *   `tweets`: Stored tweets and their sentiment scores.
    *   `stocks`: Stored historical daily stock prices.
    *   `stock_news` & `stock_tweets`: Linking tables to manage many-to-many relationships between stocks and news/tweets (though not fully populated in the automated sandbox flow, the schema was designed for this).
*   **Population:** While the schema was created, the full population of these tables from the JSON files would be the next step in a continued local workflow, typically involving Python scripts to parse the JSON and insert data into the SQL tables.

## 3. Exploratory Data Analysis (EDA)

EDA was performed to uncover initial patterns, trends, and relationships in the data. The `generate_dashboard_visualizations.py` script was used to create plots and a consolidated CSV for Tableau.

*   **Key Visualizations and Findings:**
    *   **Stock Prices Over Time:** Line charts showed the historical price trends for AAPL, MSFT, and GOOGL.
    *   **News Sentiment Over Time:** Line charts displayed the average daily compound sentiment scores derived from news articles for each stock, revealing periods of predominantly positive or negative news flow.
    *   **Sentiment Distribution:** Box plots illustrated the distribution of news sentiment scores for each stock, highlighting differences in overall sentiment profiles.
    *   **Sentiment vs. Price Change (Scatter Plot):** For AAPL, a scatter plot explored the relationship between lagged news sentiment and daily stock price percentage changes, providing a visual cue for potential correlations.
    *   **Data for Tableau:** A `master_sentiment_stock_data.csv` file was generated, merging daily stock prices with aggregated daily news sentiment, suitable for deeper exploration in Tableau.

## 4. Advanced Modeling

The `advanced_modeling.py` script was developed to explore predictive modeling.

### 4.1. Random Forest Regressor

*   **Objective:** To predict the next day’s closing price for AAPL using features like the current day’s close price, volume, current news sentiment, and lagged news sentiment.
*   **Process:**
    1.  Data for AAPL (stock prices and news sentiment) was merged and features were engineered (e.g., `target_close_next_day`, `sentiment_lag1`).
    2.  The data was split into training and testing sets (chronologically, without shuffling).
    3.  A Random Forest Regressor model was trained.
*   **Results:** The model yielded a Mean Squared Error (MSE) for AAPL price prediction. A plot comparing actual vs. predicted prices was generated (`aapl_rf_prediction.png`). The MSE indicated the average squared difference between the actual and predicted values, providing a measure of prediction accuracy.

### 4.2. Vector Autoregression (VAR) Model

*   **Objective:** To model the interdependencies between multiple time series, specifically AAPL’s closing price and its news sentiment.
*   **Process:** A VAR model was attempted using the `statsmodels` library.
*   **Results:** The VAR model encountered an error during fitting (`2-th leading minor of the array is not positive definite`). This typically indicates issues with the data, such as multicollinearity or non-stationarity. VAR models require careful data preparation, including tests for stationarity (e.g., Augmented Dickey-Fuller test) and differencing or other transformations if series are non-stationary. This was noted as an area for further work.

## 5. Key Findings & Insights (Summary)

*   **Sentiment Fluctuation:** News sentiment for the selected tech stocks showed noticeable fluctuations over time, often correlating with major company announcements or market events (though specific event correlation was not part of this automated analysis).
*   **Visual Correlation:** EDA plots visually suggested periods where heightened sentiment (either positive or negative) appeared to coincide with or precede stock price movements, although this requires more rigorous statistical testing (like Granger causality tests).
*   **Predictive Potential (Random Forest):** The Random Forest model demonstrated some capability in predicting next-day closing prices, although the MSE suggests room for improvement and further feature engineering.
*   **Modeling Challenges (VAR):** The attempt to use a VAR model highlighted the importance of rigorous time series diagnostics (like stationarity checks) before applying such models.

## 6. Limitations

*   **Twitter Data:** Full Twitter data collection and integration were conceptual for the sandbox and would require local setup of Twitter API access.
*   **Sentiment Analysis Nuance:** VADER is a general-purpose sentiment analyzer. Domain-specific financial sentiment lexicons or more advanced NLP models (e.g., fine-tuned transformers like FinBERT) could provide more nuanced sentiment scores.
*   **Causality vs. Correlation:** The analysis primarily explored correlations. Establishing causal links between sentiment and price movements is more complex and would require advanced econometric techniques.
*   **Data Volume and Granularity:** The Marketaux API free tier has limits on data volume. Access to more granular (e.g., intraday) data and a larger historical dataset could yield different insights.
*   **Model Complexity and Tuning:** The predictive models were implemented with basic configurations. Extensive hyperparameter tuning and feature engineering could improve their performance.
*   **External Factors:** Stock prices are influenced by a multitude of factors beyond news sentiment (e.g., macroeconomic indicators, broader market trends, company fundamentals). This project focused primarily on sentiment.

## 7. Conclusion & Potential Future Work

This project successfully demonstrated an end-to-end workflow for analyzing the relationship between market sentiment and stock prices. It highlighted the feasibility of collecting and processing diverse data types and applying NLP and machine learning techniques to derive insights.

**Potential Future Work:**

*   **Full Twitter Integration:** Implement robust Twitter data collection and analysis using the official API.
*   **Advanced Sentiment Analysis:** Explore domain-specific sentiment lexicons or transformer-based models (e.g., FinBERT).
*   **Granular Data:** Analyze intraday stock prices and real-time news/tweet sentiment if accessible.
*   **Richer Feature Engineering:** Incorporate features like sentiment volatility, volume of news/tweets, and interaction terms.
*   **Advanced Time Series Models:** Properly implement and evaluate VAR, VECM, or GARCH models after thorough data diagnostics.
*   **Granger Causality Tests:** Statistically test for causal relationships between sentiment and price movements.
*   **Comprehensive Backtesting:** For any trading strategies derived from predictive models, perform rigorous backtesting.
*   **Interactive Dashboard:** Develop a fully interactive dashboard in Tableau or using Python libraries like Dash/Streamlit to allow dynamic exploration of the data and model results.

This project provides a solid foundation and a valuable learning experience in the domain of financial data analytics and sentiment analysis.

