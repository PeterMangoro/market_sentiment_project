"""
ARIMA model implementation.

This module provides an ARIMA model for time series analysis of market data.
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Union, Tuple

from ..base_model import BaseModel
from ...utils.logging_utils import get_logger

logger = get_logger(__name__)

class ARIMAModel(BaseModel):
    """
    ARIMA model for time series analysis.
    
    This class implements an ARIMA (AutoRegressive Integrated Moving Average) model
    for time series forecasting of stock prices and market sentiment.
    """
    
    def __init__(
        self, 
        order: Tuple[int, int, int] = (5, 1, 0),
        seasonal_order: Optional[Tuple[int, int, int, int]] = None,
        **kwargs
    ):
        """
        Initialize the ARIMA model.
        
        Args:
            order: ARIMA order (p, d, q) parameters. Defaults to (5, 1, 0).
            seasonal_order: Seasonal order (P, D, Q, s) parameters. Defaults to None.
            **kwargs: Additional parameters to pass to ARIMA.
        """
        super().__init__(name="arima")
        
        self.params = {
            "order": order,
            "seasonal_order": seasonal_order,
            **kwargs
        }
        
        # Import statsmodels here to avoid dependency issues if not installed
        try:
            from statsmodels.tsa.arima.model import ARIMA
            self.model_class = ARIMA
            logger.info(f"Initialized ARIMAModel with order {order}")
        except ImportError:
            logger.warning("statsmodels not installed. Will attempt to import when training.")
            self.model_class = None
    
    def train(self, data, target_column=None, **kwargs) -> 'ARIMAModel':
        """
        Train the ARIMA model.
        
        Args:
            data: Training data as a pandas Series or DataFrame.
                 If DataFrame, target_column must be specified.
            target_column: Column name to use as target if data is a DataFrame.
            **kwargs: Additional training parameters.
        
        Returns:
            Self for method chaining.
        
        Raises:
            ImportError: If statsmodels is not installed.
            ValueError: If data format is invalid.
        """
        # Import statsmodels if not already imported
        if self.model_class is None:
            try:
                from statsmodels.tsa.arima.model import ARIMA
                self.model_class = ARIMA
            except ImportError:
                logger.error("statsmodels is not installed. Please install it with 'pip install statsmodels'.")
                raise ImportError("statsmodels is not installed. Please install it with 'pip install statsmodels'.")
        
        # Extract target series if data is a DataFrame
        if isinstance(data, pd.DataFrame):
            if target_column is None:
                logger.error("target_column must be specified when data is a DataFrame")
                raise ValueError("target_column must be specified when data is a DataFrame")
            
            logger.info(f"Training ARIMAModel on column '{target_column}' with {len(data)} samples")
            series = data[target_column]
        elif isinstance(data, pd.Series):
            logger.info(f"Training ARIMAModel on Series with {len(data)} samples")
            series = data
        else:
            logger.error(f"Unsupported data type: {type(data)}. Expected DataFrame or Series.")
            raise ValueError(f"Unsupported data type: {type(data)}. Expected DataFrame or Series.")
        
        try:
            # Create and fit the ARIMA model
            model = self.model_class(
                series,
                order=self.params["order"],
                seasonal_order=self.params["seasonal_order"]
            )
            
            self.model_result = model.fit(**kwargs)
            self.trained = True
            
            # Store the training data index for forecasting
            self.train_index = series.index
            
            logger.info("ARIMAModel training completed successfully")
            logger.debug(f"Model summary:\n{self.model_result.summary().tables[0].as_text()}")
            
            return self
        except Exception as e:
            logger.error(f"Error training ARIMAModel: {e}")
            raise
    
    def predict(self, steps: int = 1, **kwargs) -> pd.Series:
        """
        Make predictions with the ARIMA model.
        
        Args:
            steps: Number of steps to forecast. Defaults to 1.
            **kwargs: Additional prediction parameters.
        
        Returns:
            Pandas Series of predictions.
        
        Raises:
            RuntimeError: If the model has not been trained.
        """
        super().predict(None)  # This will raise RuntimeError if not trained
        
        logger.info(f"Forecasting {steps} steps with ARIMAModel")
        
        try:
            forecast = self.model_result.forecast(steps=steps, **kwargs)
            
            # If the training data had a DatetimeIndex, try to extend it for the forecast
            if isinstance(self.train_index, pd.DatetimeIndex):
                try:
                    # Get the frequency of the index
                    freq = pd.infer_freq(self.train_index)
                    if freq:
                        # Create a new index for the forecast
                        last_date = self.train_index[-1]
                        forecast_index = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=steps, freq=freq)
                        forecast.index = forecast_index
                except Exception as e:
                    logger.warning(f"Could not create DatetimeIndex for forecast: {e}")
            
            return forecast
        except Exception as e:
            logger.error(f"Error forecasting with ARIMAModel: {e}")
            raise
    
    def evaluate(self, test_data, **kwargs) -> Dict[str, float]:
        """
        Evaluate the ARIMA model.
        
        Args:
            test_data: Test data as a pandas Series.
            **kwargs: Additional evaluation parameters.
        
        Returns:
            Dictionary of evaluation metrics:
            - mse: Mean squared error
            - rmse: Root mean squared error
            - mae: Mean absolute error
        
        Raises:
            RuntimeError: If the model has not been trained.
        """
        super().evaluate(None, None)  # This will raise RuntimeError if not trained
        
        logger.info(f"Evaluating ARIMAModel on {len(test_data)} samples")
        
        from sklearn.metrics import mean_squared_error, mean_absolute_error
        
        # Generate predictions for the test period
        predictions = self.model_result.forecast(steps=len(test_data))
        
        # Calculate metrics
        mse = mean_squared_error(test_data, predictions)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(test_data, predictions)
        
        metrics = {
            "mse": mse,
            "rmse": rmse,
            "mae": mae
        }
        
        logger.info(f"Evaluation metrics: MSE={mse:.4f}, RMSE={rmse:.4f}, MAE={mae:.4f}")
        return metrics
    
    def get_params(self) -> Dict[str, Any]:
        """
        Get the model parameters.
        
        Returns:
            Dictionary of model parameters.
        """
        params = super().get_params()
        params.update(self.params)
        return params
