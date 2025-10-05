"""
🗄️ Database Manager
SQLite database operations for stock data, news, alerts, and portfolio
"""

import sqlite3
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import pandas as pd
import os


class DatabaseManager:
    """Manage SQLite database operations"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize database manager
        
        Args:
            config: Configuration dictionary with database settings
        """
        self.logger = logging.getLogger(__name__)
        
        # Get database path from config
        if isinstance(config, str):
            self.db_path = config
        elif isinstance(config, dict):
            self.db_path = config.get('path', './data/stock_data.db')
        else:
            self.db_path = './data/stock_data.db'

        # Connection management (needed for in-memory databases)
        self._shared_connection: Optional[sqlite3.Connection] = None
        self._use_shared_connection = False

        # Detect in-memory database usage and keep a persistent connection alive
        if isinstance(self.db_path, str) and (self.db_path == ':memory:' or self.db_path.startswith('file::memory')):
            self._use_shared_connection = True
            try:
                if self.db_path == ':memory:':
                    self._shared_connection = sqlite3.connect(':memory:', check_same_thread=False)
                else:
                    self._shared_connection = sqlite3.connect(self.db_path, uri=True, check_same_thread=False)
                self._shared_connection.row_factory = sqlite3.Row
            except Exception as e:
                self.logger.error(f"Error initializing shared SQLite connection: {e}")
                raise

        # Ensure data directory exists (skip for pure in-memory databases)
        if self.db_path != ':memory:' and not self.db_path.startswith('file::memory'):
            os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else './data', exist_ok=True)

        # Initialize database tables
        self._initialize_database()

    def __del__(self):
        """Ensure shared connections are properly closed when the manager is garbage-collected"""
        if self._use_shared_connection and self._shared_connection:
            try:
                self._shared_connection.close()
            except Exception:
                pass
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        if self._use_shared_connection:
            return self._shared_connection

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn

    def _close_connection(self, conn: sqlite3.Connection):
        """Close connection unless using a shared in-memory database"""
        if self._use_shared_connection:
            return
        conn.close()
    
    def _initialize_database(self):
        """Create database tables if they don't exist"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Stock prices cache
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_prices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    date TEXT NOT NULL,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume INTEGER,
                    adj_close REAL,
                    fetched_at TEXT,
                    UNIQUE(symbol, date)
                )
            ''')
            
            # News articles
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS news_articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    url TEXT UNIQUE,
                    source TEXT,
                    published_date TEXT,
                    sentiment_score REAL,
                    sentiment_label TEXT,
                    fetched_at TEXT
                )
            ''')
            
            # Social media mentions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS social_mentions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    platform TEXT,
                    content TEXT,
                    author TEXT,
                    url TEXT,
                    posted_date TEXT,
                    score INTEGER,
                    sentiment_score REAL,
                    fetched_at TEXT
                )
            ''')
            
            # Monthly scores
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS monthly_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    date TEXT NOT NULL,
                    total_score REAL,
                    trend_score REAL,
                    momentum_score REAL,
                    sentiment_score REAL,
                    divergence_score REAL,
                    volume_score REAL,
                    recommendation TEXT,
                    entry_price REAL,
                    stop_loss REAL,
                    target_price REAL,
                    UNIQUE(symbol, date)
                )
            ''')
            
            # Alerts log
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    alert_type TEXT,
                    priority TEXT,
                    message TEXT,
                    value REAL,
                    created_at TEXT,
                    sent_channels TEXT,
                    acknowledged BOOLEAN DEFAULT 0,
                    acknowledged_at TEXT
                )
            ''')
            
            # Watchlist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS watchlist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT UNIQUE NOT NULL,
                    company_name TEXT,
                    sector TEXT,
                    added_at TEXT,
                    notes TEXT
                )
            ''')
            
            # Portfolio positions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS positions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    entry_date TEXT,
                    entry_price REAL,
                    shares INTEGER,
                    position_value REAL,
                    stop_loss REAL,
                    target_price REAL,
                    status TEXT DEFAULT 'open',
                    notes TEXT
                )
            ''')
            
            # Closed trades
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS closed_trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    entry_date TEXT,
                    entry_price REAL,
                    exit_date TEXT,
                    exit_price REAL,
                    shares INTEGER,
                    pnl REAL,
                    pnl_pct REAL,
                    hold_days INTEGER,
                    strategy TEXT,
                    notes TEXT
                )
            ''')
            
            # User settings
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TEXT
                )
            ''')
            
            # Create indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_news_symbol ON news_articles(symbol)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_news_date ON news_articles(published_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_scores_symbol ON monthly_scores(symbol)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_scores_date ON monthly_scores(date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_symbol ON alerts(symbol)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_date ON alerts(created_at)')
            
            conn.commit()
            self._close_connection(conn)
            
            self.logger.info(f"Database initialized successfully: {self.db_path}")
            
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
            raise
    
    # ==================== Stock Prices ====================
    
    def save_stock_prices(self, symbol: str, df: pd.DataFrame) -> bool:
        """
        Save stock price data to database
        
        Args:
            symbol: Stock symbol
            df: DataFrame with OHLCV data
            
        Returns:
            True if successful
        """
        try:
            conn = self._get_connection()
            
            # Prepare data
            df_copy = df.copy()
            df_copy['symbol'] = symbol
            df_copy['date'] = df_copy.index.strftime('%Y-%m-%d')
            df_copy['fetched_at'] = datetime.now().isoformat()
            
            # Rename columns to match database schema
            df_copy.rename(columns={
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume',
                'Adj Close': 'adj_close'
            }, inplace=True)
            
            # Insert or replace
            df_copy.to_sql('stock_prices', conn, if_exists='append', index=False)
            
            conn.commit()
            self._close_connection(conn)
            
            self.logger.info(f"Saved {len(df_copy)} price records for {symbol}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving stock prices for {symbol}: {e}")
            return False
    
    def get_stock_prices(self, symbol: str, start_date: Optional[str] = None, 
                         end_date: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        Retrieve stock price data from database
        
        Args:
            symbol: Stock symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            DataFrame with price data or None
        """
        try:
            conn = self._get_connection()
            
            query = "SELECT * FROM stock_prices WHERE symbol = ?"
            params = [symbol]
            
            if start_date:
                query += " AND date >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND date <= ?"
                params.append(end_date)
            
            query += " ORDER BY date ASC"
            
            df = pd.read_sql_query(query, conn, params=params)
            self._close_connection(conn)
            
            if df.empty:
                return None
            
            # Set date as index
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error retrieving stock prices for {symbol}: {e}")
            return None
    
    # ==================== News Articles ====================
    
    def save_news_article(self, symbol: str, article: Dict[str, Any]) -> bool:
        """
        Save news article to database
        
        Args:
            symbol: Stock symbol
            article: Article dictionary with title, url, etc.
            
        Returns:
            True if successful
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO news_articles 
                (symbol, title, description, url, source, published_date, 
                 sentiment_score, sentiment_label, fetched_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                symbol,
                article.get('title'),
                article.get('description'),
                article.get('url'),
                article.get('source'),
                article.get('published_date'),
                article.get('sentiment_score'),
                article.get('sentiment_label'),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            self._close_connection(conn)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving news article: {e}")
            return False
    
    def get_recent_news(self, symbol: str, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get recent news articles for a symbol
        
        Args:
            symbol: Stock symbol
            days: Number of days to look back
            
        Returns:
            List of article dictionaries
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cutoff_date = (datetime.now() - pd.Timedelta(days=days)).isoformat()
            
            cursor.execute('''
                SELECT * FROM news_articles 
                WHERE symbol = ? AND published_date >= ?
                ORDER BY published_date DESC
            ''', (symbol, cutoff_date))
            
            rows = cursor.fetchall()
            self._close_connection(conn)
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            self.logger.error(f"Error retrieving news for {symbol}: {e}")
            return []
    
    # ==================== Monthly Scores ====================
    
    def save_monthly_score(self, symbol: str, score: float = None, recommendation: str = None,
                           components: Dict[str, Any] = None, entry_price: float = None,
                           stop_loss: float = None, target_price: float = None,
                           risk_reward: float = None, score_data: Dict[str, Any] = None) -> bool:
        """
        Save monthly trading score
        
        Args:
            symbol: Stock symbol
            score_data: Dictionary with score components
            
        Returns:
            True if successful
        """
        try:
            # Support both old and new API
            if score_data is None:
                score_data = {
                    'total_score': score,
                    'recommendation': recommendation,
                    'entry_price': entry_price,
                    'stop_loss': stop_loss,
                    'target_price': target_price
                }
                if components:
                    score_data.update(components)
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Extract recommendation if it's a dict
            rec = score_data.get('recommendation')
            if isinstance(rec, dict):
                rec = rec.get('action', str(rec))
            
            cursor.execute('''
                INSERT OR REPLACE INTO monthly_scores
                (symbol, date, total_score, trend_score, momentum_score, 
                 sentiment_score, divergence_score, volume_score, recommendation,
                 entry_price, stop_loss, target_price)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                symbol,
                datetime.now().date().isoformat(),
                score_data.get('total_score'),
                score_data.get('trend_score'),
                score_data.get('momentum_score'),
                score_data.get('sentiment_score'),
                score_data.get('divergence_score'),
                score_data.get('volume_score'),
                rec,
                score_data.get('entry_price'),
                score_data.get('stop_loss'),
                score_data.get('target_price')
            ))
            
            conn.commit()
            self._close_connection(conn)
            
            self.logger.info(f"Saved monthly score for {symbol}: {score_data.get('total_score')}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving monthly score for {symbol}: {e}")
            return False
    
    def get_latest_score(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get latest monthly score for a symbol
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Score dictionary or None
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM monthly_scores 
                WHERE symbol = ? 
                ORDER BY date DESC 
                LIMIT 1
            ''', (symbol,))
            
            row = cursor.fetchone()
            self._close_connection(conn)
            
            return dict(row) if row else None
            
        except Exception as e:
            self.logger.error(f"Error retrieving latest score for {symbol}: {e}")
            return None
    
    def get_monthly_score_history(self, symbol: str, days: int = 90) -> List[Dict[str, Any]]:
        """
        Get historical monthly scores for a symbol
        
        Args:
            symbol: Stock symbol
            days: Number of days to look back (default: 90)
            
        Returns:
            List of score dictionaries ordered by date (newest first)
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM monthly_scores 
                WHERE symbol = ? 
                AND date >= date('now', '-' || ? || ' days')
                ORDER BY date DESC
            ''', (symbol, days))
            
            rows = cursor.fetchall()
            self._close_connection(conn)
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            self.logger.error(f"Error retrieving score history for {symbol}: {e}")
            return []
    
    # ==================== Alerts ====================
    
    def log_alert(self, symbol: str, alert_type: str, priority: str, 
                   message: str, value: Optional[float] = None) -> bool:
        """
        Log an alert to database
        
        Args:
            symbol: Stock symbol
            alert_type: Type of alert
            priority: Priority level (CRITICAL, HIGH, MEDIUM, LOW)
            message: Alert message
            value: Optional numeric value
            
        Returns:
            True if successful
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO alerts 
                (symbol, alert_type, priority, message, value, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                symbol,
                alert_type,
                priority,
                message,
                value,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            self._close_connection(conn)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error logging alert: {e}")
            return False
    
    def get_active_alerts(self, acknowledged: bool = False) -> List[Dict[str, Any]]:
        """
        Get active alerts
        
        Args:
            acknowledged: Include acknowledged alerts
            
        Returns:
            List of alert dictionaries
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if acknowledged:
                query = "SELECT * FROM alerts ORDER BY created_at DESC LIMIT 100"
            else:
                query = "SELECT * FROM alerts WHERE acknowledged = 0 ORDER BY created_at DESC"
            
            cursor.execute(query)
            rows = cursor.fetchall()
            self._close_connection(conn)
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            self.logger.error(f"Error retrieving alerts: {e}")
            return []
    
    # ==================== Watchlist ====================
    
    def add_to_watchlist(self, symbol: str, company_name: Optional[str] = None,
                         sector: Optional[str] = None, notes: Optional[str] = None) -> bool:
        """
        Add stock to watchlist
        
        Args:
            symbol: Stock symbol
            company_name: Company name
            sector: Sector
            notes: Optional notes
            
        Returns:
            True if successful
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO watchlist 
                (symbol, company_name, sector, added_at, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                symbol,
                company_name,
                sector,
                datetime.now().isoformat(),
                notes
            ))
            
            conn.commit()
            self._close_connection(conn)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding {symbol} to watchlist: {e}")
            return False
    
    def get_watchlist(self) -> List[Dict[str, Any]]:
        """
        Get watchlist stocks
        
        Returns:
            List of stock dictionaries
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM watchlist ORDER BY symbol ASC")
            rows = cursor.fetchall()
            self._close_connection(conn)
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            self.logger.error(f"Error retrieving watchlist: {e}")
            return []
    
    def remove_from_watchlist(self, symbol: str) -> bool:
        """
        Remove stock from watchlist
        
        Args:
            symbol: Stock symbol
            
        Returns:
            True if successful
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM watchlist WHERE symbol = ?", (symbol,))
            
            conn.commit()
            self._close_connection(conn)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing {symbol} from watchlist: {e}")
            return False
    
    # ==================== Portfolio ====================
    
    def open_position(self, symbol: str, entry_price: float, shares: int,
                      stop_loss: Optional[float] = None, 
                      target_price: Optional[float] = None,
                      notes: Optional[str] = None) -> bool:
        """
        Open a new trading position
        
        Args:
            symbol: Stock symbol
            entry_price: Entry price
            shares: Number of shares
            stop_loss: Stop loss price
            target_price: Target price
            notes: Optional notes
            
        Returns:
            True if successful
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            position_value = entry_price * shares
            
            cursor.execute('''
                INSERT INTO positions 
                (symbol, entry_date, entry_price, shares, position_value, 
                 stop_loss, target_price, status, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'open', ?)
            ''', (
                symbol,
                datetime.now().date().isoformat(),
                entry_price,
                shares,
                position_value,
                stop_loss,
                target_price,
                notes
            ))
            
            conn.commit()
            self._close_connection(conn)
            
            self.logger.info(f"Opened position: {symbol} x{shares} @ ${entry_price}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error opening position for {symbol}: {e}")
            return False
    
    def get_open_positions(self) -> List[Dict[str, Any]]:
        """
        Get all open positions
        
        Returns:
            List of position dictionaries
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM positions 
                WHERE status = 'open' 
                ORDER BY entry_date DESC
            ''')
            
            rows = cursor.fetchall()
            self._close_connection(conn)
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            self.logger.error(f"Error retrieving open positions: {e}")
            return []
    
    def close_position(self, position_id: int, exit_price: float, 
                       notes: Optional[str] = None) -> bool:
        """
        Close a trading position
        
        Args:
            position_id: Position ID
            exit_price: Exit price
            notes: Optional notes
            
        Returns:
            True if successful
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get position data
            cursor.execute("SELECT * FROM positions WHERE id = ?", (position_id,))
            position = cursor.fetchone()
            
            if not position:
                self.logger.error(f"Position {position_id} not found")
                return False
            
            # Calculate P&L
            entry_date = datetime.fromisoformat(position['entry_date'])
            exit_date = datetime.now().date()
            hold_days = (exit_date - entry_date.date()).days
            
            entry_value = position['entry_price'] * position['shares']
            exit_value = exit_price * position['shares']
            pnl = exit_value - entry_value
            pnl_pct = (pnl / entry_value) * 100
            
            # Save to closed trades
            cursor.execute('''
                INSERT INTO closed_trades 
                (symbol, entry_date, entry_price, exit_date, exit_price, 
                 shares, pnl, pnl_pct, hold_days, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                position['symbol'],
                position['entry_date'],
                position['entry_price'],
                exit_date.isoformat(),
                exit_price,
                position['shares'],
                pnl,
                pnl_pct,
                hold_days,
                notes or position['notes']
            ))
            
            # Update position status
            cursor.execute('''
                UPDATE positions 
                SET status = 'closed' 
                WHERE id = ?
            ''', (position_id,))
            
            conn.commit()
            self._close_connection(conn)
            
            self.logger.info(f"Closed position {position_id}: P&L ${pnl:.2f} ({pnl_pct:.2f}%)")
            return True
            
        except Exception as e:
            self.logger.error(f"Error closing position {position_id}: {e}")
            return False
    
    def delete_position(self, position_id: int) -> bool:
        """
        Delete a trading position (removes from database)
        
        Args:
            position_id: Position ID to delete
            
        Returns:
            True if successful
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Delete the position
            cursor.execute("DELETE FROM positions WHERE id = ?", (position_id,))
            
            conn.commit()
            self._close_connection(conn)
            
            self.logger.info(f"Deleted position {position_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting position {position_id}: {e}")
            return False
    
    def delete_all_positions(self) -> bool:
        """
        Delete all trading positions (removes all from database)
        
        Returns:
            True if successful
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Count positions before deletion
            cursor.execute("SELECT COUNT(*) FROM positions")
            count = cursor.fetchone()[0]
            
            if count == 0:
                self.logger.info("No positions to delete")
                return True
            
            # Delete all positions
            cursor.execute("DELETE FROM positions")
            
            conn.commit()
            self._close_connection(conn)
            
            self.logger.info(f"Deleted all {count} positions")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting all positions: {e}")
            return False
    
    def get_closed_trades(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get closed trades history
        
        Args:
            limit: Maximum number of trades to return
            
        Returns:
            List of trade dictionaries
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM closed_trades 
                ORDER BY exit_date DESC 
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            self._close_connection(conn)
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            self.logger.error(f"Error retrieving closed trades: {e}")
            return []
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics
        
        Returns:
            Dictionary with database stats
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            stats = {}
            
            # Count records in each table
            tables = ['stock_prices', 'news_articles', 'social_mentions', 
                     'monthly_scores', 'alerts', 'watchlist', 'positions', 'closed_trades']
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                stats[f'{table}_count'] = count
            
            # Database size
            cursor.execute("SELECT page_count * page_size FROM pragma_page_count(), pragma_page_size()")
            size = cursor.fetchone()[0]
            stats['database_size_mb'] = round(size / (1024 * 1024), 2)
            
            self._close_connection(conn)
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting database stats: {e}")
            return {}
