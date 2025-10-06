"""
🚀 AI Stock Trading Dashboard - Refactored with Monthly Signals
Professional trading interface with 0-100 scoring system
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import logging
import os

# Load environment variables FIRST (before any module that needs API keys)
from dotenv import load_dotenv
load_dotenv()  # Load .env file with API keys

# Import our custom modules
from modules.utils import (
    load_config, setup_logging, is_market_open, 
    format_currency, format_percentage, get_sentiment_emoji, get_trend_emoji,
    get_robust_ticker
)
from modules.database_manager import DatabaseManager
from modules.news_aggregator import NewsAggregator
from modules.sentiment_analyzer import SentimentAnalyzer
from modules.social_aggregator import SocialAggregator
from modules.technical_indicators import TechnicalIndicators
from modules.monthly_signals import MonthlySignals
from modules.alert_manager import AlertManager
from modules.portfolio_tracker import PortfolioTracker
from modules.backtester import Backtester
from modules.ml_predictor import MLPredictor
from modules.gemini_analyzer import GeminiAnalyzer
from modules.pro_mode_guard import ProModeGuard

# Configure page
st.set_page_config(
    page_title="AI Stock Trading Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #00ff88, #007aff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .score-badge {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem;
        border-radius: 15px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: rgba(255,255,255,0.05);
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(0,255,136,0.1);
        border-bottom: 2px solid #00ff88;
    }
</style>
""", unsafe_allow_html=True)

class TradingDashboard:
    """Main dashboard application"""
    
    def __init__(self):
        """Initialize dashboard with all components - Gemini-first architecture"""
        # Load configuration
        self.config = load_config()
        
        # Setup logging
        setup_logging(self.config.get('logging', {}))
        self.logger = logging.getLogger(__name__)
        
        # STEP 1: Initialize Gemini AI as the core intelligence
        self.gemini_analyzer = GeminiAnalyzer(self.config)
        if self.gemini_analyzer.enabled:
            self.logger.info("Gemini AI initialized - Enhanced intelligence mode activated")
        else:
            self.logger.warning("Gemini AI not available - Using traditional analysis")
        
        # STEP 2: Initialize database and core services
        self.db = DatabaseManager(self.config.get('database', {}))
        self.news_aggregator = NewsAggregator(self.config)
        self.social_aggregator = SocialAggregator(self.config)
        self.technical_indicators = TechnicalIndicators()
        
        # STEP 3: Initialize analysis modules with Gemini integration
        self.sentiment_analyzer = SentimentAnalyzer(self.config, self.gemini_analyzer)
        self.ml_predictor = MLPredictor(self.config, self.gemini_analyzer)
        
        # STEP 4: Initialize composite modules
        self.monthly_signals = MonthlySignals(
            self.config,
            self.sentiment_analyzer,
            self.technical_indicators
        )
        self.alert_manager = AlertManager(self.config)
        self.portfolio_tracker = PortfolioTracker(self.config, self.db)
        self.backtester = Backtester(self.config, self.monthly_signals, self.db)
        
        # Professional mode enforcement - ALWAYS ACTIVE
        self.pro_guard = ProModeGuard(self.config, self.db)
        
        # MANDATORY professional readiness validation
        try:
            self.pro_guard.ensure_production_ready(enforce=True)
            self.logger.info("Professional trading system operational")
        except RuntimeError as e:
            self.logger.error(f"Professional mode validation failed: {e}")
            st.error(f"SYSTEM ERROR: {e}")
            st.error("This is a professional trading tool. All safeguards must be operational.")
            st.stop()
        
        # Log initialization summary
        gemini_status = "ENABLED" if self.gemini_analyzer.enabled else "DISABLED"
        self.logger.info(f"Dashboard initialized successfully - Gemini AI: {gemini_status}")
    
    def _get_default_watchlist(self):
        """Get default watchlist from config"""
        watchlist_config = self.config.get('watchlist', {})
        if isinstance(watchlist_config, dict):
            return watchlist_config.get('stocks', [])
        elif isinstance(watchlist_config, list):
            return watchlist_config
        return []
    
    
    def _calculate_rsi(self, prices, period=14):
        """Calculate RSI for late entry detection"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if not rsi.empty else 50.0
    def _render_trending_stock_banner(self):
        """Render AI-powered trading opportunities at the top"""
        # Fast mode check - skip AI analysis if enabled (for instant loading)
        if st.session_state.get('fast_mode', True):
            if 'trading_opportunities' not in st.session_state:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.info("⚡ **Fast Mode Active** - AI market scan disabled for instant loading")
                with col2:
                    if st.button("🚀 Scan Market Now", key="enable_ai_scan", use_container_width=True):
                        st.session_state.fast_mode = False
                        st.rerun()
                return
        
        # Use session state to cache the analysis (refresh every 4 hours for faster loading)
        cache_duration_seconds = 4 * 3600  # 4 hours instead of 1 hour
        
        if 'trading_opportunities' not in st.session_state or \
           (datetime.now() - st.session_state.get('opportunities_timestamp', datetime.min)).total_seconds() > cache_duration_seconds:
            
            with st.spinner("🚀 AI scanning entire market for trading opportunities..."):
                # Fetch GENERAL market news (reduced from 100 to 50 for speed)
                all_news = self.news_aggregator.fetch_market_news(max_articles=50)
                
                if not all_news or len(all_news) < 5:  # Reduced threshold from 10 to 5
                    self.logger.warning(f"Insufficient market news: {len(all_news)} articles")
                    st.session_state.trading_opportunities = []
                    st.session_state.opportunities_timestamp = datetime.now()
                    return
                
                self.logger.info(f"Analyzing {len(all_news)} market articles with Gemini AI")
                
                # Optional: Get watchlist for prioritization (not restriction)
                watchlist = self._get_default_watchlist()
                
                # Analyze with Gemini to discover multiple opportunities
                analysis_result = self.gemini_analyzer.analyze_trending_stock(
                    all_news, 
                    watchlist=watchlist if watchlist else None
                )
                
                if analysis_result:
                    opportunities = analysis_result.get('opportunities', [])
                    
                    # If no opportunities list, handle old format
                    if not opportunities and 'trending_stock' in analysis_result:
                        # Legacy format - convert to new format
                        opportunities = [{
                            'ticker': analysis_result.get('trending_stock'),
                            'confidence': analysis_result.get('confidence', 0),
                            'reasoning': analysis_result.get('reasoning', ''),
                            'sentiment': analysis_result.get('sentiment', 'neutral'),
                            'key_topics': analysis_result.get('key_topics', []),
                            'news_count': analysis_result.get('news_count', 0),
                            'explosion_catalysts': analysis_result.get('explosion_catalysts', []),
                            'timeframe': analysis_result.get('timeframe', '7-30 days'),
                            'risk_level': analysis_result.get('risk_level', 'medium')
                        }]
                    
                    # ✅ NEWS VALIDATION: Fetch specific news for TOP 3 opportunities only (speed optimization)
                    top_opportunities = opportunities[:3]  # Validate only top 3
                    self.logger.info(f"📰 Fetching specific news for top {len(top_opportunities)} opportunities...")
                    for opp in top_opportunities:
                        symbol = opp.get('ticker')
                        try:
                            # Fetch symbol-specific news
                            symbol_news = self.news_aggregator.fetch_all_news(symbol)
                            opp['specific_news'] = symbol_news
                            opp['specific_news_count'] = len(symbol_news)
                            
                            self.logger.info(f"  📰 {symbol}: {len(symbol_news)} specific articles")
                            
                            # Validate with Gemini using specific news
                            if symbol_news and len(symbol_news) >= 3:
                                validation = self.gemini_analyzer.validate_opportunity(
                                    symbol, opp, symbol_news
                                )
                                if validation:
                                    opp['validation'] = validation
                                    opp['confirmed'] = validation.get('confirmed', True)
                                    opp['validation_confidence'] = validation.get('confidence', opp['confidence'])
                                    opp['red_flags'] = validation.get('red_flags', [])
                                    opp['validation_reasoning'] = validation.get('reasoning', '')
                                    
                                    self.logger.info(f"  ✅ {symbol}: Validated (Confirmed: {validation.get('confirmed')}, Confidence: {validation.get('confidence')}%)")
                            else:
                                opp['confirmed'] = True  # No news to contradict
                                self.logger.warning(f"  ⚠️ {symbol}: Insufficient news for validation ({len(symbol_news)} articles)")
                                
                        except Exception as e:
                            self.logger.error(f"  ❌ {symbol}: News validation failed - {e}")
                            opp['specific_news'] = []
                            opp['confirmed'] = True  # Benefit of the doubt
                    
                    # Mark remaining opportunities as not validated (skip for speed)
                    for opp in opportunities[3:]:
                        opp['confirmed'] = True
                        opp['specific_news'] = []
                        opp['specific_news_count'] = 0
                    
                    # ⚠️ LATE ENTRY RISK CHECK for TOP 3 opportunities only (speed optimization)
                    for opp in top_opportunities:  # Only check top 3
                        symbol = opp.get('ticker')
                        try:
                            ticker = get_robust_ticker(symbol)
                            hist = ticker.history(period="3mo")
                            
                            if not hist.empty:
                                current_price = hist['Close'].iloc[-1]
                                price_data = {
                                    'current_price': float(current_price),
                                    'change_1d': float((hist['Close'].iloc[-1] / hist['Close'].iloc[-2] - 1) * 100) if len(hist) > 1 else 0,
                                    'change_5d': float((hist['Close'].iloc[-1] / hist['Close'].iloc[-6] - 1) * 100) if len(hist) > 5 else 0,
                                    'change_20d': float((hist['Close'].iloc[-1] / hist['Close'].iloc[-21] - 1) * 100) if len(hist) > 20 else 0,
                                    'rsi': float(self._calculate_rsi(hist['Close'])),
                                    'distance_from_ma20': float((current_price / hist['Close'].rolling(20).mean().iloc[-1] - 1) * 100) if len(hist) > 20 else 0,
                                    'distance_from_ma50': float((current_price / hist['Close'].rolling(50).mean().iloc[-1] - 1) * 100) if len(hist) > 50 else 0,
                                    'volume_ratio': float(hist['Volume'].iloc[-1] / hist['Volume'].rolling(20).mean().iloc[-1]) if len(hist) > 20 else 1,
                                    'distance_from_52w_high': float((current_price / hist['Close'].max() - 1) * 100)
                                }
                                
                                # Get late entry risk assessment
                                late_entry_risk = self.gemini_analyzer.detect_late_entry_risk(
                                    symbol, price_data, all_news[:20]  # Reduced from 30 to 20 articles
                                )
                                opp['late_entry_risk'] = late_entry_risk
                                
                                self.logger.info(f"⚠️ Late entry risk for {symbol}: {late_entry_risk.get('late_entry_risk')}")
                        except Exception as e:
                            self.logger.warning(f"Could not assess late entry risk for {symbol}: {e}")
                            opp['late_entry_risk'] = None
                    
                    # Skip late entry risk for remaining opportunities (for speed)
                    for opp in opportunities[3:]:
                        opp['late_entry_risk'] = None
                    
                    st.session_state.trading_opportunities = opportunities
                    st.session_state.market_overview = analysis_result.get('market_overview', '')
                    st.session_state.opportunities_timestamp = datetime.now()
                    
                    self.logger.info(f"✅ AI identified {len(opportunities)} trading opportunities")
                    
                    # 🚨 Send alerts for LOW RISK opportunities (prioritize them)
                    low_risk_opportunities = [opp for opp in opportunities if opp.get('risk_level') == 'low']
                    if low_risk_opportunities:
                        self.logger.info(f"🚨 Sending alerts for {len(low_risk_opportunities)} LOW RISK opportunities...")
                        for opp in low_risk_opportunities:
                            symbol = opp.get('ticker', 'N/A')
                            try:
                                if self.alert_manager.send_opportunity_alert(opp):
                                    self.logger.info(f"✅ Alert sent successfully for {symbol}")
                                else:
                                    self.logger.warning(f"⚠️ Failed to send alert for {symbol}")
                            except Exception as e:
                                self.logger.error(f"❌ Error sending alert for {symbol}: {e}")
        
        # Display trading opportunities
        if 'trading_opportunities' in st.session_state and st.session_state.trading_opportunities:
            opportunities = st.session_state.trading_opportunities
            market_overview = st.session_state.get('market_overview', '')
            
            # Display market overview if available
            if market_overview:
                st.info(f"📊 **Market Overview:** {market_overview}")
            
            # Display each opportunity
            for idx, data in enumerate(opportunities):
                symbol = data.get('ticker', 'N/A')
                confidence = data.get('confidence', 0)
                reasoning = data.get('reasoning', '')
                sentiment = data.get('sentiment', 'neutral')
                news_count = data.get('news_count', 0)
                catalysts = data.get('explosion_catalysts', data.get('key_topics', []))
                timeframe = data.get('timeframe', '7-30 days')
                risk_level = data.get('risk_level', 'medium')
                
                # Color based on risk level (sorted low to high)
                if risk_level == 'low':
                    bg_color = "rgba(0, 255, 136, 0.15)"
                    border_color = "#00ff88"
                    emoji = "💎"
                    label = "LOW RISK OPPORTUNITY"
                elif risk_level == 'medium':
                    bg_color = "rgba(255, 200, 0, 0.15)"
                    border_color = "#ffc800"
                    emoji = "🚀"
                    label = "MEDIUM RISK OPPORTUNITY"
                else:  # high
                    bg_color = "rgba(255, 100, 100, 0.15)"
                    border_color = "#ff6464"
                    emoji = "⚡"
                    label = "HIGH RISK OPPORTUNITY"
                
                # Risk badge color
                risk_colors = {
                    'low': '#00ff88',
                    'medium': '#ffc800',
                    'high': '#ff6464'
                }
                risk_color = risk_colors.get(risk_level, '#6496ff')
                
                # Catalysts display
                catalysts_html = " • ".join(catalysts[:3]) if catalysts else "Multiple factors"
                
                # ✅ Display validation status if present
                validation_section = ""
                if data.get('validation'):
                    validation = data['validation']
                    confirmed = validation.get('confirmed', True)
                    val_confidence = validation.get('confidence', confidence)
                    # Convert confidence_change to int/float if it's a string
                    confidence_change = validation.get('confidence_change', 0)
                    if isinstance(confidence_change, str):
                        try:
                            confidence_change = float(confidence_change)
                        except (ValueError, TypeError):
                            confidence_change = 0
                    val_reasoning = validation.get('reasoning', '')
                    red_flags = validation.get('red_flags', [])
                    recommendation = validation.get('recommendation', 'NEUTRAL')
                    news_alignment = validation.get('news_alignment', 'Unknown')
                    updated_risk = validation.get('updated_risk_level', risk_level)
                    
                    if confirmed:
                        val_color = '#00ff88' if recommendation == 'STRONG_CONFIRM' else '#ffc800'
                        val_emoji = '✅' if recommendation == 'STRONG_CONFIRM' else '👍'
                        val_title = 'VALIDATED' if recommendation == 'STRONG_CONFIRM' else 'CONFIRMED'
                    else:
                        val_color = '#ff4444'
                        val_emoji = '❌'
                        val_title = 'REJECTED'
                    
                    # Build red flags list
                    red_flags_html = ''.join([f'<li style="color: #ff6464;">{flag}</li>' for flag in red_flags]) if red_flags else '<li>None detected</li>'
                    
                    validation_section = (
                        f"<div style='background: rgba(100,150,255,0.15); border: 2px solid {val_color}; "
                        f"padding: 1rem; border-radius: 8px; margin: 1rem 0;'>"
                        f"<strong style='color: {val_color};'>{val_emoji} NEWS VALIDATION: {val_title}</strong>"
                        f"<p style='margin: 0.5rem 0; font-size: 0.95rem;'>"
                        f"Confidence: {val_confidence}% ({'+' if confidence_change > 0 else ''}{confidence_change}) | "
                        f"News Alignment: {news_alignment} | "
                        f"Updated Risk: {updated_risk.upper()}</p>"
                        f"<p style='margin: 0.5rem 0; font-size: 0.9rem; color: #ddd;'>{val_reasoning}</p>"
                        f"<details style='margin-top: 0.5rem;'>"
                        f"<summary style='cursor: pointer; color: {val_color};'>Red Flags ({len(red_flags)})</summary>"
                        f"<ul style='margin: 0.5rem 0; padding-left: 1.5rem;'>{red_flags_html}</ul>"
                        f"</details></div>"
                    )
                
                # ⚠️ Display late entry risk warning if present
                late_entry_warning = ""
                if data.get('late_entry_risk'):
                    late_risk = data['late_entry_risk']
                    risk_level_entry = late_risk.get('late_entry_risk', 'LOW')
                    
                    if risk_level_entry in ['HIGH', 'CRITICAL']:
                        warning_color = '#ff4444' if risk_level_entry == 'CRITICAL' else '#ff9500'
                        warning_emoji = '🚨' if risk_level_entry == 'CRITICAL' else '⚠️'
                        action = late_risk.get('recommended_action', 'WAIT')
                        risk_score = late_risk.get('risk_score', 0)
                        reasoning_text = late_risk.get('reasoning', '')
                        
                        # Build risk list HTML separately
                        risk_items = ''.join([f'<li>{risk}</li>' for risk in late_risk.get('key_risks', [])])
                        
                        # Build late entry warning HTML with single quotes to avoid conflicts
                        late_entry_warning = (
                            f"<div style='background: rgba(255,68,68,0.15); border: 2px solid {warning_color}; "
                            f"padding: 1rem; border-radius: 8px; margin: 1rem 0;'>"
                            f"<strong style='color: {warning_color};'>{warning_emoji} LATE ENTRY RISK: {risk_level_entry}</strong>"
                            f"<p style='margin: 0.5rem 0; font-size: 0.95rem;'>Risk Score: {risk_score}% | Action: {action}</p>"
                            f"<p style='margin: 0.5rem 0; font-size: 0.9rem; color: #ccc;'>{reasoning_text}</p>"
                            f"<details style='margin-top: 0.5rem;'>"
                            f"<summary style='cursor: pointer; color: {warning_color};'>Key Risks</summary>"
                            f"<ul style='margin: 0.5rem 0; padding-left: 1.5rem;'>{risk_items}</ul>"
                            f"</details></div>"
                        )
                
                # Build main card HTML - separate header and content to avoid escaping issues
                header_html = f"""<div style="background: {bg_color}; border-left: 6px solid {border_color}; padding: 1.5rem; border-radius: 10px; margin: 1rem 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <h2 style="margin:0; color: {border_color};">#{idx+1} {emoji} {label}: <strong style="font-size: 1.4em;">{symbol}</strong></h2>
                        <span style="background: {risk_color}; color: white; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.85rem; font-weight: bold;">
                            RISK: {risk_level.upper()}
                        </span>
                    </div>"""
                
                content_html = f"""<p style="margin: 0.8rem 0; font-size: 1.1rem; line-height: 1.5; color: #fff;">{reasoning}</p>
                    <div style="background: rgba(0,0,0,0.2); padding: 0.8rem; border-radius: 5px; margin: 0.8rem 0;">
                        <strong style="color: {border_color};">⚡ Catalysts:</strong> {catalysts_html}
                    </div>
                    <div style="display: flex; gap: 2rem; margin-top: 1rem; font-size: 0.95rem; flex-wrap: wrap;">
                        <span>🎯 <strong>Confidence:</strong> {confidence}%</span>
                        <span>📰 <strong>Articles:</strong> {news_count}</span>
                        <span>💹 <strong>Sentiment:</strong> {sentiment.upper()}</span>
                        <span>⏱️ <strong>Timeframe:</strong> {timeframe}</span>
                        <span>🤖 <strong>Source:</strong> {data.get('source', 'AI')}</span>
                    </div>
                </div>"""
                
                # Combine parts - validation_section and late_entry_warning are already HTML
                main_html = header_html + validation_section + late_entry_warning + content_html
                
                st.markdown(main_html, unsafe_allow_html=True)
                
                # Add quick action buttons for each opportunity
                col1, col2, col3, col4 = st.columns([1.5, 1.5, 1, 3])
                with col1:
                    if st.button(f"📊 Deep Analysis {symbol}", key=f"analyze_opp_{idx}", width='stretch'):
                        # Add to watchlist if not present
                        if symbol not in st.session_state.watchlist:
                            st.session_state.watchlist.append(symbol)
                            self.db.add_to_watchlist(symbol)
                        st.session_state.selected_symbol = symbol
                        st.rerun()
                with col2:
                    if st.button(f"➕ Add {symbol}", key=f"add_opp_{idx}", width='stretch'):
                        if symbol not in st.session_state.watchlist:
                            st.session_state.watchlist.append(symbol)
                            self.db.add_to_watchlist(symbol)
                            st.success(f"✅ {symbol} added!")
                            st.rerun()
                        else:
                            st.info(f"{symbol} already in watchlist")
                with col3:
                    if idx == 0:  # Only show refresh on first opportunity
                        if st.button("🔄 Refresh", key="refresh_opportunities", width='stretch'):
                            if 'trading_opportunities' in st.session_state:
                                del st.session_state.trading_opportunities
                            st.rerun()
    
    def run(self):
        """Run the main dashboard application"""
        # Header
        st.markdown('<div class="main-header">🛡️ Professional Trading System</div>', unsafe_allow_html=True)
        
        # Fast loading mode toggle (in sidebar, before heavy operations)
        if 'fast_mode' not in st.session_state:
            st.session_state.fast_mode = True  # Default to fast mode for instant loading
        st.markdown("**Institutional-Grade Market Analysis & Signal Generation**")
        
        # System status indicator
        st.success("🔒 **PROFESSIONAL SYSTEM OPERATIONAL** - All safeguards active")
        
        # Real-time market status
        market_open = is_market_open()
        if market_open:
            st.info("🟢 **MARKETS OPEN** - Live trading signals active")
        else:
            st.info("🔴 **MARKETS CLOSED** - Pre-market analysis mode")
        
        # AI-Powered Trending Stock Highlight
        self._render_trending_stock_banner()
        
        # Sidebar
        self._render_sidebar()
        
        # Market status indicator
        market_open = is_market_open()
        status_icon = "🟢" if market_open else "🔴"
        status_text = "MARKET OPEN" if market_open else "MARKET CLOSED"
        st.sidebar.markdown(f"### {status_icon} {status_text}")
        
        # Main tabs
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
            "🚨 Live Alerts",
            "⚡ Intraday Trading",
            "📊 Monthly Signals",
            "📰 News & Sentiment", 
            "💼 Portfolio",
            "📈 Technical Analysis",
            "🔮 ML Predictions",
            "🔙 Backtesting",
            "⚙️ Settings"
        ])
        
        with tab1:
            self._render_live_alerts()
        
        with tab2:
            self._render_intraday_trading()
        
        with tab3:
            self._render_monthly_signals()
        
        with tab4:
            self._render_news_sentiment()
        
        with tab5:
            self._render_portfolio()
        
        with tab6:
            self._render_technical_analysis()
        
        with tab7:
            self._render_ml_predictions()
        
        with tab8:
            self._render_backtesting()
        
        with tab9:
            self._render_settings()
        
        # Footer
        self._render_footer()
    
    def _render_sidebar(self):
        """Render sidebar controls"""
        st.sidebar.header("📊 Trading Dashboard")
        st.sidebar.markdown("---")
        
        # Performance mode toggle
        st.sidebar.subheader("⚡ Performance Mode")
        fast_mode = st.sidebar.checkbox(
            "Fast Loading (Skip AI Market Scan)",
            value=st.session_state.get('fast_mode', True),
            help="Enable for instant loading. Disable to scan entire market with AI at startup."
        )
        if fast_mode != st.session_state.get('fast_mode', True):
            st.session_state.fast_mode = fast_mode
            if not fast_mode and 'trading_opportunities' in st.session_state:
                del st.session_state.trading_opportunities  # Force refresh
            st.rerun()
        
        # Manual scan button (always available)
        if st.sidebar.button("🚀 Scan Market Now", use_container_width=True, type="primary" if fast_mode else "secondary"):
            if 'trading_opportunities' in st.session_state:
                del st.session_state.trading_opportunities
            st.session_state.fast_mode = False  # Temporarily disable fast mode
            st.rerun()
        
        st.sidebar.markdown("---")
        
        # Stock selection - Use config or database
        watchlist = self._get_default_watchlist()
        
        # Get saved watchlist from database (priority over config)
        db_watchlist = self.db.get_watchlist()
        if db_watchlist:
            watchlist = [item['symbol'] for item in db_watchlist]
        
        # Store in session state
        if 'watchlist' not in st.session_state:
            st.session_state.watchlist = watchlist
        
        st.sidebar.subheader("🎯 Select Stock")
        symbol = st.sidebar.selectbox(
            "Watchlist:",
            options=st.session_state.watchlist,
            index=0,
            key='selected_symbol'
        )
        
        # Add custom symbol
        with st.sidebar.expander("➕ Add Custom Symbol"):
            new_symbol = st.text_input("Symbol:", key='new_symbol').upper()
            if st.button("Add to Watchlist") and new_symbol:
                if new_symbol not in st.session_state.watchlist:
                    st.session_state.watchlist.append(new_symbol)
                    self.db.add_to_watchlist(new_symbol)
                    st.success(f"Added {new_symbol}!")
                    st.rerun()
        
        # Time period
        st.sidebar.subheader("📅 Analysis Period")
        period = st.sidebar.selectbox(
            "Period:",
            options=['1mo', '3mo', '6mo', '1y', '2y', '5y'],
            index=3,
            key='analysis_period'
        )
        
        st.sidebar.markdown("---")
        
        # Quick actions
        st.sidebar.subheader("⚡ Quick Actions")
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("🔄 Refresh", width='stretch'):
                st.cache_data.clear()
                st.rerun()
        
        with col2:
            if st.button("🔔 Alerts", width='stretch'):
                st.session_state.show_alerts = True
        
        # Display recent alerts
        if st.session_state.get('show_alerts', False):
            with st.sidebar.expander("📬 Recent Alerts", expanded=True):
                recent_alerts = self.db.get_recent_alerts(limit=5)
                if recent_alerts:
                    for alert in recent_alerts:
                        priority_emoji = "🔴" if alert['priority'] == 'CRITICAL' else "🟡" if alert['priority'] == 'HIGH' else "🔵"
                        st.caption(f"{priority_emoji} {alert['alert_type']}: {alert['symbol']}")
                        st.caption(f"_{alert['message']}_")
                        st.caption(f"⏰ {alert['timestamp']}")
                        st.divider()
                else:
                    st.info("No recent alerts")
        
        return symbol, period
    
    def _render_live_alerts(self):
        """Render live alerts and monitoring status - NEW TAB"""
        st.header("🚨 Live Alerts & Real-Time Monitoring")
        
        # Status row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            premarket_running = self._check_monitor_status('premarket_catalyst_scanner')
            status = "🟢 ONLINE" if premarket_running else "🔴 OFFLINE"
            st.metric("🌅 Premarket Scanner", status)
            if not premarket_running:
                if st.button("▶️ Start Premarket"):
                    st.info("Launching premarket scanner...")
                    st.code("python scripts/launch_trading_system.py --premarket")
        
        with col2:
            realtime_running = self._check_monitor_status('realtime_pump_scanner')
            status = "🟢 ONLINE" if realtime_running else "🔴 OFFLINE"
            st.metric("💎 Realtime Scanner", status)
            if not realtime_running:
                if st.button("▶️ Start Realtime"):
                    st.info("Launching realtime scanner...")
                    st.code("python scripts/launch_trading_system.py --realtime")
        
        with col3:
            market_open = is_market_open()
            market_status = "🟢 OPEN" if market_open else "🔴 CLOSED"
            st.metric("📊 Market Status", market_status)
        
        with col4:
            # Count today's alerts
            alerts = self.db.get_recent_alerts(limit=1000)
            today_alerts = [a for a in alerts if a['timestamp'].startswith(datetime.now().strftime('%Y-%m-%d'))]
            st.metric("📬 Alerts Today", len(today_alerts))
        
        st.divider()
        
        # Recent alerts section
        st.subheader("📋 Recent Alerts (Last 24 hours)")
        
        # Fetch alerts
        recent_alerts = self.db.get_recent_alerts(limit=50)
        
        if not recent_alerts:
            st.info("No recent alerts. The monitoring system will alert you when opportunities are detected.")
            st.info("💡 **Tip**: Start the monitoring system to receive real-time alerts")
            return
        
        # Filter controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            priority_filter = st.multiselect(
                "Filter by Priority",
                options=['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'],
                default=['CRITICAL', 'HIGH']
            )
        
        with col2:
            alert_type_filter = st.multiselect(
                "Filter by Type",
                options=['PREMARKET_CATALYST', 'PUMP_STOCK', 'MONTHLY_SIGNAL', 'PRICE_MOVE', 'VOLUME_SURGE'],
                default=None
            )
        
        with col3:
            show_count = st.slider("Show alerts", min_value=10, max_value=100, value=20, step=10)
        
        # Filter alerts
        filtered_alerts = recent_alerts
        
        if priority_filter:
            filtered_alerts = [a for a in filtered_alerts if a.get('priority') in priority_filter]
        
        if alert_type_filter:
            filtered_alerts = [a for a in filtered_alerts if a.get('alert_type') in alert_type_filter]
        
        filtered_alerts = filtered_alerts[:show_count]
        
        # Display alerts
        st.write(f"**Showing {len(filtered_alerts)} alerts**")
        
        for alert in filtered_alerts:
            priority = alert.get('priority', 'MEDIUM')
            alert_type = alert.get('alert_type', 'UNKNOWN')
            symbol = alert.get('symbol', 'N/A')
            message = alert.get('message', '')
            timestamp = alert.get('timestamp', '')
            score = alert.get('score', 0)
            
            # Color coding
            if priority == 'CRITICAL':
                border_color = "#ff0000"
                emoji = "🔴"
            elif priority == 'HIGH':
                border_color = "#ff9500"
                emoji = "🟡"
            elif priority == 'MEDIUM':
                border_color = "#00a8ff"
                emoji = "🔵"
            else:
                border_color = "#888888"
                emoji = "⚪"
            
            # Display alert card
            with st.container():
                st.markdown(f"""
                <div style="
                    border-left: 4px solid {border_color};
                    padding: 1rem;
                    margin: 0.5rem 0;
                    background: rgba(255,255,255,0.03);
                    border-radius: 5px;
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong style="font-size: 1.1rem;">{emoji} {symbol} - {alert_type}</strong>
                            <span style="color: #888; margin-left: 1rem; font-size: 0.9rem;">{timestamp}</span>
                        </div>
                        <div style="text-align: right;">
                            <span style="font-size: 1.2rem; font-weight: bold;">Score: {score:.1f}</span>
                        </div>
                    </div>
                    <div style="margin-top: 0.5rem; white-space: pre-wrap; font-family: monospace; font-size: 0.9rem;">
                        {message}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        
        # Alert statistics
        st.subheader("📊 Alert Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            critical_count = sum(1 for a in recent_alerts if a.get('priority') == 'CRITICAL')
            st.metric("🔴 Critical", critical_count)
        
        with col2:
            high_count = sum(1 for a in recent_alerts if a.get('priority') == 'HIGH')
            st.metric("🟡 High", high_count)
        
        with col3:
            medium_count = sum(1 for a in recent_alerts if a.get('priority') == 'MEDIUM')
            st.metric("🔵 Medium", medium_count)
        
        with col4:
            unique_symbols = len(set(a.get('symbol') for a in recent_alerts))
            st.metric("📊 Unique Symbols", unique_symbols)
        
        # Alert timeline chart
        if recent_alerts:
            st.subheader("📈 Alert Timeline (Last 24h)")
            
            # Convert to DataFrame
            df = pd.DataFrame(recent_alerts)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            
            # Group by hour
            hourly_counts = df.groupby('hour').size().reindex(range(24), fill_value=0)
            
            # Create bar chart
            fig = px.bar(
                x=hourly_counts.index,
                y=hourly_counts.values,
                labels={'x': 'Hour of Day', 'y': 'Number of Alerts'},
                title='Alerts Distribution by Hour'
            )
            fig.update_traces(marker_color='#00ff88')
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Quick actions
        st.subheader("⚡ Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🎛️ Open Control Center"):
                st.info("Opening Control Center...")
                st.code("streamlit run scripts/control_center.py --server.port 8502")
        
        with col2:
            if st.button("🧪 Test Alert System"):
                st.info("Testing alert channels...")
                try:
                    results = self.alert_manager.test_alerts()
                    st.success("**Test Results:**")
                    for channel, success in results.items():
                        status = "✅" if success else "❌"
                        st.write(f"{status} {channel.upper()}")
                except Exception as e:
                    st.error(f"Test failed: {e}")
        
        with col3:
            if st.button("🔄 Refresh Alerts"):
                st.rerun()
    
    def _check_monitor_status(self, script_name: str) -> bool:
        """Check if a monitor script is running"""
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info['cmdline']
                    if cmdline and any(script_name in arg for arg in cmdline):
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return False
        except:
            return False
    
    def _render_intraday_trading(self):
        """Render intraday trading tab"""
        st.header("⚡ Intraday Trading - Système Automatique")
        
        st.markdown("""
        ### 🚀 Trading Intraday 100% Automatique
        
        Recevez des **notifications Telegram** pour chaque opportunité de trading intraday :
        - 📈 **Entry signals** avec prix, stop loss, target
        - 💰 **Exit signals** avec profit/perte
        - 🔔 **Auto-close** avant 16h (pas de risque overnight)
        
        **Heures actives**: 9:30-16:00 ET (lundi-vendredi)
        """)
        
        # Status du système
        st.markdown("---")
        st.subheader("📊 Status du Système")
        
        col1, col2, col3 = st.columns(3)
        
        # Vérifier si le scanner tourne
        with col1:
            intraday_running = self._check_monitor_status("intraday_trader.py")
            if intraday_running:
                st.success("✅ **Scanner Intraday**")
                st.write("Status: 🟢 ONLINE")
            else:
                st.error("❌ **Scanner Intraday**")
                st.write("Status: 🔴 OFFLINE")
                if st.button("▶️ Démarrer", key="start_intraday"):
                    st.info("Exécutez: `python scripts/intraday_trader.py`")
        
        with col2:
            # Heures de marché
            import pytz
            et_tz = pytz.timezone('America/New_York')
            now_et = datetime.now(et_tz)
            is_market_hours = (now_et.weekday() < 5 and 
                             now_et.hour >= 9 and 
                             (now_et.hour < 16 or (now_et.hour == 9 and now_et.minute >= 30)))
            
            if is_market_hours:
                st.success("✅ **Heures de Marché**")
                st.write(f"🕐 {now_et.strftime('%H:%M:%S ET')}")
            else:
                st.warning("⏰ **Hors Heures Marché**")
                st.write(f"🕐 {now_et.strftime('%H:%M:%S ET')}")
        
        with col3:
            # Alertes aujourd'hui
            try:
                alerts = self.db_manager.get_active_alerts()
                today_alerts = [a for a in alerts if 
                              'intraday' in a.get('alert_type', '').lower() and
                              datetime.fromisoformat(a.get('created_at', '')).date() == datetime.now().date()]
                
                st.metric("📱 **Alertes Aujourd'hui**", len(today_alerts))
            except:
                st.metric("📱 **Alertes Aujourd'hui**", "N/A")
        
        # Alertes récentes
        st.markdown("---")
        st.subheader("📱 Alertes Intraday Récentes")
        
        try:
            alerts = self.db_manager.get_active_alerts()
            intraday_alerts = [a for a in alerts if 'intraday' in a.get('alert_type', '').lower()]
            intraday_alerts = sorted(intraday_alerts, 
                                   key=lambda x: x.get('created_at', ''), 
                                   reverse=True)[:20]
            
            if intraday_alerts:
                for alert in intraday_alerts:
                    symbol = alert.get('symbol', 'N/A')
                    alert_type = alert.get('alert_type', '')
                    priority = alert.get('priority', 'MEDIUM')
                    message = alert.get('message', '')
                    created_at = alert.get('created_at', '')
                    
                    # Couleur selon priorité
                    if priority == 'CRITICAL':
                        color = "#ff0000"
                        emoji = "🚨"
                    elif priority == 'HIGH':
                        color = "#ff9500"
                        emoji = "🔥"
                    elif priority == 'MEDIUM':
                        color = "#00a8ff"
                        emoji = "📊"
                    else:
                        color = "#95a5a6"
                        emoji = "ℹ️"
                    
                    # Type d'alerte
                    if "ENTRY" in alert_type:
                        type_emoji = "🟢"
                        type_text = "ENTRY"
                    elif "EXIT" in alert_type:
                        type_emoji = "🔴"
                        type_text = "EXIT"
                    else:
                        type_emoji = "📊"
                        type_text = "INFO"
                    
                    # Afficher alerte
                    with st.container():
                        st.markdown(f"""
                        <div style="border-left: 4px solid {color}; padding: 10px; margin: 10px 0; background-color: rgba(255,255,255,0.05);">
                            <div style="display: flex; justify-content: space-between;">
                                <div>
                                    <strong>{emoji} {symbol}</strong> - {type_emoji} {type_text}
                                    <br>
                                    <small style="color: #888;">{created_at}</small>
                                </div>
                                <div style="text-align: right;">
                                    <span style="background-color: {color}; color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.8em;">
                                        {priority}
                                    </span>
                                </div>
                            </div>
                            <div style="margin-top: 8px;">
                                {message}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("Aucune alerte intraday récente")
                st.markdown("""
                **Pour recevoir des alertes** :
                1. Configurez Telegram dans `.env`
                2. Lancez : `python scripts/intraday_trader.py`
                3. Surveillez votre téléphone pendant 9:30-16:00 ET
                """)
        
        except Exception as e:
            st.error(f"Erreur lors de la récupération des alertes: {e}")
        
        # Configuration rapide
        st.markdown("---")
        st.subheader("⚙️ Configuration Rapide")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Lancement Standard** (recommandé) :
            ```bash
            python scripts/intraday_trader.py
            ```
            
            **Critères** :
            - Prix: +3% minimum
            - Volume: 5x average
            - Score: 75/100 minimum
            - Scan: 30 secondes
            
            **Résultat** : 3-7 alertes/jour
            """)
        
        with col2:
            st.markdown("""
            **Lancement Agressif** (plus d'alertes) :
            ```bash
            python scripts/intraday_trader.py --aggressive
            ```
            
            **Critères** :
            - Prix: +2% minimum
            - Volume: 3x average
            - Score: 70/100 minimum
            - Scan: 15 secondes
            
            **Résultat** : 10-20 alertes/jour
            """)
        
        # Documentation
        st.markdown("---")
        st.subheader("📚 Documentation")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📖 Guide Complet", use_container_width=True):
                st.info("Voir: `docs/INTRADAY_TRADING_GUIDE.md`")
        
        with col2:
            if st.button("🧪 Tester le Système", use_container_width=True):
                st.info("Exécutez: `python scripts/test_intraday_system.py`")
        
        with col3:
            if st.button("🤖 Auto-Start Config", use_container_width=True):
                st.info("Voir section Task Scheduler dans la documentation")
        
        # Watchlist intraday
        st.markdown("---")
        st.subheader("📋 Watchlist Intraday")
        
        watchlist_intraday = [
            "AAPL", "TSLA", "NVDA", "AMD", "MSFT", "GOOGL", "META", "AMZN",
            "GME", "AMC", "PLTR", "SOFI", "RIOT", "MARA",
            "SPY", "QQQ", "IWM",
            "NIO", "LCID", "RIVN", "F", "BAC", "T", "INTC"
        ]
        
        cols = st.columns(6)
        for idx, symbol in enumerate(watchlist_intraday):
            with cols[idx % 6]:
                st.button(symbol, key=f"watch_{symbol}", use_container_width=True)
        
        st.info("💡 **Personnaliser** : Éditez `config.yaml` → `watchlist.intraday`")
        
        # Types de setups
        st.markdown("---")
        st.subheader("🎯 Types de Setups Détectés")
        
        setup_col1, setup_col2 = st.columns(2)
        
        with setup_col1:
            st.markdown("""
            **1. Opening Range Breakout (ORB)**
            - Prix casse le range des 5 premières minutes
            - Confirmation: Volume élevé
            - Meilleur timing: 9:35-10:00 AM
            
            **2. Momentum Breakout**
            - Prix explose avec volume massif
            - MACD bullish
            - Momentum > 80/100
            
            **3. VWAP Reversal**
            - Prix rebondit autour VWAP
            - RSI < 35 (bullish) ou > 65 (bearish)
            - Confirmation: Volume
            """)
        
        with setup_col2:
            st.markdown("""
            **4. Volume Surge Play**
            - Volume anormal (5x+)
            - Mouvement prix significatif
            - News catalyst possible
            
            **5. Bollinger Band Breakout**
            - Prix dépasse BB upper/lower
            - Volatilité confirmée
            - Squeeze pattern
            """)
        
        # Disclaimer
        st.markdown("---")
        st.warning("""
        ⚠️ **DISCLAIMER IMPORTANT**
        
        Le trading intraday comporte des **risques élevés de perte en capital**.
        - Ce système est fourni **à titre éducatif uniquement**
        - Ce n'est **PAS** un conseil financier
        - Les performances passées ne garantissent **PAS** les résultats futurs
        - **Ne tradez jamais** avec de l'argent que vous ne pouvez pas perdre
        - Consultez un **conseiller financier agréé**
        
        **Recommandations** :
        - ✅ Commencez en **paper trading** (simulation)
        - ✅ Respectez **toujours** les stop loss
        - ✅ Ne risquez que **1-2% du capital par trade**
        - ✅ Max **3 positions simultanées**
        - ✅ **Pas de positions overnight** (le système ferme automatiquement)
        """)
    
    def _render_monthly_signals(self):
        """Render monthly signals tab - THE CORE FEATURE"""
        st.header("🎯 Monthly Trading Signals - Decisive 0-100 Scoring")
        
        symbol = st.session_state.get('selected_symbol', 'AAPL')
        period = st.session_state.get('analysis_period', '1y')
        
        # Fetch data
        with st.spinner(f"📡 Fetching data for {symbol}..."):
            stock_data = self._fetch_stock_data(symbol, period)
            
            if stock_data is None or stock_data.empty:
                st.error(f"❌ Could not fetch data for {symbol}")
                return
            
            # MANDATORY data quality validation
            validation = self.pro_guard.validate_market_data(symbol, stock_data)
            if not validation.passed:
                st.error("🚫 **DATA QUALITY FAILURE** - Professional standards not met:")
                for issue in validation.issues:
                    st.error(f"• {issue}")
                return
            if validation.warnings:
                st.warning("⚠️ **DATA QUALITY WARNINGS:**")
                for warning in validation.warnings:
                    st.warning(f"• {warning}")
        
        # Calculate monthly score
        with st.spinner("🔬 Calculating monthly score..."):
            try:
                # Fetch news and sentiment (with Gemini AI enhancement)
                news_articles = self.news_aggregator.fetch_all_news(symbol)
                news_sentiment = self.sentiment_analyzer.calculate_aggregate_sentiment(
                    news_articles, days=7, symbol=symbol
                ) if news_articles else None
                
                # Fetch social sentiment
                social_data = self.social_aggregator.fetch_reddit_mentions(symbol, days=7)
                social_sentiment = self.social_aggregator.calculate_social_sentiment(
                    social_data
                ) if social_data else None
                
                # Calculate score
                score_data = self.monthly_signals.calculate_monthly_score(
                    stock_data, symbol, news_sentiment, social_sentiment
                )
                
                if not score_data:
                    st.warning("⚠️ Could not calculate monthly score - insufficient data")
                    return
                
                # Save to database
                self.db.save_monthly_score(
                    symbol=symbol,
                    score=score_data['total_score'],
                    recommendation=score_data['recommendation'],
                    components=score_data['components'],
                    entry_price=score_data.get('entry_price'),
                    stop_loss=score_data.get('stop_loss'),
                    target_price=score_data.get('target_price'),
                    risk_reward=score_data.get('risk_reward')
                )
                
            except Exception as e:
                self.logger.error(f"Error calculating monthly score: {e}")
                st.error(f"Error: {e}")
                return
        
        # Display score
        self._display_monthly_score(symbol, score_data, stock_data)
        
        # Historical scores
        self._display_score_history(symbol)
    
    def _display_monthly_score(self, symbol: str, score_data: dict, stock_data: pd.DataFrame):
        """Display the monthly score with detailed breakdown"""
        
        # Main score card
        col1, col2, col3 = st.columns([2, 3, 2])
        
        with col1:
            # Score badge
            score = score_data['total_score']
            recommendation = score_data['recommendation']
            
            # Color based on score
            if score >= 75:
                color = "#00ff88"  # Green
            elif score >= 60:
                color = "#ffcc00"  # Yellow
            elif score >= 40:
                color = "#ff9500"  # Orange
            else:
                color = "#ff4444"  # Red
            
            st.markdown(f"""
            <div class="score-badge" style="background: linear-gradient(135deg, {color}22, {color}44); border: 3px solid {color};">
                <div style="color: {color};">{score}/100</div>
                <div style="font-size: 1.2rem; margin-top: 0.5rem;">{recommendation}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Display late entry penalty warning if applicable
            late_entry_penalty = score_data.get('late_entry_penalty', 0)
            if late_entry_penalty > 0:
                original_score = score_data.get('original_score', score)
                late_warning = score_data.get('late_entry_warning', '')
                st.warning(f"⚠️ **Late Entry Penalty: -{late_entry_penalty} points**")
                st.caption(f"Original Score: {original_score}/100 → Final Score: {score}/100")
                if late_warning:
                    st.caption(f"🚨 {late_warning}")
            
            # Confidence
            confidence = score_data.get('confidence', 'MEDIUM')
            confidence_emoji = "🟢🟢🟢" if confidence == 'HIGH' else "🟡🟡" if confidence == 'MEDIUM' else "🔴"
            st.markdown(f"**Confidence:** {confidence_emoji} {confidence}")
        
        with col2:
            # Component breakdown
            st.subheader("📊 Score Breakdown")
            
            components = score_data['components']
            
            # Create horizontal bar chart
            comp_df = pd.DataFrame([
                {'Component': 'Trend', 'Score': components['trend']['score'], 'Weight': 30},
                {'Component': 'Momentum', 'Score': components['momentum']['score'], 'Weight': 20},
                {'Component': 'Sentiment', 'Score': components['sentiment']['score'], 'Weight': 25},
                {'Component': 'Divergence', 'Score': components['divergence']['score'], 'Weight': 15},
                {'Component': 'Volume', 'Score': components['volume']['score'], 'Weight': 10}
            ])
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=comp_df['Score'],
                y=comp_df['Component'],
                orientation='h',
                text=[f"{s:.0f}" for s in comp_df['Score']],
                textposition='auto',
                marker=dict(
                    color=comp_df['Score'],
                    colorscale=['red', 'yellow', 'green'],
                    cmin=0,
                    cmax=100,
                    showscale=False
                ),
                hovertemplate='%{y}: %{x:.1f}/100 (Weight: %{customdata}%)<extra></extra>',
                customdata=comp_df['Weight']
            ))
            
            fig.update_layout(
                title="Component Scores",
                xaxis_title="Score",
                xaxis=dict(range=[0, 100]),
                height=300,
                template='plotly_dark',
                showlegend=False
            )
            
            st.plotly_chart(fig, width='stretch')
        
        with col3:
            # Trade parameters
            st.subheader("💡 Trade Setup")
            
            current_price = stock_data['Close'].iloc[-1]
            entry_price = score_data.get('entry_price', current_price)
            stop_loss = score_data.get('stop_loss')
            target = score_data.get('target_price')
            risk_reward = score_data.get('risk_reward')
            position_size = score_data.get('position_size_pct', 5)
            
            st.metric("Entry Price", format_currency(entry_price))
            st.metric("Stop Loss", format_currency(stop_loss), 
                     delta=f"{((stop_loss - entry_price) / entry_price * 100):.1f}%")
            st.metric("Target Price", format_currency(target),
                     delta=f"+{((target - entry_price) / entry_price * 100):.1f}%")
            
            if risk_reward:
                st.metric("Risk/Reward", f"1:{risk_reward:.1f}")
            
            st.metric("Position Size", f"{position_size}%")
        
        # Detailed analysis
        st.markdown("---")
        st.subheader("📋 Detailed Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Trend analysis
            with st.expander("📈 **Trend Analysis (30%)**", expanded=True):
                trend = components['trend']
                st.write(f"**Score:** {trend['score']:.1f}/100")
                st.write(f"**Status:** {trend.get('status', 'N/A')}")
                
                details = trend.get('details', {})
                if details:
                    st.caption(f"• SMA Alignment: {details.get('sma_alignment', 'N/A')}")
                    st.caption(f"• ADX: {details.get('adx', 'N/A'):.1f}")
                    st.caption(f"• Monthly Direction: {details.get('monthly_direction', 'N/A')}")
            
            # Momentum analysis
            with st.expander("⚡ **Momentum Analysis (20%)**"):
                momentum = components['momentum']
                st.write(f"**Score:** {momentum['score']:.1f}/100")
                st.write(f"**Status:** {momentum.get('status', 'N/A')}")
                
                details = momentum.get('details', {})
                if details:
                    st.caption(f"• RSI: {details.get('rsi', 'N/A'):.1f}")
                    st.caption(f"• MACD: {details.get('macd_status', 'N/A')}")
                    st.caption(f"• ROC: {details.get('roc', 'N/A'):.2f}%")
            
            # Volume analysis
            with st.expander("📊 **Volume Analysis (10%)**"):
                volume = components['volume']
                st.write(f"**Score:** {volume['score']:.1f}/100")
                st.write(f"**Status:** {volume.get('status', 'N/A')}")
                
                details = volume.get('details', {})
                if details:
                    st.caption(f"• Volume Trend: {details.get('volume_trend', 'N/A')}")
                    st.caption(f"• VWAP Position: {details.get('vwap_position', 'N/A')}")
                    st.caption(f"• MFI: {details.get('mfi', 'N/A'):.1f}")
        
        with col2:
            # Sentiment analysis
            with st.expander("💭 **Sentiment Analysis (25%)**", expanded=True):
                sentiment = components['sentiment']
                st.write(f"**Score:** {sentiment['score']:.1f}/100")
                st.write(f"**Status:** {sentiment.get('status', 'N/A')}")
                
                details = sentiment.get('details', {})
                if details:
                    news_score = details.get('news_sentiment', 0)
                    social_score = details.get('social_sentiment', 0)
                    st.caption(f"• News Sentiment: {get_sentiment_emoji(news_score)} {news_score:.2f}")
                    st.caption(f"• Social Sentiment: {get_sentiment_emoji(social_score)} {social_score:.2f}")
                    st.caption(f"• Article Count: {details.get('news_count', 0)}")
            
            # Divergence analysis
            with st.expander("🔄 **Divergence Analysis (15%)**"):
                divergence = components['divergence']
                st.write(f"**Score:** {divergence['score']:.1f}/100")
                st.write(f"**Status:** {divergence.get('status', 'N/A')}")
                
                details = divergence.get('details', {})
                if details:
                    st.caption(f"• Price-RSI: {details.get('price_rsi', 'None')}")
                    st.caption(f"• Price-MACD: {details.get('price_macd', 'None')}")
                    st.caption(f"• OBV Trend: {details.get('obv_trend', 'N/A')}")
        
        # Trading plan
        st.markdown("---")
        with st.expander("📝 **Complete Trading Plan**", expanded=False):
            trading_plan = self.monthly_signals.generate_trading_plan(
                score_data, symbol
            )
            st.markdown(trading_plan)
    
    def _display_score_history(self, symbol: str):
        """Display historical monthly scores"""
        st.markdown("---")
        st.subheader("📊 Score History")
        
        # Get historical scores from database
        history = self.db.get_monthly_score_history(symbol, days=90)
        
        if not history:
            st.info("No historical data available yet")
            return
        
        df = pd.DataFrame(history)
        df['date'] = pd.to_datetime(df['date'])
        
        # Create score chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['total_score'],
            mode='lines+markers',
            name='Monthly Score',
            line=dict(color='#00ff88', width=3),
            marker=dict(size=8),
            fill='tozeroy',
            fillcolor='rgba(0,255,136,0.1)'
        ))
        
        # Add threshold lines
        fig.add_hline(y=75, line_dash="dash", line_color="green", annotation_text="BUY")
        fig.add_hline(y=60, line_dash="dot", line_color="yellow", annotation_text="MODERATE BUY")
        fig.add_hline(y=40, line_dash="dot", line_color="orange", annotation_text="HOLD")
        fig.add_hline(y=25, line_dash="dash", line_color="red", annotation_text="SELL")
        
        fig.update_layout(
            title=f"{symbol} - Monthly Score Trend",
            xaxis_title="Date",
            yaxis_title="Score",
            yaxis=dict(range=[0, 100]),
            template='plotly_dark',
            height=400
        )
        
        st.plotly_chart(fig, width='stretch')
    
    def _render_news_sentiment(self):
        """Render news and sentiment analysis tab"""
        st.header("📰 News & Sentiment Analysis")
        
        symbol = st.session_state.get('selected_symbol', 'AAPL')
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            days_back = st.slider("Days of news:", 1, 30, 7)
            refresh_news = st.button("🔄 Refresh News", width='stretch')
        
        # Fetch news
        with st.spinner(f"📡 Fetching news for {symbol}..."):
            news_articles = self.news_aggregator.fetch_all_news(symbol)
        
        # Fetch Reddit mentions (in parallel)
        with st.spinner(f"💬 Fetching social sentiment for {symbol}..."):
            reddit_mentions = self.social_aggregator.fetch_reddit_mentions(symbol, days=days_back)
            social_sentiment = self.social_aggregator.calculate_social_sentiment(reddit_mentions) if reddit_mentions else None
        
        if not news_articles:
            st.warning(f"No news found for {symbol}")
            return
        
        # Calculate aggregate sentiment
        sentiment_data = self.sentiment_analyzer.calculate_aggregate_sentiment(
            news_articles, days=days_back
        )
        
        # Display sentiment metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            sentiment_score = sentiment_data.get('weighted_sentiment', 0.0)
            emoji = get_sentiment_emoji(sentiment_score)
            st.metric("Sentiment Score", f"{emoji} {sentiment_score:.2f}", 
                     delta="Very Positive" if sentiment_score > 0.5 else "Very Negative" if sentiment_score < -0.5 else "Neutral")
        
        with col2:
            st.metric("Total Articles", sentiment_data.get('total_articles', len(news_articles)))
        
        with col3:
            confidence_pct = sentiment_data.get('confidence', 0.0) * 100
            st.metric("Confidence", f"{confidence_pct:.0f}%")
        
        with col4:
            st.metric("Trend", sentiment_data.get('sentiment_trend', 'neutral').title())
        
        # Reddit Social Sentiment Section
        if social_sentiment:
            st.markdown("---")
            st.subheader("💬 Reddit Social Sentiment")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_mentions = social_sentiment.get('total_mentions', 0)
                st.metric("Reddit Mentions", f"{total_mentions}")
            
            with col2:
                avg_score = social_sentiment.get('average_score', 0)
                st.metric("Average Score", f"{avg_score:.1f}")
            
            with col3:
                buzz_level = social_sentiment.get('buzz_level', 'low')
                buzz_emoji = "🔥" if buzz_level == 'very_high' else "📈" if buzz_level == 'high' else "📊" if buzz_level == 'medium' else "📉"
                st.metric("Buzz Level", f"{buzz_emoji} {buzz_level.replace('_', ' ').title()}")
            
            with col4:
                sentiment = social_sentiment.get('sentiment', 'neutral')
                sent_emoji = "🟢" if 'positive' in sentiment else "🔴" if 'negative' in sentiment else "⚪"
                st.metric("Sentiment", f"{sent_emoji} {sentiment.replace('_', ' ').title()}")
            
            # Top Reddit posts
            if reddit_mentions:
                top_posts = sorted(reddit_mentions, key=lambda x: x.get('score', 0), reverse=True)[:5]
                
                with st.expander(f"🔥 Top {len(top_posts)} Reddit Posts", expanded=False):
                    for post in top_posts:
                        st.markdown(f"**r/{post['subreddit']}** • ⬆️ {post['score']} • 💬 {post['num_comments']}")
                        st.markdown(f"[{post['title']}]({post['url']})")
                        if post.get('content'):
                            st.caption(post['content'][:200] + "...")
                        st.divider()
        else:
            st.info("💡 Reddit data not available. Configure Reddit API in `.env` to see social sentiment.")
        
        # Sentiment over time
        st.markdown("---")
        st.subheader("📈 News Sentiment Trend")
        
        df = pd.DataFrame(news_articles)
        df['published_date'] = pd.to_datetime(df['published_date'])
        df = df.sort_values('published_date')
        
        # Calculate rolling sentiment
        df['sentiment'] = df.apply(lambda x: self.sentiment_analyzer.analyze_article(x.to_dict())['sentiment_score'], axis=1)
        df['rolling_sentiment'] = df['sentiment'].rolling(window=5, min_periods=1).mean()
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['published_date'],
            y=df['rolling_sentiment'],
            mode='lines',
            name='Sentiment',
            line=dict(color='#00ff88', width=2),
            fill='tozeroy'
        ))
        
        fig.update_layout(
            title="News Sentiment Over Time (5-article rolling average)",
            xaxis_title="Date",
            yaxis_title="Sentiment",
            yaxis=dict(range=[-1, 1]),
            template='plotly_dark',
            height=300
        )
        
        st.plotly_chart(fig, width='stretch')
        
        # Display articles
        st.subheader("📋 Recent News Articles")
        
        for article in news_articles[:10]:  # Show top 10
            with st.expander(f"{article['title'][:100]}..."):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Source:** {article['source']}")
                    st.markdown(f"**Published:** {article['published_date']}")
                    if article.get('description'):
                        st.write(article['description'][:300] + "...")
                    st.markdown(f"[Read more]({article['url']})")
                
                with col2:
                    analysis = self.sentiment_analyzer.analyze_article(article)
                    sentiment = analysis['sentiment_score']
                    emoji = get_sentiment_emoji(sentiment)
                    
                    st.metric("Sentiment", f"{emoji} {sentiment:.2f}")
                    st.caption(f"VADER: {analysis['vader_score']:.2f}")
                    st.caption(f"TextBlob: {analysis['textblob_score']:.2f}")
                    st.caption(f"Keywords: {analysis['keyword_score']:.2f}")
    
    def _render_portfolio(self):
        """Render portfolio tracking tab"""
        st.header("💼 Portfolio Management")
        
        # Get current prices for all positions
        open_positions = self.db.get_open_positions()
        
        if not open_positions:
            st.info("📭 No open positions. Start trading to see your portfolio here!")
            
            # Paper trading simulator
            st.subheader("🎮 Paper Trading Simulator")
            st.write("Practice trading without real money")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                sim_symbol = st.text_input("Symbol:", value="AAPL")
            with col2:
                sim_shares = st.number_input("Shares:", min_value=1, value=10)
            with col3:
                if st.button("📈 Open Position", width='stretch'):
                    # Fetch current price
                    stock_data = self._fetch_stock_data(sim_symbol, '1d')
                    if stock_data is not None:
                        entry_price = stock_data['Close'].iloc[-1]
                        self.db.open_position(
                            symbol=sim_symbol,
                            entry_price=entry_price,
                            shares=sim_shares,
                            notes="Manual Entry"
                        )
                        st.success(f"Opened {sim_shares} shares of {sim_symbol} @ ${entry_price:.2f}")
                        st.rerun()
            
            return
        
        # Fetch current prices
        current_prices = {}
        for pos in open_positions:
            symbol = pos['symbol']
            stock_data = self._fetch_stock_data(symbol, '1d')
            if stock_data is not None:
                current_prices[symbol] = stock_data['Close'].iloc[-1]
            else:
                current_prices[symbol] = pos['entry_price']
        
        # Get portfolio value
        portfolio = self.portfolio_tracker.get_portfolio_value(current_prices)
        
        # MANDATORY portfolio risk validation
        risk_validation = self.pro_guard.validate_portfolio_limits(self.portfolio_tracker, current_prices)
        if not risk_validation.passed:
            st.error("🚫 **RISK LIMIT VIOLATIONS** - Immediate action required:")
            for issue in risk_validation.issues:
                st.error(f"• {issue}")
        if risk_validation.warnings:
            st.warning("⚠️ **RISK MANAGEMENT ALERTS:**")
            for warning in risk_validation.warnings:
                st.warning(f"• {warning}")
        
        # Display summary
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Value", format_currency(portfolio['total_value']))
        
        with col2:
            st.metric("Invested", format_currency(portfolio['invested']))
        
        with col3:
            pnl = portfolio['unrealized_pnl']
            pnl_pct = portfolio['unrealized_pnl_pct']
            st.metric("Unrealized P&L", format_currency(pnl), 
                     delta=f"{pnl_pct:+.2f}%")
        
        with col4:
            st.metric("Cash", format_currency(portfolio['cash']))
        
        # Portfolio management buttons
        st.markdown("---")
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col2:
            if st.button("🗑️ Delete All Positions", type="secondary", width='stretch'):
                if st.session_state.get('confirm_delete_all', False):
                    # Actually delete all positions
                    if self.db.delete_all_positions():
                        st.success("✅ All positions deleted successfully!")
                        st.session_state['confirm_delete_all'] = False
                        st.rerun()
                    else:
                        st.error("❌ Failed to delete positions")
                else:
                    # Show confirmation
                    st.session_state['confirm_delete_all'] = True
                    st.warning("⚠️ Click again to confirm deletion of ALL positions")
        
        with col3:
            if st.session_state.get('confirm_delete_all', False):
                if st.button("❌ Cancel", width='stretch'):
                    st.session_state['confirm_delete_all'] = False
                    st.rerun()
        
        # Positions table
        st.subheader("📊 Open Positions")
        
        positions_df = pd.DataFrame(portfolio['positions'])
        if not positions_df.empty:
            # Headers for the table
            col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1.5, 1, 1, 1, 1, 1, 1, 1])
            with col1:
                st.markdown("**Symbol**")
            with col2:
                st.markdown("**Shares**")
            with col3:
                st.markdown("**Entry**")
            with col4:
                st.markdown("**Current**")
            with col5:
                st.markdown("**P&L**")
            with col6:
                st.markdown("**P&L %**")
            with col7:
                st.markdown("**Days**")
            with col8:
                st.markdown("**Action**")
            
            st.divider()
            
            # Interactive positions table with delete buttons
            for i, (idx, position) in enumerate(positions_df.iterrows()):
                with st.container():
                    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1.5, 1, 1, 1, 1, 1, 1, 1])
                    
                    # Position data
                    with col1:
                        st.write(f"**{position['symbol']}**")
                    with col2:
                        st.write(f"{position['shares']} shares")
                    with col3:
                        st.write(f"${position['entry_price']:.2f}")
                    with col4:
                        st.write(f"${position['current_price']:.2f}")
                    with col5:
                        pnl_color = "green" if position['unrealized_pnl'] >= 0 else "red"
                        st.markdown(f"<span style='color: {pnl_color}'>${position['unrealized_pnl']:.2f}</span>", 
                                   unsafe_allow_html=True)
                    with col6:
                        pnl_pct_color = "green" if position['unrealized_pnl_pct'] >= 0 else "red"
                        st.markdown(f"<span style='color: {pnl_pct_color}'>{position['unrealized_pnl_pct']:+.2f}%</span>", 
                                   unsafe_allow_html=True)
                    with col7:
                        st.write(f"{position['days_held']} days")
                    with col8:
                        # Get position ID from open_positions
                        position_id = open_positions[i]['id']
                        
                        # Delete button with confirmation
                        delete_key = f"delete_{position_id}"
                        confirm_key = f"confirm_delete_{position_id}"
                        
                        if st.session_state.get(confirm_key, False):
                            # Show confirmation buttons
                            sub_col1, sub_col2 = st.columns(2)
                            with sub_col1:
                                if st.button("✅", key=f"confirm_yes_{position_id}", help="Confirm delete"):
                                    if self.db.delete_position(position_id):
                                        st.success(f"✅ Deleted {position['symbol']} position")
                                        st.session_state[confirm_key] = False
                                        st.rerun()
                                    else:
                                        st.error("❌ Failed to delete position")
                            with sub_col2:
                                if st.button("❌", key=f"confirm_no_{position_id}", help="Cancel delete"):
                                    st.session_state[confirm_key] = False
                                    st.rerun()
                        else:
                            # Normal delete button
                            if st.button("🗑️", key=delete_key, help=f"Delete {position['symbol']} position"):
                                st.session_state[confirm_key] = True
                                st.rerun()
                    
                    if i < len(positions_df) - 1:
                        st.divider()
        
        # Performance metrics
        st.markdown("---")
        st.subheader("📈 Performance Metrics")
        
        metrics = self.portfolio_tracker.calculate_performance_metrics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Trades", metrics['total_trades'])
            st.metric("Win Rate", f"{metrics['win_rate']:.1f}%")
        
        with col2:
            st.metric("Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}")
            st.metric("Sortino Ratio", f"{metrics['sortino_ratio']:.2f}")
        
        with col3:
            st.metric("Max Drawdown", f"{metrics['max_drawdown_pct']:.2f}%")
            st.metric("Profit Factor", f"{metrics['profit_factor']:.2f}")
        
        with col4:
            st.metric("Avg Win", format_currency(metrics['average_win']))
            st.metric("Avg Loss", format_currency(metrics['average_loss']))
        
        # Trade history
        with st.expander("📜 Trade History"):
            trade_history = self.portfolio_tracker.get_trade_history_dataframe()
            if not trade_history.empty:
                st.dataframe(trade_history, width='stretch')
            else:
                st.info("No closed trades yet")
    
    def _render_technical_analysis(self):
        """Render technical analysis tab"""
        st.header("📈 Advanced Technical Analysis")
        
        symbol = st.session_state.get('selected_symbol', 'AAPL')
        period = st.session_state.get('analysis_period', '1y')
        
        # Fetch data
        stock_data = self._fetch_stock_data(symbol, period)
        
        if stock_data is None or stock_data.empty:
            st.error(f"Could not fetch data for {symbol}")
            return
        
        # Calculate all technical indicators
        with st.spinner("Calculating technical indicators..."):
            stock_data = self._calculate_all_indicators(stock_data)
        
        # Create advanced chart
        chart = self._create_technical_chart(stock_data, symbol)
        st.plotly_chart(chart, width='stretch')
        
        # Current indicator values
        st.subheader("📊 Current Indicator Values")
        
        latest = stock_data.iloc[-1]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("RSI", f"{latest.get('RSI', 0):.1f}")
            st.metric("MACD", f"{latest.get('MACD', 0):.2f}")
        
        with col2:
            st.metric("ADX", f"{latest.get('ADX', 0):.1f}")
            st.metric("MFI", f"{latest.get('MFI', 0):.1f}")
        
        with col3:
            st.metric("ATR", f"{latest.get('ATR', 0):.2f}")
            st.metric("OBV", f"{latest.get('OBV', 0):,.0f}")
        
        with col4:
            sma20_dist = ((latest['Close'] - latest.get('SMA_20', latest['Close'])) / 
                         latest.get('SMA_20', latest['Close']) * 100)
            st.metric("vs SMA20", f"{sma20_dist:+.1f}%")
            
            sma50_dist = ((latest['Close'] - latest.get('SMA_50', latest['Close'])) / 
                         latest.get('SMA_50', latest['Close']) * 100)
            st.metric("vs SMA50", f"{sma50_dist:+.1f}%")
    
    def _render_ml_predictions(self):
        """Render ML predictions tab with ensemble forecasting + Gemini AI"""
        st.header("🤖 Quantitative Model Ensemble + AI")
        st.markdown("*Multi-factor predictive models enhanced with Gemini AI intelligence*")
        
        # System status with Gemini indicator
        if self.gemini_analyzer.enabled:
            st.success("""
            🎯 **MODEL STATUS**: Active ensemble of 4 ML algorithms + Gemini AI (25% weight).
            AI-enhanced predictions with news sentiment and market context analysis.
            """)
        else:
            st.warning("""
            🎯 **MODEL STATUS**: Active ensemble of 4 validated algorithms (Traditional Mode).
            Configure GEMINI_API_KEY in .env to enable AI-enhanced predictions.
            """)
        
        # Symbol selection
        watchlist = st.session_state.get('watchlist', self._get_default_watchlist())
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_symbol = st.selectbox(
                "Select Stock for ML Prediction:",
                options=watchlist,
                key='ml_symbol'
            )
        
        with col2:
            forecast_horizon = st.selectbox(
                "Forecast Horizon:",
                options=[7, 14, 30, 60, 90],
                index=2,  # 30 days default
                format_func=lambda x: f"{x} days",
                key='ml_horizon'
            )
        
        if not selected_symbol:
            st.warning("⚠️ Please select a stock symbol")
            return
        
        # Action buttons
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            train_button = st.button("🎯 Train Models", width='stretch')
        with col2:
            predict_button = st.button("🔮 Generate Prediction", width='stretch')
        with col3:
            backtest_button = st.button("📊 Backtest Accuracy", width='stretch')
        with col4:
            if st.button("💾 Save Models", width='stretch'):
                try:
                    self.ml_predictor._save_models(selected_symbol)
                    st.success(f"✅ Models saved for {selected_symbol}")
                except Exception as e:
                    st.error(f"❌ Save failed: {e}")
        
        # Fetch data
        try:
            with st.spinner(f"📡 Fetching data for {selected_symbol}..."):
                # Get historical data (need extra for feature engineering)
                lookback_days = self.ml_predictor.lookback_days + 100
                ticker = get_robust_ticker(selected_symbol)
                data = ticker.history(period=f"{lookback_days}d")
                
                if data.empty:
                    st.error(f"❌ No data available for {selected_symbol}")
                    return
                
                st.success(f"✅ Retrieved {len(data)} days of historical data")
        
        except Exception as e:
            st.error(f"❌ Data fetch failed: {e}")
            return
        
        # TRAIN MODELS
        if train_button:
            st.markdown("---")
            st.subheader("🎯 Training ML Models")
            
            with st.spinner("🔄 Training ensemble models... This may take 1-2 minutes..."):
                # Update forecast horizon in config
                self.ml_predictor.forecast_days = forecast_horizon
                
                # Train models
                training_results = self.ml_predictor.train_models(data, selected_symbol)
            
            if training_results['status'] == 'success':
                st.success(f"✅ Training completed successfully!")
                
                # Display metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Training Samples", f"{training_results['training_samples']:,}")
                with col2:
                    st.metric("Features Used", training_results['features_count'])
                with col3:
                    st.metric("Ensemble R²", f"{training_results['ensemble_r2']:.4f}")
                with col4:
                    training_time = datetime.fromisoformat(training_results['training_date'])
                    st.metric("Training Date", training_time.strftime("%Y-%m-%d %H:%M"))
                
                # Individual model metrics
                st.markdown("### 📊 Individual Model Performance")
                metrics_df = pd.DataFrame(training_results['individual_metrics']).T
                metrics_df = metrics_df.round(4)
                
                # Format for display
                display_metrics = metrics_df[['r2', 'rmse', 'mae', 'cv_mean', 'cv_std']].copy()
                display_metrics.columns = ['R² Score', 'RMSE', 'MAE', 'CV Mean', 'CV Std']
                
                st.dataframe(display_metrics, width='stretch')
                
                # Interpretation
                st.info("""
                **Model Performance Guide:**
                - **R² Score**: Closer to 1.0 = better fit (>0.7 excellent, 0.5-0.7 good, <0.5 poor)
                - **RMSE/MAE**: Lower = better (error in scaled units)
                - **CV Mean**: Cross-validation score (consistency across time periods)
                - **CV Std**: Lower = more stable predictions
                """)
            else:
                st.error(f"❌ Training failed: {training_results.get('error', 'Unknown error')}")
        
        # GENERATE PREDICTION
        if predict_button:
            st.markdown("---")
            st.subheader("🔮 Price Prediction")
            
            # Check if models exist
            if not self.ml_predictor.is_trained:
                # Try to load saved models
                if not self.ml_predictor._load_models(selected_symbol):
                    st.warning("⚠️ No trained models found. Please train models first.")
                    return
            
            # Check if retraining needed
            if self.ml_predictor.needs_retraining():
                st.info("ℹ️ Models are outdated (>7 days old). Consider retraining for best accuracy.")
            
            with st.spinner("🔮 Generating AI-enhanced prediction..."):
                # Update forecast horizon
                self.ml_predictor.forecast_days = forecast_horizon
                
                # Fetch news articles for Gemini AI analysis
                news_articles = []
                if self.gemini_analyzer.enabled:
                    try:
                        news_articles = self.news_aggregator.fetch_all_news(selected_symbol)
                        if news_articles:
                            st.info(f"📰 Analyzing {len(news_articles)} news articles with Gemini AI...")
                    except Exception as e:
                        self.logger.warning(f"News fetch failed: {e}")
                
                # Generate prediction with news context
                prediction = self.ml_predictor.predict_price(data, selected_symbol, news_articles)
            
            if prediction['status'] == 'success':
                # Display prediction summary
                current_price = prediction['current_price']
                predicted_price = prediction['predicted_price']
                change_pct = prediction['predicted_change_pct']
                
                # Color coding
                if change_pct > 5:
                    color = "#26a69a"  # Green
                    emoji = "📈"
                elif change_pct < -5:
                    color = "#ef5350"  # Red
                    emoji = "📉"
                else:
                    color = "#757575"  # Gray
                    emoji = "➡️"
                
                # Main prediction display
                st.markdown(f"""
                <div style='background: rgba(255,255,255,0.05); padding: 2rem; border-radius: 15px; border: 2px solid {color};'>
                    <h2 style='text-align: center; margin: 0;'>{emoji} {selected_symbol} Prediction</h2>
                    <div style='display: flex; justify-content: space-around; margin-top: 1.5rem;'>
                        <div style='text-align: center;'>
                            <p style='color: #888; margin: 0;'>Current Price</p>
                            <h3 style='margin: 0.5rem 0;'>${current_price:.2f}</h3>
                        </div>
                        <div style='text-align: center;'>
                            <p style='color: #888; margin: 0;'>Predicted Price ({forecast_horizon} days)</p>
                            <h3 style='margin: 0.5rem 0; color: {color};'>${predicted_price:.2f}</h3>
                        </div>
                        <div style='text-align: center;'>
                            <p style='color: #888; margin: 0;'>Expected Change</p>
                            <h3 style='margin: 0.5rem 0; color: {color};'>{change_pct:+.2f}%</h3>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Display Gemini AI insights if available
                if prediction.get('source') == 'hybrid-gemini' and prediction.get('gemini_prediction'):
                    gemini_data = prediction['gemini_prediction']
                    st.markdown("### 🤖 Gemini AI Analysis")
                    
                    col_g1, col_g2, col_g3 = st.columns(3)
                    with col_g1:
                        direction = gemini_data.get('predicted_direction', 'neutral')
                        direction_emoji = "📈" if direction == 'bullish' else "📉" if direction == 'bearish' else "➡️"
                        st.metric("AI Direction", f"{direction_emoji} {direction.upper()}")
                    with col_g2:
                        ai_confidence = gemini_data.get('confidence', 0)
                        st.metric("AI Confidence", f"{ai_confidence}%")
                    with col_g3:
                        target_price = gemini_data.get('target_price', 0)
                        if target_price:
                            st.metric("AI Target", f"${target_price:.2f}")
                    
                    if gemini_data.get('reasoning'):
                        st.info(f"**AI Reasoning:** {gemini_data['reasoning']}")
                    
                    if gemini_data.get('key_catalysts'):
                        st.markdown("**⚡ Key Catalysts:**")
                        for catalyst in gemini_data['key_catalysts'][:3]:
                            st.markdown(f"- {catalyst}")
                    
                    if gemini_data.get('key_risks'):
                        st.markdown("**⚠️ Key Risks:**")
                        for risk in gemini_data['key_risks'][:3]:
                            st.markdown(f"- {risk}")
                    
                    st.markdown("---")
                
                # Metrics row
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    agreement = prediction['model_agreement']
                    agreement_color = "#26a69a" if agreement > 70 else "#ffa726" if agreement > 50 else "#ef5350"
                    st.markdown(f"""
                    <div style='text-align: center; padding: 1rem; background: rgba(255,255,255,0.05); border-radius: 10px;'>
                        <p style='color: #888; margin: 0; font-size: 0.9rem;'>Model Agreement</p>
                        <h2 style='margin: 0.5rem 0; color: {agreement_color};'>{agreement:.1f}%</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    ci_lower = prediction['confidence_interval']['lower']
                    st.metric("Lower Bound (95% CI)", f"${ci_lower:.2f}")
                
                with col3:
                    ci_upper = prediction['confidence_interval']['upper']
                    st.metric("Upper Bound (95% CI)", f"${ci_upper:.2f}")
                
                with col4:
                    target_date = datetime.fromisoformat(prediction['target_date'])
                    st.metric("Target Date", target_date.strftime("%Y-%m-%d"))
                
                # Trading signal
                st.markdown("---")
                st.subheader("📊 AI Trading Signal")
                
                signal = self.ml_predictor.generate_trading_signal(prediction)
                
                # Signal color mapping
                signal_colors = {
                    'STRONG_BUY': '#00ff88',
                    'BUY': '#26a69a',
                    'HOLD': '#757575',
                    'SELL': '#ff6b6b',
                    'STRONG_SELL': '#ef5350'
                }
                
                signal_color = signal_colors.get(signal['signal'], '#757575')
                
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.markdown(f"""
                    <div style='text-align: center; padding: 2rem; background: rgba(255,255,255,0.05); border-radius: 15px; border: 3px solid {signal_color};'>
                        <h1 style='margin: 0; color: {signal_color};'>{signal['signal'].replace('_', ' ')}</h1>
                        <p style='color: #888; margin: 0.5rem 0;'>Confidence: {signal['confidence']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    **Recommended Action:** {signal['action']}
                    
                    **Reasoning:** {signal['reasoning']}
                    
                    **Risk Assessment:**
                    - Expected move: {signal['predicted_change']:+.1f}%
                    - Model consensus: {signal['model_agreement']:.1f}%
                    - Confidence interval: ${ci_lower:.2f} - ${ci_upper:.2f}
                    """)
                
                # Individual model predictions
                st.markdown("---")
                st.subheader("🤖 Individual Model Predictions")
                
                models_data = []
                for model_name, pred in prediction['individual_predictions'].items():
                    models_data.append({
                        'Model': model_name.replace('_', ' ').title(),
                        'Predicted Price': f"${pred['predicted_price']:.2f}",
                        'Change %': f"{pred['predicted_change_pct']:+.2f}%",
                        'Weight': f"{self.ml_predictor.model_weights[model_name]*100:.0f}%"
                    })
                
                models_df = pd.DataFrame(models_data)
                st.dataframe(models_df, width='stretch', hide_index=True)
                
                # Highlight Gemini contribution if present
                if 'gemini_ai' in prediction['individual_predictions']:
                    st.success("✨ **Gemini AI Contribution:** The ensemble includes AI-powered analysis of news, technical patterns, and market context.")
                
                # Visualization: Prediction chart
                st.markdown("---")
                st.subheader("📈 Price Forecast Visualization")
                
                # Create forecast chart
                fig = go.Figure()
                
                # Historical prices (last 60 days)
                hist_data = data.tail(60).copy()
                fig.add_trace(go.Scatter(
                    x=hist_data.index,
                    y=hist_data['Close'],
                    mode='lines',
                    name='Historical Price',
                    line=dict(color='#1f77b4', width=2)
                ))
                
                # Prediction point
                pred_date = target_date
                fig.add_trace(go.Scatter(
                    x=[data.index[-1], pred_date],
                    y=[current_price, predicted_price],
                    mode='lines+markers',
                    name='Predicted',
                    line=dict(color=signal_color, width=3, dash='dash'),
                    marker=dict(size=10)
                ))
                
                # Confidence interval
                fig.add_trace(go.Scatter(
                    x=[pred_date, pred_date],
                    y=[ci_lower, ci_upper],
                    mode='lines',
                    name='95% Confidence Interval',
                    line=dict(color=signal_color, width=6),
                    opacity=0.3
                ))
                
                fig.update_layout(
                    title=f"{selected_symbol} - {forecast_horizon}-Day Forecast",
                    xaxis_title="Date",
                    yaxis_title="Price ($)",
                    hovermode='x unified',
                    template='plotly_dark',
                    height=500
                )
                
                st.plotly_chart(fig, width='stretch')
                
                # Model performance metrics (if available)
                if self.ml_predictor.model_metrics:
                    with st.expander("📊 Model Training Metrics"):
                        metrics_df = pd.DataFrame(self.ml_predictor.model_metrics).T
                        st.dataframe(metrics_df.round(4), width='stretch')
            
            else:
                st.error(f"❌ Prediction failed: {prediction.get('error', 'Unknown error')}")
        
        # BACKTEST ACCURACY
        if backtest_button:
            st.markdown("---")
            st.subheader("📊 Prediction Accuracy Backtest")
            st.info("Testing ML prediction accuracy on historical data using walk-forward analysis...")
            
            with st.spinner("🔄 Running backtest... This may take several minutes..."):
                # Update forecast horizon
                self.ml_predictor.forecast_days = forecast_horizon
                
                # Run backtest
                backtest_results = self.ml_predictor.backtest_predictions(data, selected_symbol)
            
            if backtest_results['status'] == 'success':
                st.success("✅ Backtest completed!")
                
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Predictions", backtest_results['total_predictions'])
                
                with col2:
                    direction_acc = backtest_results['direction_accuracy_pct']
                    delta_color = "normal" if direction_acc >= 60 else "inverse"
                    st.metric(
                        "Direction Accuracy",
                        f"{direction_acc:.1f}%",
                        delta=f"{direction_acc - 50:.1f}% vs random",
                        delta_color=delta_color
                    )
                
                with col3:
                    mae = backtest_results['mean_absolute_error_pct']
                    st.metric("Mean Absolute Error", f"{mae:.2f}%")
                
                with col4:
                    ci_coverage = backtest_results['confidence_interval_coverage_pct']
                    st.metric("CI Coverage", f"{ci_coverage:.1f}%", help="95% CI should cover ~95% of actual prices")
                
                # Interpretation
                st.markdown("### 📝 Performance Interpretation")
                
                if direction_acc >= 65:
                    st.success("🎯 **Excellent** - Models consistently predict price direction correctly")
                elif direction_acc >= 55:
                    st.info("✅ **Good** - Models show predictive power above random chance")
                elif direction_acc >= 50:
                    st.warning("⚠️ **Weak** - Models barely outperform random guessing")
                else:
                    st.error("❌ **Poor** - Models may be overfitting or data quality issues")
                
                # Historical predictions table
                if backtest_results.get('predictions'):
                    st.markdown("### 📋 Recent Predictions (Last 10)")
                    
                    pred_data = []
                    for pred in backtest_results['predictions']:
                        pred_data.append({
                            'Date': pred['date'].strftime('%Y-%m-%d') if hasattr(pred['date'], 'strftime') else str(pred['date']),
                            'Predicted': f"${pred['predicted_price']:.2f}",
                            'Actual': f"${pred['actual_price']:.2f}",
                            'Pred Change': f"{pred['predicted_change']:+.1f}%",
                            'Actual Change': f"{pred['actual_change']:+.1f}%",
                            'Error': f"{pred['prediction_error']:.1f}%",
                            'Direction ✓': '✅' if pred['direction_correct'] else '❌',
                            'In CI': '✅' if pred['in_confidence_interval'] else '❌'
                        })
                    
                    pred_df = pd.DataFrame(pred_data)
                    st.dataframe(pred_df, width='stretch', hide_index=True)
            
            else:
                st.error(f"❌ Backtest failed: {backtest_results.get('error', 'Unknown error')}")
        
        # Information section
        st.markdown("---")
        with st.expander("ℹ️ About ML Predictions"):
            st.markdown("""
            ### 🤖 How It Works
            
            **Ensemble Architecture:**
            - **Random Forest** (35% weight): Captures non-linear patterns and feature interactions
            - **Gradient Boosting** (30% weight): Sequential error correction for accuracy
            - **Ridge Regression** (20% weight): Linear trends with L2 regularization
            - **Support Vector Regression** (15% weight): Complex pattern recognition
            
            **Features Engineered (60+ features):**
            - Price momentum: returns, velocity, acceleration at multiple timeframes
            - Technical indicators: RSI, MACD, Bollinger Bands, ATR, ADX, etc.
            - Volume dynamics: OBV, VWAP, volume ratios
            - Statistical measures: volatility, momentum, high-low ranges
            - Time-based: day of week, month, quarter effects
            
            **Training Process:**
            1. Engineer 60+ features from historical OHLCV data
            2. Train each model independently with time-series cross-validation
            3. Combine predictions using weighted ensemble
            4. Calculate confidence intervals from model agreement
            
            **Best Practices:**
            - Retrain weekly for fresh patterns
            - Use 30-day forecast for swing trading
            - Verify model agreement >60% for confidence
            - Always use stop losses (models can be wrong!)
            - Combine with monthly signals for best results
            
            **Limitations:**
            - Cannot predict black swan events
            - Historical patterns may not repeat
            - Works best in trending markets
            - Requires 200+ days of quality data
            """)
        
        st.markdown("---")
        st.caption("""
        💡 **Pro Tip**: Combine ML predictions with Monthly Signals (Tab 1) for comprehensive analysis.
        Use ML for directional bias, Monthly Signals for entry/exit timing.
        """)
    
    def _render_backtesting(self):
        """Render backtesting tab"""
        st.header("🔙 Strategy Backtesting")
        st.markdown("*Test monthly signals on historical data with comprehensive performance metrics*")
        
        # Configuration section
        with st.expander("⚙️ Backtest Configuration", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Symbol selection
                watchlist = st.session_state.get('watchlist', self._get_default_watchlist())
                selected_symbols = st.multiselect(
                    "Select Stocks to Test:",
                    options=watchlist,
                    default=watchlist[:3],
                    key='backtest_symbols'
                )
            
            with col2:
                # Date range
                end_date = datetime.now()
                start_date = end_date - timedelta(days=730)  # 2 years default
                
                backtest_start = st.date_input(
                    "Start Date:",
                    value=start_date,
                    max_value=end_date,
                    key='backtest_start'
                )
                
                backtest_end = st.date_input(
                    "End Date:",
                    value=end_date,
                    max_value=end_date,
                    key='backtest_end'
                )
            
            with col3:
                # Rebalancing frequency
                rebalance_freq = st.selectbox(
                    "Rebalance Frequency:",
                    options=['monthly', 'weekly', 'daily'],
                    index=0,
                    key='rebalance_freq'
                )
                
                # Initial capital
                initial_capital = st.number_input(
                    "Initial Capital ($):",
                    min_value=1000,
                    max_value=1000000,
                    value=10000,
                    step=1000,
                    key='backtest_capital'
                )
        
        # Run backtest button
        if st.button("� Run Backtest", type="primary", width='stretch'):
            if not selected_symbols:
                st.error("⚠️ Please select at least one stock to backtest!")
                return
            
            if backtest_start >= backtest_end:
                st.error("⚠️ Start date must be before end date!")
                return
            
            # Run backtest with progress
            with st.spinner("🔄 Running backtest... This may take a few minutes..."):
                try:
                    # Update config with user inputs
                    backtest_config = self.config.get('backtesting', {}).copy()
                    backtest_config['initial_capital'] = initial_capital
                    
                    # Create temporary backtester with updated config
                    temp_config = self.config.copy()
                    temp_config['backtesting'] = backtest_config
                    backtester = Backtester(temp_config, self.monthly_signals, self.db)
                    
                    # Run backtest
                    results = backtester.run_backtest(
                        symbols=selected_symbols,
                        start_date=backtest_start.strftime('%Y-%m-%d'),
                        end_date=backtest_end.strftime('%Y-%m-%d'),
                        rebalance_frequency=rebalance_freq
                    )
                    
                    # Store results in session state
                    st.session_state.backtest_results = results
                    st.success("✅ Backtest completed successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Backtest failed: {str(e)}")
                    self.logger.error(f"Backtest error: {e}", exc_info=True)
                    return
        
        # Display results if available
        if 'backtest_results' in st.session_state:
            results = st.session_state.backtest_results
            
            if 'error' in results:
                st.error(f"❌ Error: {results['error']}")
                return
            
            # Display comprehensive results
            st.markdown("---")
            st.subheader("📊 Backtest Results")
            
            # Key metrics in columns
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Return",
                    format_percentage(results['returns']['total_return_pct']),
                    delta=format_currency(results['returns']['profit_loss'])
                )
            
            with col2:
                st.metric(
                    "Annualized Return",
                    format_percentage(results['returns']['annualized_return_pct'])
                )
            
            with col3:
                st.metric(
                    "Sharpe Ratio",
                    f"{results['risk']['sharpe_ratio']:.2f}",
                    delta="Good" if results['risk']['sharpe_ratio'] > 1.0 else "Poor"
                )
            
            with col4:
                st.metric(
                    "Max Drawdown",
                    format_percentage(results['risk']['max_drawdown_pct']),
                    delta="High Risk" if abs(results['risk']['max_drawdown_pct']) > 20 else "Moderate"
                )
            
            # Detailed metrics tabs
            tab1, tab2, tab3, tab4 = st.tabs([
                "📈 Performance", "⚠️ Risk Analysis", "📊 Trades", "🏆 vs Benchmark"
            ])
            
            with tab1:
                st.subheader("Performance Metrics")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Returns**")
                    st.write(f"• Initial Capital: {format_currency(results['returns']['initial_capital'])}")
                    st.write(f"• Final Value: {format_currency(results['returns']['final_value'])}")
                    st.write(f"• Profit/Loss: {format_currency(results['returns']['profit_loss'])}")
                    st.write(f"• Total Return: {format_percentage(results['returns']['total_return_pct'])}")
                    st.write(f"• Annualized Return: {format_percentage(results['returns']['annualized_return_pct'])}")
                
                with col2:
                    st.markdown("**Portfolio Exposure**")
                    st.write(f"• Avg Exposure: {format_percentage(results['exposure']['avg_exposure_pct'])}")
                    st.write(f"• Avg Cash: {format_currency(results['exposure']['avg_cash'])}")
                    st.write(f"• Avg Invested: {format_currency(results['exposure']['avg_invested'])}")
                
                # Equity curve
                if results.get('portfolio_values'):
                    st.subheader("Equity Curve")
                    df_values = pd.DataFrame(results['portfolio_values'])
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df_values['date'],
                        y=df_values['value'],
                        mode='lines',
                        name='Portfolio Value',
                        line=dict(color='#00ff88', width=2),
                        fill='tozeroy',
                        fillcolor='rgba(0,255,136,0.1)'
                    ))
                    
                    fig.update_layout(
                        title="Portfolio Value Over Time",
                        xaxis_title="Date",
                        yaxis_title="Value ($)",
                        template="plotly_dark",
                        height=400
                    )
                    
                    st.plotly_chart(fig, width='stretch')
            
            with tab2:
                st.subheader("Risk Metrics")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Volatility & Risk**")
                    st.write(f"• Volatility: {format_percentage(results['risk']['volatility_pct'])}")
                    st.write(f"• Max Drawdown: {format_percentage(results['risk']['max_drawdown_pct'])}")
                
                with col2:
                    st.markdown("**Risk-Adjusted Returns**")
                    st.write(f"• Sharpe Ratio: {results['risk']['sharpe_ratio']:.2f}")
                    st.write(f"• Sortino Ratio: {results['risk']['sortino_ratio']:.2f}")
                    st.write(f"• Calmar Ratio: {results['risk']['calmar_ratio']:.2f}")
                
                # Risk interpretation
                sharpe = results['risk']['sharpe_ratio']
                if sharpe > 2.0:
                    risk_assessment = "🌟 Excellent - High return per unit of risk"
                elif sharpe > 1.0:
                    risk_assessment = "✅ Good - Favorable risk-adjusted returns"
                elif sharpe > 0.5:
                    risk_assessment = "⚠️ Adequate - Moderate risk compensation"
                else:
                    risk_assessment = "❌ Poor - Too much risk for the return"
                
                st.info(f"**Risk Assessment:** {risk_assessment}")
            
            with tab3:
                st.subheader("Trading Activity")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Trades", results['trades']['total_trades'])
                
                with col2:
                    st.metric("Win Rate", format_percentage(results['trades']['win_rate_pct']))
                
                with col3:
                    avg_trades_per_month = results['trades']['total_trades'] / max(results['period']['years'] * 12, 1)
                    st.metric("Avg Trades/Month", f"{avg_trades_per_month:.1f}")
                
                # Trade log
                if results.get('trades_log'):
                    st.subheader("Trade History")
                    df_trades = pd.DataFrame(results['trades_log'])
                    
                    # Format for display
                    if not df_trades.empty:
                        df_trades['date'] = pd.to_datetime(df_trades['date']).dt.strftime('%Y-%m-%d')
                        df_trades['price'] = df_trades['price'].apply(lambda x: f"${x:.2f}")
                        
                        st.dataframe(
                            df_trades,
                            width='stretch',
                            hide_index=True,
                            height=400
                        )
                        
                        # Download button
                        csv = df_trades.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Trade Log",
                            data=csv,
                            file_name=f"backtest_trades_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
                else:
                    st.info("No trades executed during backtest period")
            
            with tab4:
                st.subheader("Benchmark Comparison")
                
                if 'benchmark' in results and 'error' not in results['benchmark']:
                    bm = results['benchmark']
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Strategy Performance**")
                        st.write(f"• Total Return: {format_percentage(results['returns']['total_return_pct'])}")
                        st.write(f"• Annualized: {format_percentage(results['returns']['annualized_return_pct'])}")
                        st.write(f"• Sharpe Ratio: {results['risk']['sharpe_ratio']:.2f}")
                        st.write(f"• Max Drawdown: {format_percentage(results['risk']['max_drawdown_pct'])}")
                    
                    with col2:
                        st.markdown(f"**Benchmark ({bm['symbol']}) Performance**")
                        st.write(f"• Total Return: {format_percentage(bm['total_return_pct'])}")
                        st.write(f"• Annualized: {format_percentage(bm['annualized_return_pct'])}")
                        st.write(f"• Sharpe Ratio: {bm['sharpe_ratio']:.2f}")
                        st.write(f"• Max Drawdown: {format_percentage(bm['max_drawdown_pct'])}")
                    
                    # Alpha calculation
                    alpha = results['returns']['annualized_return_pct'] - bm['annualized_return_pct']
                    
                    st.markdown("---")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric(
                            "Alpha (Outperformance)",
                            format_percentage(alpha),
                            delta="Strategy outperforms" if alpha > 0 else "Strategy underperforms"
                        )
                    
                    with col2:
                        outperformance = "✅ YES" if alpha > 0 else "❌ NO"
                        st.markdown(f"**Beats Benchmark:** {outperformance}")
                        
                        if alpha > 0:
                            st.success(f"Strategy generated {format_percentage(abs(alpha))} more return than {bm['symbol']}")
                        else:
                            st.warning(f"Strategy underperformed {bm['symbol']} by {format_percentage(abs(alpha))}")
                else:
                    st.warning("Benchmark data not available")
            
            # Text report
            with st.expander("📄 View Full Text Report"):
                report = self.backtester.generate_backtest_report(results)
                st.code(report, language=None)
    
    def _render_settings(self):
        """Render settings tab"""
        st.header("⚙️ System Settings")
        
        tab1, tab2, tab3 = st.tabs(["📊 Trading Rules", "🔔 Alerts", "🗂️ Database"])
        
        with tab1:
            st.subheader("Trading Configuration")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.number_input("Initial Capital", value=10000, step=1000)
                st.number_input("Position Size %", value=5, step=1, min_value=1, max_value=20)
                st.number_input("Risk Per Trade %", value=2.0, step=0.5, min_value=0.5, max_value=5.0)
            
            with col2:
                st.number_input("Max Positions", value=10, step=1, min_value=1, max_value=50)
                st.number_input("Stop Loss %", value=8, step=1, min_value=1, max_value=20)
                st.number_input("Take Profit %", value=25, step=5, min_value=5, max_value=100)
        
        with tab2:
            st.subheader("Alert Configuration")
            
            st.checkbox("Desktop Notifications", value=True)
            st.checkbox("Email Alerts", value=True)
            st.checkbox("Telegram Alerts", value=True)
            st.checkbox("Audio Alerts", value=True)
            
            if st.button("🔔 Test All Alerts"):
                results = self.alert_manager.test_alerts()
                for channel, success in results.items():
                    if success:
                        st.success(f"✅ {channel.title()} working")
                    else:
                        st.error(f"❌ {channel.title()} failed")
        
        with tab3:
            st.subheader("Database Management")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🗑️ Clear Cache"):
                    st.cache_data.clear()
                    st.success("Cache cleared!")
            
            with col2:
                if st.button("💾 Backup Database"):
                    st.info("Database backup feature coming soon")
            
            with col3:
                if st.button("📊 View Stats"):
                    stats = self.db.get_database_stats()
                    st.json(stats)
    
    def _render_footer(self):
        """Render footer"""
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666; padding: 20px;'>
            <p>� <strong>Professional Trading System</strong> - Institutional-Grade Analytics</p>
            <p><em>🔒 RISK MANAGED: Advanced portfolio optimization with professional safeguards</em></p>
            <p>Real-time market intelligence • Quantitative signal generation • Professional risk controls</p>
        </div>
        """, unsafe_allow_html=True)
    
    def _fetch_stock_data(self, symbol: str, period: str) -> pd.DataFrame:
        """Fetch stock data from yfinance"""
        try:
            ticker = get_robust_ticker(symbol)
            data = ticker.history(period=period)
            
            if data.empty:
                return None
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error fetching data for {symbol}: {e}")
            return None
    
    def _calculate_all_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators"""
        df = data.copy()
        
        # Use TechnicalIndicators class
        # SMAs
        for period in [20, 50, 200]:
            df[f'SMA_{period}'] = df['Close'].rolling(window=period).mean()
        
        # EMAs
        df['EMA_12'] = df['Close'].ewm(span=12).mean()
        df['EMA_26'] = df['Close'].ewm(span=26).mean()
        
        # MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_histogram'] = df['MACD'] - df['MACD_signal']
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Use custom indicators (assign to columns, don't overwrite df)
        df['ADX'] = self.technical_indicators.calculate_adx(df, return_series=True)
        df['OBV'] = self.technical_indicators.calculate_obv(df, return_series=True)
        df['VWAP'] = self.technical_indicators.calculate_vwap(df)
        df['MFI'] = self.technical_indicators.calculate_mfi(df)
        
        # ATR
        df['High_Low'] = df['High'] - df['Low']
        df['High_Close'] = np.abs(df['High'] - df['Close'].shift())
        df['Low_Close'] = np.abs(df['Low'] - df['Close'].shift())
        df['True_Range'] = df[['High_Low', 'High_Close', 'Low_Close']].max(axis=1)
        df['ATR'] = df['True_Range'].rolling(window=14).mean()
        
        return df
    
    def _create_technical_chart(self, data: pd.DataFrame, symbol: str):
        """Create comprehensive technical chart"""
        fig = make_subplots(
            rows=4, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=(
                f'{symbol} - Price & Moving Averages',
                'Volume',
                'MACD',
                'RSI'
            ),
            row_heights=[0.5, 0.15, 0.2, 0.15]
        )
        
        # Candlestick
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name='Price',
                increasing_line_color='#00ff88',
                decreasing_line_color='#ff4444'
            ),
            row=1, col=1
        )
        
        # Moving averages
        for ma, color in [('SMA_20', '#ff9500'), ('SMA_50', '#007aff'), ('SMA_200', '#5856d6')]:
            if ma in data.columns:
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data[ma],
                        name=ma,
                        line=dict(color=color, width=1.5)
                    ),
                    row=1, col=1
                )
        
        # Volume
        volume_colors = [
            '#00ff88' if data['Close'].iloc[i] >= data['Open'].iloc[i] else '#ff4444'
            for i in range(len(data))
        ]
        
        fig.add_trace(
            go.Bar(
                x=data.index,
                y=data['Volume'],
                name='Volume',
                marker_color=volume_colors,
                opacity=0.7
            ),
            row=2, col=1
        )
        
        # MACD
        if 'MACD' in data.columns:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['MACD'],
                    name='MACD',
                    line=dict(color='#007aff', width=2)
                ),
                row=3, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['MACD_signal'],
                    name='Signal',
                    line=dict(color='#ff9500', width=2)
                ),
                row=3, col=1
            )
            
            histogram_colors = [
                '#00ff88' if val >= 0 else '#ff4444'
                for val in data['MACD_histogram']
            ]
            
            fig.add_trace(
                go.Bar(
                    x=data.index,
                    y=data['MACD_histogram'],
                    name='Histogram',
                    marker_color=histogram_colors,
                    opacity=0.6
                ),
                row=3, col=1
            )
        
        # RSI
        if 'RSI' in data.columns:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['RSI'],
                    name='RSI',
                    line=dict(color='#af52de', width=2)
                ),
                row=4, col=1
            )
            
            fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=4, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=4, col=1)
        
        fig.update_layout(
            title=f'{symbol} - Complete Technical Analysis',
            xaxis_rangeslider_visible=False,
            height=900,
            showlegend=True,
            template='plotly_dark'
        )
        
        return fig


def main():
    """Main application entry point"""
    dashboard = TradingDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
