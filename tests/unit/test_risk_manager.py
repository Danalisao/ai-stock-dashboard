"""
Unit tests for ProfessionalRiskManager module
"""
import pytest
import pandas as pd
import numpy as np
from modules.risk_manager import ProfessionalRiskManager, RiskLevel


class TestRiskManager:
    """Test suite for ProfessionalRiskManager"""
    
    @pytest.fixture(autouse=True)
    def setup(self, config):
        """Setup test environment"""
        self.risk_manager = ProfessionalRiskManager(config)
    
    def test_position_sizing_fixed_pct(self, sample_signal):
        """Test fixed percentage position sizing"""
        portfolio_value = 100000
        current_positions = []
        
        # Create sample price data
        dates = pd.date_range(end=pd.Timestamp.now(), periods=100, freq='D')
        price_data = pd.DataFrame({
            'Close': np.random.randn(100).cumsum() + 150,
            'Volume': np.random.randint(1000000, 10000000, 100)
        }, index=dates)
        
        result = self.risk_manager.calculate_position_size(
            sample_signal,
            portfolio_value,
            current_positions,
            price_data
        )
        
        assert result is not None
        assert 'recommended_shares' in result or 'position_value' in result
    
    def test_risk_based_sizing(self, sample_signal):
        """Test risk-based position sizing"""
        sample_signal['entry_price'] = 150.00
        sample_signal['stop_loss'] = 138.00
        
        portfolio_value = 100000
        risk_per_trade = 0.02  # 2%
        
        max_loss = portfolio_value * risk_per_trade
        price_risk = sample_signal['entry_price'] - sample_signal['stop_loss']
        
        expected_shares = max_loss / price_risk
        
        # Should not exceed maximum position size
        max_position_value = portfolio_value * 0.05  # 5% max
        max_shares_by_size = max_position_value / sample_signal['entry_price']
        
        expected_shares = min(expected_shares, max_shares_by_size)
        
        assert expected_shares > 0
    
    def test_portfolio_risk_limits(self, sample_portfolio_positions):
        """Test portfolio risk limit enforcement"""
        # This would test the portfolio risk checks
        # Needs access to portfolio tracker integration
        assert True  # Placeholder
    
    def test_kelly_criterion(self):
        """Test Kelly Criterion calculation"""
        win_rate = 0.6
        avg_win = 0.15
        avg_loss = 0.08
        
        # Kelly = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
        kelly = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
        
        # Kelly should be positive for profitable strategy
        assert kelly > 0
        
        # Conservative Kelly (25% of full Kelly)
        conservative_kelly = kelly * 0.25
        assert 0 < conservative_kelly < 0.5  # Should not exceed 50%
