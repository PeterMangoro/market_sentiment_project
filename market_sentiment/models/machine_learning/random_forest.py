"""
Random Forest model implementation.

This module provides a Random Forest model for market sentiment analysis.
"""

import logging
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from typing import Dict, List, Any, Optional, Union, Tuple

from ..base_model import BaseModel
from ...utils.logging_utils import get_logger

logger = get_logger(__name__)

class RandomForestModel(BaseModel):
    """
    Random Forest model for market sentiment analysis.
    
    This class implements a Random Forest regressor for predicting stock prices
    based on market sentiment and historical price data.
    """
    
    def __init__(
        self, 
        n_estimators: int = 100, 
        max_depth: Optional[int] = None,
        random_state: int = 42,
        n_jobs: int = -1,
        **kwargs
    ):
        """
        Initialize the Random Forest model.
        
        Args:
            n_estimators: Number of trees in the forest. Defaults to 100.
            max_depth: Maximum depth of the trees. If None, nodes are expanded until all leaves are pure.
            random_state: Random state for reproducibility. Defaults to 42.
            n_jobs: Number of jobs to run in parallel. -1 means using all processors.
            **kwargs: Additional parameters to pass to RandomForestRegressor.
        """
        super().__init__(name="random_forest")
        
        self.params = {
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "random_state": random_state,
            "n_jobs": n_jobs,
            **kwargs
        }
        
        self.model = RandomForestRegressor(**self.params)
        logger.info(f"Initialized RandomForestModel with {n_estimators} estimators")
    
    def train(self, X, y, **kwargs) -> 'RandomForestModel':
        """
        Train the Random Forest model.
        
        Args:
            X: Training features as a pandas DataFrame or numpy array.
            y: Training targets as a pandas Series or numpy array.
            **kwargs: Additional training parameters.
        
        Returns:
            Self for method chaining.
        """
        logger.info(f"Training RandomForestModel on {X.shape[0]} samples with {X.shape[1]} features")
        
        try:
            self.model.fit(X, y)
            self.trained = True
            logger.info("RandomForestModel training completed successfully")
            
            # Log feature importances
            if hasattr(X, 'columns'):
                feature_importances = dict(zip(X.columns, self.model.feature_importances_))
                sorted_importances = sorted(feature_importances.items(), key=lambda x: x[1], reverse=True)
                logger.info("Feature importances:")
                for feature, importance in sorted_importances:
                    logger.info(f"  {feature}: {importance:.4f}")
            
            return self
        except Exception as e:
            logger.error(f"Error training RandomForestModel: {e}")
            raise
    
    def predict(self, X) -> np.ndarray:
        """
        Make predictions with the Random Forest model.
        
        Args:
            X: Features to predict on as a pandas DataFrame or numpy array.
        
        Returns:
            Numpy array of predictions.
        
        Raises:
            RuntimeError: If the model has not been trained.
        """
        super().predict(X)  # This will raise RuntimeError if not trained
        
        logger.info(f"Making predictions with RandomForestModel on {X.shape[0]} samples")
        return self.model.predict(X)
    
    def evaluate(self, X, y, **kwargs) -> Dict[str, float]:
        """
        Evaluate the Random Forest model.
        
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
        
        logger.info(f"Evaluating RandomForestModel on {X.shape[0]} samples")
        
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
            logger.error("RandomForestModel has not been trained")
            raise RuntimeError("RandomForestModel has not been trained")
        
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
