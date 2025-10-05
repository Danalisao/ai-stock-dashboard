"""
💼 Portfolio Tracker
Track trading positions, calculate P&L, and measure performance
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from modules.database_manager import DatabaseManager


class PortfolioTracker:
    """Track portfolio positions and performance"""
    
    def __init__(self, config: Dict[str, Any], db_manager: DatabaseManager):
        """
        Initialize portfolio tracker
        
        Args:
            config: Configuration dictionary
            db_manager: Database manager instance
        """
        self.config = config.get('portfolio', {})
        self.logger = logging.getLogger(__name__)
        self.db = db_manager
        
        # Portfolio settings
        self.initial_capital = self.config.get('initial_capital', 10000)
        self.position_size_pct = self.config.get('position_size_pct', 5)
        self.risk_per_trade_pct = self.config.get('risk_per_trade_pct', 2)
        self.max_positions = self.config.get('max_positions', 10)
    
    def get_portfolio_value(self, current_prices: Dict[str, float]) -> Dict[str, Any]:
        """
        Calculate current portfolio value
        
        Args:
            current_prices: Dictionary of symbol: current_price
            
        Returns:
            Portfolio value breakdown
        """
        try:
            # Get open positions
            positions = self.db.get_open_positions()
            
            if not positions:
                return {
                    'total_value': self.initial_capital,
                    'cash': self.initial_capital,
                    'invested': 0.0,
                    'unrealized_pnl': 0.0,
                    'unrealized_pnl_pct': 0.0,
                    'positions': []
                }
            
            # Calculate position values
            total_invested = 0.0
            total_current_value = 0.0
            position_details = []
            
            for pos in positions:
                symbol = pos['symbol']
                entry_price = pos['entry_price']
                shares = pos['shares']
                entry_value = entry_price * shares
                
                # Get current price
                current_price = current_prices.get(symbol, entry_price)
                current_value = current_price * shares
                
                # Calculate P&L
                pnl = current_value - entry_value
                pnl_pct = (pnl / entry_value) * 100 if entry_value > 0 else 0.0
                
                total_invested += entry_value
                total_current_value += current_value
                
                position_details.append({
                    'symbol': symbol,
                    'shares': shares,
                    'entry_price': entry_price,
                    'current_price': current_price,
                    'entry_value': entry_value,
                    'current_value': current_value,
                    'unrealized_pnl': pnl,
                    'unrealized_pnl_pct': pnl_pct,
                    'entry_date': pos['entry_date'],
                    'days_held': (datetime.now().date() - datetime.fromisoformat(pos['entry_date']).date()).days
                })
            
            # Calculate totals
            unrealized_pnl = total_current_value - total_invested
            unrealized_pnl_pct = (unrealized_pnl / total_invested) * 100 if total_invested > 0 else 0.0
            
            # Cash (assuming we started with initial capital)
            cash = self.initial_capital - total_invested + self._get_realized_pnl()
            total_value = cash + total_current_value
            
            return {
                'total_value': round(total_value, 2),
                'cash': round(cash, 2),
                'invested': round(total_invested, 2),
                'current_value': round(total_current_value, 2),
                'unrealized_pnl': round(unrealized_pnl, 2),
                'unrealized_pnl_pct': round(unrealized_pnl_pct, 2),
                'positions': position_details,
                'position_count': len(positions)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating portfolio value: {e}")
            return {}
    
    def _get_realized_pnl(self) -> float:
        """Calculate total realized P&L from closed trades"""
        try:
            closed_trades = self.db.get_closed_trades()
            total_pnl = sum(trade['pnl'] for trade in closed_trades)
            return total_pnl
        except Exception as e:
            self.logger.error(f"Error getting realized P&L: {e}")
            return 0.0
    
    def calculate_performance_metrics(self, benchmark_returns: Optional[pd.Series] = None) -> Dict[str, Any]:
        """
        Calculate comprehensive performance metrics
        
        Args:
            benchmark_returns: Optional benchmark returns (e.g., SPY) for comparison
            
        Returns:
            Dictionary of performance metrics
        """
        try:
            closed_trades = self.db.get_closed_trades()
            
            if not closed_trades:
                return self._get_empty_metrics()
            
            # Convert to DataFrame
            df = pd.DataFrame(closed_trades)
            
            # Basic metrics
            total_trades = len(df)
            winning_trades = len(df[df['pnl'] > 0])
            losing_trades = len(df[df['pnl'] < 0])
            win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0.0
            
            # P&L metrics
            total_pnl = df['pnl'].sum()
            avg_pnl = df['pnl'].mean()
            best_trade = df['pnl'].max()
            worst_trade = df['pnl'].min()
            
            avg_win = df[df['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0.0
            avg_loss = df[df['pnl'] < 0]['pnl'].mean() if losing_trades > 0 else 0.0
            
            # Profit factor
            gross_profit = df[df['pnl'] > 0]['pnl'].sum()
            gross_loss = abs(df[df['pnl'] < 0]['pnl'].sum())
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
            
            # Expectancy
            expectancy = (win_rate / 100 * avg_win) - ((1 - win_rate / 100) * abs(avg_loss))
            
            # Returns
            returns = df['pnl_pct'] / 100  # Convert to decimal
            
            # Sharpe ratio (assuming daily returns)
            if len(returns) > 1:
                sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0.0
            else:
                sharpe_ratio = 0.0
            
            # Sortino ratio (downside deviation)
            downside_returns = returns[returns < 0]
            if len(downside_returns) > 1:
                downside_std = downside_returns.std()
                sortino_ratio = (returns.mean() / downside_std) * np.sqrt(252) if downside_std > 0 else 0.0
            else:
                sortino_ratio = 0.0
            
            # Calmar ratio (return / max drawdown)
            cumulative_returns = (1 + returns).cumprod()
            running_max = cumulative_returns.cummax()
            drawdown = (cumulative_returns - running_max) / running_max
            max_drawdown = drawdown.min() * 100
            
            total_return = ((self.initial_capital + total_pnl) / self.initial_capital - 1) * 100
            calmar_ratio = total_return / abs(max_drawdown) if max_drawdown != 0 else 0.0
            
            # Consecutive wins/losses
            df['win'] = df['pnl'] > 0
            consecutive_wins = self._max_consecutive(df['win'].tolist(), True)
            consecutive_losses = self._max_consecutive(df['win'].tolist(), False)
            
            # Average hold time
            avg_hold_days = df['hold_days'].mean() if 'hold_days' in df.columns else 0
            
            return {
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': round(win_rate, 2),
                'total_pnl': round(total_pnl, 2),
                'total_return_pct': round(total_return, 2),
                'average_pnl': round(avg_pnl, 2),
                'best_trade': round(best_trade, 2),
                'worst_trade': round(worst_trade, 2),
                'average_win': round(avg_win, 2),
                'average_loss': round(avg_loss, 2),
                'profit_factor': round(profit_factor, 2),
                'expectancy': round(expectancy, 2),
                'sharpe_ratio': round(sharpe_ratio, 2),
                'sortino_ratio': round(sortino_ratio, 2),
                'calmar_ratio': round(calmar_ratio, 2),
                'max_drawdown_pct': round(max_drawdown, 2),
                'consecutive_wins': consecutive_wins,
                'consecutive_losses': consecutive_losses,
                'avg_hold_days': round(avg_hold_days, 1)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating performance metrics: {e}")
            return self._get_empty_metrics()
    
    def _max_consecutive(self, values: List[bool], target: bool) -> int:
        """Calculate maximum consecutive occurrences"""
        max_count = 0
        current_count = 0
        
        for val in values:
            if val == target:
                current_count += 1
                max_count = max(max_count, current_count)
            else:
                current_count = 0
        
        return max_count
    
    def _get_empty_metrics(self) -> Dict[str, Any]:
        """Return empty metrics structure"""
        return {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0.0,
            'total_pnl': 0.0,
            'total_return_pct': 0.0,
            'average_pnl': 0.0,
            'best_trade': 0.0,
            'worst_trade': 0.0,
            'average_win': 0.0,
            'average_loss': 0.0,
            'profit_factor': 0.0,
            'expectancy': 0.0,
            'sharpe_ratio': 0.0,
            'sortino_ratio': 0.0,
            'calmar_ratio': 0.0,
            'max_drawdown_pct': 0.0,
            'consecutive_wins': 0,
            'consecutive_losses': 0,
            'avg_hold_days': 0.0
        }
    
    def calculate_position_size(self, symbol: str, entry_price: float, 
                                 stop_loss: float, account_value: float) -> int:
        """
        Calculate position size based on risk management rules
        
        Args:
            symbol: Stock symbol
            entry_price: Entry price
            stop_loss: Stop loss price
            account_value: Current account value
            
        Returns:
            Number of shares to buy
        """
        try:
            # Risk amount (e.g., 2% of account)
            risk_amount = account_value * (self.risk_per_trade_pct / 100)
            
            # Risk per share
            risk_per_share = abs(entry_price - stop_loss)
            
            if risk_per_share == 0:
                return 0
            
            # Calculate shares based on risk
            shares_by_risk = int(risk_amount / risk_per_share)
            
            # Also check position size limit (e.g., 5% of account)
            max_position_value = account_value * (self.position_size_pct / 100)
            shares_by_size = int(max_position_value / entry_price)
            
            # Use the more conservative (smaller) value
            shares = min(shares_by_risk, shares_by_size)
            
            # Ensure at least 1 share if affordable
            if shares == 0 and entry_price < account_value:
                shares = 1
            
            self.logger.info(f"Position size for {symbol}: {shares} shares @ ${entry_price}")
            return shares
            
        except Exception as e:
            self.logger.error(f"Error calculating position size: {e}")
            return 0
    
    def check_risk_limits(self, current_prices: Dict[str, float]) -> Dict[str, Any]:
        """
        Check if portfolio is within risk limits
        
        Args:
            current_prices: Current prices for all positions
            
        Returns:
            Risk analysis dictionary
        """
        try:
            portfolio = self.get_portfolio_value(current_prices)
            
            # Check position count
            position_count = portfolio['position_count']
            position_limit_ok = position_count <= self.max_positions
            
            # Check total exposure
            total_value = portfolio['total_value']
            invested = portfolio['invested']
            exposure_pct = (invested / total_value) * 100 if total_value > 0 else 0.0
            
            # Typical limit: 80-100% invested
            exposure_ok = exposure_pct <= 100
            
            # Check individual position sizes
            oversized_positions = []
            for pos in portfolio['positions']:
                position_pct = (pos['current_value'] / total_value) * 100
                if position_pct > self.position_size_pct * 2:  # 2x normal size
                    oversized_positions.append({
                        'symbol': pos['symbol'],
                        'size_pct': round(position_pct, 2),
                        'limit': self.position_size_pct * 2
                    })
            
            # Check unrealized losses
            unrealized_pnl_pct = portfolio['unrealized_pnl_pct']
            drawdown_ok = unrealized_pnl_pct > -20  # Don't let unrealized losses exceed 20%
            
            all_ok = position_limit_ok and exposure_ok and len(oversized_positions) == 0 and drawdown_ok
            
            return {
                'all_checks_passed': all_ok,
                'position_count': position_count,
                'max_positions': self.max_positions,
                'position_limit_ok': position_limit_ok,
                'exposure_pct': round(exposure_pct, 2),
                'exposure_ok': exposure_ok,
                'oversized_positions': oversized_positions,
                'unrealized_pnl_pct': round(unrealized_pnl_pct, 2),
                'drawdown_ok': drawdown_ok,
                'warnings': self._generate_risk_warnings(
                    position_limit_ok, exposure_ok, oversized_positions, drawdown_ok
                )
            }
            
        except Exception as e:
            self.logger.error(f"Error checking risk limits: {e}")
            return {'all_checks_passed': False, 'error': str(e)}
    
    def _generate_risk_warnings(self, position_limit_ok: bool, exposure_ok: bool,
                                oversized_positions: List[Dict], drawdown_ok: bool) -> List[str]:
        """Generate risk warning messages"""
        warnings = []
        
        if not position_limit_ok:
            warnings.append(f"⚠️ Too many positions (limit: {self.max_positions})")
        
        if not exposure_ok:
            warnings.append("⚠️ Over-invested (>100% of capital)")
        
        if oversized_positions:
            for pos in oversized_positions:
                warnings.append(f"⚠️ {pos['symbol']} position too large ({pos['size_pct']:.1f}%)")
        
        if not drawdown_ok:
            warnings.append("⚠️ Large unrealized losses (>20%) - consider reducing risk")
        
        return warnings
    
    def get_portfolio_summary(self, current_prices: Dict[str, float]) -> str:
        """
        Get formatted portfolio summary
        
        Args:
            current_prices: Current prices
            
        Returns:
            Formatted summary string
        """
        portfolio = self.get_portfolio_value(current_prices)
        metrics = self.calculate_performance_metrics()
        
        summary = f"""
╔══════════════════════════════════════════════════════════════╗
║                    💼 PORTFOLIO SUMMARY                      ║
╠══════════════════════════════════════════════════════════════╣
║ Total Value:        ${portfolio['total_value']:>12,.2f}             ║
║ Cash:               ${portfolio['cash']:>12,.2f}             ║
║ Invested:           ${portfolio['invested']:>12,.2f}             ║
║ Unrealized P&L:     ${portfolio['unrealized_pnl']:>12,.2f} ({portfolio['unrealized_pnl_pct']:>6.2f}%)  ║
║ Open Positions:     {portfolio['position_count']:>3}                                    ║
╠══════════════════════════════════════════════════════════════╣
║                   📊 PERFORMANCE METRICS                     ║
╠══════════════════════════════════════════════════════════════╣
║ Total Trades:       {metrics['total_trades']:>3}                                    ║
║ Win Rate:           {metrics['win_rate']:>6.2f}%                               ║
║ Total Return:       {metrics['total_return_pct']:>6.2f}%                               ║
║ Sharpe Ratio:       {metrics['sharpe_ratio']:>6.2f}                                  ║
║ Max Drawdown:       {metrics['max_drawdown_pct']:>6.2f}%                               ║
║ Profit Factor:      {metrics['profit_factor']:>6.2f}                                  ║
╚══════════════════════════════════════════════════════════════╝
"""
        return summary
    
    def get_trade_history_dataframe(self) -> pd.DataFrame:
        """
        Get trade history as pandas DataFrame
        
        Returns:
            DataFrame with trade history
        """
        try:
            trades = self.db.get_closed_trades()
            
            if not trades:
                return pd.DataFrame()
            
            df = pd.DataFrame(trades)
            
            # Convert dates
            df['entry_date'] = pd.to_datetime(df['entry_date'])
            df['exit_date'] = pd.to_datetime(df['exit_date'])
            
            # Sort by exit date
            df = df.sort_values('exit_date', ascending=False)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error getting trade history: {e}")
            return pd.DataFrame()
    
    def export_to_csv(self, filename: str) -> bool:
        """
        Export trade history to CSV
        
        Args:
            filename: Output filename
            
        Returns:
            True if successful
        """
        try:
            df = self.get_trade_history_dataframe()
            
            if df.empty:
                self.logger.warning("No trades to export")
                return False
            
            df.to_csv(filename, index=False)
            self.logger.info(f"Trade history exported to {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting to CSV: {e}")
            return False
