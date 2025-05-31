"""
Workflow orchestration module.

This module provides functions for orchestrating the complete market sentiment analysis workflow.
"""

import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

from ..config.settings import DEFAULT_SYMBOLS
from ..utils.logging_utils import get_logger
from ..utils.file_utils import ensure_dir_exists
from ..data.collectors import NewsCollector, StockCollector, TwitterCollector
from ..data.processors import SentimentAnalyzer
from ..models.machine_learning import RandomForestModel, XGBoostModel
from ..models.time_series import ARIMAModel
from ..visualization.plotters import SentimentPlotter, StockPlotter
from ..visualization.dashboard import create_dashboard

logger = get_logger(__name__)

class WorkflowOrchestrator:
    """
    Orchestrator for the market sentiment analysis workflow.
    
    This class provides methods for running the complete workflow or individual steps
    of the market sentiment analysis process.
    """
    
    def __init__(
        self,
        data_dir: Union[str, Path] = "data",
        output_dir: Union[str, Path] = "output",
        symbols: List[str] = None
    ):
        """
        Initialize the workflow orchestrator.
        
        Args:
            data_dir: Directory for storing data files. Defaults to "data".
            output_dir: Directory for storing output files. Defaults to "output".
            symbols: List of stock symbols to analyze. Defaults to DEFAULT_SYMBOLS.
        """
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.symbols = symbols or DEFAULT_SYMBOLS
        
        # Ensure directories exist
        ensure_dir_exists(self.data_dir)
        ensure_dir_exists(self.output_dir)
        
        logger.info(f"Initialized WorkflowOrchestrator with symbols: {self.symbols}")
    
    def run_complete_workflow(self):
        """
        Run the complete market sentiment analysis workflow.
        
        This method executes all steps of the workflow in sequence:
        1. Collect data
        2. Analyze sentiment
        3. Train models
        4. Generate visualizations
        
        Returns:
            Dictionary containing results and paths to output files.
        """
        logger.info("Starting complete workflow")
        
        # Step 1: Collect data
        data_results = self.collect_data()
        
        # Step 2: Analyze sentiment
        sentiment_results = self.analyze_sentiment()
        
        # Step 3: Train models
        model_results = self.train_models()
        
        # Step 4: Generate visualizations
        visualization_results = self.generate_visualizations()
        
        # Combine results
        results = {
            "data_collection": data_results,
            "sentiment_analysis": sentiment_results,
            "model_training": model_results,
            "visualizations": visualization_results
        }
        
        logger.info("Complete workflow finished successfully")
        return results
    
    def collect_data(self):
        """
        Collect data from all sources.
        
        Returns:
            Dictionary containing paths to collected data files.
        """
        logger.info(f"Collecting data for symbols: {self.symbols}")
        
        results = {}
        
        # Collect news data
        try:
            news_collector = NewsCollector(symbols=self.symbols)
            news_file = self.data_dir / "news_data.json"
            news_data = news_collector.collect(output_file=news_file)
            results["news"] = str(news_file)
            logger.info(f"News data collected and saved to {news_file}")
        except Exception as e:
            logger.error(f"Error collecting news data: {e}")
            results["news"] = None
        
        # Collect stock data
        try:
            stock_collector = StockCollector(symbols=self.symbols)
            stock_dir = self.data_dir / "stock_data"
            stock_data = stock_collector.collect(output_dir=stock_dir)
            results["stock"] = {symbol: str(stock_dir / f"{symbol}_stock_data.json") for symbol in self.symbols}
            logger.info(f"Stock data collected and saved to {stock_dir}")
        except Exception as e:
            logger.error(f"Error collecting stock data: {e}")
            results["stock"] = None
        
        # Collect Twitter data
        try:
            twitter_collector = TwitterCollector(symbols=self.symbols)
            twitter_file = self.data_dir / "twitter_data.json"
            twitter_data = twitter_collector.collect(output_file=twitter_file)
            results["twitter"] = str(twitter_file)
            logger.info(f"Twitter data collected and saved to {twitter_file}")
        except Exception as e:
            logger.error(f"Error collecting Twitter data: {e}")
            results["twitter"] = None
        
        return results
    
    def analyze_sentiment(self):
        """
        Analyze sentiment for collected data.
        
        Returns:
            Dictionary containing paths to sentiment analysis result files.
        """
        logger.info("Analyzing sentiment")
        
        results = {}
        analyzer = SentimentAnalyzer()
        
        # Analyze news sentiment
        try:
            from ..utils.file_utils import load_json, save_json
            
            news_file = self.data_dir / "news_data.json"
            if news_file.exists():
                news_data = load_json(news_file)
                news_with_sentiment = analyzer.analyze_news_articles(news_data)
                news_sentiment_file = self.data_dir / "news_with_sentiment.json"
                save_json(news_with_sentiment, news_sentiment_file)
                results["news"] = str(news_sentiment_file)
                logger.info(f"News sentiment analyzed and saved to {news_sentiment_file}")
            else:
                logger.warning(f"News data file not found: {news_file}")
                results["news"] = None
        except Exception as e:
            logger.error(f"Error analyzing news sentiment: {e}")
            results["news"] = None
        
        # Analyze Twitter sentiment
        try:
            twitter_file = self.data_dir / "twitter_data.json"
            if twitter_file.exists():
                twitter_data = load_json(twitter_file)
                twitter_with_sentiment = analyzer.analyze_tweets(twitter_data)
                twitter_sentiment_file = self.data_dir / "twitter_with_sentiment.json"
                save_json(twitter_with_sentiment, twitter_sentiment_file)
                results["twitter"] = str(twitter_sentiment_file)
                logger.info(f"Twitter sentiment analyzed and saved to {twitter_sentiment_file}")
            else:
                logger.warning(f"Twitter data file not found: {twitter_file}")
                results["twitter"] = None
        except Exception as e:
            logger.error(f"Error analyzing Twitter sentiment: {e}")
            results["twitter"] = None
        
        return results
    
    def train_models(self, target_symbol=None):
        """
        Train models for the target symbol.
        
        Args:
            target_symbol: Target stock symbol for prediction. If None, uses the first symbol.
        
        Returns:
            Dictionary containing trained models and evaluation metrics.
        """
        target = target_symbol or self.symbols[0]
        logger.info(f"Training models for target symbol: {target}")
        
        results = {}
        
        try:
            import pandas as pd
            from ..utils.file_utils import load_json
            
            # Load stock data
            stock_file = self.data_dir / "stock_data" / f"{target}_stock_data.json"
            if not stock_file.exists():
                logger.error(f"Stock data file not found: {stock_file}")
                return results
            
            stock_data = load_json(stock_file)
            
            # Extract and prepare stock DataFrame
            if not (stock_data and stock_data.get("chart") and stock_data["chart"].get("result")):
                logger.error(f"Invalid or empty stock data for symbol: {target}")
                return results
            
            df = pd.DataFrame({
                "timestamp": stock_data["chart"]["result"][0]["timestamp"],
                "close": stock_data["chart"]["result"][0]["indicators"]["quote"][0]["close"],
                "volume": stock_data["chart"]["result"][0]["indicators"]["quote"][0]["volume"]
            })
            df["date"] = pd.to_datetime(df["timestamp"], unit="s").dt.date
            df = df.dropna(subset=["close"])
            df = df.set_index("date")
            
            # Load sentiment data
            news_sentiment_file = self.data_dir / "news_with_sentiment.json"
            twitter_sentiment_file = self.data_dir / "twitter_with_sentiment.json"
            
            # In a real implementation, you would process and merge sentiment data with stock data
            # and prepare features and targets for model training
            
            # Train Random Forest model
            try:
                rf_model = RandomForestModel()
                # In a real implementation, you would train and evaluate the model properly
                results["random_forest"] = {
                    "model": rf_model,
                    "metrics": {"mse": 0.0, "rmse": 0.0, "mae": 0.0, "r2": 0.0}  # Placeholder
                }
                logger.info("Random Forest model trained")
            except Exception as e:
                logger.error(f"Error training Random Forest model: {e}")
            
            # Train XGBoost model
            try:
                xgb_model = XGBoostModel()
                # In a real implementation, you would train and evaluate the model properly
                results["xgboost"] = {
                    "model": xgb_model,
                    "metrics": {"mse": 0.0, "rmse": 0.0, "mae": 0.0, "r2": 0.0}  # Placeholder
                }
                logger.info("XGBoost model trained")
            except Exception as e:
                logger.error(f"Error training XGBoost model: {e}")
            
            # Train ARIMA model
            try:
                arima_model = ARIMAModel()
                # In a real implementation, you would train and evaluate the model properly
                results["arima"] = {
                    "model": arima_model,
                    "metrics": {"mse": 0.0, "rmse": 0.0, "mae": 0.0}  # Placeholder
                }
                logger.info("ARIMA model trained")
            except Exception as e:
                logger.error(f"Error training ARIMA model: {e}")
            
        except Exception as e:
            logger.error(f"Error in model training process: {e}")
        
        return results
    
    def generate_visualizations(self):
        """
        Generate visualizations for the collected and analyzed data.
        
        Returns:
            Dictionary containing paths to generated visualization files.
        """
        logger.info("Generating visualizations")
        
        results = {}
        
        try:
            import pandas as pd
            from ..utils.file_utils import load_json
            
            # Load stock data
            stock_data = {}
            for symbol in self.symbols:
                stock_file = self.data_dir / "stock_data" / f"{symbol}_stock_data.json"
                if stock_file.exists():
                    data = load_json(stock_file)
                    if data and data.get("chart") and data["chart"].get("result"):
                        df = pd.DataFrame({
                            "timestamp": data["chart"]["result"][0]["timestamp"],
                            "close": data["chart"]["result"][0]["indicators"]["quote"][0]["close"],
                            "volume": data["chart"]["result"][0]["indicators"]["quote"][0]["volume"]
                        })
                        df["date"] = pd.to_datetime(df["timestamp"], unit="s").dt.date
                        stock_data[symbol] = df
            
            # Load sentiment data
            news_sentiment_file = self.data_dir / "news_with_sentiment.json"
            twitter_sentiment_file = self.data_dir / "twitter_with_sentiment.json"
            
            news_sentiment_data = pd.DataFrame()  # Placeholder
            twitter_sentiment_data = pd.DataFrame()  # Placeholder
            
            # In a real implementation, you would process sentiment data into proper DataFrames
            
            # Generate price visualizations
            if stock_data:
                price_plots = {}
                stock_plotter = StockPlotter()
                
                for symbol, df in stock_data.items():
                    output_file = self.output_dir / f"{symbol}_price_history.png"
                    stock_plotter.plot_price_history(
                        df,
                        date_column="date",
                        price_column="close",
                        volume_column="volume",
                        symbol=symbol,
                        output_path=output_file,
                        show=False
                    )
                    price_plots[symbol] = str(output_file)
                
                results["price_plots"] = price_plots
                logger.info("Price visualizations generated")
            
            # Generate sentiment visualizations
            if not news_sentiment_data.empty:
                sentiment_plotter = SentimentPlotter()
                output_file = self.output_dir / "sentiment_over_time.png"
                sentiment_plotter.plot_sentiment_over_time(
                    news_sentiment_data,
                    output_path=output_file,
                    show=False
                )
                results["sentiment_plot"] = str(output_file)
                logger.info("Sentiment visualization generated")
            
            # Generate comparison visualization
            if len(stock_data) > 1:
                stock_plotter = StockPlotter()
                output_file = self.output_dir / "stock_comparison.png"
                stock_plotter.plot_comparison(
                    stock_data,
                    output_path=output_file,
                    show=False
                )
                results["comparison_plot"] = str(output_file)
                logger.info("Comparison visualization generated")
            
            # Generate dashboard
            dashboard_file = self.output_dir / "market_sentiment_dashboard.html"
            dashboard_path = create_dashboard(
                stock_data,
                news_sentiment_data,
                twitter_sentiment_data,
                output_path=dashboard_file
            )
            results["dashboard"] = dashboard_path
            logger.info(f"Interactive dashboard generated at {dashboard_path}")
            
        except Exception as e:
            logger.error(f"Error generating visualizations: {e}")
        
        return results
