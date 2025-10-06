"""
🤖 Machine Learning Price Prediction Module
Multi-model ensemble for stock price forecasting with risk-aware predictions

DISCLAIMER: ML predictions are probabilistic estimates based on historical patterns.
They do NOT guarantee future returns. Always use with proper risk management.
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ML imports
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge, Lasso
from sklearn.svm import SVR
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
import os


class MLPredictor:
    """
    Machine Learning predictor for stock prices using ensemble methods
    
    Models used:
    - Random Forest: Captures non-linear patterns
    - Gradient Boosting: Sequential error correction
    - Ridge Regression: Linear trends with regularization
    - Support Vector Regression: Pattern recognition
    
    Features engineered:
    - Price momentum (returns, velocity, acceleration)
    - Technical indicators (RSI, MACD, Bollinger, ADX)
    - Volume dynamics (OBV, volume trends)
    - Statistical features (volatility, correlation)
    - Time-based features (day of week, month, quarter)
    """
    
    def __init__(self, config: Dict[str, Any] = None, gemini_analyzer=None):
        """
        Initialize ML predictor
        
        Args:
            config: Configuration dictionary with ML parameters
            gemini_analyzer: Optional GeminiAnalyzer for AI-enhanced predictions
        """
        self.config = config.get('ml_predictor', {}) if config else {}
        self.logger = logging.getLogger(__name__)
        self.gemini_analyzer = gemini_analyzer
        
        # Model parameters
        self.lookback_days = self.config.get('lookback_days', 60)  # Historical window
        self.forecast_days = self.config.get('forecast_days', 30)  # Prediction horizon
        self.retrain_interval = self.config.get('retrain_interval_days', 7)  # Weekly retrain
        self.min_training_samples = self.config.get('min_training_samples', 200)
        
        # Model weights for ensemble (adjusted for Gemini integration)
        if gemini_analyzer and gemini_analyzer.enabled:
            self.model_weights = {
                'random_forest': 0.25,      # Reduced to make room for Gemini
                'gradient_boost': 0.25,      # Reduced
                'ridge': 0.15,               # Reduced
                'svr': 0.10,                 # Reduced
                'gemini_ai': 0.25            # AI gets significant weight
            }
            self.logger.info("🤖 ML Predictor initialized with Gemini AI integration")
        else:
            self.model_weights = {
                'random_forest': 0.35,      # Best for non-linear patterns
                'gradient_boost': 0.30,      # Good for sequential learning
                'ridge': 0.20,               # Captures linear trends
                'svr': 0.15                  # Pattern recognition
            }
            self.logger.info("ML Predictor initialized (traditional mode)")
        
        # Initialize models
        self.models = self._initialize_models()
        self.scaler = StandardScaler()
        self.target_scaler = MinMaxScaler()
        
        # Model state
        self.is_trained = False
        self.last_training_date = None
        self.feature_names = []
        self.model_metrics = {}
        
        # Model persistence
        self.model_dir = self.config.get('model_dir', 'models')
        os.makedirs(self.model_dir, exist_ok=True)
    
    def _initialize_models(self) -> Dict[str, Any]:
        """Initialize ML models with optimized hyperparameters"""
        models = {
            'random_forest': RandomForestRegressor(
                n_estimators=100,
                max_depth=15,
                min_samples_split=10,
                min_samples_leaf=4,
                max_features='sqrt',
                random_state=42,
                n_jobs=-1
            ),
            'gradient_boost': GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.05,
                max_depth=5,
                min_samples_split=10,
                min_samples_leaf=4,
                subsample=0.8,
                random_state=42
            ),
            'ridge': Ridge(
                alpha=1.0,
                random_state=42
            ),
            'svr': SVR(
                kernel='rbf',
                C=1.0,
                epsilon=0.1,
                gamma='scale'
            )
        }
        return models
    
    def engineer_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Engineer comprehensive features for ML prediction
        
        Features include:
        - Price momentum (returns, velocity, acceleration)
        - Technical indicators (20+ indicators)
        - Volume dynamics
        - Statistical measures (volatility, skewness)
        - Time-based features
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataFrame with engineered features
        """
        df = data.copy()
        
        # ========== PRICE FEATURES ==========
        
        # Returns at multiple timeframes
        df['returns_1d'] = df['Close'].pct_change(1)
        df['returns_5d'] = df['Close'].pct_change(5)
        df['returns_10d'] = df['Close'].pct_change(10)
        df['returns_20d'] = df['Close'].pct_change(20)
        
        # Price velocity (rate of change)
        df['velocity_5d'] = df['returns_5d'] - df['returns_1d']
        df['velocity_10d'] = df['returns_10d'] - df['returns_5d']
        
        # Price acceleration (change in velocity)
        df['acceleration'] = df['velocity_5d'] - df['velocity_5d'].shift(5)
        
        # ========== TECHNICAL INDICATORS ==========
        
        # Moving averages
        for period in [5, 10, 20, 50]:
            df[f'sma_{period}'] = df['Close'].rolling(period).mean()
            df[f'ema_{period}'] = df['Close'].ewm(span=period).mean()
            df[f'price_to_sma_{period}'] = df['Close'] / df[f'sma_{period}']
        
        # RSI (Relative Strength Index)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        ema_12 = df['Close'].ewm(span=12).mean()
        ema_26 = df['Close'].ewm(span=26).mean()
        df['macd'] = ema_12 - ema_26
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']
        
        # Bollinger Bands
        sma_20 = df['Close'].rolling(20).mean()
        std_20 = df['Close'].rolling(20).std()
        df['bb_upper'] = sma_20 + (2 * std_20)
        df['bb_lower'] = sma_20 - (2 * std_20)
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / sma_20
        df['bb_position'] = (df['Close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # ATR (Average True Range) - Volatility
        high_low = df['High'] - df['Low']
        high_close = abs(df['High'] - df['Close'].shift())
        low_close = abs(df['Low'] - df['Close'].shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['atr'] = true_range.rolling(14).mean()
        df['atr_pct'] = df['atr'] / df['Close']
        
        # ADX (Average Directional Index) - Trend strength
        df['adx'] = self._calculate_adx(df)
        
        # ========== VOLUME FEATURES ==========
        
        # Volume changes
        df['volume_1d'] = df['Volume'].pct_change(1)
        df['volume_5d'] = df['Volume'].pct_change(5)
        df['volume_ratio'] = df['Volume'] / df['Volume'].rolling(20).mean()
        
        # OBV (On-Balance Volume)
        df['obv'] = (np.sign(df['Close'].diff()) * df['Volume']).fillna(0).cumsum()
        df['obv_ema'] = df['obv'].ewm(span=20).mean()
        
        # VWAP (Volume-Weighted Average Price)
        df['vwap'] = (df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()
        df['price_to_vwap'] = df['Close'] / df['vwap']
        
        # ========== STATISTICAL FEATURES ==========
        
        # Volatility at multiple windows
        df['volatility_5d'] = df['returns_1d'].rolling(5).std()
        df['volatility_10d'] = df['returns_1d'].rolling(10).std()
        df['volatility_20d'] = df['returns_1d'].rolling(20).std()
        
        # Price momentum
        df['momentum_5d'] = df['Close'] / df['Close'].shift(5) - 1
        df['momentum_10d'] = df['Close'] / df['Close'].shift(10) - 1
        
        # High-Low range
        df['hl_range'] = (df['High'] - df['Low']) / df['Close']
        df['hl_range_avg'] = df['hl_range'].rolling(10).mean()
        
        # ========== TIME-BASED FEATURES ==========
        
        if 'Date' in df.columns or df.index.name == 'Date':
            date_index = df.index if df.index.name == 'Date' else pd.to_datetime(df['Date'])
            df['day_of_week'] = date_index.dayofweek
            df['day_of_month'] = date_index.day
            df['month'] = date_index.month
            df['quarter'] = date_index.quarter
            df['is_month_start'] = date_index.is_month_start.astype(int)
            df['is_month_end'] = date_index.is_month_end.astype(int)
        
        # ========== LAG FEATURES ==========
        
        # Include past prices as features
        for lag in [1, 2, 3, 5, 10]:
            df[f'close_lag_{lag}'] = df['Close'].shift(lag)
            df[f'volume_lag_{lag}'] = df['Volume'].shift(lag)
        
        return df
    
    def _calculate_adx(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average Directional Index (ADX)"""
        high = df['High']
        low = df['Low']
        close = df['Close']
        
        # Directional movement
        plus_dm = high.diff()
        minus_dm = -low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        
        # True range
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Smoothed indicators
        atr = tr.rolling(period).mean()
        plus_di = 100 * (plus_dm.rolling(period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(period).mean() / atr)
        
        # ADX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(period).mean()
        
        return adx
    
    def prepare_training_data(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare features and target for training
        
        Args:
            data: DataFrame with engineered features
            
        Returns:
            (X, y): Features and target variable
        """
        df = data.copy()
        
        # Target: Future price change (% return over forecast horizon)
        df['target'] = df['Close'].shift(-self.forecast_days) / df['Close'] - 1
        
        # Drop rows with NaN (from feature engineering and target creation)
        df = df.dropna()
        
        if len(df) < self.min_training_samples:
            self.logger.warning(f"Limited data: {len(df)} samples (recommended: {self.min_training_samples}+)")
            if len(df) < 30:  # Absolute minimum
                raise ValueError(f"Insufficient data: {len(df)} samples, need at least 30")
        
        # Separate features and target
        target_col = 'target'
        feature_cols = [col for col in df.columns if col not in [
            'target', 'Open', 'High', 'Low', 'Close', 'Volume', 'Date',
            'Adj Close', 'Dividends', 'Stock Splits'
        ]]
        
        X = df[feature_cols]
        y = df[target_col]
        
        self.feature_names = feature_cols
        
        return X, y
    
    def train_models(self, data: pd.DataFrame, symbol: str) -> Dict[str, Any]:
        """
        Train ensemble of ML models
        
        Args:
            data: Historical stock data with OHLCV
            symbol: Stock ticker symbol
            
        Returns:
            Training metrics and model performance
        """
        self.logger.info(f"Training ML models for {symbol}...")
        
        try:
            # Engineer features
            df_features = self.engineer_features(data)
            
            # Prepare training data
            X, y = self.prepare_training_data(df_features)
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            y_scaled = self.target_scaler.fit_transform(y.values.reshape(-1, 1)).ravel()
            
            # Time series cross-validation
            tscv = TimeSeriesSplit(n_splits=5)
            
            # Train each model
            metrics = {}
            for name, model in self.models.items():
                self.logger.info(f"Training {name}...")
                
                # Cross-validation scores
                cv_scores = cross_val_score(
                    model, X_scaled, y_scaled, 
                    cv=tscv, scoring='r2', n_jobs=-1
                )
                
                # Train on full dataset
                model.fit(X_scaled, y_scaled)
                
                # Predictions
                y_pred = model.predict(X_scaled)
                
                # Calculate metrics
                mse = mean_squared_error(y_scaled, y_pred)
                mae = mean_absolute_error(y_scaled, y_pred)
                r2 = r2_score(y_scaled, y_pred)
                
                metrics[name] = {
                    'mse': float(mse),
                    'rmse': float(np.sqrt(mse)),
                    'mae': float(mae),
                    'r2': float(r2),
                    'cv_mean': float(cv_scores.mean()),
                    'cv_std': float(cv_scores.std())
                }
                
                self.logger.info(f"{name} - R²: {r2:.4f}, RMSE: {np.sqrt(mse):.4f}")
            
            # Update state
            self.is_trained = True
            self.last_training_date = datetime.now()
            self.model_metrics = metrics
            
            # Save models
            self._save_models(symbol)
            
            # Ensemble metrics (only for trained models, excluding Gemini AI)
            trained_model_names = list(metrics.keys())
            trained_model_weights = [self.model_weights[name] for name in trained_model_names]
            
            # Normalize weights to sum to 1.0
            weight_sum = sum(trained_model_weights)
            normalized_weights = [w / weight_sum for w in trained_model_weights]
            
            ensemble_r2 = np.average([m['r2'] for m in metrics.values()], 
                                     weights=normalized_weights)
            
            return {
                'symbol': symbol,
                'training_samples': len(X),
                'features_count': len(self.feature_names),
                'training_date': self.last_training_date.isoformat(),
                'individual_metrics': metrics,
                'ensemble_r2': float(ensemble_r2),
                'status': 'success'
            }
            
        except Exception as e:
            self.logger.error(f"Training failed for {symbol}: {e}")
            return {
                'symbol': symbol,
                'status': 'failed',
                'error': str(e)
            }
    
    def predict_price(self, data: pd.DataFrame, symbol: str, news_articles: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Predict future price using ensemble of models + Gemini AI
        
        Args:
            data: Recent historical data
            symbol: Stock ticker symbol
            news_articles: Optional news articles for Gemini analysis
            
        Returns:
            Prediction results with confidence intervals
        """
        if not self.is_trained:
            # Try to load saved models
            if not self._load_models(symbol):
                raise ValueError(f"No trained models found for {symbol}. Train first.")
        
        try:
            # Engineer features
            df_features = self.engineer_features(data)
            
            # Get latest features (most recent data point)
            latest_features = df_features[self.feature_names].iloc[-1:].values
            
            # Scale features
            latest_scaled = self.scaler.transform(latest_features)
            
            # Get predictions from each ML model
            predictions_scaled = {}
            for name, model in self.models.items():
                pred = model.predict(latest_scaled)[0]
                predictions_scaled[name] = pred
            
            # Current price
            current_price = data['Close'].iloc[-1]
            
            # Traditional ensemble prediction (weighted average of ML models)
            ml_weights_sum = sum(self.model_weights[name] for name in self.models.keys())
            ml_ensemble_pred_scaled = sum(
                predictions_scaled[name] * (self.model_weights[name] / ml_weights_sum)
                for name in self.models.keys()
            )
            
            # Inverse scale to get actual price change %
            ml_ensemble_pred = self.target_scaler.inverse_transform([[ml_ensemble_pred_scaled]])[0][0]
            ml_predicted_price = current_price * (1 + ml_ensemble_pred)
            
            # 🤖 GET GEMINI AI PREDICTION if available
            gemini_prediction = None
            final_predicted_price = ml_predicted_price
            final_predicted_change = ml_ensemble_pred
            
            if self.gemini_analyzer and self.gemini_analyzer.enabled and 'gemini_ai' in self.model_weights:
                try:
                    # Prepare technical data for Gemini
                    technical_data = {
                        'current_price': float(current_price),
                        'rsi': float(df_features['rsi'].iloc[-1]) if 'rsi' in df_features else 50.0,
                        'macd_signal': 'bullish' if df_features['macd_hist'].iloc[-1] > 0 else 'bearish' if 'macd_hist' in df_features else 'neutral',
                        'trend': 'bullish' if df_features['sma_20'].iloc[-1] < current_price else 'bearish' if 'sma_20' in df_features else 'neutral',
                        'volume_status': 'high' if df_features['volume_ratio'].iloc[-1] > 1.2 else 'low' if 'volume_ratio' in df_features else 'normal',
                        'volatility': float(df_features['volatility_20d'].iloc[-1] * 100) if 'volatility_20d' in df_features else 0.0
                    }
                    
                    gemini_prediction = self.gemini_analyzer.predict_price_movement_ai(
                        symbol, technical_data, news_articles or []
                    )
                    
                    if gemini_prediction:
                        gemini_change_pct = gemini_prediction.get('predicted_change_pct', 0.0) / 100.0
                        gemini_price = current_price * (1 + gemini_change_pct)
                        
                        # Combine ML and Gemini predictions
                        gemini_weight = self.model_weights.get('gemini_ai', 0.25)
                        ml_weight = 1.0 - gemini_weight
                        
                        final_predicted_price = (ml_predicted_price * ml_weight) + (gemini_price * gemini_weight)
                        final_predicted_change = (final_predicted_price / current_price) - 1
                        
                        self.logger.info(f"✅ Enhanced ML prediction with Gemini AI for {symbol}")
                except Exception as e:
                    self.logger.warning(f"Gemini prediction enhancement failed: {e}")
            
            # Calculate confidence intervals (using prediction spread)
            predictions_unscaled = [
                self.target_scaler.inverse_transform([[p]])[0][0]
                for p in predictions_scaled.values()
            ]
            std_dev = np.std(predictions_unscaled)
            
            # 95% confidence interval (±1.96 standard deviations)
            lower_bound = final_predicted_price - (1.96 * std_dev * current_price)
            upper_bound = final_predicted_price + (1.96 * std_dev * current_price)
            
            # Model agreement (lower std = higher agreement)
            agreement_score = max(0, 100 - (std_dev * 1000))  # Normalized to 0-100
            
            result = {
                'symbol': symbol,
                'current_price': float(current_price),
                'predicted_price': float(final_predicted_price),
                'predicted_change_pct': float(final_predicted_change * 100),
                'forecast_horizon_days': self.forecast_days,
                'prediction_date': datetime.now().isoformat(),
                'target_date': (datetime.now() + timedelta(days=self.forecast_days)).isoformat(),
                'confidence_interval': {
                    'lower': float(lower_bound),
                    'upper': float(upper_bound),
                    'std_dev': float(std_dev)
                },
                'model_agreement': float(agreement_score),
                'individual_predictions': {
                    name: {
                        'predicted_price': float(current_price * (1 + self.target_scaler.inverse_transform([[p]])[0][0])),
                        'predicted_change_pct': float(self.target_scaler.inverse_transform([[p]])[0][0] * 100)
                    }
                    for name, p in predictions_scaled.items()
                },
                'model_metrics': self.model_metrics,
                'status': 'success',
                'source': 'hybrid-gemini' if gemini_prediction else 'ml-only'
            }
            
            # Add Gemini details if available
            if gemini_prediction:
                result['gemini_prediction'] = {
                    'predicted_direction': gemini_prediction.get('predicted_direction'),
                    'predicted_change_pct': gemini_prediction.get('predicted_change_pct'),
                    'confidence': gemini_prediction.get('confidence'),
                    'target_price': gemini_prediction.get('target_price'),
                    'key_catalysts': gemini_prediction.get('key_catalysts', []),
                    'key_risks': gemini_prediction.get('key_risks', []),
                    'reasoning': gemini_prediction.get('reasoning')
                }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Prediction failed for {symbol}: {e}")
            return {
                'symbol': symbol,
                'status': 'failed',
                'error': str(e)
            }
    
    def generate_trading_signal(self, prediction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate trading signal from ML prediction
        
        Signal logic:
        - Strong Buy: Predicted gain >10%, agreement >70%
        - Buy: Predicted gain >5%, agreement >60%
        - Hold: Predicted change -2% to +5%, or low agreement
        - Sell: Predicted loss <-5%, agreement >60%
        - Strong Sell: Predicted loss <-10%, agreement >70%
        
        Args:
            prediction: Prediction dictionary from predict_price()
            
        Returns:
            Trading signal with recommendation
        """
        if prediction.get('status') != 'success':
            return {'signal': 'HOLD', 'reason': 'Prediction failed'}
        
        change_pct = prediction['predicted_change_pct']
        agreement = prediction['model_agreement']
        
        # Decision logic
        if change_pct > 10 and agreement > 70:
            signal = 'STRONG_BUY'
            confidence = 'High'
            action = 'Enter full position'
        elif change_pct > 5 and agreement > 60:
            signal = 'BUY'
            confidence = 'Moderate'
            action = 'Enter 50-75% position'
        elif change_pct < -10 and agreement > 70:
            signal = 'STRONG_SELL'
            confidence = 'High'
            action = 'Exit all positions, consider short'
        elif change_pct < -5 and agreement > 60:
            signal = 'SELL'
            confidence = 'Moderate'
            action = 'Reduce position by 50-75%'
        else:
            signal = 'HOLD'
            confidence = 'Low' if agreement < 50 else 'Moderate'
            action = 'Wait for better setup'
        
        return {
            'signal': signal,
            'confidence': confidence,
            'action': action,
            'predicted_change': change_pct,
            'model_agreement': agreement,
            'reasoning': self._explain_signal(change_pct, agreement, signal)
        }
    
    def _explain_signal(self, change_pct: float, agreement: float, signal: str) -> str:
        """Generate human-readable explanation for signal"""
        explanations = []
        
        if abs(change_pct) > 10:
            explanations.append(f"Large predicted move ({change_pct:+.1f}%)")
        elif abs(change_pct) > 5:
            explanations.append(f"Moderate predicted move ({change_pct:+.1f}%)")
        else:
            explanations.append(f"Small predicted move ({change_pct:+.1f}%)")
        
        if agreement > 70:
            explanations.append("Strong model consensus")
        elif agreement > 50:
            explanations.append("Moderate model consensus")
        else:
            explanations.append("Low model consensus - uncertainty high")
        
        return "; ".join(explanations)
    
    def backtest_predictions(self, data: pd.DataFrame, symbol: str) -> Dict[str, Any]:
        """
        Backtest ML prediction accuracy on historical data
        
        Args:
            data: Historical data spanning several forecast periods
            symbol: Stock ticker
            
        Returns:
            Backtest results with accuracy metrics
        """
        self.logger.info(f"Backtesting ML predictions for {symbol}...")
        
        try:
            # We need enough data: lookback + multiple forecast periods
            min_required = self.lookback_days + (self.forecast_days * 3)
            if len(data) < min_required:
                return {'status': 'failed', 'error': 'Insufficient data for backtesting'}
            
            # Walk-forward validation
            results = []
            
            # Step through time with forecast_days intervals
            for i in range(self.lookback_days, len(data) - self.forecast_days, self.forecast_days):
                # Training window
                train_data = data.iloc[i-self.lookback_days:i]
                
                # Train models
                self.train_models(train_data, symbol)
                
                # Predict
                prediction = self.predict_price(train_data, symbol)
                
                if prediction['status'] != 'success':
                    continue
                
                # Actual future price
                actual_future_price = data.iloc[i + self.forecast_days]['Close']
                predicted_price = prediction['predicted_price']
                current_price = prediction['current_price']
                
                # Actual change
                actual_change = (actual_future_price - current_price) / current_price * 100
                predicted_change = prediction['predicted_change_pct']
                
                # Check if within confidence interval
                in_confidence_interval = (
                    prediction['confidence_interval']['lower'] <= actual_future_price <= 
                    prediction['confidence_interval']['upper']
                )
                
                results.append({
                    'date': data.index[i],
                    'current_price': current_price,
                    'predicted_price': predicted_price,
                    'actual_price': actual_future_price,
                    'predicted_change': predicted_change,
                    'actual_change': actual_change,
                    'prediction_error': abs(predicted_change - actual_change),
                    'direction_correct': np.sign(predicted_change) == np.sign(actual_change),
                    'in_confidence_interval': in_confidence_interval
                })
            
            # Calculate aggregate metrics
            df_results = pd.DataFrame(results)
            
            direction_accuracy = (df_results['direction_correct'].sum() / len(df_results)) * 100
            mean_error = df_results['prediction_error'].mean()
            confidence_coverage = (df_results['in_confidence_interval'].sum() / len(df_results)) * 100
            
            return {
                'symbol': symbol,
                'total_predictions': len(results),
                'direction_accuracy_pct': float(direction_accuracy),
                'mean_absolute_error_pct': float(mean_error),
                'confidence_interval_coverage_pct': float(confidence_coverage),
                'predictions': results[-10:],  # Last 10 predictions
                'status': 'success'
            }
            
        except Exception as e:
            self.logger.error(f"Backtesting failed for {symbol}: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def _save_models(self, symbol: str):
        """Save trained models to disk"""
        model_path = os.path.join(self.model_dir, f"{symbol}_models.pkl")
        state = {
            'models': self.models,
            'scaler': self.scaler,
            'target_scaler': self.target_scaler,
            'feature_names': self.feature_names,
            'last_training_date': self.last_training_date,
            'model_metrics': self.model_metrics
        }
        joblib.dump(state, model_path)
        self.logger.info(f"Models saved to {model_path}")
    
    def _load_models(self, symbol: str) -> bool:
        """Load trained models from disk"""
        model_path = os.path.join(self.model_dir, f"{symbol}_models.pkl")
        if not os.path.exists(model_path):
            return False
        
        try:
            state = joblib.load(model_path)
            self.models = state['models']
            self.scaler = state['scaler']
            self.target_scaler = state['target_scaler']
            self.feature_names = state['feature_names']
            self.last_training_date = state['last_training_date']
            self.model_metrics = state['model_metrics']
            self.is_trained = True
            self.logger.info(f"Models loaded from {model_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to load models: {e}")
            return False
    
    def needs_retraining(self) -> bool:
        """Check if models need retraining based on time interval"""
        if not self.is_trained or self.last_training_date is None:
            return True
        
        days_since_training = (datetime.now() - self.last_training_date).days
        return days_since_training >= self.retrain_interval
