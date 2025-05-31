"""
XGBoost model implementation.

This module provides an XGBoost model for market sentiment analysis.
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Union, Tuple

from ..base_model import BaseModel
from ...utils.logging_utils import get_logger

logger = get_logger(__name__)

class XGBoostModel(BaseModel):
    """
    XGBoost model for market sentiment analysis.
    
    This class implements an XGBoost regressor for predicting stock prices
    based on market sentiment and historical price data.
    """
    
    def __init__(
        self, 
        n_estimators: int = 100, 
        learning_rate: float = 0.1,
        max_depth: int = 5,
        random_state: int = 42,
        **kwargs
    ):
        """
        Initialize the XGBoost model.
        
        Args:
            n_estimators: Number of boosting rounds. Defaults to 100.
            learning_rate: Step size shrinkage used to prevent overfitting. Defaults to 0.1.
            max_depth: Maximum depth of a tree. Defaults to 5.
            random_state: Random state for reproducibility. Defaults to 42.
            **kwargs: Additional parameters to pass to XGBRegressor.
        """
        super().__init__(name="xgboost")
        
        self.params = {
            "n_estimators": n_estimators,
            "learning_rate": learning_rate,
            "max_depth": max_depth,
            "random_state": random_state,
            **kwargs
        }
        
        # Import XGBoost here to avoid dependency issues if not installed
        try:
            from xgboost import XGBRegressor
            self.model = XGBRegressor(**self.params)
            logger.info(f"Initialized XGBoostModel with {n_estimators} estimators")
        except ImportError:
            logger.warning("XGBoost not installed. Will attempt to import when training.")
            self.model = None
    
    def train(self, X, y, **kwargs) -> 'XGBoostModel':
        """
        Train the XGBoost model.
        
        Args:
            X: Training features as a pandas DataFrame or numpy array.
            y: Training targets as a pandas Series or numpy array.
            **kwargs: Additional training parameters.
        
        Returns:
            Self for method chaining.
        
        Raises:
            ImportError: If XGBoost is not installed.
        """
        logger.info(f"Training XGBoostModel on {X.shape[0]} samples with {X.shape[1]} features")
        
        # Import XGBoost if not already imported
        if self.model is None:
            try:
                from xgboost import XGBRegressor
                self.model = XGBRegressor(**self.params)
            except ImportError:
                logger.error("XGBoost is not installed. Please install it with 'pip install xgboost'.")
                raise ImportError("XGBoost is not installed. Please install it with 'pip install xgboost'.")
        
        try:
            self.model.fit(X, y, **kwargs)
            self.trained = True
            logger.info("XGBoostModel training completed successfully")
            
            # Log feature importances
            if hasattr(X, 'columns'):
                feature_importances = dict(zip(X.columns, self.model.feature_importances_))
                sorted_importances = sorted(feature_importances.items(), key=lambda x: x[1], reverse=True)
                logger.info("Feature importances:")
                for feature, importance in sorted_importances:
                    logger.info(f"  {feature}: {importance:.4f}")
            
            return self
        except Exception as e:
            logger.error(f"Error training XGBoostModel: {e}")
            raise
    
    def predict(self, X) -> np.ndarray:
        """
        Make predictions with the XGBoost model.
        
        Args:
            X: Features to predict on as a pandas DataFrame or numpy array.
        
        Returns:
            Numpy array of predictions.
        
        Raises:
            RuntimeError: If the model has not been trained.
        """
        super().predict(X)  # This will raise RuntimeError if not trained
        
        logger.info(f"Making predictions with XGBoostModel on {X.shape[0]} samples")
        return self.model.predict(X)
    
    def evaluate(self, X, y, **kwargs) -> Dict[str, float]:
        """
        Evaluate the XGBoost model.
        
        Args:
            X: Evaluation features as a pandas DataFrame or numpy array.
            y: Evaluation targets as a pandas Series or numpy array.
            **kwargs: Additional evaluation parameters.
        
        Returns:
            Dictionary of evaluation metrics:
            - mse: Mean squared error
            - rmse: Root mean squared error
            - mae: Mean absolute error
            - r2: R-squared score
        
        Raises:
            RuntimeError: If the model has not been trained.
        """
        super().evaluate(X, y)  # This will raise RuntimeError if not trained
        
        logger.info(f"Evaluating XGBoostModel on {X.shape[0]} samples")
        
        from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
        
        y_pred = self.predict(X)
        
        mse = mean_squared_error(y, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y, y_pred)
        r2 = r2_score(y, y_pred)
        
        metrics = {
            "mse": mse,
            "rmse": rmse,
            "mae": mae,
            "r2": r2
        }
        
        logger.info(f"Evaluation metrics: MSE={mse:.4f}, RMSE={rmse:.4f}, MAE={mae:.4f}, R2={r2:.4f}")
        return metrics
    
    def get_feature_importances(self, feature_names: Optional[List[str]] = None) -> Dict[str, float]:
        """
        Get the feature importances from the trained model.
        
        Args:
            feature_names: List of feature names. If None, uses numbered features.
        
        Returns:
            Dictionary mapping feature names to importance scores.
        
        Raises:
            RuntimeError: If the model has not been trained.
        """
        if not self.trained:
            logger.error("XGBoostModel has not been trained")
            raise RuntimeError("XGBoostModel has not been trained")
        
        importances = self.model.feature_importances_
        
        if feature_names is None:
            feature_names = [f"feature_{i}" for i in range(len(importances))]
        
        if len(feature_names) != len(importances):
            logger.warning(f"Number of feature names ({len(feature_names)}) does not match number of features ({len(importances)})")
            feature_names = [f"feature_{i}" for i in range(len(importances))]
        
        return dict(zip(feature_names, importances))
    
    def get_params(self) -> Dict[str, Any]:
        """
        Get the model parameters.
        
        Returns:
            Dictionary of model parameters.
        """
        params = super().get_params()
        params.update(self.params)
        return params
