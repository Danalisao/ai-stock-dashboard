"""
📊 Professional Risk Management Engine
Institutional-grade risk controls and position sizing
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

class RiskLevel(Enum):
    """Risk level classification"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    SPECULATIVE = "speculative"

@dataclass
class RiskMetrics:
    """Comprehensive risk metrics"""
    var_1d: float  # 1-day Value at Risk
    var_5d: float  # 5-day Value at Risk
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    volatility: float
    beta: float
    correlation_spy: float
    concentration_risk: float
    sector_exposure: Dict[str, float]

class ProfessionalRiskManager:
    """Advanced risk management for institutional trading"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Risk parameters
        risk_config = config.get('risk_management', {})
        self.max_portfolio_var = risk_config.get('max_portfolio_var_pct', 2.5) / 100
        self.max_single_position = risk_config.get('max_single_position_pct', 5) / 100
        self.max_sector_exposure = risk_config.get('max_sector_exposure_pct', 25) / 100
        self.max_correlation = risk_config.get('max_correlation', 0.7)
        self.min_sharpe_ratio = risk_config.get('min_sharpe_ratio', 1.0)
        self.max_drawdown_limit = risk_config.get('max_drawdown_limit_pct', 10) / 100
        
        # Kelly Criterion parameters
        self.use_kelly = risk_config.get('use_kelly_criterion', True)
        self.kelly_multiplier = risk_config.get('kelly_multiplier', 0.25)  # Conservative Kelly
        
        # Volatility targeting
        self.target_volatility = risk_config.get('target_volatility_pct', 15) / 100
        
    def calculate_position_size(self, 
                              signal: Dict[str, Any],
                              portfolio_value: float,
                              current_positions: List[Dict[str, Any]],
                              price_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate optimal position size using multiple methods
        
        Args:
            signal: Trading signal data
            portfolio_value: Current portfolio value
            current_positions: List of current positions
            price_data: Historical price data for volatility calculation
            
        Returns:
            Position sizing recommendation
        """
        symbol = signal['symbol']
        entry_price = signal.get('entry_price', 0)
        stop_loss = signal.get('stop_loss', 0)
        confidence = signal.get('confidence', 0.5)
        win_rate = signal.get('historical_win_rate', 0.6)
        avg_win = signal.get('avg_win_pct', 0.15)
        avg_loss = signal.get('avg_loss_pct', 0.08)
        
        # Calculate different position sizes
        sizing_methods = {}
        
        # 1. Fixed percentage method
        sizing_methods['fixed_pct'] = self._fixed_percentage_sizing(
            portfolio_value, self.max_single_position
        )
        
        # 2. Risk-based sizing (based on stop loss)
        if stop_loss and entry_price:
            sizing_methods['risk_based'] = self._risk_based_sizing(
                portfolio_value, entry_price, stop_loss
            )
        
        # 3. Kelly Criterion
        if self.use_kelly and win_rate and avg_win and avg_loss:
            sizing_methods['kelly'] = self._kelly_criterion_sizing(
                portfolio_value, win_rate, avg_win, avg_loss, entry_price
            )
        
        # 4. Volatility-based sizing
        if len(price_data) > 20:
            sizing_methods['volatility'] = self._volatility_based_sizing(
                portfolio_value, price_data, entry_price
            )
        
        # 5. Confidence-adjusted sizing
        sizing_methods['confidence'] = self._confidence_based_sizing(
            portfolio_value, confidence, entry_price
        )
        
        # Choose conservative size (minimum of all methods)
        position_sizes = [size for size in sizing_methods.values() if size > 0]
        if not position_sizes:
            return {'recommended_size': 0, 'error': 'No valid position size calculated'}
        
        recommended_shares = min(position_sizes)
        
        # Apply portfolio-level risk checks
        portfolio_risk = self._check_portfolio_risk(
            symbol, recommended_shares, entry_price, current_positions, portfolio_value
        )
        
        if not portfolio_risk['approved']:
            recommended_shares = portfolio_risk['max_allowed_shares']
        
        return {
            'recommended_shares': int(recommended_shares),
            'recommended_value': recommended_shares * entry_price,
            'portfolio_allocation_pct': (recommended_shares * entry_price) / portfolio_value * 100,
            'sizing_methods': sizing_methods,
            'risk_checks': portfolio_risk,
            'risk_per_share': abs(entry_price - stop_loss) if stop_loss else 0,
            'max_loss_amount': recommended_shares * abs(entry_price - stop_loss) if stop_loss else 0
        }
    
    def _fixed_percentage_sizing(self, portfolio_value: float, percentage: float) -> float:
        """Fixed percentage of portfolio method"""
        return (portfolio_value * percentage) / 100  # Returns dollar amount
    
    def _risk_based_sizing(self, portfolio_value: float, entry_price: float, stop_loss: float) -> float:
        """Risk-based position sizing (fixed $ risk per trade)"""
        max_risk = portfolio_value * 0.02  # Risk 2% per trade
        risk_per_share = abs(entry_price - stop_loss)
        if risk_per_share == 0:
            return 0
        return max_risk / risk_per_share  # Returns number of shares
    
    def _kelly_criterion_sizing(self, portfolio_value: float, win_rate: float, 
                               avg_win: float, avg_loss: float, entry_price: float) -> float:
        """Kelly Criterion optimal position sizing"""
        # Kelly formula: f = (bp - q) / b
        # where b = odds received on the wager (avg_win/avg_loss)
        # p = probability of winning
        # q = probability of losing (1-p)
        
        b = avg_win / avg_loss  # Odds ratio
        p = win_rate
        q = 1 - p
        
        kelly_fraction = (b * p - q) / b
        
        # Apply conservative multiplier
        kelly_fraction *= self.kelly_multiplier
        
        # Ensure positive and reasonable
        kelly_fraction = max(0, min(kelly_fraction, 0.1))  # Cap at 10%
        
        return (portfolio_value * kelly_fraction) / entry_price  # Returns shares
    
    def _volatility_based_sizing(self, portfolio_value: float, 
                                price_data: pd.DataFrame, entry_price: float) -> float:
        """Volatility-based position sizing for risk parity"""
        # Calculate 20-day volatility
        returns = price_data['Close'].pct_change().dropna()
        if len(returns) < 20:
            return 0
        
        volatility = returns.rolling(20).std().iloc[-1] * np.sqrt(252)  # Annualized
        
        # Target portfolio volatility contribution
        target_contribution = self.target_volatility / 10  # Assume 10 positions max
        
        # Position size to achieve target volatility contribution
        position_volatility = target_contribution / volatility
        position_value = portfolio_value * position_volatility
        
        return position_value / entry_price  # Returns shares
    
    def _confidence_based_sizing(self, portfolio_value: float, 
                                confidence: float, entry_price: float) -> float:
        """Adjust position size based on signal confidence"""
        base_allocation = 0.03  # 3% base allocation
        confidence_multiplier = 0.5 + (confidence * 1.5)  # 0.5x to 2.0x based on confidence
        
        adjusted_allocation = base_allocation * confidence_multiplier
        position_value = portfolio_value * adjusted_allocation
        
        return position_value / entry_price  # Returns shares
    
    def _check_portfolio_risk(self, symbol: str, shares: float, price: float,
                             current_positions: List[Dict[str, Any]], 
                             portfolio_value: float) -> Dict[str, Any]:
        """Comprehensive portfolio risk checks"""
        position_value = shares * price
        
        # Check single position limit
        position_pct = position_value / portfolio_value
        if position_pct > self.max_single_position:
            max_allowed_value = portfolio_value * self.max_single_position
            max_allowed_shares = max_allowed_value / price
            return {
                'approved': False,
                'reason': 'Exceeds single position limit',
                'max_allowed_shares': max_allowed_shares,
                'limit_pct': self.max_single_position * 100
            }
        
        # Check sector concentration (simplified - would need sector mapping)
        # For now, assume tech stocks
        tech_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSM']
        if symbol in tech_symbols:
            current_tech_value = sum(
                float(pos.get('market_value', 0)) 
                for pos in current_positions 
                if pos.get('symbol', '') in tech_symbols
            )
            new_tech_value = current_tech_value + position_value
            tech_exposure = new_tech_value / portfolio_value
            
            if tech_exposure > self.max_sector_exposure:
                max_additional = (portfolio_value * self.max_sector_exposure) - current_tech_value
                max_allowed_shares = max(0, max_additional / price)
                return {
                    'approved': False,
                    'reason': 'Exceeds sector exposure limit',
                    'max_allowed_shares': max_allowed_shares,
                    'current_sector_exposure': current_tech_value / portfolio_value * 100,
                    'limit_pct': self.max_sector_exposure * 100
                }
        
        return {
            'approved': True,
            'position_pct': position_pct * 100,
            'position_value': position_value
        }
    
    def calculate_portfolio_risk_metrics(self, positions: List[Dict[str, Any]], 
                                       price_history: Dict[str, pd.DataFrame],
                                       portfolio_value: float) -> RiskMetrics:
        """Calculate comprehensive portfolio risk metrics"""
        
        # Extract returns for each position
        position_returns = {}
        position_weights = {}
        
        for position in positions:
            symbol = position['symbol']
            market_value = float(position.get('market_value', 0))
            weight = market_value / portfolio_value
            position_weights[symbol] = weight
            
            if symbol in price_history and len(price_history[symbol]) > 252:
                returns = price_history[symbol]['Close'].pct_change().dropna()
                position_returns[symbol] = returns.tail(252)  # Last year
        
        if not position_returns:
            return self._empty_risk_metrics()
        
        # Create portfolio returns
        portfolio_returns = pd.Series(0.0, index=list(position_returns.values())[0].index)
        
        for symbol, returns in position_returns.items():
            weight = position_weights.get(symbol, 0)
            aligned_returns = returns.reindex(portfolio_returns.index, fill_value=0)
            portfolio_returns += aligned_returns * weight
        
        # Calculate metrics
        daily_vol = portfolio_returns.std()
        annual_vol = daily_vol * np.sqrt(252)
        
        # Value at Risk (95% confidence)
        var_1d = np.percentile(portfolio_returns, 5) * portfolio_value
        var_5d = var_1d * np.sqrt(5)
        
        # Sharpe ratio (assuming 2% risk-free rate)
        excess_returns = portfolio_returns - (0.02 / 252)
        sharpe = excess_returns.mean() / excess_returns.std() * np.sqrt(252)
        
        # Sortino ratio (downside deviation)
        downside_returns = portfolio_returns[portfolio_returns < 0]
        if len(downside_returns) > 0:
            downside_std = downside_returns.std()
            sortino = excess_returns.mean() / downside_std * np.sqrt(252)
        else:
            sortino = float('inf')
        
        # Maximum drawdown
        cumulative = (1 + portfolio_returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Beta vs SPY (simplified - would need SPY data)
        beta = 1.0  # Placeholder
        correlation_spy = 0.7  # Placeholder
        
        # Concentration risk (Herfindahl index)
        weights_squared = sum(w**2 for w in position_weights.values())
        concentration_risk = weights_squared
        
        # Sector exposure (simplified)
        sector_exposure = {"Technology": 0.6, "Healthcare": 0.2, "Finance": 0.2}  # Placeholder
        
        return RiskMetrics(
            var_1d=var_1d,
            var_5d=var_5d,
            sharpe_ratio=sharpe,
            sortino_ratio=sortino,
            max_drawdown=max_drawdown,
            volatility=annual_vol,
            beta=beta,
            correlation_spy=correlation_spy,
            concentration_risk=concentration_risk,
            sector_exposure=sector_exposure
        )
    
    def _empty_risk_metrics(self) -> RiskMetrics:
        """Return empty risk metrics when no data available"""
        return RiskMetrics(
            var_1d=0.0,
            var_5d=0.0,
            sharpe_ratio=0.0,
            sortino_ratio=0.0,
            max_drawdown=0.0,
            volatility=0.0,
            beta=1.0,
            correlation_spy=0.0,
            concentration_risk=0.0,
            sector_exposure={}
        )
    
    def check_risk_limits(self, risk_metrics: RiskMetrics, portfolio_value: float) -> Dict[str, Any]:
        """Check if portfolio exceeds risk limits"""
        violations = []
        warnings = []
        
        # VaR limit check
        var_pct = abs(risk_metrics.var_1d) / portfolio_value
        if var_pct > self.max_portfolio_var:
            violations.append({
                'type': 'VAR_EXCEEDED',
                'current': var_pct * 100,
                'limit': self.max_portfolio_var * 100,
                'severity': 'HIGH'
            })
        
        # Drawdown check
        if abs(risk_metrics.max_drawdown) > self.max_drawdown_limit:
            violations.append({
                'type': 'DRAWDOWN_EXCEEDED',
                'current': abs(risk_metrics.max_drawdown) * 100,
                'limit': self.max_drawdown_limit * 100,
                'severity': 'CRITICAL'
            })
        
        # Sharpe ratio check
        if risk_metrics.sharpe_ratio < self.min_sharpe_ratio:
            warnings.append({
                'type': 'LOW_SHARPE',
                'current': risk_metrics.sharpe_ratio,
                'target': self.min_sharpe_ratio,
                'severity': 'MEDIUM'
            })
        
        # Concentration risk
        if risk_metrics.concentration_risk > 0.3:  # 30% concentration limit
            warnings.append({
                'type': 'HIGH_CONCENTRATION',
                'current': risk_metrics.concentration_risk * 100,
                'limit': 30,
                'severity': 'MEDIUM'
            })
        
        return {
            'violations': violations,
            'warnings': warnings,
            'overall_risk_level': self._calculate_overall_risk_level(risk_metrics),
            'action_required': len(violations) > 0
        }
    
    def _calculate_overall_risk_level(self, risk_metrics: RiskMetrics) -> RiskLevel:
        """Calculate overall portfolio risk level"""
        risk_score = 0
        
        # Volatility component
        if risk_metrics.volatility > 0.25:
            risk_score += 3
        elif risk_metrics.volatility > 0.20:
            risk_score += 2
        elif risk_metrics.volatility > 0.15:
            risk_score += 1
        
        # Sharpe ratio component
        if risk_metrics.sharpe_ratio < 0.5:
            risk_score += 3
        elif risk_metrics.sharpe_ratio < 1.0:
            risk_score += 2
        elif risk_metrics.sharpe_ratio < 1.5:
            risk_score += 1
        
        # Drawdown component
        if abs(risk_metrics.max_drawdown) > 0.15:
            risk_score += 3
        elif abs(risk_metrics.max_drawdown) > 0.10:
            risk_score += 2
        elif abs(risk_metrics.max_drawdown) > 0.05:
            risk_score += 1
        
        # Concentration component
        if risk_metrics.concentration_risk > 0.4:
            risk_score += 2
        elif risk_metrics.concentration_risk > 0.3:
            risk_score += 1
        
        # Map score to risk level
        if risk_score >= 8:
            return RiskLevel.SPECULATIVE
        elif risk_score >= 6:
            return RiskLevel.AGGRESSIVE
        elif risk_score >= 3:
            return RiskLevel.MODERATE
        else:
            return RiskLevel.CONSERVATIVE