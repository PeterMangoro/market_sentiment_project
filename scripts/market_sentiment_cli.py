#!/usr/bin/env python3
"""
Main entry point for the Market Sentiment Project.

This script provides a command-line interface for the Market Sentiment Project,
allowing users to collect data, analyze sentiment, train models, and generate visualizations.
"""

import argparse
import logging
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from market_sentiment.config.settings import DEFAULT_SYMBOLS
from market_sentiment.utils.logging_utils import setup_logging
from market_sentiment.utils.file_utils import ensure_dir_exists

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Market Sentiment Analysis Tool",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Common arguments
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level"
    )
    parser.add_argument(
        "--log-file",
        type=str,
        help="Path to log file. If not specified, logs are only written to console."
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default=str(Path(__file__).parent / "data"),
        help="Directory for storing data files"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(Path(__file__).parent / "output"),
        help="Directory for storing output files"
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Collect command
    collect_parser = subparsers.add_parser("collect", help="Collect data")
    collect_parser.add_argument(
        "--source",
        choices=["news", "stock", "twitter", "all"],
        default="all",
        help="Data source to collect from"
    )
    collect_parser.add_argument(
        "--symbols",
        type=str,
        default=",".join(DEFAULT_SYMBOLS),
        help="Comma-separated list of stock symbols"
    )
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze sentiment")
    analyze_parser.add_argument(
        "--data-type",
        choices=["news", "twitter", "all"],
        default="all",
        help="Type of data to analyze"
    )
    
    # Train command
    train_parser = subparsers.add_parser("train", help="Train models")
    train_parser.add_argument(
        "--model",
        choices=["random-forest", "xgboost", "arima", "all"],
        default="all",
        help="Model to train"
    )
    train_parser.add_argument(
        "--target",
        type=str,
        default=DEFAULT_SYMBOLS[0],
        help="Target stock symbol for prediction"
    )
    
    # Visualize command
    visualize_parser = subparsers.add_parser("visualize", help="Generate visualizations")
    visualize_parser.add_argument(
        "--type",
        choices=["price", "sentiment", "comparison", "dashboard", "all"],
        default="all",
        help="Type of visualization to generate"
    )
    visualize_parser.add_argument(
        "--output",
        type=str,
        help="Output file path for visualization"
    )
    
    return parser.parse_args()

def main():
    """Main entry point."""
    args = parse_args()
    
    # Set up logging
    log_level = getattr(logging, args.log_level)
    setup_logging(
        log_file=args.log_file,
        log_level=log_level
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Starting Market Sentiment Project with command: {args.command}")
    
    # Ensure directories exist
    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)
    ensure_dir_exists(data_dir)
    ensure_dir_exists(output_dir)
    
    # Parse symbols
    symbols = args.symbols.split(",") if hasattr(args, "symbols") else DEFAULT_SYMBOLS
    
    # Execute command
    if args.command == "collect":
        from market_sentiment.data.collectors import NewsCollector, StockCollector, TwitterCollector
        
        if args.source in ["news", "all"]:
            logger.info(f"Collecting news data for symbols: {symbols}")
            news_collector = NewsCollector(symbols=symbols)
            news_data = news_collector.collect(output_file=data_dir / "news_data.json")
            logger.info("News data collection complete")
        
        if args.source in ["stock", "all"]:
            logger.info(f"Collecting stock data for symbols: {symbols}")
            stock_collector = StockCollector(symbols=symbols)
            stock_data = stock_collector.collect(output_dir=data_dir / "stock_data")
            logger.info("Stock data collection complete")
        
        if args.source in ["twitter", "all"]:
            logger.info(f"Collecting Twitter data for symbols: {symbols}")
            twitter_collector = TwitterCollector(symbols=symbols)
            twitter_data = twitter_collector.collect(output_file=data_dir / "twitter_data.json")
            logger.info("Twitter data collection complete")
    
    elif args.command == "analyze":
        from market_sentiment.data.processors import SentimentAnalyzer
        from market_sentiment.utils.file_utils import load_json, save_json
        
        analyzer = SentimentAnalyzer()
        
        if args.data_type in ["news", "all"]:
            logger.info("Analyzing news sentiment")
            try:
                news_data = load_json(data_dir / "news_data.json")
                news_with_sentiment = analyzer.analyze_news_articles(news_data)
                save_json(news_with_sentiment, data_dir / "news_with_sentiment.json")
                logger.info("News sentiment analysis complete")
            except Exception as e:
                logger.error(f"Error analyzing news sentiment: {e}")
        
        if args.data_type in ["twitter", "all"]:
            logger.info("Analyzing Twitter sentiment")
            try:
                twitter_data = load_json(data_dir / "twitter_data.json")
                twitter_with_sentiment = analyzer.analyze_tweets(twitter_data)
                save_json(twitter_with_sentiment, data_dir / "twitter_with_sentiment.json")
                logger.info("Twitter sentiment analysis complete")
            except Exception as e:
                logger.error(f"Error analyzing Twitter sentiment: {e}")
    
    elif args.command == "train":
        import pandas as pd
        from market_sentiment.utils.file_utils import load_json
        from market_sentiment.models.machine_learning import RandomForestModel, XGBoostModel
        from market_sentiment.models.time_series import ARIMAModel
        
        target = args.target
        logger.info(f"Training models for target symbol: {target}")
        
        # Load data
        try:
            # Load stock data
            stock_file = data_dir / "stock_data" / f"{target}_stock_data.json"
            stock_data = load_json(stock_file)
            
            # Extract and prepare stock DataFrame
            if stock_data and stock_data.get("chart") and stock_data["chart"].get("result"):
                df = pd.DataFrame({
                    "timestamp": stock_data["chart"]["result"][0]["timestamp"],
                    "close": stock_data["chart"]["result"][0]["indicators"]["quote"][0]["close"],
                    "volume": stock_data["chart"]["result"][0]["indicators"]["quote"][0]["volume"]
                })
                df["date"] = pd.to_datetime(df["timestamp"], unit="s").dt.date
                df = df.dropna(subset=["close"])
                df = df.set_index("date")
                
                # Load sentiment data
                news_sentiment = load_json(data_dir / "news_with_sentiment.json")
                
                # Process and merge sentiment data
                # This is a simplified example - in a real implementation, you would
                # need to match sentiment data to stock data by date and symbol
                
                # Train models
                if args.model in ["random-forest", "all"]:
                    logger.info("Training Random Forest model")
                    rf_model = RandomForestModel()
                    # In a real implementation, you would prepare features and target
                    # and train the model properly
                    
                if args.model in ["xgboost", "all"]:
                    logger.info("Training XGBoost model")
                    xgb_model = XGBoostModel()
                    # In a real implementation, you would prepare features and target
                    # and train the model properly
                
                if args.model in ["arima", "all"]:
                    logger.info("Training ARIMA model")
                    arima_model = ARIMAModel()
                    # In a real implementation, you would prepare the time series
                    # and train the model properly
                
                logger.info("Model training complete")
            else:
                logger.error(f"Invalid or empty stock data for symbol: {target}")
        
        except Exception as e:
            logger.error(f"Error training models: {e}")
    
    elif args.command == "visualize":
        import pandas as pd
        from market_sentiment.utils.file_utils import load_json
        from market_sentiment.visualization.plotters import SentimentPlotter, StockPlotter
        from market_sentiment.visualization.dashboard import create_dashboard
        
        try:
            # Load stock data
            stock_data = {}
            for symbol in symbols:
                stock_file = data_dir / "stock_data" / f"{symbol}_stock_data.json"
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
            news_sentiment_file = data_dir / "news_with_sentiment.json"
            twitter_sentiment_file = data_dir / "twitter_with_sentiment.json"
            
            news_sentiment_data = pd.DataFrame()
            twitter_sentiment_data = pd.DataFrame()
            
            if news_sentiment_file.exists():
                news_sentiment = load_json(news_sentiment_file)
                # In a real implementation, you would process this into a proper DataFrame
                
            if twitter_sentiment_file.exists():
                twitter_sentiment = load_json(twitter_sentiment_file)
                # In a real implementation, you would process this into a proper DataFrame
            
            # Generate visualizations
            if args.type in ["price", "all"] and stock_data:
                logger.info("Generating price visualizations")
                stock_plotter = StockPlotter()
                for symbol, df in stock_data.items():
                    output_file = output_dir / f"{symbol}_price_history.png"
                    stock_plotter.plot_price_history(
                        df,
                        date_column="date",
                        price_column="close",
                        volume_column="volume",
                        symbol=symbol,
                        output_path=output_file,
                        show=False
                    )
            
            if args.type in ["sentiment", "all"] and not news_sentiment_data.empty:
                logger.info("Generating sentiment visualizations")
                sentiment_plotter = SentimentPlotter()
                output_file = output_dir / "sentiment_over_time.png"
                sentiment_plotter.plot_sentiment_over_time(
                    news_sentiment_data,
                    output_path=output_file,
                    show=False
                )
            
            if args.type in ["comparison", "all"] and len(stock_data) > 1:
                logger.info("Generating comparison visualization")
                stock_plotter = StockPlotter()
                output_file = output_dir / "stock_comparison.png"
                stock_plotter.plot_comparison(
                    stock_data,
                    output_path=output_file,
                    show=False
                )
            
            if args.type in ["dashboard", "all"]:
                logger.info("Generating interactive dashboard")
                output_file = args.output or output_dir / "market_sentiment_dashboard.html"
                dashboard_path = create_dashboard(
                    stock_data,
                    news_sentiment_data,
                    twitter_sentiment_data,
                    output_path=output_file
                )
                logger.info(f"Dashboard created at: {dashboard_path}")
            
            logger.info("Visualization generation complete")
        
        except Exception as e:
            logger.error(f"Error generating visualizations: {e}")
    
    else:
        logger.error(f"Unknown command: {args.command}")
        return 1
    
    logger.info("Market Sentiment Project execution complete")
    return 0

if __name__ == "__main__":
    sys.exit(main())
