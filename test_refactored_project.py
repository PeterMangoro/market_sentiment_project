#!/usr/bin/env python3
"""
Test script for the refactored Market Sentiment Project.

This script tests the functionality of the refactored modules to ensure
they work correctly both individually and together.
"""

import os
import sys
import unittest
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Import modules to test
from market_sentiment.utils.logging_utils import setup_logging, get_logger
from market_sentiment.utils.file_utils import ensure_dir_exists, load_json, save_json
from market_sentiment.utils.date_utils import get_date_range, parse_date
from market_sentiment.config.settings import DEFAULT_SYMBOLS
from market_sentiment.models.base_model import BaseModel
from market_sentiment.models.machine_learning import RandomForestModel, XGBoostModel
from market_sentiment.models.time_series import ARIMAModel
from market_sentiment.visualization.plotters import SentimentPlotter, StockPlotter
from market_sentiment.workflow import WorkflowOrchestrator

# Set up logging
setup_logging(log_level=logging.INFO)
logger = get_logger(__name__)

class TestUtilities(unittest.TestCase):
    """Test utility functions."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = project_root / "test_output"
        ensure_dir_exists(self.test_dir)
    
    def test_logging_utils(self):
        """Test logging utilities."""
        logger = get_logger("test_logger")
        self.assertIsNotNone(logger)
        logger.info("Test log message")
    
    def test_file_utils(self):
        """Test file utilities."""
        # Test ensure_dir_exists
        test_subdir = self.test_dir / "subdir"
        ensure_dir_exists(test_subdir)
        self.assertTrue(test_subdir.exists())
        
        # Test save_json and load_json
        test_data = {"test": "data", "numbers": [1, 2, 3]}
        test_file = self.test_dir / "test_data.json"
        save_json(test_data, test_file)
        self.assertTrue(test_file.exists())
        
        loaded_data = load_json(test_file)
        self.assertEqual(loaded_data, test_data)
    
    def test_date_utils(self):
        """Test date utilities."""
        # Test get_date_range
        date_range = get_date_range(days_back=7)
        self.assertIn('start', date_range)
        self.assertIn('end', date_range)
        
        # Test parse_date
        date_str = "2023-01-01"
        date_obj = parse_date(date_str)
        self.assertEqual(date_obj.year, 2023)
        self.assertEqual(date_obj.month, 1)
        self.assertEqual(date_obj.day, 1)

class TestModels(unittest.TestCase):
    """Test model classes."""
    
    def test_random_forest_model(self):
        """Test RandomForestModel."""
        model = RandomForestModel()
        self.assertIsNotNone(model)
        self.assertEqual(model.name, "random_forest")
        self.assertFalse(model.trained)
    
    def test_xgboost_model(self):
        """Test XGBoostModel."""
        model = XGBoostModel()
        self.assertIsNotNone(model)
        self.assertEqual(model.name, "xgboost")
        self.assertFalse(model.trained)
    
    def test_arima_model(self):
        """Test ARIMAModel."""
        model = ARIMAModel()
        self.assertIsNotNone(model)
        self.assertEqual(model.name, "arima")
        self.assertFalse(model.trained)

class TestVisualization(unittest.TestCase):
    """Test visualization classes."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = project_root / "test_output"
        ensure_dir_exists(self.test_dir)
    
    def test_sentiment_plotter(self):
        """Test SentimentPlotter."""
        plotter = SentimentPlotter()
        self.assertIsNotNone(plotter)
    
    def test_stock_plotter(self):
        """Test StockPlotter."""
        plotter = StockPlotter()
        self.assertIsNotNone(plotter)

class TestWorkflow(unittest.TestCase):
    """Test workflow orchestration."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = project_root / "test_output"
        ensure_dir_exists(self.test_dir)
    
    def test_workflow_orchestrator(self):
        """Test WorkflowOrchestrator."""
        orchestrator = WorkflowOrchestrator(
            data_dir=self.test_dir / "data",
            output_dir=self.test_dir / "output",
            symbols=["AAPL", "MSFT"]
        )
        self.assertIsNotNone(orchestrator)
        self.assertEqual(orchestrator.symbols, ["AAPL", "MSFT"])

def run_tests():
    """Run all tests."""
    logger.info("Starting tests for Market Sentiment Project")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    logger.info("All tests completed")

if __name__ == "__main__":
    run_tests()
