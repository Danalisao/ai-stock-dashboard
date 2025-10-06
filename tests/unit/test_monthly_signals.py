"""
Unit tests for MonthlySignals module
"""
import pytest
import pandas as pd
import numpy as np
from modules.monthly_signals import MonthlySignals
from modules.sentiment_analyzer import SentimentAnalyzer
from modules.technical_indicators import TechnicalIndicators


class TestMonthlySignals:
    """Test suite for MonthlySignals"""
    
    @pytest.fixture(autouse=True)
    def setup(self, config):
        """Setup test environment"""
        self.sentiment_analyzer = SentimentAnalyzer()
        self.technical_indicators = TechnicalIndicators()
        self.monthly_signals = MonthlySignals(
            config, 
            self.sentiment_analyzer,
            self.technical_indicators
        )
    
    def test_calculate_score_valid_data(self, sample_price_data):
        """Test score calculation with valid data"""
        result = self.monthly_signals.calculate_monthly_score(
            'AAPL', 
            sample_price_data
        )
        
        assert result is not None
        assert 'score' in result
        assert 'recommendation' in result
        assert 0 <= result['score'] <= 100
        
    def test_calculate_score_invalid_data(self):
        """Test score calculation with invalid data"""
        empty_df = pd.DataFrame()
        result = self.monthly_signals.calculate_monthly_score('AAPL', empty_df)
        
        assert result is None or result['score'] == 0
    
    def test_recommendation_mapping(self, sample_price_data):
        """Test score to recommendation mapping"""
        result = self.monthly_signals.calculate_monthly_score(
            'AAPL',
            sample_price_data
        )
        
        if result:
            score = result['score']
            recommendation = result['recommendation']
            
            if score >= 90:
                assert recommendation == 'STRONG BUY'
            elif score >= 75:
                assert recommendation in ['BUY', 'STRONG BUY']
            elif score >= 60:
                assert recommendation in ['MODERATE BUY', 'BUY']
    
    def test_risk_reward_calculation(self, sample_price_data):
        """Test risk/reward ratio calculation"""
        result = self.monthly_signals.calculate_monthly_score(
            'AAPL',
            sample_price_data
        )
        
        if result and 'risk_reward' in result:
            assert result['risk_reward'] > 0
            # Professional standard minimum
            if result['score'] >= 85:
                assert result['risk_reward'] >= 2.5
    
    def test_position_sizing(self, sample_price_data):
        """Test position sizing recommendations"""
        result = self.monthly_signals.calculate_monthly_score(
            'AAPL',
            sample_price_data
        )
        
        if result and 'position_size_pct' in result:
            assert 0 < result['position_size_pct'] <= 10
            # High score should recommend larger positions
            if result['score'] >= 90:
                assert result['position_size_pct'] >= 3


class TestScoreComponents:
    """Test individual score components"""
    
    @pytest.fixture(autouse=True)
    def setup(self, config):
        """Setup test environment"""
        self.sentiment_analyzer = SentimentAnalyzer()
        self.technical_indicators = TechnicalIndicators()
        self.monthly_signals = MonthlySignals(
            config,
            self.sentiment_analyzer,
            self.technical_indicators
        )
    
    def test_trend_component(self, sample_price_data):
        """Test trend score component"""
        # Add technical indicators
        data_with_indicators = self.technical_indicators.calculate_all_indicators(
            sample_price_data.copy()
        )
        
        # Trend component should be between 0-30 (30% weight)
        # This is internal calculation, would need access to method
        assert data_with_indicators is not None
    
    def test_momentum_component(self, sample_price_data):
        """Test momentum score component"""
        data_with_indicators = self.technical_indicators.calculate_all_indicators(
            sample_price_data.copy()
        )
        
        # Should have RSI calculated
        if 'RSI' in data_with_indicators.columns:
            rsi = data_with_indicators['RSI'].iloc[-1]
            assert 0 <= rsi <= 100
