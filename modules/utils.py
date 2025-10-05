"""
🛠️ Utility Functions
Common helper functions used across the application
"""

import os
import yaml
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file
    
    Args:
        config_path: Path to config file
        
    Returns:
        Dictionary with configuration
    """
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        logging.error(f"Configuration file not found: {config_path}")
        return {}
    except yaml.YAMLError as e:
        logging.error(f"Error parsing config file: {e}")
        return {}


def setup_logging(config: Dict[str, Any]) -> logging.Logger:
    """
    Configure logging based on config settings
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Configured logger
    """
    log_config = config.get('logging', {})
    
    # Create logs directory if it doesn't exist
    log_file = log_config.get('log_file', './logs/app.log')
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_config.get('level', 'INFO')),
        format=log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)


def load_env_variables():
    """Load environment variables from .env file"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        return True
    except ImportError:
        logging.warning("python-dotenv not installed. Using system environment variables.")
        return False
    except Exception as e:
        logging.error(f"Error loading .env file: {e}")
        return False


def validate_symbol(symbol: str) -> bool:
    """
    Validate stock symbol format
    
    Args:
        symbol: Stock ticker symbol
        
    Returns:
        True if valid format
    """
    if not symbol:
        return False
    
    # Remove whitespace and convert to uppercase
    symbol = symbol.strip().upper()
    
    # Basic validation: 1-5 characters, alphanumeric
    if not symbol.isalnum():
        return False
    
    if len(symbol) < 1 or len(symbol) > 5:
        return False
    
    return True


def format_currency(value: float, currency: str = "$") -> str:
    """
    Format number as currency
    
    Args:
        value: Numeric value
        currency: Currency symbol
        
    Returns:
        Formatted string
    """
    if pd.isna(value):
        return "N/A"
    
    return f"{currency}{value:,.2f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format number as percentage
    
    Args:
        value: Numeric value (0.15 = 15%)
        decimals: Number of decimal places
        
    Returns:
        Formatted string
    """
    if pd.isna(value):
        return "N/A"
    
    return f"{value * 100:.{decimals}f}%"


def calculate_returns(prices: pd.Series) -> pd.Series:
    """
    Calculate simple returns from price series
    
    Args:
        prices: Series of prices
        
    Returns:
        Series of returns
    """
    return prices.pct_change()


def calculate_log_returns(prices: pd.Series) -> pd.Series:
    """
    Calculate logarithmic returns from price series
    
    Args:
        prices: Series of prices
        
    Returns:
        Series of log returns
    """
    return np.log(prices / prices.shift(1))


def calculate_volatility(returns: pd.Series, periods: int = 252) -> float:
    """
    Calculate annualized volatility
    
    Args:
        returns: Series of returns
        periods: Trading periods per year (252 for daily)
        
    Returns:
        Annualized volatility
    """
    return returns.std() * np.sqrt(periods)


def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02, periods: int = 252) -> float:
    """
    Calculate Sharpe ratio
    
    Args:
        returns: Series of returns
        risk_free_rate: Annual risk-free rate
        periods: Trading periods per year
        
    Returns:
        Sharpe ratio
        
    Interpretation:
        > 2.0: Excellent
        1.0-2.0: Good
        0.5-1.0: Adequate
        < 0.5: Poor
    """
    if returns.std() == 0:
        return 0.0
    
    excess_returns = returns - (risk_free_rate / periods)
    return np.sqrt(periods) * excess_returns.mean() / returns.std()


def calculate_sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.02, periods: int = 252) -> float:
    """
    Calculate Sortino ratio (similar to Sharpe but uses downside deviation)
    
    Args:
        returns: Series of returns
        risk_free_rate: Annual risk-free rate
        periods: Trading periods per year
        
    Returns:
        Sortino ratio
        
    Interpretation:
        > 2.0: Excellent
        1.0-2.0: Good
        0.5-1.0: Adequate
        < 0.5: Poor
        
    Note: Sortino is better than Sharpe for asymmetric return distributions
          because it only penalizes downside volatility
    """
    if len(returns) < 2:
        return 0.0
    
    excess_returns = returns - (risk_free_rate / periods)
    
    # Calculate downside deviation (only negative returns)
    downside_returns = returns[returns < 0]
    
    if len(downside_returns) == 0 or downside_returns.std() == 0:
        return 0.0  # No downside = infinite Sortino, return 0 for safety
    
    downside_std = downside_returns.std()
    return np.sqrt(periods) * excess_returns.mean() / downside_std


def calculate_max_drawdown(prices: pd.Series) -> float:
    """
    Calculate maximum drawdown
    
    Args:
        prices: Series of prices
        
    Returns:
        Maximum drawdown as decimal (e.g., -0.25 = -25%)
    """
    cumulative = (1 + prices.pct_change()).cumprod()
    running_max = cumulative.cummax()
    drawdown = (cumulative - running_max) / running_max
    return drawdown.min()


def is_market_open() -> bool:
    """
    Check if US stock market is currently open
    
    Returns:
        True if market is open
    """
    from datetime import datetime
    import pytz
    
    # US Eastern Time
    tz = pytz.timezone('US/Eastern')
    now = datetime.now(tz)
    
    # Market hours: Mon-Fri, 9:30 AM - 4:00 PM ET
    if now.weekday() >= 5:  # Weekend
        return False
    
    market_open = now.replace(hour=9, minute=30, second=0)
    market_close = now.replace(hour=16, minute=0, second=0)
    
    return market_open <= now <= market_close


def get_next_market_open() -> datetime:
    """
    Get next market open datetime
    
    Returns:
        Datetime of next market open
    """
    from datetime import datetime
    import pytz
    
    tz = pytz.timezone('US/Eastern')
    now = datetime.now(tz)
    
    # Next day at 9:30 AM
    next_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
    
    # If after 4 PM today, use tomorrow
    if now.hour >= 16:
        next_open += timedelta(days=1)
    
    # Skip weekends
    while next_open.weekday() >= 5:
        next_open += timedelta(days=1)
    
    return next_open


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file system operations
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    import re
    
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    
    return filename


def get_sentiment_emoji(score: float) -> str:
    """
    Get emoji representing sentiment score
    
    Args:
        score: Sentiment score from -1 to +1
        
    Returns:
        Emoji string
    """
    if score >= 0.5:
        return "😊"  # Very positive
    elif score >= 0.2:
        return "🙂"  # Positive
    elif score >= -0.2:
        return "😐"  # Neutral
    elif score >= -0.5:
        return "😟"  # Negative
    else:
        return "😞"  # Very negative


def get_trend_emoji(value: float) -> str:
    """
    Get emoji representing trend direction
    
    Args:
        value: Trend value (positive/negative/zero)
        
    Returns:
        Emoji string
    """
    if value > 0.01:
        return "↗️"  # Uptrend
    elif value < -0.01:
        return "↘️"  # Downtrend
    else:
        return "➡️"  # Sideways


def get_recommendation_emoji(score: float) -> str:
    """
    Get emoji for trading recommendation
    
    Args:
        score: Monthly score (0-100)
        
    Returns:
        Emoji string
    """
    if score >= 80:
        return "🟢🟢🟢"  # Strong buy
    elif score >= 75:
        return "🟢🟢"  # Buy
    elif score >= 60:
        return "🟢"  # Moderate buy
    elif score >= 40:
        return "⚖️"  # Hold
    elif score >= 26:
        return "🔴"  # Moderate sell
    elif score >= 11:
        return "🔴🔴"  # Sell
    else:
        return "🔴🔴🔴"  # Strong sell


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Original text
        max_length: Maximum length
        suffix: Suffix to append if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


class RateLimiter:
    """Simple rate limiter for API calls"""
    
    def __init__(self, calls_per_minute: int = 60):
        """
        Initialize rate limiter
        
        Args:
            calls_per_minute: Maximum calls allowed per minute
        """
        self.calls_per_minute = calls_per_minute
        self.calls = []
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        import time
        
        now = time.time()
        
        # Remove calls older than 1 minute
        self.calls = [call_time for call_time in self.calls if now - call_time < 60]
        
        # If at limit, wait
        if len(self.calls) >= self.calls_per_minute:
            sleep_time = 60 - (now - self.calls[0])
            if sleep_time > 0:
                logging.debug(f"Rate limit reached, sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
                self.calls = []
        
        # Record this call
        self.calls.append(now)


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if denominator is zero
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division by zero
        
    Returns:
        Result of division or default
    """
    if denominator == 0 or pd.isna(denominator):
        return default
    
    return numerator / denominator
