"""
pytest configuration and shared fixtures
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.utils import load_config
from modules.database_manager import DatabaseManager


@pytest.fixture(scope="session")
def config():
    """Load configuration for tests"""
    return load_config()


@pytest.fixture(scope="function")
def test_db():
    """Create in-memory database for testing"""
    db = DatabaseManager({'path': ':memory:'})
    yield db
    # Cleanup if needed
    

@pytest.fixture(scope="function")
def sample_price_data():
    """Generate sample price data for testing"""
    dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
    np.random.seed(42)
    
    # Generate realistic stock data
    close_prices = 100 + np.cumsum(np.random.randn(100) * 2)
    close_prices = np.maximum(close_prices, 10)  # Prevent negative prices
    
    data = pd.DataFrame({
        'Open': close_prices * (1 + np.random.randn(100) * 0.01),
        'High': close_prices * (1 + np.abs(np.random.randn(100)) * 0.02),
        'Low': close_prices * (1 - np.abs(np.random.randn(100)) * 0.02),
        'Close': close_prices,
        'Volume': np.random.randint(1000000, 10000000, 100),
        'Adj Close': close_prices
    }, index=dates)
    
    return data


@pytest.fixture(scope="function")
def sample_signal():
    """Generate sample trading signal"""
    return {
        'symbol': 'AAPL',
        'score': 87.5,
        'recommendation': 'BUY',
        'entry_price': 150.00,
        'stop_loss': 138.00,
        'take_profit': 180.00,
        'confidence': 0.85,
        'risk_reward': 2.5
    }


@pytest.fixture(scope="function")
def sample_news_articles():
    """Generate sample news articles"""
    return [
        {
            'title': 'Apple announces record earnings',
            'description': 'AAPL reports strong Q4 results',
            'content': 'Apple Inc. exceeded analyst expectations',
            'published': datetime.now(),
            'source': 'Yahoo Finance'
        },
        {
            'title': 'Tech stocks rally on positive sentiment',
            'description': 'Market optimism drives tech sector',
            'content': 'Technology stocks surge as investors show confidence',
            'published': datetime.now() - timedelta(days=1),
            'source': 'Finviz'
        }
    ]


@pytest.fixture(scope="function")
def sample_portfolio_positions():
    """Generate sample portfolio positions"""
    return [
        {
            'symbol': 'AAPL',
            'quantity': 10,
            'entry_price': 145.00,
            'current_price': 150.00,
            'entry_date': datetime.now() - timedelta(days=30)
        },
        {
            'symbol': 'MSFT',
            'quantity': 5,
            'entry_price': 320.00,
            'current_price': 335.00,
            'entry_date': datetime.now() - timedelta(days=45)
        }
    ]
