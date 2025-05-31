# Market Sentiment Project Database Module Documentation

## Overview

This document provides a comprehensive guide to the modularized database setup and data loading system for the Market Sentiment Project. The system has been refactored into a clean, maintainable, and extensible structure that follows modern Python best practices.

## Directory Structure

```
market_sentiment_project/
├── db/                           # Main database package
│   ├── __init__.py               # Package initialization
│   ├── config.py                 # Configuration settings
│   ├── schema.py                 # Database schema definition
│   ├── cli.py                    # Command-line interface
│   ├── loaders/                  # Data loader modules
│   │   ├── __init__.py           # Loaders package initialization
│   │   ├── stock_loader.py       # Stock data loader
│   │   ├── news_loader.py        # News data loader
│   │   ├── twitter_loader.py     # Twitter data loader
│   ├── utils/                    # Utility modules
│       ├── __init__.py           # Utils package initialization
│       ├── logging_utils.py      # Logging configuration
│       ├── path_utils.py         # File path operations
├── db_setup.py                   # Main entry point script
```

## Key Features

- **Modular Design**: Each component has a single responsibility
- **Flexible Configuration**: Centralized settings in `config.py`
- **Robust Error Handling**: Comprehensive exception handling and logging
- **Command-Line Interface**: Powerful CLI with various options
- **Importable Modules**: Can be used programmatically in other scripts
- **Cross-Platform Compatibility**: Works on Windows, macOS, and Linux

## Usage

### Command-Line Interface

The database can be set up and populated using the command-line interface:

```bash
# Create database schema only
python -m db.cli --schema-only

# Load all data
python -m db.cli --load-all

# Load specific data types
python -m db.cli --load-stocks --load-news

# Specify custom paths
python -m db.cli --db-path /path/to/database.db --data-dir /path/to/data

# Enable verbose logging
python -m db.cli --verbose
```

### Programmatic Usage

The modules can also be imported and used in other Python scripts:

```python
# Import the main setup function
from db_setup import setup_database

# Set up database with all data
result = setup_database(load_all=True)

# Or import specific modules
from db.schema import create_database
from db.loaders import load_stock_data

# Create database
create_database()

# Load specific data
with get_db_connection() as conn:
    load_stock_data(conn)
```

## Module Descriptions

### `config.py`

Contains all configuration settings for the database, including:
- File paths
- Database name
- Logging configuration
- Stock symbols to track
- Sentiment thresholds

### `schema.py`

Defines the database schema and provides functions for:
- Creating the database and tables
- Managing database connections
- Retrieving stock symbol mappings
- Determining sentiment labels

### `loaders/`

Contains modules for loading different types of data:
- `stock_loader.py`: Loads stock price data from JSON files
- `news_loader.py`: Loads news articles with sentiment analysis
- `twitter_loader.py`: Loads tweets with sentiment analysis

### `utils/`

Contains utility functions:
- `logging_utils.py`: Configures logging for the application
- `path_utils.py`: Handles file path operations and validation

### `cli.py`

Implements the command-line interface with options for:
- Creating the schema only
- Loading specific data types
- Specifying custom file paths
- Enabling verbose logging

### `db_setup.py`

Main entry point that:
- Provides a convenient setup function
- Handles command-line execution
- Ensures proper Python path configuration

## Extending the System

### Adding New Data Sources

To add a new data source:

1. Create a new loader module in the `loaders/` directory
2. Implement the loader function following the pattern of existing loaders
3. Update the `__init__.py` file to expose the new loader
4. Add CLI options in `cli.py` if needed

### Modifying the Schema

To modify the database schema:

1. Update the table creation statements in `schema.py`
2. Consider adding migration functions if backward compatibility is needed

## Windows Compatibility

The system is designed to work seamlessly on Windows:
- Uses `pathlib.Path` for cross-platform path handling
- Avoids platform-specific file operations
- Handles file paths consistently

## Troubleshooting

### Common Issues

- **Missing Data Files**: Ensure all required data files exist in the expected locations
- **Database Permissions**: Check that the application has write permissions for the database file
- **Import Errors**: Verify that the project root is in the Python path

### Logging

The system uses Python's logging module with configurable levels:
- Set verbose mode with `--verbose` for detailed logging
- Check log files for error details
- Configure custom log locations in `config.py`
