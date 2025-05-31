"""
Dashboard components module.

This module provides functionality for creating interactive dashboards for market sentiment analysis.
"""

import logging
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple

from ...utils.logging_utils import get_logger
from ...utils.file_utils import ensure_dir_exists

logger = get_logger(__name__)

def create_dashboard(
    stock_data: Dict[str, pd.DataFrame],
    news_sentiment_data: pd.DataFrame,
    twitter_sentiment_data: pd.DataFrame,
    model_predictions: Optional[Dict[str, pd.DataFrame]] = None,
    output_path: Optional[Union[str, Path]] = None,
    title: str = "Market Sentiment Dashboard",
    **kwargs
) -> str:
    """
    Create an interactive dashboard for market sentiment analysis.
    
    Args:
        stock_data: Dictionary mapping stock symbols to their price DataFrames.
        news_sentiment_data: DataFrame containing news sentiment data.
        twitter_sentiment_data: DataFrame containing Twitter sentiment data.
        model_predictions: Optional dictionary mapping stock symbols to prediction DataFrames.
        output_path: Path to save the dashboard HTML file. If None, a temporary file is created.
        title: Dashboard title. Defaults to "Market Sentiment Dashboard".
        **kwargs: Additional keyword arguments for dashboard customization.
    
    Returns:
        Path to the generated dashboard HTML file.
    """
    logger.info(f"Creating interactive dashboard for {len(stock_data)} stocks")
    
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        import dash
        from dash import dcc, html
    except ImportError:
        logger.error("Required packages not installed. Please install plotly and dash with 'pip install plotly dash'.")
        raise ImportError("Required packages not installed. Please install plotly and dash with 'pip install plotly dash'.")
    
    # Determine output path
    if output_path is None:
        import tempfile
        output_dir = tempfile.gettempdir()
        output_path = Path(output_dir) / "market_sentiment_dashboard.html"
    else:
        output_path = Path(output_path)
        ensure_dir_exists(output_path.parent)
    
    # Create a simple HTML dashboard using Plotly
    # In a real implementation, this would be a full Dash application
    
    # Create figure with subplots
    fig = make_subplots(
        rows=3, 
        cols=1,
        subplot_titles=(
            "Stock Prices", 
            "News Sentiment", 
            "Twitter Sentiment"
        ),
        vertical_spacing=0.1,
        specs=[
            [{"type": "scatter"}],
            [{"type": "scatter"}],
            [{"type": "scatter"}]
        ]
    )
    
    # Add stock price traces
    for symbol, data in stock_data.items():
        if 'date' in data.columns:
            x = data['date']
        else:
            x = data.index
            
        if 'close' in data.columns:
            y = data['close']
        else:
            y = data.iloc[:, 0]  # Use first column as fallback
            
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode='lines',
                name=f"{symbol} Price"
            ),
            row=1, col=1
        )
    
    # Add news sentiment trace
    if 'date' in news_sentiment_data.columns and 'compound' in news_sentiment_data.columns:
        fig.add_trace(
            go.Scatter(
                x=news_sentiment_data['date'],
                y=news_sentiment_data['compound'],
                mode='lines',
                name="News Sentiment",
                line=dict(color='blue')
            ),
            row=2, col=1
        )
    
    # Add Twitter sentiment trace
    if 'date' in twitter_sentiment_data.columns and 'compound' in twitter_sentiment_data.columns:
        fig.add_trace(
            go.Scatter(
                x=twitter_sentiment_data['date'],
                y=twitter_sentiment_data['compound'],
                mode='lines',
                name="Twitter Sentiment",
                line=dict(color='green')
            ),
            row=3, col=1
        )
    
    # Add model predictions if provided
    if model_predictions:
        for symbol, pred_data in model_predictions.items():
            if 'date' in pred_data.columns and 'prediction' in pred_data.columns:
                fig.add_trace(
                    go.Scatter(
                        x=pred_data['date'],
                        y=pred_data['prediction'],
                        mode='lines',
                        name=f"{symbol} Prediction",
                        line=dict(dash='dash')
                    ),
                    row=1, col=1
                )
    
    # Update layout
    fig.update_layout(
        title=title,
        height=900,
        width=1200,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Add range slider to x-axis
    fig.update_xaxes(
        rangeslider_visible=True,
        row=1, col=1
    )
    
    # Add horizontal reference lines for sentiment plots
    fig.add_shape(
        type="line",
        x0=0,
        y0=0,
        x1=1,
        y1=0,
        xref="paper",
        line=dict(color="gray", width=1, dash="dash"),
        row=2, col=1
    )
    
    fig.add_shape(
        type="line",
        x0=0,
        y0=0,
        x1=1,
        y1=0,
        xref="paper",
        line=dict(color="gray", width=1, dash="dash"),
        row=3, col=1
    )
    
    # Write to HTML file
    try:
        fig.write_html(
            output_path,
            full_html=True,
            include_plotlyjs='cdn',
            **kwargs
        )
        logger.info(f"Dashboard saved to {output_path}")
        return str(output_path)
    except Exception as e:
        logger.error(f"Error saving dashboard to {output_path}: {e}")
        raise
