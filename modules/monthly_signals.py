"""
🎯 Monthly Trading Signals Generator
Calculate 0-100 scores and generate decisive trading recommendations
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple
from datetime import datetime


class MonthlySignals:
    """Generate monthly trading signals with 0-100 scoring"""
    
    def __init__(self, config: Dict[str, Any], sentiment_analyzer=None, technical_indicators=None):
        """
        Initialize monthly signals generator
        
        Args:
            config: Configuration dictionary
            sentiment_analyzer: Optional SentimentAnalyzer instance
            technical_indicators: Optional TechnicalIndicators instance
        """
        self.config = config.get('monthly_signals', {})
        self.logger = logging.getLogger(__name__)
        self.sentiment_analyzer = sentiment_analyzer
        self.technical_indicators = technical_indicators
        
        # Component weights
        self.trend_weight = self.config.get('trend_weight', 0.30)
        self.momentum_weight = self.config.get('momentum_weight', 0.20)
        self.sentiment_weight = self.config.get('sentiment_weight', 0.25)
        self.divergence_weight = self.config.get('divergence_weight', 0.15)
        self.volume_weight = self.config.get('volume_weight', 0.10)
        
        # Thresholds
        self.strong_buy = self.config.get('strong_buy', 80)
        self.buy = self.config.get('buy', 75)
        self.moderate_buy = self.config.get('moderate_buy', 60)
        self.hold = self.config.get('hold', 40)
        self.moderate_sell = self.config.get('moderate_sell', 26)
        self.sell = self.config.get('sell', 11)
    
    def calculate_monthly_score(self, data: pd.DataFrame, 
                                 symbol: str,
                                 news_sentiment: Optional[Dict[str, Any]] = None,
                                 social_sentiment: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Calculate comprehensive monthly trading score (0-100)
        
        Args:
            data: Historical price data
            indicators: Technical indicators dictionary
            news_sentiment: News sentiment analysis results
            social_sentiment: Social media sentiment results
            
        Returns:
            Dictionary with score breakdown and recommendation
        """
        try:
            # Calculate technical indicators if needed
            if self.technical_indicators:
                data = self.technical_indicators.calculate_all_indicators(data)
            
            # Calculate each component
            trend_score = self._analyze_trend(data)
            momentum_score = self._analyze_momentum(data)
            sentiment_score = self._analyze_sentiment(news_sentiment, social_sentiment)
            divergence_score = self._analyze_divergences(data)
            volume_score = self._analyze_volume(data)
            
            # Calculate weighted total score
            total_score = (
                trend_score * self.trend_weight +
                momentum_score * self.momentum_weight +
                sentiment_score * self.sentiment_weight +
                divergence_score * self.divergence_weight +
                volume_score * self.volume_weight
            )
            
            # ⚠️ APPLY LATE ENTRY PENALTY
            late_entry_penalty = 0
            late_entry_warning = None
            
            # Check for late entry risk (overextended moves)
            try:
                current_price = data['Close'].iloc[-1]
                
                # Calculate price extension metrics
                change_5d = ((data['Close'].iloc[-1] / data['Close'].iloc[-6]) - 1) * 100 if len(data) > 5 else 0
                change_20d = ((data['Close'].iloc[-1] / data['Close'].iloc[-21]) - 1) * 100 if len(data) > 20 else 0
                
                # Calculate RSI
                delta = data['Close'].diff()
                gain = delta.where(delta > 0, 0).rolling(14).mean()
                loss = -delta.where(delta < 0, 0).rolling(14).mean()
                rs = gain / loss
                rsi = (100 - (100 / (1 + rs))).iloc[-1] if not rs.empty else 50
                
                # Calculate distance from moving averages
                ma_20 = data['Close'].rolling(20).mean().iloc[-1] if len(data) > 20 else current_price
                ma_50 = data['Close'].rolling(50).mean().iloc[-1] if len(data) > 50 else current_price
                distance_ma20 = ((current_price / ma_20) - 1) * 100 if ma_20 > 0 else 0
                distance_ma50 = ((current_price / ma_50) - 1) * 100 if ma_50 > 0 else 0
                
                # Apply penalties based on late entry indicators
                
                # 1. Extreme RSI penalty (overbought)
                if rsi > 80:
                    late_entry_penalty += 25
                    late_entry_warning = f"CRITICAL: Extreme overbought (RSI: {rsi:.1f})"
                elif rsi > 70:
                    late_entry_penalty += 15
                    late_entry_warning = f"WARNING: Overbought conditions (RSI: {rsi:.1f})"
                
                # 2. Parabolic move penalty
                if change_5d > 20:
                    late_entry_penalty += 20
                    if not late_entry_warning:
                        late_entry_warning = f"WARNING: Parabolic move (+{change_5d:.1f}% in 5 days)"
                elif change_5d > 15:
                    late_entry_penalty += 10
                
                # 3. Extended from MA penalty
                if distance_ma20 > 15:
                    late_entry_penalty += 15
                    if not late_entry_warning:
                        late_entry_warning = f"WARNING: Far from 20-MA (+{distance_ma20:.1f}%)"
                elif distance_ma20 > 10:
                    late_entry_penalty += 8
                
                # 4. Long-term extension penalty
                if change_20d > 40:
                    late_entry_penalty += 10
                
                # Log penalty if significant
                if late_entry_penalty > 0:
                    self.logger.warning(f"⚠️ Late entry penalty applied: -{late_entry_penalty} points for {symbol}")
                    
            except Exception as e:
                self.logger.debug(f"Could not calculate late entry penalty: {e}")
            
            # Apply penalty (cap at 40 points maximum)
            late_entry_penalty = min(late_entry_penalty, 40)
            original_score = total_score
            total_score = total_score - late_entry_penalty
            
            # Ensure score is 0-100
            total_score = max(0, min(100, total_score))
            
            # Generate recommendation
            recommendation = self._get_recommendation(total_score)
            
            # Calculate entry/exit prices
            current_price = data['Close'].iloc[-1]
            entry_price, stop_loss, target_price = self._calculate_trade_params(
                data, total_score, current_price
            )
            
            # Calculate risk/reward
            risk_reward = self._calculate_risk_reward(entry_price, stop_loss, target_price)
            
            # Build components dictionary for database storage
            components = {
                'trend': {'score': round(trend_score, 2)},
                'momentum': {'score': round(momentum_score, 2)},
                'sentiment': {'score': round(sentiment_score, 2)},
                'divergence': {'score': round(divergence_score, 2)},
                'volume': {'score': round(volume_score, 2)}
            }
            
            return {
                'date': datetime.now().isoformat(),
                'total_score': round(total_score, 2),
                'original_score': round(original_score, 2) if late_entry_penalty > 0 else round(total_score, 2),
                'late_entry_penalty': round(late_entry_penalty, 2),
                'late_entry_warning': late_entry_warning,
                'trend_score': round(trend_score, 2),
                'momentum_score': round(momentum_score, 2),
                'sentiment_score': round(sentiment_score, 2),
                'divergence_score': round(divergence_score, 2),
                'volume_score': round(volume_score, 2),
                'components': components,
                'recommendation': recommendation,
                'entry_price': round(entry_price, 2),
                'stop_loss': round(stop_loss, 2),
                'target_price': round(target_price, 2),
                'risk_reward_ratio': round(risk_reward, 2),
                'confidence': self._calculate_confidence(total_score, data)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating monthly score: {e}")
            return self._get_neutral_score()
    
    def _analyze_trend(self, data: pd.DataFrame) -> float:
        """
        Analyze trend component (30% weight)
        Score: 0-100
        
        Factors:
        - SMA alignment (20, 50, 200)
        - ADX strength
        - Monthly direction
        """
        score = 50.0  # Start neutral
        
        try:
            current_price = data['Close'].iloc[-1]
            
            # SMA alignment (40 points)
            sma_20 = data['SMA_20'].iloc[-1] if 'SMA_20' in data.columns and not data['SMA_20'].isna().all() else current_price
            sma_50 = data['SMA_50'].iloc[-1] if 'SMA_50' in data.columns and not data['SMA_50'].isna().all() else current_price
            sma_200 = data['SMA_200'].iloc[-1] if 'SMA_200' in data.columns and not data['SMA_200'].isna().all() else current_price
            
            # Bullish alignment: price > SMA_20 > SMA_50 > SMA_200
            if current_price > sma_20 > sma_50 > sma_200:
                score += 25  # Perfect bullish
            elif current_price > sma_20 > sma_50:
                score += 15  # Strong bullish
            elif current_price > sma_20:
                score += 10  # Mild bullish
            elif current_price < sma_20 < sma_50 < sma_200:
                score -= 25  # Perfect bearish
            elif current_price < sma_20 < sma_50:
                score -= 15  # Strong bearish
            elif current_price < sma_20:
                score -= 10  # Mild bearish
            
            # ADX strength (30 points)
            adx = data['ADX'].iloc[-1] if 'ADX' in data.columns and not data['ADX'].isna().all() else 20
            if adx > 50:
                score += 15  # Very strong trend
            elif adx > 40:
                score += 12
            elif adx > 25:
                score += 8  # Strong trend
            elif adx < 20:
                score -= 5  # Weak trend (risky)
            
            # Monthly direction (30 points)
            monthly_change = ((data['Close'].iloc[-1] - data['Close'].iloc[-30]) / data['Close'].iloc[-30]) * 100
            if monthly_change > 10:
                score += 15
            elif monthly_change > 5:
                score += 10
            elif monthly_change > 0:
                score += 5
            elif monthly_change < -10:
                score -= 15
            elif monthly_change < -5:
                score -= 10
            else:
                score -= 5
            
        except Exception as e:
            self.logger.error(f"Error analyzing trend: {e}")
        
        return max(0, min(100, score))
    
    def _analyze_momentum(self, data: pd.DataFrame) -> float:
        """
        Analyze momentum component (20% weight)
        Score: 0-100
        """
        score = 50.0
        
        try:
            # RSI (35 points)
            rsi = data['RSI'].iloc[-1] if 'RSI' in data.columns and not data['RSI'].isna().all() else 50
            if 40 <= rsi <= 60:
                score += 17  # Neutral/healthy
            elif 30 <= rsi < 40:
                score += 12  # Oversold but recovering
            elif rsi < 30:
                score += 5  # Very oversold (contrarian buy)
            elif 60 < rsi <= 70:
                score += 10  # Overbought but strong
            elif rsi > 70:
                score -= 10  # Overbought (risky)
            
            # MACD (35 points)
            macd = data['MACD'].iloc[-1] if 'MACD' in data.columns and not data['MACD'].isna().all() else 0
            macd_signal = data['MACD_signal'].iloc[-1] if 'MACD_signal' in data.columns and not data['MACD_signal'].isna().all() else 0
            macd_hist = data['MACD_histogram'].iloc[-1] if 'MACD_histogram' in data.columns and not data['MACD_histogram'].isna().all() else 0
            
            if macd > macd_signal and macd_hist > 0:
                score += 17  # Bullish crossover with positive histogram
            elif macd > macd_signal:
                score += 10  # Bullish crossover
            elif macd < macd_signal and macd_hist < 0:
                score -= 17  # Bearish crossover with negative histogram
            elif macd < macd_signal:
                score -= 10  # Bearish crossover
            
            # ROC 30-day (30 points)
            roc = data['ROC'].iloc[-1] if 'ROC' in data.columns and not data['ROC'].isna().all() else 0
            if roc > 20:
                score += 15
            elif roc > 10:
                score += 12
            elif roc > 5:
                score += 8
            elif roc > 0:
                score += 5
            elif roc < -20:
                score -= 15
            elif roc < -10:
                score -= 12
            elif roc < -5:
                score -= 8
            else:
                score -= 5
            
        except Exception as e:
            self.logger.error(f"Error analyzing momentum: {e}")
        
        return max(0, min(100, score))
    
    def _analyze_sentiment(self, news_sentiment: Optional[Dict[str, Any]], 
                           social_sentiment: Optional[Dict[str, Any]]) -> float:
        """
        Analyze sentiment component (25% weight)
        Score: 0-100
        """
        score = 50.0
        
        try:
            # News sentiment (60% of sentiment component)
            if news_sentiment:
                weighted_sent = news_sentiment.get('weighted_sentiment', 0.0)
                article_count = news_sentiment.get('total_articles', 0)
                confidence = news_sentiment.get('confidence', 0.0)
                
                # Convert -1 to +1 range to 0 to 100
                news_score = 50 + (weighted_sent * 50)
                
                # Adjust for article count (more articles = more confidence)
                if article_count > 20:
                    weight = 0.6
                elif article_count > 10:
                    weight = 0.5
                else:
                    weight = 0.3
                
                score = score * (1 - weight) + news_score * weight
            
            # Social sentiment (40% of sentiment component)
            if social_sentiment:
                social_score_raw = social_sentiment.get('average_score', 0)
                mentions = social_sentiment.get('total_mentions', 0)
                
                # Normalize social score to 0-100
                social_score = min(100, max(0, 50 + social_score_raw))
                
                # Adjust for mention count
                if mentions > 50:
                    weight = 0.4
                elif mentions > 20:
                    weight = 0.3
                else:
                    weight = 0.2
                
                score = score * (1 - weight) + social_score * weight
            
        except Exception as e:
            self.logger.error(f"Error analyzing sentiment: {e}")
        
        return max(0, min(100, score))
    
    def _analyze_divergences(self, data: pd.DataFrame) -> float:
        """
        Analyze divergences component (15% weight)
        Score: 0-100
        """
        score = 50.0
        
        try:
            # Price vs RSI divergence (35 points)
            if 'RSI' in data.columns and len(data) >= 20 and not data['RSI'].isna().all():
                price_trend = data['Close'].iloc[-1] - data['Close'].iloc[-20]
                rsi_trend = data['RSI'].iloc[-1] - data['RSI'].iloc[-20]
                
                # Bullish divergence: price down, RSI up
                if price_trend < 0 and rsi_trend > 0:
                    score += 17
                # Bearish divergence: price up, RSI down
                elif price_trend > 0 and rsi_trend < 0:
                    score -= 17
                # Confirmation: both same direction
                elif (price_trend > 0 and rsi_trend > 0) or (price_trend < 0 and rsi_trend < 0):
                    score += 8
            
            # Price vs MACD divergence (35 points)
            if 'MACD' in data.columns and len(data) >= 20 and not data['MACD'].isna().all():
                price_trend = data['Close'].iloc[-1] - data['Close'].iloc[-20]
                macd_trend = data['MACD'].iloc[-1] - data['MACD'].iloc[-20]
                
                if price_trend < 0 and macd_trend > 0:
                    score += 17
                elif price_trend > 0 and macd_trend < 0:
                    score -= 17
                elif (price_trend > 0 and macd_trend > 0) or (price_trend < 0 and macd_trend < 0):
                    score += 8
            
            # OBV trend (30 points)
            if 'OBV' in data.columns and len(data) >= 20 and not data['OBV'].isna().all():
                obv_trend = data['OBV'].iloc[-1] - data['OBV'].iloc[-20]
                price_trend = data['Close'].iloc[-1] - data['Close'].iloc[-20]
                
                # OBV confirms price
                if (obv_trend > 0 and price_trend > 0) or (obv_trend < 0 and price_trend < 0):
                    score += 15
                # OBV diverges from price
                elif obv_trend > 0 and price_trend < 0:
                    score += 10  # Bullish divergence
                elif obv_trend < 0 and price_trend > 0:
                    score -= 10  # Bearish divergence
            
        except Exception as e:
            self.logger.error(f"Error analyzing divergences: {e}")
        
        return max(0, min(100, score))
    
    def _analyze_volume(self, data: pd.DataFrame) -> float:
        """
        Analyze volume component (10% weight)
        Score: 0-100
        """
        score = 50.0
        
        try:
            # Volume trend (40 points)
            if 'Volume_SMA' in data.columns and not data['Volume_SMA'].isna().all():
                current_volume = data['Volume'].iloc[-1]
                avg_volume = data['Volume_SMA'].iloc[-1]
                volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
                
                if volume_ratio > 2.0:
                    score += 20  # High volume surge
                elif volume_ratio > 1.5:
                    score += 15
                elif volume_ratio > 1.2:
                    score += 10
                elif volume_ratio < 0.5:
                    score -= 10  # Low volume (lack of conviction)
            
            # VWAP position (30 points)
            if 'VWAP' in data.columns and not data['VWAP'].isna().all():
                current_price = data['Close'].iloc[-1]
                vwap = data['VWAP'].iloc[-1]
                
                if current_price > vwap * 1.02:
                    score += 15  # Above VWAP (institutional support)
                elif current_price > vwap:
                    score += 8
                elif current_price < vwap * 0.98:
                    score -= 15  # Below VWAP
                else:
                    score -= 8
            
            # MFI (30 points)
            if 'MFI' in data.columns and not data['MFI'].isna().all():
                mfi = data['MFI'].iloc[-1]
                
                if 40 <= mfi <= 60:
                    score += 15  # Balanced
                elif 30 <= mfi < 40:
                    score += 10  # Oversold
                elif mfi < 30:
                    score += 5  # Very oversold
                elif 60 < mfi <= 80:
                    score += 8
                elif mfi > 80:
                    score -= 10  # Overbought
            
        except Exception as e:
            self.logger.error(f"Error analyzing volume: {e}")
        
        return max(0, min(100, score))
    
    def _get_recommendation(self, score: float) -> Dict[str, Any]:
        """Get trading recommendation based on score"""
        if score >= self.strong_buy:
            return {
                'action': 'STRONG BUY',
                'emoji': '🟢🟢🟢',
                'position_size': '5-10%',
                'conviction': 'HIGH',
                'description': 'High conviction long opportunity'
            }
        elif score >= self.buy:
            return {
                'action': 'BUY',
                'emoji': '🟢🟢',
                'position_size': '3-5%',
                'conviction': 'GOOD',
                'description': 'Good entry opportunity'
            }
        elif score >= self.moderate_buy:
            return {
                'action': 'MODERATE BUY',
                'emoji': '🟢',
                'position_size': '1-3%',
                'conviction': 'MODERATE',
                'description': 'Decent setup, smaller position'
            }
        elif score >= self.hold:
            return {
                'action': 'HOLD / NEUTRAL',
                'emoji': '⚖️',
                'position_size': '0%',
                'conviction': 'NEUTRAL',
                'description': 'Wait for better setup'
            }
        elif score >= self.moderate_sell:
            return {
                'action': 'MODERATE SELL',
                'emoji': '🔴',
                'position_size': '-25-50%',
                'conviction': 'CAUTION',
                'description': 'Reduce position, take profits'
            }
        elif score >= self.sell:
            return {
                'action': 'SELL',
                'emoji': '🔴🔴',
                'position_size': '-50-75%',
                'conviction': 'WEAK',
                'description': 'Exit most of position'
            }
        else:
            return {
                'action': 'STRONG SELL',
                'emoji': '🔴🔴🔴',
                'position_size': '-100%',
                'conviction': 'HIGH RISK',
                'description': 'Exit completely, consider short'
            }
    
    def _calculate_trade_params(self, data: pd.DataFrame, score: float, 
                                 current_price: float) -> Tuple[float, float, float]:
        """
        Calculate entry, stop loss, and target prices
        
        Returns:
            Tuple of (entry_price, stop_loss, target_price)
        """
        # Entry price (current or slight pullback)
        entry_price = current_price
        
        # Stop loss based on score and ATR
        if 'ATR' in data.columns:
            atr = data['ATR'].iloc[-1]
        else:
            # Calculate simple ATR if not available
            atr = (data['High'] - data['Low']).tail(14).mean()
        
        # Adjust risk based on score
        if score >= 80:
            stop_pct = 0.06  # 6% stop for high conviction
            target_pct = 0.25  # 25% target
        elif score >= 60:
            stop_pct = 0.08
            target_pct = 0.20
        elif score >= 40:
            stop_pct = 0.05
            target_pct = 0.10
        else:
            stop_pct = 0.08
            target_pct = 0.15
        
        stop_loss = entry_price * (1 - stop_pct)
        target_price = entry_price * (1 + target_pct)
        
        return entry_price, stop_loss, target_price
    
    def _calculate_risk_reward(self, entry: float, stop: float, target: float) -> float:
        """Calculate risk/reward ratio"""
        risk = entry - stop
        reward = target - entry
        
        if risk <= 0:
            return 0.0
        
        return reward / risk
    
    def _calculate_confidence(self, score: float, data: pd.DataFrame) -> float:
        """
        Calculate confidence level (0-1)
        Based on data quality and indicator agreement
        """
        confidence = 0.5
        
        # Score distance from neutral
        score_confidence = abs(score - 50) / 50
        confidence += score_confidence * 0.3
        
        # Indicator availability
        indicator_count = len([col for col in data.columns if col not in ['Open', 'High', 'Low', 'Close', 'Volume']])
        if indicator_count > 15:
            confidence += 0.2
        elif indicator_count > 10:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _get_neutral_score(self) -> Dict[str, Any]:
        """Return neutral score in case of errors"""
        components = {
            'trend': {'score': 50.0},
            'momentum': {'score': 50.0},
            'sentiment': {'score': 50.0},
            'divergence': {'score': 50.0},
            'volume': {'score': 50.0}
        }
        
        return {
            'date': datetime.now().isoformat(),
            'total_score': 50.0,
            'trend_score': 50.0,
            'momentum_score': 50.0,
            'sentiment_score': 50.0,
            'divergence_score': 50.0,
            'volume_score': 50.0,
            'components': components,
            'recommendation': self._get_recommendation(50.0),
            'entry_price': 0.0,
            'stop_loss': 0.0,
            'target_price': 0.0,
            'risk_reward_ratio': 0.0,
            'confidence': 0.0
        }
    
    def generate_trading_plan(self, score_data: Dict[str, Any], 
                              symbol: str) -> Dict[str, Any]:
        """
        Generate comprehensive trading plan
        
        Args:
            score_data: Monthly score data
            symbol: Stock symbol
            
        Returns:
            Trading plan dictionary
        """
        recommendation = score_data['recommendation']
        
        return {
            'symbol': symbol,
            'date': score_data['date'],
            'action': recommendation['action'],
            'conviction': recommendation['conviction'],
            'score': score_data['total_score'],
            'entry_strategy': {
                'price': score_data['entry_price'],
                'method': 'Market order' if score_data['total_score'] > 80 else 'Limit order',
                'size': recommendation['position_size']
            },
            'risk_management': {
                'stop_loss': score_data['stop_loss'],
                'target': score_data['target_price'],
                'risk_reward': score_data['risk_reward_ratio'],
                'max_hold_days': 90
            },
            'confidence': score_data['confidence'],
            'notes': recommendation['description']
        }
