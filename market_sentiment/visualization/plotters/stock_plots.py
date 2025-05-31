"""
Stock plotting module.

This module provides functionality for creating stock price visualizations.
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

class StockPlotter:
    """
    Plotter for stock price visualizations.
    
    This class provides methods for creating various visualizations
    related to stock price data and technical indicators.
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
        Initialize the StockPlotter.
        
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
        
        logger.info(f"Initialized StockPlotter with style '{style}' and palette '{palette}'")
    
    def plot_price_history(
        self,
        price_data: pd.DataFrame,
        date_column: str = 'date',
        price_column: str = 'close',
        volume_column: Optional[str] = 'volume',
        title: str = 'Stock Price History',
        symbol: Optional[str] = None,
        output_path: Optional[Union[str, Path]] = None,
        show: bool = True,
        **kwargs
    ) -> plt.Figure:
        """
        Plot stock price history with optional volume.
        
        Args:
            price_data: DataFrame containing price data.
            date_column: Name of the column containing dates. Defaults to 'date'.
            price_column: Name of the column containing prices. Defaults to 'close'.
            volume_column: Name of the column containing volume. If None, volume is not plotted.
            title: Plot title. Defaults to 'Stock Price History'.
            symbol: Stock symbol to include in the title. If None, not included.
            output_path: Path to save the plot. If None, the plot is not saved.
            show: Whether to display the plot. Defaults to True.
            **kwargs: Additional keyword arguments to pass to plt.plot().
        
        Returns:
            Matplotlib Figure object.
        """
        logger.info(f"Creating price history plot with {len(price_data)} data points")
        
        # Ensure date column is datetime
        if date_column in price_data.columns and not pd.api.types.is_datetime64_any_dtype(price_data[date_column]):
            price_data = price_data.copy()
            price_data[date_column] = pd.to_datetime(price_data[date_column])
        
        # Create figure
        if volume_column and volume_column in price_data.columns:
            # Create figure with two subplots
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=self.figsize, gridspec_kw={'height_ratios': [3, 1]}, sharex=True)
        else:
            # Create figure with one subplot
            fig, ax1 = plt.subplots(figsize=self.figsize)
        
        # Plot price on top subplot
        price_data.plot(
            x=date_column,
            y=price_column,
            ax=ax1,
            **kwargs
        )
        
        # Set title with symbol if provided
        if symbol:
            title = f"{title} - {symbol}"
        ax1.set_title(title)
        
        # Set labels
        ax1.set_xlabel('')
        ax1.set_ylabel('Price')
        
        # Add grid
        ax1.grid(True, alpha=0.3)
        
        # Plot volume on bottom subplot if available
        if volume_column and volume_column in price_data.columns:
            price_data.plot(
                x=date_column,
                y=volume_column,
                kind='bar',
                ax=ax2,
                alpha=0.3,
                color='blue',
                **kwargs
            )
            
            # Set labels
            ax2.set_xlabel('Date')
            ax2.set_ylabel('Volume')
            
            # Add grid
            ax2.grid(True, alpha=0.3)
            
            # Rotate x-axis labels for better readability
            plt.xticks(rotation=45)
        else:
            # If no volume, set x-label on price plot
            ax1.set_xlabel('Date')
            plt.xticks(rotation=45)
        
        # Tight layout
        plt.tight_layout()
        
        # Save if output_path is provided
        if output_path:
            output_path = Path(output_path)
            ensure_dir_exists(output_path.parent)
            plt.savefig(output_path, dpi=self.dpi)
            logger.info(f"Saved price history plot to {output_path}")
        
        # Show if requested
        if show:
            plt.show()
        else:
            plt.close(fig)
        
        return fig
    
    def plot_candlestick(
        self,
        price_data: pd.DataFrame,
        date_column: str = 'date',
        open_column: str = 'open',
        high_column: str = 'high',
        low_column: str = 'low',
        close_column: str = 'close',
        title: str = 'Candlestick Chart',
        symbol: Optional[str] = None,
        output_path: Optional[Union[str, Path]] = None,
        show: bool = True,
        **kwargs
    ) -> plt.Figure:
        """
        Plot a candlestick chart.
        
        Args:
            price_data: DataFrame containing price data.
            date_column: Name of the column containing dates. Defaults to 'date'.
            open_column: Name of the column containing opening prices. Defaults to 'open'.
            high_column: Name of the column containing high prices. Defaults to 'high'.
            low_column: Name of the column containing low prices. Defaults to 'low'.
            close_column: Name of the column containing closing prices. Defaults to 'close'.
            title: Plot title. Defaults to 'Candlestick Chart'.
            symbol: Stock symbol to include in the title. If None, not included.
            output_path: Path to save the plot. If None, the plot is not saved.
            show: Whether to display the plot. Defaults to True.
            **kwargs: Additional keyword arguments to pass to plt.plot().
        
        Returns:
            Matplotlib Figure object.
        """
        logger.info(f"Creating candlestick chart with {len(price_data)} data points")
        
        try:
            from mplfinance import plot as mpl_plot
            
            # Ensure date column is datetime and set as index
            price_data = price_data.copy()
            if not pd.api.types.is_datetime64_any_dtype(price_data[date_column]):
                price_data[date_column] = pd.to_datetime(price_data[date_column])
            
            # Set date as index if it's not already
            if price_data.index.name != date_column:
                price_data = price_data.set_index(date_column)
            
            # Rename columns to match mplfinance requirements
            column_map = {
                open_column: 'Open',
                high_column: 'High',
                low_column: 'Low',
                close_column: 'Close'
            }
            price_data = price_data.rename(columns=column_map)
            
            # Set title with symbol if provided
            if symbol:
                title = f"{title} - {symbol}"
            
            # Create figure
            fig, _ = plt.subplots(figsize=self.figsize)
            
            # Plot candlestick chart
            mpl_plot(
                price_data,
                type='candle',
                style='yahoo',
                title=title,
                figsize=self.figsize,
                **kwargs
            )
            
            # Save if output_path is provided
            if output_path:
                output_path = Path(output_path)
                ensure_dir_exists(output_path.parent)
                plt.savefig(output_path, dpi=self.dpi)
                logger.info(f"Saved candlestick chart to {output_path}")
            
            # Show if requested
            if show:
                plt.show()
            else:
                plt.close(fig)
            
            return fig
            
        except ImportError:
            logger.warning("mplfinance not installed. Falling back to basic OHLC plot.")
            
            # Create figure
            fig, ax = plt.subplots(figsize=self.figsize)
            
            # Plot high-low lines
            ax.vlines(
                x=price_data[date_column],
                ymin=price_data[low_column],
                ymax=price_data[high_column],
                color='black',
                **kwargs
            )
            
            # Plot open markers
            ax.scatter(
                price_data[date_column],
                price_data[open_column],
                color='green',
                marker='_',
                s=50,
                **kwargs
            )
            
            # Plot close markers
            ax.scatter(
                price_data[date_column],
                price_data[close_column],
                color='red',
                marker='_',
                s=50,
                **kwargs
            )
            
            # Set title with symbol if provided
            if symbol:
                title = f"{title} - {symbol}"
            ax.set_title(title)
            
            # Set labels
            ax.set_xlabel('Date')
            ax.set_ylabel('Price')
            
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
                logger.info(f"Saved basic OHLC plot to {output_path}")
            
            # Show if requested
            if show:
                plt.show()
            else:
                plt.close(fig)
            
            return fig
    
    def plot_returns(
        self,
        price_data: pd.DataFrame,
        date_column: str = 'date',
        price_column: str = 'close',
        period: int = 1,
        title: str = 'Stock Returns',
        symbol: Optional[str] = None,
        output_path: Optional[Union[str, Path]] = None,
        show: bool = True,
        **kwargs
    ) -> plt.Figure:
        """
        Plot stock returns over time.
        
        Args:
            price_data: DataFrame containing price data.
            date_column: Name of the column containing dates. Defaults to 'date'.
            price_column: Name of the column containing prices. Defaults to 'close'.
            period: Period for calculating returns. Defaults to 1 (daily returns).
            title: Plot title. Defaults to 'Stock Returns'.
            symbol: Stock symbol to include in the title. If None, not included.
            output_path: Path to save the plot. If None, the plot is not saved.
            show: Whether to display the plot. Defaults to True.
            **kwargs: Additional keyword arguments to pass to plt.plot().
        
        Returns:
            Matplotlib Figure object.
        """
        logger.info(f"Creating returns plot with {len(price_data)} data points")
        
        # Ensure date column is datetime
        price_data = price_data.copy()
        if date_column in price_data.columns and not pd.api.types.is_datetime64_any_dtype(price_data[date_column]):
            price_data[date_column] = pd.to_datetime(price_data[date_column])
        
        # Calculate returns
        if price_data.index.name != date_column and date_column in price_data.columns:
            price_data = price_data.set_index(date_column)
        
        price_data['returns'] = price_data[price_column].pct_change(period) * 100
        
        # Create figure
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Plot returns
        price_data['returns'].plot(
            ax=ax,
            **kwargs
        )
        
        # Add a horizontal line at y=0
        ax.axhline(y=0, color='gray', linestyle='--', alpha=0.7)
        
        # Set title with symbol if provided
        if symbol:
            title = f"{title} - {symbol}"
        ax.set_title(title)
        
        # Set labels
        ax.set_xlabel('Date')
        ax.set_ylabel('Returns (%)')
        
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
            logger.info(f"Saved returns plot to {output_path}")
        
        # Show if requested
        if show:
            plt.show()
        else:
            plt.close(fig)
        
        return fig
    
    def plot_comparison(
        self,
        price_data_dict: Dict[str, pd.DataFrame],
        date_column: str = 'date',
        price_column: str = 'close',
        normalize: bool = True,
        title: str = 'Stock Price Comparison',
        output_path: Optional[Union[str, Path]] = None,
        show: bool = True,
        **kwargs
    ) -> plt.Figure:
        """
        Plot a comparison of multiple stock prices.
        
        Args:
            price_data_dict: Dictionary mapping stock symbols to their price DataFrames.
            date_column: Name of the column containing dates. Defaults to 'date'.
            price_column: Name of the column containing prices. Defaults to 'close'.
            normalize: Whether to normalize prices to start at 100. Defaults to True.
            title: Plot title. Defaults to 'Stock Price Comparison'.
            output_path: Path to save the plot. If None, the plot is not saved.
            show: Whether to display the plot. Defaults to True.
            **kwargs: Additional keyword arguments to pass to plt.plot().
        
        Returns:
            Matplotlib Figure object.
        """
        logger.info(f"Creating price comparison plot for {len(price_data_dict)} stocks")
        
        # Create figure
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Process and plot each stock
        for symbol, price_data in price_data_dict.items():
            # Ensure date column is datetime
            price_data = price_data.copy()
            if date_column in price_data.columns and not pd.api.types.is_datetime64_any_dtype(price_data[date_column]):
                price_data[date_column] = pd.to_datetime(price_data[date_column])
            
            # Set date as index if it's not already
            if price_data.index.name != date_column and date_column in price_data.columns:
                price_data = price_data.set_index(date_column)
            
            # Normalize if requested
            if normalize:
                first_price = price_data[price_column].iloc[0]
                price_data[f'{symbol}_{price_column}'] = price_data[price_column] / first_price * 100
                plot_column = f'{symbol}_{price_column}'
            else:
                plot_column = price_column
            
            # Plot the stock price
            price_data[plot_column].plot(
                ax=ax,
                label=symbol,
                **kwargs
            )
        
        # Set title
        ax.set_title(title)
        
        # Set labels
        ax.set_xlabel('Date')
        if normalize:
            ax.set_ylabel('Normalized Price (Base=100)')
        else:
            ax.set_ylabel('Price')
        
        # Add grid
        ax.grid(True, alpha=0.3)
        
        # Add legend
        ax.legend()
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)
        
        # Tight layout
        plt.tight_layout()
        
        # Save if output_path is provided
        if output_path:
            output_path = Path(output_path)
            ensure_dir_exists(output_path.parent)
            plt.savefig(output_path, dpi=self.dpi)
            logger.info(f"Saved price comparison plot to {output_path}")
        
        # Show if requested
        if show:
            plt.show()
        else:
            plt.close(fig)
        
        return fig
