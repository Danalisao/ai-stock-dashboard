#!/usr/bin/env python3
"""
🚀 INTRADAY TRADER - Système Automatique de Trading Intraday
=============================================================

Détecte automatiquement les opportunités de trading intraday et envoie
des notifications Telegram pour entry/exit sans action humaine requise.

FOCUS: Trades qui s'ouvrent et se ferment le même jour (9:30-16:00 ET)

STRATÉGIES:
- Scalping (targets 0.5-2%)
- Momentum breakouts (targets 2-5%)
- VWAP reversals
- Opening Range Breakouts (ORB)
- Volume surge plays

CRITÈRES INTRADAY:
- Volume > 5x average (liquidité pour entrer/sortir rapidement)
- Volatilité suffisante (ATR > 1.5%)
- Patterns intraday clairs
- Stops serrés (1-2%)
- Targets rapides (2-5%)
- Auto-exit avant 15:45 (éviter risque overnight)

NOTIFICATIONS TELEGRAM:
[ENTRY] Nouveau setup détecté avec prix, stop, target, R/R
[EXIT] Signal de sortie avec profit/perte estimé
[WARNING] Stop loss atteint
[AUTO-CLOSE] Fermeture automatique avant fin de journée
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import time
import logging
from datetime import datetime, timedelta
import pytz
import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple

from modules.alert_manager import AlertManager
from modules.database_manager import DatabaseManager
from modules.technical_indicators import TechnicalIndicators
from modules.utils import get_robust_ticker, load_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/intraday_trader.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class IntradayTrader:
    """
    Scanner de trading intraday automatique.
    Détecte les setups intraday et envoie des notifications Telegram.
    """
    
    def __init__(self, aggressive_mode: bool = False):
        """
        Initialize intraday trader.
        
        Args:
            aggressive_mode: Si True, critères plus souples (plus de trades)
        """
        self.config = load_config()
        self.alert_manager = AlertManager(self.config)
        self.db_manager = DatabaseManager(self.config)
        self.tech_indicators = TechnicalIndicators()
        self.aggressive_mode = aggressive_mode
        
        # Watchlist pour intraday
        self.watchlist = self._get_intraday_watchlist()
        
        # Seuils (ajustés selon mode)
        if aggressive_mode:
            self.min_volume_multiplier = 3.0  # 3x volume
            self.min_price_change = 2.0  # 2% minimum
            self.min_atr_percent = 1.0  # 1% ATR
            self.scan_interval = 15  # 15 secondes
            self.min_score = 70  # Score minimum 70
        else:
            self.min_volume_multiplier = 5.0  # 5x volume
            self.min_price_change = 3.0  # 3% minimum
            self.min_atr_percent = 1.5  # 1.5% ATR
            self.scan_interval = 30  # 30 secondes
            self.min_score = 75  # Score minimum 75
        
        # Tracking des positions alertées (éviter duplicatas)
        self.active_positions: Dict[str, Dict] = {}
        self.last_alerts: Dict[str, datetime] = {}
        self.alert_cooldown = timedelta(minutes=5)
        
        logger.info(f"✅ Intraday Trader initialized (aggressive={aggressive_mode})")
        logger.info(f"   Watchlist: {len(self.watchlist)} symbols")
        logger.info(f"   Scan interval: {self.scan_interval}s")
        logger.info(f"   Min score: {self.min_score}")
    
    def _get_intraday_watchlist(self) -> List[str]:
        """
        Obtenir watchlist optimisée pour intraday.
        Focus: actions avec volume élevé et volatilité.
        """
        # Stocks populaires intraday (high volume, high volatility)
        popular_intraday = [
            # Tech high volume
            "AAPL", "TSLA", "NVDA", "AMD", "MSFT", "GOOGL", "META", "AMZN",
            # Momentum stocks
            "GME", "AMC", "PLTR", "SOFI", "RIOT", "MARA",
            # SPY & QQQ (indices ETF)
            "SPY", "QQQ", "IWM",
            # High volatility
            "NIO", "LCID", "RIVN", "F", "BAC", "T", "INTC"
        ]
        
        # Charger watchlist depuis config si disponible
        config_watchlist = self.config.get('watchlist', {}).get('intraday', [])
        
        # Combiner les deux listes
        full_watchlist = list(set(popular_intraday + config_watchlist))
        
        logger.info(f"📋 Intraday watchlist: {len(full_watchlist)} symbols")
        return full_watchlist
    
    def is_market_hours(self) -> bool:
        """Vérifier si on est pendant les heures de marché (9:30-16:00 ET)."""
        et_tz = pytz.timezone('America/New_York')
        now_et = datetime.now(et_tz)
        
        # Vérifier jour de semaine (lundi=0, dimanche=6)
        if now_et.weekday() >= 5:  # Weekend
            return False
        
        # Heures de marché: 9:30-16:00 ET
        market_open = now_et.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now_et.replace(hour=16, minute=0, second=0, microsecond=0)
        
        return market_open <= now_et <= market_close
    
    def should_auto_close(self) -> bool:
        """
        Vérifier si on doit auto-closer les positions (avant 15:45 ET).
        On évite de tenir des positions après 15:45 (risque overnight).
        """
        et_tz = pytz.timezone('America/New_York')
        now_et = datetime.now(et_tz)
        auto_close_time = now_et.replace(hour=15, minute=45, second=0, microsecond=0)
        
        return now_et >= auto_close_time
    
    def calculate_vwap(self, df: pd.DataFrame) -> float:
        """
        Calculer VWAP (Volume Weighted Average Price).
        
        Args:
            df: DataFrame avec colonnes 'Close', 'High', 'Low', 'Volume'
        
        Returns:
            VWAP actuel
        """
        if df.empty or len(df) < 2:
            return 0.0
        
        # Typical price = (High + Low + Close) / 3
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        
        # VWAP = Sum(Typical Price * Volume) / Sum(Volume)
        vwap = (typical_price * df['Volume']).sum() / df['Volume'].sum()
        
        return float(vwap)
    
    def detect_opening_range_breakout(self, df: pd.DataFrame, current_price: float) -> Tuple[bool, str]:
        """
        Détecter Opening Range Breakout (ORB).
        
        Opening Range = High/Low des 5 premières minutes après ouverture.
        Breakout = prix dépasse ce range avec volume.
        
        Args:
            df: DataFrame intraday
            current_price: Prix actuel
        
        Returns:
            (is_breakout, direction) - direction = "BULLISH" ou "BEARISH"
        """
        if df.empty or len(df) < 10:
            return False, ""
        
        # Opening range = 5 premières bougies (5 min si timeframe=1min)
        opening_range = df.head(5)
        or_high = opening_range['High'].max()
        or_low = opening_range['Low'].min()
        
        # Breakout haussier
        if current_price > or_high * 1.002:  # > 0.2% au-dessus
            return True, "BULLISH"
        
        # Breakout baissier
        if current_price < or_low * 0.998:  # < 0.2% en-dessous
            return True, "BEARISH"
        
        return False, ""
    
    def scan_for_intraday_setups(self) -> List[Dict]:
        """
        Scanner principal: détecte tous les setups intraday.
        
        Returns:
            Liste de setups détectés avec scoring
        """
        if not self.is_market_hours():
            logger.info("⏰ Hors heures de marché - scan suspendu")
            return []
        
        logger.info(f"🔍 Scanning {len(self.watchlist)} symbols for intraday setups...")
        
        setups = []
        
        for symbol in self.watchlist:
            try:
                setup = self._analyze_intraday_setup(symbol)
                if setup and setup['score'] >= self.min_score:
                    setups.append(setup)
                    logger.info(f"   ✅ {symbol}: Score {setup['score']:.1f} - {setup['setup_type']}")
                
            except Exception as e:
                logger.error(f"   ❌ Error analyzing {symbol}: {e}")
                continue
        
        # Trier par score (meilleurs d'abord)
        setups.sort(key=lambda x: x['score'], reverse=True)
        
        logger.info(f"✅ Found {len(setups)} intraday setups")
        return setups
    
    def _analyze_intraday_setup(self, symbol: str) -> Optional[Dict]:
        """
        Analyser un symbole pour détecter setup intraday.
        
        Returns:
            Dict avec détails du setup ou None si pas de setup
        """
        # 1. Récupérer données intraday (1min, dernier jour)
        ticker = get_robust_ticker(symbol)
        if not ticker:
            return None
        
        # Data 1-minute pour aujourd'hui
        df_1min = ticker.history(period="1d", interval="1m")
        if df_1min.empty or len(df_1min) < 30:
            return None
        
        current_price = float(df_1min['Close'].iloc[-1])
        current_volume = int(df_1min['Volume'].iloc[-1])
        
        # 2. Calculer volume average (derniers 20 jours)
        df_daily = ticker.history(period="20d", interval="1d")
        if df_daily.empty:
            return None
        
        avg_volume = df_daily['Volume'].mean()
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
        
        # Filtre volume minimum
        if volume_ratio < self.min_volume_multiplier:
            return None
        
        # 3. Calculer price change (depuis open du jour)
        open_price = float(df_1min['Open'].iloc[0])
        price_change_pct = ((current_price - open_price) / open_price) * 100
        
        # Filtre prix minimum
        if abs(price_change_pct) < self.min_price_change:
            return None
        
        # 4. Calculer indicateurs techniques intraday
        indicators = self._calculate_intraday_indicators(df_1min, df_daily)
        
        # Filtre ATR minimum (volatilité)
        if indicators['atr_percent'] < self.min_atr_percent:
            return None
        
        # 5. Détecter type de setup
        setup_type, direction, confidence = self._detect_setup_type(
            df_1min, current_price, price_change_pct, indicators
        )
        
        if not setup_type:
            return None
        
        # 6. Calculer entry, stop, target
        entry_price = current_price
        stop_loss, take_profit, risk_reward = self._calculate_entry_exit(
            entry_price, direction, indicators
        )
        
        # 7. Calculer score global
        score = self._calculate_intraday_score(
            price_change_pct, volume_ratio, indicators, confidence
        )
        
        # 8. Construire setup
        setup = {
            'symbol': symbol,
            'timestamp': datetime.now(pytz.timezone('America/New_York')),
            'setup_type': setup_type,
            'direction': direction,
            'score': score,
            'confidence': confidence,
            
            # Prix
            'current_price': current_price,
            'open_price': open_price,
            'price_change_pct': price_change_pct,
            
            # Volume
            'current_volume': current_volume,
            'avg_volume': avg_volume,
            'volume_ratio': volume_ratio,
            
            # Entry/Exit
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'risk_reward': risk_reward,
            
            # Indicateurs
            'indicators': indicators
        }
        
        return setup
    
    def _calculate_intraday_indicators(self, df_1min: pd.DataFrame, df_daily: pd.DataFrame) -> Dict:
        """Calculer indicateurs techniques pour intraday."""
        indicators = {}
        
        try:
            # RSI (14 periods sur 1min)
            if len(df_1min) >= 14:
                rsi = self.tech_indicators.calculate_rsi(df_1min, period=14)
                indicators['rsi'] = float(rsi.iloc[-1]) if not rsi.empty else 50.0
            else:
                indicators['rsi'] = 50.0
            
            # MACD
            macd_line, signal_line, histogram = self.tech_indicators.calculate_macd(df_1min)
            if not macd_line.empty:
                indicators['macd'] = float(macd_line.iloc[-1])
                indicators['macd_signal'] = float(signal_line.iloc[-1])
                indicators['macd_histogram'] = float(histogram.iloc[-1])
                indicators['macd_bullish'] = histogram.iloc[-1] > 0
            else:
                indicators['macd'] = 0.0
                indicators['macd_signal'] = 0.0
                indicators['macd_histogram'] = 0.0
                indicators['macd_bullish'] = False
            
            # VWAP
            indicators['vwap'] = self.calculate_vwap(df_1min)
            current_price = float(df_1min['Close'].iloc[-1])
            indicators['price_vs_vwap'] = ((current_price - indicators['vwap']) / indicators['vwap']) * 100 if indicators['vwap'] > 0 else 0
            
            # ATR (Average True Range) - volatilité
            if not df_daily.empty and len(df_daily) >= 14:
                atr = self.tech_indicators.calculate_atr(df_daily, period=14)
                indicators['atr'] = float(atr.iloc[-1]) if not atr.empty else 0.0
                indicators['atr_percent'] = (indicators['atr'] / current_price) * 100 if current_price > 0 else 0.0
            else:
                indicators['atr'] = 0.0
                indicators['atr_percent'] = 0.0
            
            # Bollinger Bands
            upper, middle, lower = self.tech_indicators.calculate_bollinger_bands(df_1min, period=20)
            if not upper.empty:
                indicators['bb_upper'] = float(upper.iloc[-1])
                indicators['bb_middle'] = float(middle.iloc[-1])
                indicators['bb_lower'] = float(lower.iloc[-1])
                indicators['bb_width'] = ((indicators['bb_upper'] - indicators['bb_lower']) / indicators['bb_middle']) * 100
            else:
                indicators['bb_upper'] = 0.0
                indicators['bb_middle'] = 0.0
                indicators['bb_lower'] = 0.0
                indicators['bb_width'] = 0.0
            
            # Support/Resistance (recent highs/lows)
            recent_data = df_1min.tail(60)  # Last hour
            indicators['resistance'] = float(recent_data['High'].max())
            indicators['support'] = float(recent_data['Low'].min())
            
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
        
        return indicators
    
    def _detect_setup_type(
        self, 
        df: pd.DataFrame, 
        current_price: float, 
        price_change_pct: float,
        indicators: Dict
    ) -> Tuple[Optional[str], str, float]:
        """
        Détecter le type de setup intraday.
        
        Returns:
            (setup_type, direction, confidence)
        """
        # 1. Opening Range Breakout (ORB)
        is_orb, orb_direction = self.detect_opening_range_breakout(df, current_price)
        if is_orb:
            confidence = 85.0 if abs(price_change_pct) > 3.0 else 75.0
            return "Opening Range Breakout", orb_direction, confidence
        
        # 2. VWAP Reversal
        vwap = indicators.get('vwap', 0)
        price_vs_vwap = indicators.get('price_vs_vwap', 0)
        
        # Reversal haussier: prix au-dessus VWAP + RSI oversold
        if price_vs_vwap > 0.3 and indicators.get('rsi', 50) < 35:
            return "VWAP Reversal", "BULLISH", 80.0
        
        # Reversal baissier: prix en-dessous VWAP + RSI overbought
        if price_vs_vwap < -0.3 and indicators.get('rsi', 50) > 65:
            return "VWAP Reversal", "BEARISH", 80.0
        
        # 3. Momentum Breakout
        if abs(price_change_pct) > 4.0 and indicators.get('macd_bullish', False):
            direction = "BULLISH" if price_change_pct > 0 else "BEARISH"
            confidence = 90.0 if abs(price_change_pct) > 6.0 else 80.0
            return "Momentum Breakout", direction, confidence
        
        # 4. Bollinger Band Breakout
        bb_upper = indicators.get('bb_upper', 0)
        bb_lower = indicators.get('bb_lower', 0)
        
        if current_price > bb_upper * 1.002:
            return "BB Breakout", "BULLISH", 75.0
        
        if current_price < bb_lower * 0.998:
            return "BB Breakout", "BEARISH", 75.0
        
        # 5. Volume Surge (simple)
        # Déjà filtré par min_volume_multiplier, mais confirmé ici
        if price_change_pct > 3.0:
            return "Volume Surge", "BULLISH", 70.0
        elif price_change_pct < -3.0:
            return "Volume Surge", "BEARISH", 70.0
        
        return None, "", 0.0
    
    def _calculate_entry_exit(
        self, 
        entry_price: float, 
        direction: str, 
        indicators: Dict
    ) -> Tuple[float, float, float]:
        """
        Calculer stop loss et take profit pour intraday.
        
        Args:
            entry_price: Prix d'entrée
            direction: "BULLISH" ou "BEARISH"
            indicators: Indicateurs techniques
        
        Returns:
            (stop_loss, take_profit, risk_reward_ratio)
        """
        atr = indicators.get('atr', 0)
        atr_percent = indicators.get('atr_percent', 1.5)
        
        # Stop loss: 1.5x ATR ou 2% (le plus petit)
        stop_distance_pct = min(atr_percent * 1.5, 2.0)
        
        # Take profit: 2x le stop (ratio 1:2 minimum)
        target_distance_pct = stop_distance_pct * 2.0
        
        if direction == "BULLISH":
            stop_loss = entry_price * (1 - stop_distance_pct / 100)
            take_profit = entry_price * (1 + target_distance_pct / 100)
        else:  # BEARISH
            stop_loss = entry_price * (1 + stop_distance_pct / 100)
            take_profit = entry_price * (1 - target_distance_pct / 100)
        
        # Risk/Reward ratio
        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)
        risk_reward = reward / risk if risk > 0 else 0.0
        
        return stop_loss, take_profit, risk_reward
    
    def _calculate_intraday_score(
        self,
        price_change_pct: float,
        volume_ratio: float,
        indicators: Dict,
        confidence: float
    ) -> float:
        """
        Calculer score global 0-100 pour setup intraday.
        
        Composantes:
        - Price momentum (25%)
        - Volume (25%)
        - Technical indicators (25%)
        - Setup confidence (25%)
        """
        score = 0.0
        
        # 1. Price Momentum (0-25 points)
        price_score = min(abs(price_change_pct) * 3, 25)
        score += price_score
        
        # 2. Volume (0-25 points)
        volume_score = min((volume_ratio / self.min_volume_multiplier) * 25, 25)
        score += volume_score
        
        # 3. Technical Indicators (0-25 points)
        tech_score = 0
        
        # RSI
        rsi = indicators.get('rsi', 50)
        if 30 < rsi < 70:  # Neutral zone
            tech_score += 5
        elif rsi < 30 or rsi > 70:  # Extreme (good for reversals)
            tech_score += 8
        
        # MACD
        if indicators.get('macd_bullish', False):
            tech_score += 7
        
        # Price vs VWAP
        price_vs_vwap = abs(indicators.get('price_vs_vwap', 0))
        if price_vs_vwap > 0.5:
            tech_score += 5
        
        # ATR (volatilité)
        atr_percent = indicators.get('atr_percent', 0)
        if atr_percent >= self.min_atr_percent:
            tech_score += 5
        
        score += min(tech_score, 25)
        
        # 4. Setup Confidence (0-25 points)
        confidence_score = (confidence / 100) * 25
        score += confidence_score
        
        return min(score, 100.0)
    
    def send_entry_alert(self, setup: Dict):
        """
        Envoyer alerte d'entrée (ENTRY) via Telegram.
        """
        symbol = setup['symbol']
        
        # Vérifier cooldown (éviter spam)
        last_alert = self.last_alerts.get(symbol)
        if last_alert and (datetime.now() - last_alert) < self.alert_cooldown:
            return
        
        # Construire message Telegram
        direction_emoji = "🟢" if setup['direction'] == "BULLISH" else "🔴"
        
        message = f"""
{direction_emoji} **INTRADAY ENTRY SIGNAL** {direction_emoji}

📊 **Symbol**: {symbol}
🎯 **Setup**: {setup['setup_type']}
📈 **Direction**: {setup['direction']}
💯 **Score**: {setup['score']:.1f}/100
⭐ **Confidence**: {setup['confidence']:.0f}%

💰 **Entry**: ${setup['entry_price']:.2f}
🛑 **Stop Loss**: ${setup['stop_loss']:.2f} ({((setup['stop_loss'] - setup['entry_price']) / setup['entry_price'] * 100):.1f}%)
🎯 **Target**: ${setup['take_profit']:.2f} ({((setup['take_profit'] - setup['entry_price']) / setup['entry_price'] * 100):.1f}%)
📊 **R/R**: 1:{setup['risk_reward']:.1f}

📊 **Price**: ${setup['current_price']:.2f} ({setup['price_change_pct']:+.2f}% today)
📈 **Volume**: {setup['volume_ratio']:.1f}x average

📊 **Technical**:
  • RSI: {setup['indicators'].get('rsi', 0):.1f}
  • MACD: {"Bullish ✅" if setup['indicators'].get('macd_bullish') else "Bearish ⚠️"}
  • vs VWAP: {setup['indicators'].get('price_vs_vwap', 0):+.2f}%
  • ATR: {setup['indicators'].get('atr_percent', 0):.2f}%

🕐 **Time**: {setup['timestamp'].strftime('%H:%M:%S ET')}

⚡ **ACTION**: {'BUY' if setup['direction'] == 'BULLISH' else 'SHORT'} @ ${setup['entry_price']:.2f}
"""
        
        # Envoyer alerte
        priority = "HIGH" if setup['score'] >= 85 else "MEDIUM"
        self.alert_manager.send_alert(
            alert_type="intraday_entry",
            symbol=symbol,
            message=message,
            priority=priority,
            value=setup['current_price'],
            data=setup
        )
        
        # Enregistrer dans DB
        self.db_manager.log_alert(
            symbol=symbol,
            alert_type=f"INTRADAY_ENTRY_{setup['direction']}",
            priority=priority,
            message=f"{setup['setup_type']} - Score {setup['score']:.1f} - Entry ${setup['entry_price']:.2f}, Stop ${setup['stop_loss']:.2f}, Target ${setup['take_profit']:.2f}",
            value=setup['entry_price']
        )
        
        # Tracker la position
        self.active_positions[symbol] = setup
        self.last_alerts[symbol] = datetime.now()
        
        logger.info(f"📤 Sent ENTRY alert for {symbol} ({setup['setup_type']})")
    
    def check_exit_signals(self):
        """
        Vérifier les signaux de sortie pour les positions actives.
        Envoie alertes EXIT si target atteint ou stop loss touché.
        """
        if not self.active_positions:
            return
        
        for symbol, position in list(self.active_positions.items()):
            try:
                # Récupérer prix actuel
                ticker = get_robust_ticker(symbol)
                if not ticker:
                    continue
                
                current_data = ticker.history(period="1d", interval="1m")
                if current_data.empty:
                    continue
                
                current_price = float(current_data['Close'].iloc[-1])
                entry_price = position['entry_price']
                stop_loss = position['stop_loss']
                take_profit = position['take_profit']
                direction = position['direction']
                
                # Vérifier si target atteint
                target_hit = False
                stop_hit = False
                
                if direction == "BULLISH":
                    if current_price >= take_profit:
                        target_hit = True
                    elif current_price <= stop_loss:
                        stop_hit = True
                else:  # BEARISH
                    if current_price <= take_profit:
                        target_hit = True
                    elif current_price >= stop_loss:
                        stop_hit = True
                
                # Envoyer alerte EXIT si nécessaire
                if target_hit:
                    self._send_exit_alert(symbol, position, current_price, "TARGET_HIT")
                    del self.active_positions[symbol]
                
                elif stop_hit:
                    self._send_exit_alert(symbol, position, current_price, "STOP_LOSS")
                    del self.active_positions[symbol]
                
            except Exception as e:
                logger.error(f"Error checking exit for {symbol}: {e}")
    
    def _send_exit_alert(self, symbol: str, position: Dict, exit_price: float, exit_reason: str):
        """Envoyer alerte de sortie."""
        entry_price = position['entry_price']
        pnl_pct = ((exit_price - entry_price) / entry_price) * 100
        
        if position['direction'] == "BEARISH":
            pnl_pct = -pnl_pct
        
        profit_emoji = "💰" if pnl_pct > 0 else "⚠️"
        reason_text = "✅ Target Hit" if exit_reason == "TARGET_HIT" else "🛑 Stop Loss"
        
        message = f"""
{profit_emoji} **INTRADAY EXIT SIGNAL** {profit_emoji}

📊 **Symbol**: {symbol}
📉 **Exit Reason**: {reason_text}

💰 **Entry**: ${entry_price:.2f}
💵 **Exit**: ${exit_price:.2f}
📊 **P&L**: {pnl_pct:+.2f}%

🕐 **Time**: {datetime.now(pytz.timezone('America/New_York')).strftime('%H:%M:%S ET')}

{'🎉 **PROFIT!**' if pnl_pct > 0 else '😔 **LOSS**'}
"""
        
        priority = "HIGH" if abs(pnl_pct) > 3 else "MEDIUM"
        self.alert_manager.send_alert(
            alert_type="intraday_exit",
            symbol=symbol,
            message=message,
            priority=priority,
            value=exit_price,
            data={'entry_price': entry_price, 'exit_price': exit_price, 'pnl_pct': pnl_pct}
        )
        
        logger.info(f"📤 Sent EXIT alert for {symbol} (P&L: {pnl_pct:+.2f}%)")
    
    def auto_close_positions(self):
        """
        Fermer automatiquement toutes les positions avant 16:00 ET.
        Envoie alertes AUTO_CLOSE.
        """
        if not self.active_positions:
            return
        
        logger.info(f"🔔 Auto-closing {len(self.active_positions)} positions before market close")
        
        for symbol, position in list(self.active_positions.items()):
            try:
                # Récupérer prix actuel
                ticker = get_robust_ticker(symbol)
                if not ticker:
                    continue
                
                current_data = ticker.history(period="1d", interval="1m")
                if current_data.empty:
                    continue
                
                current_price = float(current_data['Close'].iloc[-1])
                
                # Envoyer alerte auto-close
                self._send_exit_alert(symbol, position, current_price, "AUTO_CLOSE")
                del self.active_positions[symbol]
                
            except Exception as e:
                logger.error(f"Error auto-closing {symbol}: {e}")
    
    def run(self):
        """
        Boucle principale: scanner en continu pendant les heures de marché.
        """
        logger.info("🚀 Starting Intraday Trader...")
        logger.info(f"   Scan interval: {self.scan_interval}s")
        logger.info(f"   Min score: {self.min_score}")
        logger.info(f"   Aggressive mode: {self.aggressive_mode}")
        
        while True:
            try:
                # Vérifier si on est pendant les heures de marché
                if not self.is_market_hours():
                    logger.info("⏰ Outside market hours - sleeping 60s")
                    time.sleep(60)
                    continue
                
                # Vérifier si on doit auto-closer les positions
                if self.should_auto_close() and self.active_positions:
                    self.auto_close_positions()
                    logger.info("✅ All positions auto-closed")
                    time.sleep(60)  # Wait until market close
                    continue
                
                # Scanner les setups
                setups = self.scan_for_intraday_setups()
                
                # Envoyer alertes pour nouveaux setups
                for setup in setups:
                    symbol = setup['symbol']
                    
                    # Ne pas alerter si déjà en position
                    if symbol in self.active_positions:
                        continue
                    
                    self.send_entry_alert(setup)
                
                # Vérifier les signaux de sortie pour positions actives
                self.check_exit_signals()
                
                # Attendre avant prochain scan
                logger.info(f"💤 Sleeping {self.scan_interval}s...")
                time.sleep(self.scan_interval)
                
            except KeyboardInterrupt:
                logger.info("\n🛑 Stopping Intraday Trader (user interrupt)")
                break
            except Exception as e:
                logger.error(f"❌ Error in main loop: {e}", exc_info=True)
                time.sleep(10)


def main():
    """Entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Intraday Trader - Système automatique")
    parser.add_argument(
        '--aggressive',
        action='store_true',
        help='Mode agressif (plus de trades, critères plus souples)'
    )
    
    args = parser.parse_args()
    
    # Créer et lancer trader
    trader = IntradayTrader(aggressive_mode=args.aggressive)
    trader.run()


if __name__ == "__main__":
    main()
