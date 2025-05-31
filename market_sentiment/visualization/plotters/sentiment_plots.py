"""
Sentiment plotting module.

This module provides functionality for creating sentiment analysis visualizations.
"""

import logging
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple

from ...utils.logging_utils import get_logger
from ...utils.file_utils import ensure_dir_exists

logger = get_logger(__name__)

class SentimentPlotter:
    """
    Plotter for sentiment analysis visualizations.
    
    This class provides methods for creating various visualizations
    related to sentiment analysis of financial data.
    """
    
    def __init__(
        self,
        figsize: Tuple[int, int] = (12, 8),
        style: str = 'seaborn-v0_8-darkgrid',
        palette: str = 'viridis',
        dpi: int = 100,
        interactive: bool = False
    ):
        """
        Initialize the SentimentPlotter.
        
        Args:
            figsize: Default figure size. Defaults to (12, 8).
            style: Matplotlib style to use. Defaults to 'seaborn-v0_8-darkgrid'.
            palette: Color palette to use. Defaults to 'viridis'.
            dpi: DPI for saved figures. Defaults to 100.
            interactive: Whether to create interactive plots. Defaults to False.
        """
        self.figsize = figsize
        self.style = style
        self.palette = palette
        self.dpi = dpi
        self.interactive = interactive
        
        # Set the style
        plt.style.use(style)
        sns.set_palette(palette)
        
        logger.info(f"Initialized SentimentPlotter with style '{style}' and palette '{palette}'")
    
    def plot_sentiment_over_time(
        self,
        sentiment_data: pd.DataFrame,
        date_column: str = 'date',
        sentiment_column: str = 'compound',
        title: str = 'Sentiment Over Time',
        output_path: Optional[Union[str, Path]] = None,
        show: bool = True,
        **kwargs
    ) -> plt.Figure:
        """
        Plot sentiment scores over time.
        
        Args:
            sentiment_data: DataFrame containing sentiment data.
            date_column: Name of the column containing dates. Defaults to 'date'.
            sentiment_column: Name of the column containing sentiment scores. Defaults to 'compound'.
            title: Plot title. Defaults to 'Sentiment Over Time'.
            output_path: Path to save the plot. If None, the plot is not saved.
            show: Whether to display the plot. Defaults to True.
            **kwargs: Additional keyword arguments to pass to plt.plot().
        
        Returns:
            Matplotlib Figure object.
        """
        logger.info(f"Creating sentiment over time plot with {len(sentiment_data)} data points")
        
        # Ensure date column is datetime
        if date_column in sentiment_data.columns and not pd.api.types.is_datetime64_any_dtype(sentiment_data[date_column]):
            sentiment_data = sentiment_data.copy()
            sentiment_data[date_column] = pd.to_datetime(sentiment_data[date_column])
        
        # Create figure
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Plot sentiment over time
        sentiment_data.plot(
            x=date_column,
            y=sentiment_column,
            ax=ax,
            **kwargs
        )
        
        # Add a horizontal line at y=0 (neutral sentiment)
        ax.axhline(y=0, color='gray', linestyle='--', alpha=0.7)
        
        # Add shaded regions for positive and negative sentiment
        ax.axhspan(0, 1, alpha=0.1, color='green')
        ax.axhspan(-1, 0, alpha=0.1, color='red')
        
        # Set labels and title
        ax.set_xlabel('Date')
        ax.set_ylabel('Sentiment Score')
        ax.set_title(title)
        
        # Add grid
        ax.grid(True, alpha=0.3)
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)
        
        # Tight layout
        plt.tight_layout()
        
        # Save if output_path is provided
        if output_path:
            output_path = Path(output_path)
            ensure_dir_exists(output_path.parent)
            plt.savefig(output_path, dpi=self.dpi)
            logger.info(f"Saved sentiment over time plot to {output_path}")
        
        # Show if requested
        if show:
            plt.show()
        else:
            plt.close(fig)
        
        return fig
    
    def plot_sentiment_distribution(
        self,
        sentiment_data: pd.DataFrame,
        sentiment_column: str = 'compound',
        title: str = 'Sentiment Distribution',
        output_path: Optional[Union[str, Path]] = None,
        show: bool = True,
        **kwargs
    ) -> plt.Figure:
        """
        Plot the distribution of sentiment scores.
        
        Args:
            sentiment_data: DataFrame containing sentiment data.
            sentiment_column: Name of the column containing sentiment scores. Defaults to 'compound'.
            title: Plot title. Defaults to 'Sentiment Distribution'.
            output_path: Path to save the plot. If None, the plot is not saved.
            show: Whether to display the plot. Defaults to True.
            **kwargs: Additional keyword arguments to pass to sns.histplot().
        
        Returns:
            Matplotlib Figure object.
        """
        logger.info(f"Creating sentiment distribution plot with {len(sentiment_data)} data points")
        
        # Create figure
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Plot sentiment distribution
        sns.histplot(
            data=sentiment_data,
            x=sentiment_column,
            kde=True,
            ax=ax,
            **kwargs
        )
        
        # Add vertical line at x=0 (neutral sentiment)
        ax.axvline(x=0, color='gray', linestyle='--', alpha=0.7)
        
        # Add shaded regions for positive and negative sentiment
        ax.axvspan(0, 1, alpha=0.1, color='green')
        ax.axvspan(-1, 0, alpha=0.1, color='red')
        
        # Set labels and title
        ax.set_xlabel('Sentiment Score')
        ax.set_ylabel('Frequency')
        ax.set_title(title)
        
        # Add grid
        ax.grid(True, alpha=0.3)
        
        # Tight layout
        plt.tight_layout()
        
        # Save if output_path is provided
        if output_path:
            output_path = Path(output_path)
            ensure_dir_exists(output_path.parent)
            plt.savefig(output_path, dpi=self.dpi)
            logger.info(f"Saved sentiment distribution plot to {output_path}")
        
        # Show if requested
        if show:
            plt.show()
        else:
            plt.close(fig)
        
        return fig
    
    def plot_sentiment_vs_price(
        self,
        sentiment_data: pd.DataFrame,
        price_data: pd.DataFrame,
        date_column: str = 'date',
        sentiment_column: str = 'compound',
        price_column: str = 'close',
        title: str = 'Sentiment vs. Price',
        output_path: Optional[Union[str, Path]] = None,
        show: bool = True,
        **kwargs
    ) -> plt.Figure:
        """
        Plot sentiment scores against stock prices.
        
        Args:
            sentiment_data: DataFrame containing sentiment data.
            price_data: DataFrame containing price data.
            date_column: Name of the column containing dates. Defaults to 'date'.
            sentiment_column: Name of the column containing sentiment scores. Defaults to 'compound'.
            price_column: Name of the column containing prices. Defaults to 'close'.
            title: Plot title. Defaults to 'Sentiment vs. Price'.
            output_path: Path to save the plot. If None, the plot is not saved.
            show: Whether to display the plot. Defaults to True.
            **kwargs: Additional keyword arguments to pass to plt.plot().
        
        Returns:
            Matplotlib Figure object.
        """
        logger.info(f"Creating sentiment vs. price plot")
        
        # Ensure date columns are datetime
        sentiment_data = sentiment_data.copy()
        price_data = price_data.copy()
        
        if date_column in sentiment_data.columns and not pd.api.types.is_datetime64_any_dtype(sentiment_data[date_column]):
            sentiment_data[date_column] = pd.to_datetime(sentiment_data[date_column])
        
        if date_column in price_data.columns and not pd.api.types.is_datetime64_any_dtype(price_data[date_column]):
            price_data[date_column] = pd.to_datetime(price_data[date_column])
        
        # Create figure with two y-axes
        fig, ax1 = plt.subplots(figsize=self.figsize)
        ax2 = ax1.twinx()
        
        # Plot sentiment on left y-axis
        sentiment_line = ax1.plot(
            sentiment_data[date_column],
            sentiment_data[sentiment_column],
            color='blue',
            label='Sentiment',
            **kwargs
        )
        
        # Plot price on right y-axis
        price_line = ax2.plot(
            price_data[date_column],
            price_data[price_column],
            color='green',
            label='Price',
            **kwargs
        )
        
        # Add a horizontal line at y=0 (neutral sentiment)
        ax1.axhline(y=0, color='gray', linestyle='--', alpha=0.7)
        
        # Set labels and title
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Sentiment Score', color='blue')
        ax2.set_ylabel('Price', color='green')
        plt.title(title)
        
        # Add grid
        ax1.grid(True, alpha=0.3)
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)
        
        # Add legend
        lines = sentiment_line + price_line
        labels = [line.get_label() for line in lines]
        ax1.legend(lines, labels, loc='best')
        
        # Tight layout
        plt.tight_layout()
        
        # Save if output_path is provided
        if output_path:
            output_path = Path(output_path)
            ensure_dir_exists(output_path.parent)
            plt.savefig(output_path, dpi=self.dpi)
            logger.info(f"Saved sentiment vs. price plot to {output_path}")
        
        # Show if requested
        if show:
            plt.show()
        else:
            plt.close(fig)
        
        return fig
    
    def plot_sentiment_heatmap(
        self,
        sentiment_data: pd.DataFrame,
        pivot_index: str,
        pivot_columns: str,
        pivot_values: str = 'compound',
        title: str = 'Sentiment Heatmap',
        output_path: Optional[Union[str, Path]] = None,
        show: bool = True,
        **kwargs
    ) -> plt.Figure:
        """
        Plot a heatmap of sentiment scores.
        
        Args:
            sentiment_data: DataFrame containing sentiment data.
            pivot_index: Name of the column to use as pivot table index.
            pivot_columns: Name of the column to use as pivot table columns.
            pivot_values: Name of the column containing values for the pivot table. Defaults to 'compound'.
            title: Plot title. Defaults to 'Sentiment Heatmap'.
            output_path: Path to save the plot. If None, the plot is not saved.
            show: Whether to display the plot. Defaults to True.
            **kwargs: Additional keyword arguments to pass to sns.heatmap().
        
        Returns:
            Matplotlib Figure object.
        """
        logger.info(f"Creating sentiment heatmap")
        
        # Create pivot table
        pivot = pd.pivot_table(
            sentiment_data,
            values=pivot_values,
            index=pivot_index,
            columns=pivot_columns,
            aggfunc='mean'
        )
        
        # Create figure
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Plot heatmap
        sns.heatmap(
            pivot,
            cmap='RdBu_r',
            center=0,
            annot=True,
            ax=ax,
            **kwargs
        )
        
        # Set title
        ax.set_title(title)
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)
        
        # Tight layout
        plt.tight_layout()
        
        # Save if output_path is provided
        if output_path:
            output_path = Path(output_path)
            ensure_dir_exists(output_path.parent)
            plt.savefig(output_path, dpi=self.dpi)
            logger.info(f"Saved sentiment heatmap to {output_path}")
        
        # Show if requested
        if show:
            plt.show()
        else:
            plt.close(fig)
        
        return fig
