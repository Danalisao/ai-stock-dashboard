"""
💼 Professional Trading Engine
Advanced trading operations with institutional-grade risk management
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from modules.database_manager import DatabaseManager
from modules.portfolio_tracker import PortfolioTracker
from modules.monthly_signals import MonthlySignals
from modules.pro_mode_guard import ProModeGuard, ValidationResult


class ProfessionalTradingEngine:
    """Professional-grade trading engine with advanced risk management"""
    
    def __init__(self, config: Dict[str, Any], db_manager: DatabaseManager, 
                 portfolio_tracker: PortfolioTracker, monthly_signals: MonthlySignals):
        """
        Initialize professional trading engine
        
        Args:
            config: Configuration dictionary
            db_manager: Database manager instance
            portfolio_tracker: Portfolio tracker instance
            monthly_signals: Monthly signals calculator
        """
        self.config = config
        self.db = db_manager
        self.portfolio = portfolio_tracker
        self.signals = monthly_signals
        self.logger = logging.getLogger(__name__)
        
        # Professional trading parameters
        trading_cfg = config.get('trading', {})
        self.min_score = trading_cfg.get('entry_score_min', 85)
        self.min_risk_reward = trading_cfg.get('min_risk_reward', 2.5)
        self.min_confidence = trading_cfg.get('min_confidence', 0.7)
        self.max_hold_days = trading_cfg.get('max_hold_days', 90)
        self.stop_loss_pct = trading_cfg.get('stop_loss_pct', 8) / 100
        self.take_profit_pct = trading_cfg.get('take_profit_pct', 25) / 100
        
        # Risk management
        self.max_portfolio_risk = trading_cfg.get('max_portfolio_risk_pct', 10) / 100
        self.position_size_pct = config.get('portfolio', {}).get('position_size_pct', 5) / 100
        
        # Initialize professional mode guard
        self.pro_guard = ProModeGuard(config, db_manager)
    
    def analyze_trade_opportunity(self, symbol: str, market_data: pd.DataFrame,
                                current_price: float) -> Dict[str, Any]:
        """
        Comprehensive trade opportunity analysis
        
        Args:
            symbol: Stock symbol
            market_data: Historical market data
            current_price: Current market price
            
        Returns:
            Trade analysis dictionary
        """
        try:
            # Validate market data quality
            data_validation = self.pro_guard.validate_market_data(symbol, market_data)
            if not data_validation.passed:
                return {
                    'trade_recommendation': 'REJECT',
                    'reason': 'Data quality issues',
                    'issues': data_validation.issues
                }
            
            # Calculate monthly signal score
            score_data = self.signals.calculate_monthly_score(
                market_data, symbol, None, None
            )
            
            if not score_data:
                return {
                    'trade_recommendation': 'REJECT',
                    'reason': 'Unable to calculate trading signals'
                }
            
            total_score = score_data.get('total_score', 0)
            confidence = score_data.get('confidence', 0)
            
            # Professional entry criteria
            meets_score = total_score >= self.min_score
            meets_confidence = confidence >= self.min_confidence
            
            # Risk/Reward calculation
            entry_price = current_price
            stop_loss = entry_price * (1 - self.stop_loss_pct)
            target_price = entry_price * (1 + self.take_profit_pct)
            
            risk_amount = entry_price - stop_loss
            reward_amount = target_price - entry_price
            risk_reward_ratio = reward_amount / risk_amount if risk_amount > 0 else 0
            
            meets_rr = risk_reward_ratio >= self.min_risk_reward
            
            # Portfolio impact analysis
            portfolio_impact = self._analyze_portfolio_impact(symbol, entry_price)
            
            # Final recommendation
            if meets_score and meets_confidence and meets_rr and portfolio_impact['acceptable']:
                recommendation = 'STRONG_BUY' if total_score >= 90 else 'BUY'
            elif meets_score and meets_confidence:
                recommendation = 'CONSIDER'
            else:
                recommendation = 'PASS'
            
            return {
                'symbol': symbol,
                'trade_recommendation': recommendation,
                'total_score': total_score,
                'confidence': confidence,
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'target_price': target_price,
                'risk_reward_ratio': round(risk_reward_ratio, 2),
                'position_size_shares': portfolio_impact['recommended_shares'],
                'position_value': portfolio_impact['position_value'],
                'portfolio_impact_pct': portfolio_impact['portfolio_impact_pct'],
                'criteria_met': {
                    'score': meets_score,
                    'confidence': meets_confidence,
                    'risk_reward': meets_rr,
                    'portfolio_limits': portfolio_impact['acceptable']
                },
                'score_breakdown': score_data.get('components', {}),
                'analysis_timestamp': datetime.now().isoformat(),
                'data_quality_warnings': data_validation.warnings
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing trade opportunity for {symbol}: {e}")
            return {
                'trade_recommendation': 'ERROR',
                'reason': f'Analysis failed: {str(e)}'
            }
    
    def _analyze_portfolio_impact(self, symbol: str, entry_price: float) -> Dict[str, Any]:
        """Analyze impact of new position on portfolio"""
        try:
            # Get current portfolio value
            current_positions = self.db.get_open_positions()
            total_portfolio_value = self.config.get('portfolio', {}).get('initial_capital', 10000)
            
            if current_positions:
                # Add unrealized P&L (simplified)
                for pos in current_positions:
                    total_portfolio_value += pos['position_value']
            
            # Calculate position size based on portfolio percentage
            max_position_value = total_portfolio_value * self.position_size_pct
            recommended_shares = int(max_position_value / entry_price)
            actual_position_value = recommended_shares * entry_price
            
            # Check if position is acceptable
            portfolio_impact_pct = (actual_position_value / total_portfolio_value) * 100
            position_count = len(current_positions)
            max_positions = self.config.get('portfolio', {}).get('max_positions', 10)
            
            acceptable = (
                portfolio_impact_pct <= self.position_size_pct * 100 and
                position_count < max_positions and
                recommended_shares > 0
            )
            
            return {
                'recommended_shares': recommended_shares,
                'position_value': actual_position_value,
                'portfolio_impact_pct': round(portfolio_impact_pct, 2),
                'current_positions': position_count,
                'max_positions': max_positions,
                'acceptable': acceptable
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing portfolio impact: {e}")
            return {
                'recommended_shares': 0,
                'position_value': 0,
                'portfolio_impact_pct': 0,
                'acceptable': False
            }
    
    def execute_trade(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute trade based on analysis
        
        Args:
            analysis: Trade analysis result
            
        Returns:
            Execution result
        """
        if analysis.get('trade_recommendation') not in ['BUY', 'STRONG_BUY']:
            return {
                'success': False,
                'reason': f"Trade not recommended: {analysis.get('trade_recommendation')}"
            }
        
        try:
            symbol = analysis['symbol']
            shares = analysis['position_size_shares']
            entry_price = analysis['entry_price']
            stop_loss = analysis['stop_loss']
            target_price = analysis['target_price']
            
            # Execute position opening
            success = self.db.open_position(
                symbol=symbol,
                entry_price=entry_price,
                shares=shares,
                stop_loss=stop_loss,
                target_price=target_price,
                notes=f"Professional signal: {analysis['total_score']}/100, R/R: {analysis['risk_reward_ratio']}"
            )
            
            if success:
                self.logger.info(f"✅ Opened position: {shares} shares of {symbol} @ ${entry_price:.2f}")
                return {
                    'success': True,
                    'symbol': symbol,
                    'shares': shares,
                    'entry_price': entry_price,
                    'position_value': shares * entry_price,
                    'stop_loss': stop_loss,
                    'target_price': target_price
                }
            else:
                return {
                    'success': False,
                    'reason': 'Database operation failed'
                }
                
        except Exception as e:
            self.logger.error(f"Error executing trade: {e}")
            return {
                'success': False,
                'reason': f"Execution error: {str(e)}"
            }
    
    def scan_opportunities(self, watchlist: List[str], 
                          current_prices: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Scan watchlist for trading opportunities
        
        Args:
            watchlist: List of symbols to scan
            current_prices: Current market prices
            
        Returns:
            List of trading opportunities
        """
        opportunities = []
        
        for symbol in watchlist:
            try:
                if symbol not in current_prices:
                    continue
                
                # Fetch market data (simplified - in real implementation, use cached data)
                import yfinance as yf
                ticker = yf.Ticker(symbol)
                market_data = ticker.history(period='1y')
                
                if market_data is None or market_data.empty:
                    continue
                
                # Analyze opportunity
                analysis = self.analyze_trade_opportunity(
                    symbol, market_data, current_prices[symbol]
                )
                
                if analysis.get('trade_recommendation') in ['BUY', 'STRONG_BUY', 'CONSIDER']:
                    opportunities.append(analysis)
                    
            except Exception as e:
                self.logger.error(f"Error scanning {symbol}: {e}")
                continue
        
        # Sort by score descending
        opportunities.sort(key=lambda x: x.get('total_score', 0), reverse=True)
        
        return opportunities
    
    def generate_risk_report(self, current_prices: Dict[str, float]) -> Dict[str, Any]:
        """
        Generate comprehensive risk assessment report
        
        Args:
            current_prices: Current market prices
            
        Returns:
            Risk report dictionary
        """
        try:
            # Portfolio validation
            portfolio_validation = self.pro_guard.validate_portfolio_limits(
                self.portfolio, current_prices
            )
            
            # Get portfolio metrics
            portfolio_value = self.portfolio.get_portfolio_value(current_prices)
            performance_metrics = self.portfolio.calculate_performance_metrics()
            
            # Risk assessment
            max_drawdown = performance_metrics.get('max_drawdown_pct', 0)
            sharpe_ratio = performance_metrics.get('sharpe_ratio', 0)
            
            # Risk level classification
            if max_drawdown > 20 or sharpe_ratio < 0.5:
                risk_level = 'HIGH'
            elif max_drawdown > 10 or sharpe_ratio < 1.0:
                risk_level = 'MEDIUM'
            else:
                risk_level = 'LOW'
            
            return {
                'risk_level': risk_level,
                'portfolio_validation': portfolio_validation.to_dict(),
                'max_drawdown_pct': max_drawdown,
                'sharpe_ratio': sharpe_ratio,
                'total_positions': portfolio_value.get('position_count', 0),
                'unrealized_pnl_pct': portfolio_value.get('unrealized_pnl_pct', 0),
                'recommendations': self._generate_risk_recommendations(
                    risk_level, portfolio_validation, performance_metrics
                ),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating risk report: {e}")
            return {
                'risk_level': 'UNKNOWN',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _generate_risk_recommendations(self, risk_level: str, 
                                     portfolio_validation: ValidationResult,
                                     performance_metrics: Dict[str, Any]) -> List[str]:
        """Generate risk management recommendations"""
        recommendations = []
        
        if risk_level == 'HIGH':
            recommendations.append("🚨 Consider reducing position sizes")
            recommendations.append("🚨 Implement tighter stop losses")
            recommendations.append("🚨 Review and close underperforming positions")
        
        if not portfolio_validation.passed:
            recommendations.extend([f"⚠️ {issue}" for issue in portfolio_validation.issues])
        
        sharpe = performance_metrics.get('sharpe_ratio', 0)
        if sharpe < 1.0:
            recommendations.append("📈 Focus on higher-quality trade setups")
        
        win_rate = performance_metrics.get('win_rate', 0)
        if win_rate < 50:
            recommendations.append("🎯 Review entry criteria - win rate below 50%")
        
        return recommendations