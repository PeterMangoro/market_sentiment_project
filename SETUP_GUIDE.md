# Market Sentiment Project Setup Guide

This guide provides detailed instructions for setting up and running the Market Sentiment Project on your local machine.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Database Setup](#database-setup)
5. [Running the Project](#running-the-project)
6. [Using the Dimensional Models](#using-the-dimensional-models)
7. [Jupyter Notebooks](#jupyter-notebooks)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- pip (Python package installer)
- Git (optional, for version control)

## Installation

1. **Extract the Project**
   Extract the `market_sentiment_project_refactored.zip` file to a location of your choice.

2. **Create a Virtual Environment**
   It's recommended to use a virtual environment to avoid conflicts with other Python projects:

   **Windows:**
   ```
   cd path\to\market_sentiment_project
   python -m venv venv
   venv\Scripts\activate
   ```

   **macOS/Linux:**
   ```
   cd path/to/market_sentiment_project
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   Install all required packages using pip:
   ```
   pip install -r requirements.txt
   ```

## Configuration

### API Keys Setup

1. Open the file `market_sentiment/config/api_config.py`
2. Replace the placeholder values with your actual API keys:

   ```python
   # Alpha Vantage API (Stock Data)
   ALPHA_VANTAGE_API_KEY = "YOUR_ALPHA_VANTAGE_API_KEY"
   
   # Marketaux API (News Data)
   MARKETAUX_API_KEY = "YOUR_MARKETAUX_API_KEY"
   
   # Twitter API (Twitter Data)
   TWITTER_API_KEY = "YOUR_TWITTER_API_KEY"
   TWITTER_API_SECRET = "YOUR_TWITTER_API_SECRET"
   TWITTER_ACCESS_TOKEN = "YOUR_TWITTER_ACCESS_TOKEN"
   TWITTER_ACCESS_SECRET = "YOUR_TWITTER_ACCESS_SECRET"
   TWITTER_BEARER_TOKEN = "YOUR_TWITTER_BEARER_TOKEN"
   ```

3. You can obtain these API keys from:
   - Alpha Vantage: https://www.alphavantage.co/support/#api-key
   - Marketaux: https://www.marketaux.com/
   - Twitter: https://developer.twitter.com/en/portal/dashboard

### Project Configuration

The project's general settings can be modified in `market_sentiment/config/settings.py` if needed.

## Database Setup

1. **Initialize the Database**
   Run the database setup script:
   ```
   python db_setup.py
   ```

   This will create the SQLite database with the necessary tables.

2. **Verify Database Creation**
   After running the setup script, you should see a `market_sentiment.db` file in your project directory.

## Running the Project

### Command-Line Interface

The project includes a comprehensive CLI for all major operations:

1. **Collect Data**
   ```
   python scripts/market_sentiment_cli.py collect --source all --symbols AAPL,MSFT,GOOGL
   ```
   
   Options:
   - `--source`: Data source to collect from (`stock`, `news`, `twitter`, or `all`)
   - `--symbols`: Comma-separated list of stock symbols

2. **Analyze Sentiment**
   ```
   python scripts/market_sentiment_cli.py analyze --data-type all
   ```
   
   Options:
   - `--data-type`: Type of data to analyze (`news`, `twitter`, or `all`)

3. **Train Models**
   ```
   python scripts/market_sentiment_cli.py train --model all --target AAPL
   ```
   
   Options:
   - `--model`: Model to train (`random_forest`, `xgboost`, `arima`, or `all`)
   - `--target`: Target stock symbol for prediction

4. **Generate Visualizations**
   ```
   python scripts/market_sentiment_cli.py visualize --type all
   ```
   
   Options:
   - `--type`: Type of visualization to generate (`price`, `sentiment`, `correlation`, or `all`)

### Workflow Orchestration

For end-to-end processing, you can use the workflow orchestrator:

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

## Using the Dimensional Models

The project includes two dimensional models for market sentiment analysis: Star Schema and Snowflake Schema.

1. **Run the Test Script**
   ```
   python test_dimensional_models.py
   ```
   
   This will create both Star Schema and Snowflake Schema databases, load sample data, and run comparison tests.

2. **Using the Star Schema Model**
   ```python
   from market_sentiment.dimensional_models import StarSchemaModel
   
   # Initialize the model
   star_model = StarSchemaModel("market_sentiment_star.db")
   
   # Load sample data
   star_model.load_sample_data("data")
   
   # Run queries
   sentiment_impact = star_model.query_sentiment_impact("AAPL")
   sentiment_by_category = star_model.query_sentiment_by_category()
   time_series = star_model.query_time_series_analysis("AAPL")
   
   # Close connection
   star_model.close()
   ```

3. **Using the Snowflake Schema Model**
   ```python
   from market_sentiment.dimensional_models import SnowflakeSchemaModel
   
   # Initialize the model
   snowflake_model = SnowflakeSchemaModel("market_sentiment_snowflake.db")
   
   # Load sample data
   snowflake_model.load_sample_data("data")
   
   # Run queries
   sentiment_impact = snowflake_model.query_sentiment_impact("AAPL")
   sentiment_by_category = snowflake_model.query_sentiment_by_category()
   time_series = snowflake_model.query_time_series_analysis("AAPL")
   
   # Close connection
   snowflake_model.close()
   ```

## Jupyter Notebooks

The project includes Jupyter notebooks for interactive analysis:

1. **Start Jupyter**
   ```
   jupyter notebook
   ```
   or
   ```
   jupyter lab
   ```

2. **Open the Notebooks**
   Navigate to the `notebooks` directory and open any of the notebooks:
   - `01_Data_Exploration.ipynb`: Explore the collected data
   - `02_Sentiment_Analysis_Visualization.ipynb`: Visualize sentiment analysis results
   - `03_Model_Comparison.ipynb`: Compare different prediction models
   - `04_Interactive_Dashboard.ipynb`: Create interactive dashboards

## Troubleshooting

### Common Issues

1. **Missing Dependencies**
   If you encounter errors about missing packages, install them individually:
   ```
   pip install package_name
   ```

2. **API Key Issues**
   - Verify that your API keys are correctly entered in `api_config.py`
   - Check that your API keys have not expired
   - Ensure you have sufficient quota for the API calls

3. **Database Errors**
   - If you encounter database errors, try deleting the existing database file and running `db_setup.py` again
   - Ensure SQLite is working properly on your system

4. **Data Collection Issues**
   - Check your internet connection
   - Verify that the API services are available
   - Ensure your API keys have the necessary permissions

### Getting Help

If you encounter issues not covered in this guide, refer to:
- The project documentation in the `README.md` file
- The detailed module documentation in the code comments
- The comparison document for dimensional models in `dimensional_models_comparison.md`

## Next Steps

After setting up the project, you might want to:
1. Collect data for additional stock symbols
2. Experiment with different sentiment analysis techniques
3. Develop custom visualization dashboards
4. Extend the models with your own features
5. Integrate with other data sources or APIs
