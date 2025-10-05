"""
🔙 Backtesting Engine
Test monthly trading strategies on historical data
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import yfinance as yf

from modules.monthly_signals import MonthlySignals
from modules.database_manager import DatabaseManager
from modules.utils import (
    calculate_sharpe_ratio, calculate_sortino_ratio, 
    calculate_max_drawdown, format_currency, format_percentage
)


class Backtester:
    """Backtest trading strategies on historical data"""
    
    def __init__(self, config: Dict[str, Any], monthly_signals: MonthlySignals, 
                 db_manager: DatabaseManager):
        """
        Initialize backtester
        
        Args:
            config: Configuration dictionary
            monthly_signals: MonthlySignals instance
            db_manager: DatabaseManager instance
        """
        self.config = config.get('backtesting', {})
        self.logger = logging.getLogger(__name__)
        self.monthly_signals = monthly_signals
        self.db = db_manager
        
        # Backtesting parameters
        self.initial_capital = self.config.get('initial_capital', 10000)
        self.commission = self.config.get('commission_pct', 0.0) / 100  # Convert to decimal
        self.slippage = self.config.get('slippage_pct', 0.1) / 100
        self.benchmark = self.config.get('benchmark', 'SPY')
        
        # Trading rules
        self.min_score = self.config.get('min_entry_score', 75)  # Minimum score to enter
        self.max_positions = self.config.get('max_positions', 5)
        self.position_size_pct = self.config.get('position_size_pct', 20)  # % per position
        
        self.logger.info("Backtester initialized")
    
    def run_backtest(self, symbols: List[str], start_date: str, end_date: str,
                     rebalance_frequency: str = 'monthly') -> Dict[str, Any]:
        """
        Run complete backtest
        
        Args:
            symbols: List of stock symbols to test
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            rebalance_frequency: 'monthly', 'weekly', or 'daily'
            
        Returns:
            Backtest results dictionary
        """
        self.logger.info(f"Starting backtest: {symbols} from {start_date} to {end_date}")
        
        try:
            # Initialize backtest state
            capital = self.initial_capital
            positions = {}  # symbol: {shares, entry_price, entry_date, score}
            cash = capital
            
            # Track performance
            portfolio_values = []
            trades = []
            daily_returns = []
            
            # Get date range
            start = pd.to_datetime(start_date)
            end = pd.to_datetime(end_date)
            
            # Generate rebalance dates
            rebalance_dates = self._generate_rebalance_dates(start, end, rebalance_frequency)
            
            self.logger.info(f"Generated {len(rebalance_dates)} rebalance dates")
            
            # Run backtest for each rebalance date
            for i, rebalance_date in enumerate(rebalance_dates):
                self.logger.info(f"Rebalancing {i+1}/{len(rebalance_dates)}: {rebalance_date.date()}")
                
                # Calculate scores for all symbols
                scores = {}
                for symbol in symbols:
                    try:
                        # Fetch historical data up to rebalance date
                        stock_data = self._fetch_historical_data(
                            symbol, 
                            rebalance_date - timedelta(days=365),
                            rebalance_date
                        )
                        
                        if stock_data is None or len(stock_data) < 100:
                            continue
                        
                        # Calculate monthly score (simplified - no news/social for historical)
                        score_data = self.monthly_signals.calculate_monthly_score(
                            stock_data, symbol, news_sentiment=None, social_sentiment=None
                        )
                        
                        if score_data:
                            scores[symbol] = {
                                'score': score_data['total_score'],
                                'recommendation': score_data['recommendation'],
                                'entry_price': stock_data['Close'].iloc[-1],
                                'stop_loss': score_data.get('stop_loss'),
                                'target': score_data.get('target_price')
                            }
                    
                    except Exception as e:
                        self.logger.error(f"Error calculating score for {symbol}: {e}")
                        continue
                
                # Make trading decisions
                trades_this_period = self._rebalance_portfolio(
                    positions, scores, cash, rebalance_date
                )
                trades.extend(trades_this_period)
                
                # Update cash based on trades
                for trade in trades_this_period:
                    if trade['action'] == 'BUY':
                        cost = trade['shares'] * trade['price'] * (1 + self.commission + self.slippage)
                        cash -= cost
                    elif trade['action'] == 'SELL':
                        proceeds = trade['shares'] * trade['price'] * (1 - self.commission - self.slippage)
                        cash += proceeds
                
                # Calculate current portfolio value
                portfolio_value = cash
                for symbol, pos in positions.items():
                    if pos['shares'] > 0:
                        try:
                            current_price = self._get_price_at_date(symbol, rebalance_date)
                            if current_price:
                                portfolio_value += pos['shares'] * current_price
                        except:
                            # Use entry price if can't get current
                            portfolio_value += pos['shares'] * pos['entry_price']
                
                portfolio_values.append({
                    'date': rebalance_date,
                    'value': portfolio_value,
                    'cash': cash,
                    'invested': portfolio_value - cash
                })
                
                # Calculate daily return
                if len(portfolio_values) > 1:
                    prev_value = portfolio_values[-2]['value']
                    daily_return = (portfolio_value - prev_value) / prev_value
                    daily_returns.append(daily_return)
            
            # Calculate final metrics
            results = self._calculate_backtest_metrics(
                portfolio_values, trades, daily_returns, start_date, end_date
            )
            
            # Add benchmark comparison
            benchmark_results = self._get_benchmark_performance(start_date, end_date)
            results['benchmark'] = benchmark_results
            
            self.logger.info("Backtest completed successfully")
            return results
            
        except Exception as e:
            self.logger.error(f"Backtest failed: {e}", exc_info=True)
            return {'error': str(e)}
    
    def _generate_rebalance_dates(self, start: pd.Timestamp, end: pd.Timestamp, 
                                   frequency: str) -> List[pd.Timestamp]:
        """Generate list of rebalance dates"""
        dates = []
        current = start
        
        if frequency == 'monthly':
            while current <= end:
                dates.append(current)
                # Move to next month
                if current.month == 12:
                    current = pd.Timestamp(current.year + 1, 1, 1)
                else:
                    current = pd.Timestamp(current.year, current.month + 1, 1)
        
        elif frequency == 'weekly':
            while current <= end:
                dates.append(current)
                current += timedelta(days=7)
        
        elif frequency == 'daily':
            date_range = pd.date_range(start, end, freq='D')
            dates = [d for d in date_range]
        
        return dates
    
    def _fetch_historical_data(self, symbol: str, start: pd.Timestamp, 
                                end: pd.Timestamp) -> Optional[pd.DataFrame]:
        """Fetch historical stock data"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start.strftime('%Y-%m-%d'), 
                                 end=end.strftime('%Y-%m-%d'))
            
            if data.empty:
                return None
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error fetching data for {symbol}: {e}")
            return None
    
    def _get_price_at_date(self, symbol: str, date: pd.Timestamp) -> Optional[float]:
        """Get stock price at specific date"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=date.strftime('%Y-%m-%d'), 
                                 end=(date + timedelta(days=1)).strftime('%Y-%m-%d'))
            
            if data.empty:
                return None
            
            return data['Close'].iloc[-1]
            
        except Exception as e:
            self.logger.error(f"Error getting price for {symbol} at {date}: {e}")
            return None
    
    def _rebalance_portfolio(self, positions: Dict[str, Dict], scores: Dict[str, Dict],
                            cash: float, date: pd.Timestamp) -> List[Dict[str, Any]]:
        """
        Rebalance portfolio based on scores
        
        Args:
            positions: Current positions dict
            scores: Symbol scores dict
            cash: Available cash
            date: Current date
            
        Returns:
            List of trades executed
        """
        trades = []
        
        # 1. Check exit conditions for existing positions
        symbols_to_exit = []
        for symbol, pos in positions.items():
            if pos['shares'] == 0:
                continue
            
            # Check if score dropped below threshold
            if symbol in scores:
                current_score = scores[symbol]['score']
                if current_score < 40:  # Exit if score drops below 40
                    symbols_to_exit.append(symbol)
            else:
                # No score available, hold position
                pass
        
        # Execute exits
        for symbol in symbols_to_exit:
            pos = positions[symbol]
            exit_price = scores.get(symbol, {}).get('entry_price', pos['entry_price'])
            
            trades.append({
                'date': date,
                'symbol': symbol,
                'action': 'SELL',
                'shares': pos['shares'],
                'price': exit_price,
                'reason': f"Score below threshold: {scores.get(symbol, {}).get('score', 0)}"
            })
            
            positions[symbol]['shares'] = 0
        
        # 2. Find new entry candidates
        entry_candidates = []
        for symbol, score_data in scores.items():
            # Skip if already in position
            if symbol in positions and positions[symbol]['shares'] > 0:
                continue
            
            # Check entry criteria
            if score_data['score'] >= self.min_score:
                entry_candidates.append((symbol, score_data))
        
        # Sort by score (highest first)
        entry_candidates.sort(key=lambda x: x[1]['score'], reverse=True)
        
        # 3. Enter new positions (up to max_positions)
        current_positions = sum(1 for p in positions.values() if p['shares'] > 0)
        available_slots = self.max_positions - current_positions
        
        for symbol, score_data in entry_candidates[:available_slots]:
            # Calculate position size
            position_value = cash * (self.position_size_pct / 100)
            entry_price = score_data['entry_price']
            shares = int(position_value / (entry_price * (1 + self.commission + self.slippage)))
            
            if shares > 0 and shares * entry_price < cash:
                trades.append({
                    'date': date,
                    'symbol': symbol,
                    'action': 'BUY',
                    'shares': shares,
                    'price': entry_price,
                    'score': score_data['score'],
                    'reason': f"Entry signal: {score_data['recommendation']}"
                })
                
                positions[symbol] = {
                    'shares': shares,
                    'entry_price': entry_price,
                    'entry_date': date,
                    'score': score_data['score'],
                    'stop_loss': score_data.get('stop_loss'),
                    'target': score_data.get('target')
                }
        
        return trades
    
    def _calculate_backtest_metrics(self, portfolio_values: List[Dict],
                                     trades: List[Dict], daily_returns: List[float],
                                     start_date: str, end_date: str) -> Dict[str, Any]:
        """Calculate comprehensive backtest metrics"""
        
        if not portfolio_values:
            return {'error': 'No portfolio data'}
        
        # Convert to DataFrame
        df = pd.DataFrame(portfolio_values)
        trades_df = pd.DataFrame(trades) if trades else pd.DataFrame()
        
        # Calculate returns
        total_return = (df['value'].iloc[-1] - self.initial_capital) / self.initial_capital
        total_return_pct = total_return * 100
        
        # Annualized return
        days = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days
        years = days / 365.25
        annualized_return = ((1 + total_return) ** (1 / years) - 1) * 100 if years > 0 else 0
        
        # Volatility (annualized)
        if daily_returns:
            volatility = np.std(daily_returns) * np.sqrt(252) * 100
        else:
            volatility = 0
        
        # Sharpe ratio
        returns_series = pd.Series(daily_returns)
        sharpe = calculate_sharpe_ratio(returns_series) if len(returns_series) > 1 else 0
        
        # Sortino ratio
        downside_returns = returns_series[returns_series < 0]
        if len(downside_returns) > 1:
            downside_std = downside_returns.std()
            sortino = (returns_series.mean() * 252) / (downside_std * np.sqrt(252)) if downside_std > 0 else 0
        else:
            sortino = 0
        
        # Maximum drawdown
        cumulative = (1 + returns_series).cumprod()
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min() * 100 if len(drawdown) > 0 else 0
        
        # Calmar ratio
        calmar = annualized_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        # Trade statistics
        if not trades_df.empty:
            total_trades = len(trades_df)
            buy_trades = len(trades_df[trades_df['action'] == 'BUY'])
            sell_trades = len(trades_df[trades_df['action'] == 'SELL'])
            
            # Win rate (need to match buys with sells)
            winning_trades = 0
            losing_trades = 0
            
            # Group by symbol and calculate P&L
            symbols_traded = trades_df['symbol'].unique()
            for symbol in symbols_traded:
                symbol_trades = trades_df[trades_df['symbol'] == symbol].sort_values('date')
                buys = symbol_trades[symbol_trades['action'] == 'BUY']
                sells = symbol_trades[symbol_trades['action'] == 'SELL']
                
                # Match buys with sells (simplified)
                for i in range(min(len(buys), len(sells))):
                    buy_price = buys.iloc[i]['price']
                    sell_price = sells.iloc[i]['price']
                    if sell_price > buy_price:
                        winning_trades += 1
                    else:
                        losing_trades += 1
            
            win_rate = (winning_trades / (winning_trades + losing_trades) * 100) if (winning_trades + losing_trades) > 0 else 0
        else:
            total_trades = buy_trades = sell_trades = 0
            win_rate = 0
        
        # Exposure (% of time invested)
        avg_invested = df['invested'].mean()
        avg_exposure = (avg_invested / df['value'].mean()) * 100 if df['value'].mean() > 0 else 0
        
        return {
            'period': {
                'start_date': start_date,
                'end_date': end_date,
                'days': days,
                'years': round(years, 2)
            },
            'returns': {
                'total_return_pct': round(total_return_pct, 2),
                'annualized_return_pct': round(annualized_return, 2),
                'initial_capital': self.initial_capital,
                'final_value': round(df['value'].iloc[-1], 2),
                'profit_loss': round(df['value'].iloc[-1] - self.initial_capital, 2)
            },
            'risk': {
                'volatility_pct': round(volatility, 2),
                'max_drawdown_pct': round(max_drawdown, 2),
                'sharpe_ratio': round(sharpe, 2),
                'sortino_ratio': round(sortino, 2),
                'calmar_ratio': round(calmar, 2)
            },
            'trades': {
                'total_trades': total_trades,
                'buy_trades': buy_trades,
                'sell_trades': sell_trades,
                'win_rate_pct': round(win_rate, 2)
            },
            'exposure': {
                'avg_exposure_pct': round(avg_exposure, 2),
                'avg_cash': round(df['cash'].mean(), 2),
                'avg_invested': round(avg_invested, 2)
            },
            'portfolio_values': df.to_dict('records'),
            'trades_log': trades_df.to_dict('records') if not trades_df.empty else []
        }
    
    def _get_benchmark_performance(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get benchmark (e.g., SPY) performance for comparison"""
        try:
            ticker = yf.Ticker(self.benchmark)
            data = ticker.history(start=start_date, end=end_date)
            
            if data.empty:
                return {'error': f'No data for benchmark {self.benchmark}'}
            
            # Calculate benchmark returns
            initial_price = data['Close'].iloc[0]
            final_price = data['Close'].iloc[-1]
            total_return = ((final_price - initial_price) / initial_price) * 100
            
            # Annualized return
            days = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days
            years = days / 365.25
            annualized_return = ((final_price / initial_price) ** (1 / years) - 1) * 100 if years > 0 else 0
            
            # Daily returns
            daily_returns = data['Close'].pct_change().dropna()
            volatility = daily_returns.std() * np.sqrt(252) * 100
            
            # Sharpe ratio
            sharpe = calculate_sharpe_ratio(daily_returns)
            
            # Max drawdown
            cumulative = (1 + daily_returns).cumprod()
            running_max = cumulative.cummax()
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = drawdown.min() * 100
            
            return {
                'symbol': self.benchmark,
                'total_return_pct': round(total_return, 2),
                'annualized_return_pct': round(annualized_return, 2),
                'volatility_pct': round(volatility, 2),
                'sharpe_ratio': round(sharpe, 2),
                'max_drawdown_pct': round(max_drawdown, 2),
                'initial_price': round(initial_price, 2),
                'final_price': round(final_price, 2)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating benchmark performance: {e}")
            return {'error': str(e)}
    
    def generate_backtest_report(self, results: Dict[str, Any]) -> str:
        """
        Generate formatted backtest report
        
        Args:
            results: Backtest results dictionary
            
        Returns:
            Formatted report string
        """
        if 'error' in results:
            return f"❌ Backtest Error: {results['error']}"
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║                    📊 BACKTEST REPORT                        ║
╠══════════════════════════════════════════════════════════════╣
║ Period: {results['period']['start_date']} to {results['period']['end_date']}
║ Duration: {results['period']['days']} days ({results['period']['years']} years)
╠══════════════════════════════════════════════════════════════╣
║                     💰 RETURNS                               ║
╠══════════════════════════════════════════════════════════════╣
║ Initial Capital:    {format_currency(results['returns']['initial_capital'])}
║ Final Value:        {format_currency(results['returns']['final_value'])}
║ Profit/Loss:        {format_currency(results['returns']['profit_loss'])}
║ Total Return:       {format_percentage(results['returns']['total_return_pct'])}
║ Annualized Return:  {format_percentage(results['returns']['annualized_return_pct'])}
╠══════════════════════════════════════════════════════════════╣
║                     ⚠️  RISK METRICS                         ║
╠══════════════════════════════════════════════════════════════╣
║ Volatility:         {format_percentage(results['risk']['volatility_pct'])}
║ Max Drawdown:       {format_percentage(results['risk']['max_drawdown_pct'])}
║ Sharpe Ratio:       {results['risk']['sharpe_ratio']:.2f}
║ Sortino Ratio:      {results['risk']['sortino_ratio']:.2f}
║ Calmar Ratio:       {results['risk']['calmar_ratio']:.2f}
╠══════════════════════════════════════════════════════════════╣
║                     📈 TRADING ACTIVITY                      ║
╠══════════════════════════════════════════════════════════════╣
║ Total Trades:       {results['trades']['total_trades']}
║ Buy Trades:         {results['trades']['buy_trades']}
║ Sell Trades:        {results['trades']['sell_trades']}
║ Win Rate:           {format_percentage(results['trades']['win_rate_pct'])}
╠══════════════════════════════════════════════════════════════╣
║                     💼 PORTFOLIO EXPOSURE                    ║
╠══════════════════════════════════════════════════════════════╣
║ Avg Exposure:       {format_percentage(results['exposure']['avg_exposure_pct'])}
║ Avg Cash:           {format_currency(results['exposure']['avg_cash'])}
║ Avg Invested:       {format_currency(results['exposure']['avg_invested'])}
╠══════════════════════════════════════════════════════════════╣
║                     📊 BENCHMARK COMPARISON                  ║
╠══════════════════════════════════════════════════════════════╣
"""
        
        if 'benchmark' in results and 'error' not in results['benchmark']:
            bm = results['benchmark']
            strategy_return = results['returns']['annualized_return_pct']
            benchmark_return = bm['annualized_return_pct']
            alpha = strategy_return - benchmark_return
            
            report += f"""║ Benchmark ({bm['symbol']}):
║   Return:           {format_percentage(bm['total_return_pct'])}
║   Annualized:       {format_percentage(bm['annualized_return_pct'])}
║   Volatility:       {format_percentage(bm['volatility_pct'])}
║   Sharpe:           {bm['sharpe_ratio']:.2f}
║   Max Drawdown:     {format_percentage(bm['max_drawdown_pct'])}
║
║ Strategy vs Benchmark:
║   Alpha:            {format_percentage(alpha)}
║   Outperformance:   {"✅ YES" if alpha > 0 else "❌ NO"}
"""
        
        report += "╚══════════════════════════════════════════════════════════════╝\n"
        
        return report
