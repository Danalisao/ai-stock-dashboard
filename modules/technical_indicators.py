"""
📊 Advanced Technical Indicators
Comprehensive technical analysis indicators for monthly trading signals
"""

import logging
import pandas as pd
import numpy as np
from typing import Optional, Tuple, Dict, Any


class TechnicalIndicators:
    """Advanced technical indicators calculator"""
    
    def __init__(self):
        """Initialize technical indicators calculator"""
        self.logger = logging.getLogger(__name__)
    
    # ==================== BASIC INDICATORS ====================
    
    def calculate_sma(self, data: pd.DataFrame, period: int = 20) -> pd.Series:
        """
        Calculate Simple Moving Average
        
        Args:
            data: DataFrame with Close prices
            period: Period for SMA
            
        Returns:
            SMA series
        """
        close_col = 'Close' if 'Close' in data.columns else 'close'
        return data[close_col].rolling(window=period).mean()
    
    def calculate_ema(self, data: pd.DataFrame, period: int = 20) -> pd.Series:
        """
        Calculate Exponential Moving Average
        
        Args:
            data: DataFrame with Close prices
            period: Period for EMA
            
        Returns:
            EMA series
        """
        close_col = 'Close' if 'Close' in data.columns else 'close'
        return data[close_col].ewm(span=period, adjust=False).mean()
    
    def calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index
        
        Args:
            data: DataFrame with Close prices
            period: RSI period
            
        Returns:
            RSI series (0-100)
        """
        close_col = 'Close' if 'Close' in data.columns else 'close'
        delta = data[close_col].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def calculate_macd(self, data: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Args:
            data: DataFrame with Close prices
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line period
            
        Returns:
            Dictionary with macd, signal, and histogram
        """
        close_col = 'Close' if 'Close' in data.columns else 'close'
        ema_fast = data[close_col].ewm(span=fast, adjust=False).mean()
        ema_slow = data[close_col].ewm(span=slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line
        
        return {
            'macd': macd,
            'signal': signal_line,
            'histogram': histogram
        }
    
    def calculate_bollinger_bands(self, data: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> Dict[str, pd.Series]:
        """
        Calculate Bollinger Bands
        
        Args:
            data: DataFrame with Close prices
            period: Period for moving average
            std_dev: Number of standard deviations
            
        Returns:
            Dictionary with upper, middle, lower bands
        """
        close_col = 'Close' if 'Close' in data.columns else 'close'
        middle = data[close_col].rolling(window=period).mean()
        std = data[close_col].rolling(window=period).std()
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return {
            'upper': upper,
            'middle': middle,
            'lower': lower
        }
    
    def calculate_atr(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Average True Range
        
        Args:
            data: DataFrame with High, Low, Close
            period: ATR period
            
        Returns:
            ATR series
        """
        high_col = 'High' if 'High' in data.columns else 'high'
        low_col = 'Low' if 'Low' in data.columns else 'low'
        close_col = 'Close' if 'Close' in data.columns else 'close'
        
        high_low = data[high_col] - data[low_col]
        high_close = np.abs(data[high_col] - data[close_col].shift())
        low_close = np.abs(data[low_col] - data[close_col].shift())
        
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return tr.rolling(window=period).mean()
    
    # ==================== TREND INDICATORS ====================
    
    def calculate_adx(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Average Directional Index (ADX)
        Measures trend strength (not direction)
        
        Args:
            data: DataFrame with High, Low, Close
            period: ADX period
            
        Returns:
            ADX series (0-100, >25 indicates strong trend)
        """
        high = data['High']
        low = data['Low']
        close = data['Close']
        
        # Calculate True Range
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Calculate Directional Movement
        up_move = high - high.shift()
        down_move = low.shift() - low
        
        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
        
        # Smooth TR and DM
        atr = pd.Series(tr).rolling(window=period).mean()
        plus_di = 100 * pd.Series(plus_dm).rolling(window=period).mean() / atr
        minus_di = 100 * pd.Series(minus_dm).rolling(window=period).mean() / atr
        
        # Calculate ADX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        
        return adx
    
    def calculate_parabolic_sar(self, data: pd.DataFrame, af_start: float = 0.02, 
                                 af_increment: float = 0.02, af_max: float = 0.2) -> pd.Series:
        """
        Calculate Parabolic SAR (Stop and Reverse)
        Provides entry/exit points
        
        Args:
            data: DataFrame with High, Low, Close
            af_start: Starting acceleration factor
            af_increment: AF increment
            af_max: Maximum AF
            
        Returns:
            SAR series
        """
        high = data['High'].values
        low = data['Low'].values
        close = data['Close'].values
        
        sar = np.zeros(len(close))
        ep = np.zeros(len(close))
        af = np.zeros(len(close))
        trend = np.zeros(len(close))
        
        # Initialize
        sar[0] = close[0]
        ep[0] = high[0]
        af[0] = af_start
        trend[0] = 1  # 1 for uptrend, -1 for downtrend
        
        for i in range(1, len(close)):
            # Previous values
            sar[i] = sar[i-1] + af[i-1] * (ep[i-1] - sar[i-1])
            
            if trend[i-1] == 1:  # Uptrend
                # Check for reversal
                if low[i] < sar[i]:
                    trend[i] = -1
                    sar[i] = ep[i-1]
                    ep[i] = low[i]
                    af[i] = af_start
                else:
                    trend[i] = 1
                    if high[i] > ep[i-1]:
                        ep[i] = high[i]
                        af[i] = min(af[i-1] + af_increment, af_max)
                    else:
                        ep[i] = ep[i-1]
                        af[i] = af[i-1]
            else:  # Downtrend
                # Check for reversal
                if high[i] > sar[i]:
                    trend[i] = 1
                    sar[i] = ep[i-1]
                    ep[i] = high[i]
                    af[i] = af_start
                else:
                    trend[i] = -1
                    if low[i] < ep[i-1]:
                        ep[i] = low[i]
                        af[i] = min(af[i-1] + af_increment, af_max)
                    else:
                        ep[i] = ep[i-1]
                        af[i] = af[i-1]
        
        return pd.Series(sar, index=data.index)
    
    def calculate_supertrend(self, data: pd.DataFrame, period: int = 10, 
                             multiplier: float = 3.0) -> Tuple[pd.Series, pd.Series]:
        """
        Calculate Supertrend indicator
        Dynamic support/resistance
        
        Args:
            data: DataFrame with High, Low, Close
            period: ATR period
            multiplier: ATR multiplier
            
        Returns:
            Tuple of (supertrend, trend_direction)
        """
        # Calculate ATR
        high = data['High']
        low = data['Low']
        close = data['Close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        # Calculate basic bands
        hl_avg = (high + low) / 2
        upper_band = hl_avg + (multiplier * atr)
        lower_band = hl_avg - (multiplier * atr)
        
        # Calculate Supertrend
        supertrend = pd.Series(index=data.index, dtype=float)
        direction = pd.Series(index=data.index, dtype=int)
        
        for i in range(period, len(data)):
            if i == period:
                supertrend.iloc[i] = upper_band.iloc[i]
                direction.iloc[i] = -1
            else:
                if close.iloc[i] <= supertrend.iloc[i-1]:
                    supertrend.iloc[i] = upper_band.iloc[i]
                    direction.iloc[i] = -1
                else:
                    supertrend.iloc[i] = lower_band.iloc[i]
                    direction.iloc[i] = 1
        
        return supertrend, direction
    
    # ==================== VOLUME INDICATORS ====================
    
    def calculate_obv(self, data: pd.DataFrame) -> pd.Series:
        """
        Calculate On-Balance Volume (OBV)
        Cumulative volume indicator
        
        Args:
            data: DataFrame with Close and Volume
            
        Returns:
            OBV series
        """
        # Handle both 'Volume' and 'volume' column names
        volume_col = 'Volume' if 'Volume' in data.columns else 'volume'
        close_col = 'Close' if 'Close' in data.columns else 'close'
        
        if volume_col not in data.columns or close_col not in data.columns:
            # Return zeros if required columns don't exist
            return pd.Series(0, index=data.index, dtype=float)
        
        obv = pd.Series(index=data.index, dtype=float)
        obv.iloc[0] = data[volume_col].iloc[0]
        
        for i in range(1, len(data)):
            if data[close_col].iloc[i] > data[close_col].iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] + data[volume_col].iloc[i]
            elif data[close_col].iloc[i] < data[close_col].iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] - data[volume_col].iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]
        
        return obv
    
    def calculate_vwap(self, data: pd.DataFrame) -> pd.Series:
        """
        Calculate Volume Weighted Average Price (VWAP)
        Institutional price benchmark
        
        Args:
            data: DataFrame with High, Low, Close, Volume
            
        Returns:
            VWAP series
        """
        typical_price = (data['High'] + data['Low'] + data['Close']) / 3
        vwap = (typical_price * data['Volume']).cumsum() / data['Volume'].cumsum()
        return vwap
    
    def calculate_mfi(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Money Flow Index (MFI)
        Volume-weighted RSI
        
        Args:
            data: DataFrame with High, Low, Close, Volume
            period: MFI period
            
        Returns:
            MFI series (0-100)
        """
        typical_price = (data['High'] + data['Low'] + data['Close']) / 3
        money_flow = typical_price * data['Volume']
        
        positive_flow = pd.Series(0.0, index=data.index)
        negative_flow = pd.Series(0.0, index=data.index)
        
        for i in range(1, len(data)):
            if typical_price.iloc[i] > typical_price.iloc[i-1]:
                positive_flow.iloc[i] = money_flow.iloc[i]
            elif typical_price.iloc[i] < typical_price.iloc[i-1]:
                negative_flow.iloc[i] = money_flow.iloc[i]
        
        positive_mf = positive_flow.rolling(window=period).sum()
        negative_mf = negative_flow.rolling(window=period).sum()
        
        mfi = 100 - (100 / (1 + positive_mf / negative_mf))
        return mfi
    
    def calculate_cmf(self, data: pd.DataFrame, period: int = 20) -> pd.Series:
        """
        Calculate Chaikin Money Flow (CMF)
        Buying/selling pressure
        
        Args:
            data: DataFrame with High, Low, Close, Volume
            period: CMF period
            
        Returns:
            CMF series (-1 to +1)
        """
        mfm = ((data['Close'] - data['Low']) - (data['High'] - data['Close'])) / (data['High'] - data['Low'])
        mfm = mfm.fillna(0)
        mfv = mfm * data['Volume']
        
        cmf = mfv.rolling(window=period).sum() / data['Volume'].rolling(window=period).sum()
        return cmf
    
    # ==================== MOMENTUM INDICATORS ====================
    
    def calculate_roc(self, data: pd.DataFrame, period: int = 30) -> pd.Series:
        """
        Calculate Rate of Change (ROC)
        Momentum indicator
        
        Args:
            data: DataFrame with Close
            period: ROC period
            
        Returns:
            ROC series (percentage)
        """
        roc = ((data['Close'] - data['Close'].shift(period)) / data['Close'].shift(period)) * 100
        return roc
    
    def calculate_williams_r(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Williams %R
        Overbought/oversold indicator
        
        Args:
            data: DataFrame with High, Low, Close
            period: Williams %R period
            
        Returns:
            Williams %R series (-100 to 0)
        """
        highest_high = data['High'].rolling(window=period).max()
        lowest_low = data['Low'].rolling(window=period).min()
        
        williams_r = -100 * (highest_high - data['Close']) / (highest_high - lowest_low)
        return williams_r
    
    def calculate_cci(self, data: pd.DataFrame, period: int = 20) -> pd.Series:
        """
        Calculate Commodity Channel Index (CCI)
        Trend change indicator
        
        Args:
            data: DataFrame with High, Low, Close
            period: CCI period
            
        Returns:
            CCI series
        """
        typical_price = (data['High'] + data['Low'] + data['Close']) / 3
        sma = typical_price.rolling(window=period).mean()
        mad = typical_price.rolling(window=period).apply(lambda x: np.abs(x - x.mean()).mean())
        
        cci = (typical_price - sma) / (0.015 * mad)
        return cci
    
    def calculate_ultimate_oscillator(self, data: pd.DataFrame, 
                                       period1: int = 7, period2: int = 14, 
                                       period3: int = 28) -> pd.Series:
        """
        Calculate Ultimate Oscillator
        Multi-timeframe momentum
        
        Args:
            data: DataFrame with High, Low, Close
            period1, period2, period3: Three periods
            
        Returns:
            Ultimate Oscillator series (0-100)
        """
        # Calculate buying pressure
        bp = data['Close'] - pd.concat([data['Low'], data['Close'].shift()], axis=1).min(axis=1)
        
        # Calculate true range
        tr1 = data['High'] - data['Low']
        tr2 = abs(data['High'] - data['Close'].shift())
        tr3 = abs(data['Low'] - data['Close'].shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Calculate averages
        avg1 = bp.rolling(window=period1).sum() / tr.rolling(window=period1).sum()
        avg2 = bp.rolling(window=period2).sum() / tr.rolling(window=period2).sum()
        avg3 = bp.rolling(window=period3).sum() / tr.rolling(window=period3).sum()
        
        # Calculate Ultimate Oscillator
        uo = 100 * ((4 * avg1) + (2 * avg2) + avg3) / 7
        return uo
    
    # ==================== MONTHLY-SPECIFIC INDICATORS ====================
    
    def calculate_pivot_points(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate monthly pivot points
        Support/resistance levels
        
        Args:
            data: DataFrame with High, Low, Close
            
        Returns:
            Dictionary with pivot levels
        """
        # Use last complete month
        high = data['High'].iloc[-1]
        low = data['Low'].iloc[-1]
        close = data['Close'].iloc[-1]
        
        pivot = (high + low + close) / 3
        
        r1 = 2 * pivot - low
        r2 = pivot + (high - low)
        r3 = high + 2 * (pivot - low)
        
        s1 = 2 * pivot - high
        s2 = pivot - (high - low)
        s3 = low - 2 * (high - pivot)
        
        return {
            'pivot': pivot,
            'r1': r1, 'r2': r2, 'r3': r3,
            's1': s1, 's2': s2, 's3': s3
        }
    
    def calculate_ichimoku_cloud(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        """
        Calculate Ichimoku Cloud (monthly timeframe)
        Comprehensive trend system
        
        Args:
            data: DataFrame with High, Low, Close
            
        Returns:
            Dictionary with Ichimoku lines
        """
        # Conversion Line (Tenkan-sen): 9-period
        period1_high = data['High'].rolling(window=9).max()
        period1_low = data['Low'].rolling(window=9).min()
        conversion_line = (period1_high + period1_low) / 2
        
        # Base Line (Kijun-sen): 26-period
        period2_high = data['High'].rolling(window=26).max()
        period2_low = data['Low'].rolling(window=26).min()
        base_line = (period2_high + period2_low) / 2
        
        # Leading Span A (Senkou Span A)
        leading_span_a = ((conversion_line + base_line) / 2).shift(26)
        
        # Leading Span B (Senkou Span B): 52-period
        period3_high = data['High'].rolling(window=52).max()
        period3_low = data['Low'].rolling(window=52).min()
        leading_span_b = ((period3_high + period3_low) / 2).shift(26)
        
        # Lagging Span (Chikou Span)
        lagging_span = data['Close'].shift(-26)
        
        return {
            'conversion_line': conversion_line,
            'base_line': base_line,
            'leading_span_a': leading_span_a,
            'leading_span_b': leading_span_b,
            'lagging_span': lagging_span
        }
    
    def calculate_fibonacci_retracements(self, data: pd.DataFrame, 
                                          period: int = 60) -> Dict[str, float]:
        """
        Calculate Fibonacci retracement levels
        Key support/resistance
        
        Args:
            data: DataFrame with High, Low
            period: Period to calculate levels
            
        Returns:
            Dictionary with Fibonacci levels
        """
        recent_data = data.tail(period)
        high = recent_data['High'].max()
        low = recent_data['Low'].min()
        diff = high - low
        
        levels = {
            'high': high,
            'low': low,
            'fib_0': high,
            'fib_236': high - (0.236 * diff),
            'fib_382': high - (0.382 * diff),
            'fib_500': high - (0.500 * diff),
            'fib_618': high - (0.618 * diff),
            'fib_786': high - (0.786 * diff),
            'fib_100': low
        }
        
        return levels
    
    def calculate_all_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all technical indicators at once
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataFrame with all indicators added
        """
        try:
            # Normalize column names (handle both uppercase and lowercase)
            data.columns = [col.capitalize() for col in data.columns]
            
            # Trend indicators
            data['SMA_20'] = self.calculate_sma(data, 20)
            data['SMA_50'] = self.calculate_sma(data, 50)
            data['SMA_200'] = self.calculate_sma(data, 200)
            data['EMA_12'] = self.calculate_ema(data, 12)
            data['EMA_26'] = self.calculate_ema(data, 26)
            
            # ADX for trend strength
            try:
                data['ADX'] = self.calculate_adx(data)
            except Exception as e:
                self.logger.warning(f"ADX calculation failed: {e}")
                data['ADX'] = 20  # Neutral value
            
            # Momentum indicators
            data['RSI'] = self.calculate_rsi(data)
            
            # MACD
            try:
                macd_data = self.calculate_macd(data)
                data['MACD'] = macd_data['macd']
                data['MACD_signal'] = macd_data['signal']
                data['MACD_histogram'] = macd_data['histogram']
            except Exception as e:
                self.logger.warning(f"MACD calculation failed: {e}")
                data['MACD'] = 0
                data['MACD_signal'] = 0
                data['MACD_histogram'] = 0
            
            # ROC (Rate of Change)
            data['ROC'] = self.calculate_roc(data)
            
            # Volatility indicators
            try:
                bb_data = self.calculate_bollinger_bands(data)
                data['BB_upper'] = bb_data['upper']
                data['BB_middle'] = bb_data['middle']
                data['BB_lower'] = bb_data['lower']
            except Exception as e:
                self.logger.warning(f"Bollinger Bands calculation failed: {e}")
                data['BB_upper'] = data['Close']
                data['BB_middle'] = data['Close']
                data['BB_lower'] = data['Close']
            
            # ATR
            try:
                data['ATR'] = self.calculate_atr(data)
            except Exception as e:
                self.logger.warning(f"ATR calculation failed: {e}")
                data['ATR'] = 0
            
            # Volume indicators
            try:
                data['OBV'] = self.calculate_obv(data)
            except Exception as e:
                self.logger.warning(f"OBV calculation failed: {e}")
                data['OBV'] = 0
            
            try:
                data['VWAP'] = self.calculate_vwap(data)
            except Exception as e:
                self.logger.warning(f"VWAP calculation failed: {e}")
                data['VWAP'] = data['Close']
            
            # MFI (Money Flow Index)
            try:
                data['MFI'] = self.calculate_mfi(data)
            except Exception as e:
                self.logger.warning(f"MFI calculation failed: {e}")
                data['MFI'] = 50  # Neutral value
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error calculating indicators: {e}")
            return data
