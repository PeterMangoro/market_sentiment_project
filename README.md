# Market Sentiment Project Documentation

## Project Overview

The Market Sentiment Project is a comprehensive data analytics and visualization tool designed to analyze market sentiment from various sources and correlate it with stock price movements. The project has been completely refactored into a modular, maintainable architecture that follows modern Python best practices.

## Architecture

The refactored project follows a modular architecture with clear separation of concerns:

```
market_sentiment_project/
├── market_sentiment/               # Main package
│   ├── __init__.py                 # Package initialization
│   ├── config/                     # Configuration modules
│   │   ├── __init__.py
│   │   ├── api_config.py           # API keys and endpoints
│   │   ├── paths.py                # Path configuration
│   │   └── settings.py             # General settings
│   ├── data/                       # Data handling modules
│   │   ├── __init__.py
│   │   ├── collectors/             # Data collection modules
│   │   │   ├── __init__.py
│   │   │   ├── news_collector.py   # News data collection
│   │   │   ├── stock_collector.py  # Stock data collection
│   │   │   └── twitter_collector.py # Twitter data collection
│   │   ├── processors/             # Data processing modules
│   │   │   ├── __init__.py
│   │   │   ├── sentiment_analyzer.py # Sentiment analysis
│   │   │   └── text_preprocessor.py # Text preprocessing
│   │   └── validators/             # Data validation modules
│   │       ├── __init__.py
│   │       └── data_validator.py   # Data validation
│   ├── models/                     # Modeling modules
│   │   ├── __init__.py
│   │   ├── base_model.py           # Base model class
│   │   ├── machine_learning/       # Machine learning models
│   │   │   ├── __init__.py
│   │   │   ├── random_forest.py    # Random Forest model
│   │   │   └── xgboost_model.py    # XGBoost model
│   │   └── time_series/            # Time series models
│   │       ├── __init__.py
│   │       └── arima.py            # ARIMA model
│   ├── utils/                      # Utility modules
│   │   ├── __init__.py
│   │   ├── date_utils.py           # Date utilities
│   │   ├── file_utils.py           # File utilities
│   │   └── logging_utils.py        # Logging utilities
│   ├── visualization/              # Visualization modules
│   │   ├── __init__.py
│   │   ├── dashboard/              # Dashboard components
│   │   │   ├── __init__.py
│   │   │   └── components.py       # Dashboard creation
│   │   └── plotters/               # Plotting modules
│   │       ├── __init__.py
│   │       ├── sentiment_plots.py  # Sentiment visualization
│   │       └── stock_plots.py      # Stock price visualization
│   └── workflow/                   # Workflow orchestration
│       ├── __init__.py
│       └── orchestrator.py         # Workflow orchestration
├── scripts/                        # Command-line scripts
│   └── market_sentiment_cli.py     # CLI entry point
├── db/                             # Database modules
│   ├── __init__.py
│   ├── config.py                   # Database configuration
│   ├── schema.py                   # Database schema
│   ├── cli.py                      # Database CLI
│   ├── loaders/                    # Data loaders
│   │   ├── __init__.py
│   │   ├── stock_loader.py         # Stock data loader
│   │   ├── news_loader.py          # News data loader
│   │   └── twitter_loader.py       # Twitter data loader
│   └── utils/                      # Database utilities
│       ├── __init__.py
│       ├── logging_utils.py        # Logging utilities
│       └── path_utils.py           # Path utilities
├── data/                           # Data directory
│   ├── stock_data/                 # Stock data files
│   ├── news_data.json              # News data
│   └── twitter_data.json           # Twitter data
├── output/                         # Output directory
├── db_setup.py                     # Database setup script
└── test_refactored_project.py      # Test script
```

## Key Features

1. **Modular Design**: Clear separation of concerns with specialized modules
2. **Comprehensive Error Handling**: Robust error handling and logging throughout
3. **Flexible Configuration**: Centralized settings in dedicated config modules
4. **Command-Line Interface**: Powerful CLI with various options
5. **Workflow Orchestration**: End-to-end workflow management
6. **Visualization Components**: Advanced visualization tools and interactive dashboards
7. **Testing Framework**: Unit tests for all major components
8. **Comprehensive Documentation**: Detailed documentation for all modules

## Usage Instructions

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd market_sentiment_project
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Command-Line Interface

The project provides a comprehensive command-line interface for all major operations:

```bash
# Collect data
python scripts/market_sentiment_cli.py collect --source all --symbols AAPL,MSFT,GOOGL

# Analyze sentiment
python scripts/market_sentiment_cli.py analyze --data-type all

# Train models
python scripts/market_sentiment_cli.py train --model all --target AAPL

# Generate visualizations
python scripts/market_sentiment_cli.py visualize --type all
```

### Programmatic Usage

You can also use the project programmatically in your own scripts or notebooks:

```python
from market_sentiment.workflow import WorkflowOrchestrator

# Initialize the orchestrator
orchestrator = WorkflowOrchestrator(
    data_dir="data",
    output_dir="output",
    symbols=["AAPL", "MSFT", "GOOGL"]
)

# Run the complete workflow
results = orchestrator.run_complete_workflow()

# Or run individual steps
data_results = orchestrator.collect_data()
sentiment_results = orchestrator.analyze_sentiment()
model_results = orchestrator.train_models(target_symbol="AAPL")
visualization_results = orchestrator.generate_visualizations()
```

### Database Setup

The database module provides tools for setting up and managing the project database:

```bash
# Create database schema only
python -m db.cli --schema-only

# Load all data
python -m db.cli --load-all

# Load specific data types
python -m db.cli --load-stocks --load-news

# Specify custom paths
python -m db.cli --db-path C:\path\to\database.db --data-dir C:\path\to\data
```

## Module Documentation

### Configuration (`market_sentiment.config`)

The configuration package provides centralized settings for the project:

- `api_config.py`: API keys and endpoints
- `paths.py`: Path configuration
- `settings.py`: General settings

### Data Handling (`market_sentiment.data`)

The data package handles data collection, processing, and validation:

- **Collectors**: Modules for collecting data from various sources
  - `news_collector.py`: Collects news articles
  - `stock_collector.py`: Collects stock price data
  - `twitter_collector.py`: Collects Twitter data

- **Processors**: Modules for processing and analyzing data
  - `sentiment_analyzer.py`: Analyzes sentiment in text data
  - `text_preprocessor.py`: Preprocesses text data

- **Validators**: Modules for validating data
  - `data_validator.py`: Validates data integrity and format

### Models (`market_sentiment.models`)

The models package provides machine learning and statistical models:

- **Base Model**: Abstract base class for all models
  - `base_model.py`: Defines the model interface

- **Machine Learning**: Machine learning models
  - `random_forest.py`: Random Forest model
  - `xgboost_model.py`: XGBoost model

- **Time Series**: Time series models
  - `arima.py`: ARIMA model

### Utilities (`market_sentiment.utils`)

The utils package provides utility functions:

- `date_utils.py`: Date and time utilities
- `file_utils.py`: File operations
- `logging_utils.py`: Logging configuration

### Visualization (`market_sentiment.visualization`)

The visualization package provides tools for creating visualizations:

- **Plotters**: Modules for creating static visualizations
  - `sentiment_plots.py`: Sentiment visualization
  - `stock_plots.py`: Stock price visualization

- **Dashboard**: Modules for creating interactive dashboards
  - `components.py`: Dashboard components

### Workflow (`market_sentiment.workflow`)

The workflow package provides tools for orchestrating the complete workflow:

- `orchestrator.py`: Workflow orchestration

### Database (`db`)

The database package provides tools for database management:

- `schema.py`: Database schema definition
- `cli.py`: Command-line interface for database operations
- **Loaders**: Modules for loading data into the database
  - `stock_loader.py`: Loads stock data
  - `news_loader.py`: Loads news data
  - `twitter_loader.py`: Loads Twitter data

## Testing

The project includes a comprehensive test suite to ensure all components work correctly:

```bash
python test_refactored_project.py
```

## Extending the Project

The modular architecture makes it easy to extend the project with new functionality:

1. **Adding a new data source**: Create a new collector in `market_sentiment.data.collectors`
2. **Adding a new model**: Create a new model class in `market_sentiment.models`
3. **Adding a new visualization**: Create a new plotter in `market_sentiment.visualization.plotters`

## Troubleshooting

If you encounter any issues:

1. Check the log files for error messages
2. Ensure all dependencies are installed
3. Verify that API keys are correctly configured
4. Make sure data directories exist and are writable

## Conclusion

The refactored Market Sentiment Project provides a robust, maintainable, and extensible framework for analyzing market sentiment and its relationship with stock prices. The modular architecture makes it easy to understand, use, and extend the project for various financial analysis tasks.
