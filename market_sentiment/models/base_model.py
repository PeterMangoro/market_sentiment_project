"""
Base model abstract class.

This module provides the base abstract class for all models in the Market Sentiment Project.
"""

import abc
import logging
import pickle
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple

from ..utils.logging_utils import get_logger
from ..utils.file_utils import ensure_dir_exists

logger = get_logger(__name__)

class BaseModel(abc.ABC):
    """
    Abstract base class for all models.
    
    This class defines the interface that all models must implement,
    and provides common functionality for model persistence and evaluation.
    """
    
    def __init__(self, name: str = "base_model"):
        """
        Initialize the base model.
        
        Args:
            name: Name of the model. Used for logging and saving.
        """
        self.name = name
        self.model = None
        self.trained = False
        logger.info(f"Initialized {self.name} model")
    
    @abc.abstractmethod
    def train(self, X, y, **kwargs):
        """
        Train the model.
        
        Args:
            X: Training features.
            y: Training targets.
            **kwargs: Additional training parameters.
        
        Returns:
            Self for method chaining.
        """
        pass
    
    @abc.abstractmethod
    def predict(self, X):
        """
        Make predictions with the model.
        
        Args:
            X: Features to predict on.
        
        Returns:
            Predictions.
        
        Raises:
            RuntimeError: If the model has not been trained.
        """
        if not self.trained:
            logger.error(f"{self.name} model has not been trained")
            raise RuntimeError(f"{self.name} model has not been trained")
    
    @abc.abstractmethod
    def evaluate(self, X, y, **kwargs):
        """
        Evaluate the model.
        
        Args:
            X: Evaluation features.
            y: Evaluation targets.
            **kwargs: Additional evaluation parameters.
        
        Returns:
            Dictionary of evaluation metrics.
        
        Raises:
            RuntimeError: If the model has not been trained.
        """
        if not self.trained:
            logger.error(f"{self.name} model has not been trained")
            raise RuntimeError(f"{self.name} model has not been trained")
    
    def save(self, path: Union[str, Path]) -> Path:
        """
        Save the model to a file.
        
        Args:
            path: Path to save the model to.
        
        Returns:
            Path where the model was saved.
        
        Raises:
            RuntimeError: If the model has not been trained.
        """
        if not self.trained:
            logger.error(f"{self.name} model has not been trained")
            raise RuntimeError(f"{self.name} model has not been trained")
        
        path = Path(path)
        ensure_dir_exists(path.parent)
        
        try:
            with open(path, 'wb') as f:
                pickle.dump(self.model, f)
            logger.info(f"{self.name} model saved to {path}")
            return path
        except Exception as e:
            logger.error(f"Error saving {self.name} model to {path}: {e}")
            raise
    
    def load(self, path: Union[str, Path]) -> 'BaseModel':
        """
        Load the model from a file.
        
        Args:
            path: Path to load the model from.
        
        Returns:
            Self for method chaining.
        
        Raises:
            FileNotFoundError: If the model file does not exist.
        """
        path = Path(path)
        
        if not path.exists():
            logger.error(f"Model file not found: {path}")
            raise FileNotFoundError(f"Model file not found: {path}")
        
        try:
            with open(path, 'rb') as f:
                self.model = pickle.load(f)
            self.trained = True
            logger.info(f"{self.name} model loaded from {path}")
            return self
        except Exception as e:
            logger.error(f"Error loading {self.name} model from {path}: {e}")
            raise
    
    def get_params(self) -> Dict[str, Any]:
        """
        Get the model parameters.
        
        Returns:
            Dictionary of model parameters.
        """
        return {"name": self.name, "trained": self.trained}
    
    def __str__(self) -> str:
        """
        Get a string representation of the model.
        
        Returns:
            String representation.
        """
        return f"{self.name} (trained: {self.trained})"
