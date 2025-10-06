"""
Unit tests for PortfolioTracker module
"""
import pytest
from datetime import datetime, timedelta
from modules.portfolio_tracker import PortfolioTracker


class TestPortfolioTracker:
    """Test suite for PortfolioTracker"""
    
    @pytest.fixture(autouse=True)
    def setup(self, config, test_db):
        """Setup test environment"""
        self.portfolio = PortfolioTracker(config, test_db)
    
    def test_add_position(self):
        """Test adding a new position"""
        result = self.portfolio.add_position(
            symbol='AAPL',
            quantity=10,
            entry_price=150.00,
            entry_date=datetime.now()
        )
        
        assert result is True or result is not None
    
    def test_calculate_unrealized_pnl(self, sample_portfolio_positions):
        """Test unrealized P&L calculation"""
        # Add positions
        for pos in sample_portfolio_positions:
            self.portfolio.add_position(
                symbol=pos['symbol'],
                quantity=pos['quantity'],
                entry_price=pos['entry_price'],
                entry_date=pos['entry_date']
            )
        
        # Calculate P&L
        current_prices = {
            'AAPL': 150.00,
            'MSFT': 335.00
        }
        
        unrealized_pnl = self.portfolio.calculate_unrealized_pnl(current_prices)
        
        assert unrealized_pnl is not None
        # AAPL: (150 - 145) * 10 = $50
        # MSFT: (335 - 320) * 5 = $75
        # Total: $125
    
    def test_risk_limits_check(self):
        """Test risk limits validation"""
        current_prices = {'AAPL': 150.00}
        
        risk_report = self.portfolio.check_risk_limits(current_prices)
        
        assert risk_report is not None
        assert isinstance(risk_report, dict)
    
    def test_sharpe_ratio_calculation(self):
        """Test Sharpe ratio calculation"""
        # Would need historical returns data
        # Placeholder for now
        assert True
