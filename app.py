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

# Import our custom modules
from modules.utils import (
    load_config, setup_logging, is_market_open, 
    format_currency, format_percentage, get_sentiment_emoji, get_trend_emoji
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
        """Initialize dashboard with all components"""
        # Load configuration
        self.config = load_config()
        
        # Setup logging
        setup_logging(self.config.get('logging', {}))
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.db = DatabaseManager(self.config.get('database', {}))
        self.news_aggregator = NewsAggregator(self.config)
        self.sentiment_analyzer = SentimentAnalyzer()
        self.social_aggregator = SocialAggregator(self.config)
        self.technical_indicators = TechnicalIndicators()
        self.monthly_signals = MonthlySignals(
            self.config,
            self.sentiment_analyzer,
            self.technical_indicators
        )
        self.alert_manager = AlertManager(self.config)
        self.portfolio_tracker = PortfolioTracker(self.config, self.db)
        self.backtester = Backtester(self.config, self.monthly_signals, self.db)
        
        self.logger.info("Dashboard initialized successfully")
    
    def _get_default_watchlist(self):
        """Get default watchlist from config"""
        watchlist_config = self.config.get('watchlist', {})
        if isinstance(watchlist_config, dict):
            return watchlist_config.get('stocks', [])
        elif isinstance(watchlist_config, list):
            return watchlist_config
        return []
    
    def run(self):
        """Run the main dashboard application"""
        # Header
        st.markdown('<div class="main-header">📈 AI Stock Trading Dashboard</div>', unsafe_allow_html=True)
        st.markdown("*Decisive Monthly Trading Signals with 0-100 Scoring System*")
        
        # Sidebar
        self._render_sidebar()
        
        # Market status indicator
        market_open = is_market_open()
        status_icon = "🟢" if market_open else "🔴"
        status_text = "MARKET OPEN" if market_open else "MARKET CLOSED"
        st.sidebar.markdown(f"### {status_icon} {status_text}")
        
        # Main tabs
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
            "🚨 Monthly Signals",
            "📰 News & Sentiment", 
            "💼 Portfolio",
            "📈 Technical Analysis",
            "🔮 ML Predictions",
            "🔙 Backtesting",
            "⚙️ Settings"
        ])
        
        with tab1:
            self._render_monthly_signals()
        
        with tab2:
            self._render_news_sentiment()
        
        with tab3:
            self._render_portfolio()
        
        with tab4:
            self._render_technical_analysis()
        
        with tab5:
            self._render_ml_predictions()
        
        with tab6:
            self._render_backtesting()
        
        with tab7:
            self._render_settings()
        
        # Footer
        self._render_footer()
    
    def _render_sidebar(self):
        """Render sidebar controls"""
        st.sidebar.header("📊 Trading Dashboard")
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
            if st.button("🔄 Refresh", use_container_width=True):
                st.cache_data.clear()
                st.rerun()
        
        with col2:
            if st.button("🔔 Alerts", use_container_width=True):
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
        
        # Calculate monthly score
        with st.spinner("🔬 Calculating monthly score..."):
            try:
                # Fetch news and sentiment
                news_articles = self.news_aggregator.fetch_all_news(symbol)
                news_sentiment = self.sentiment_analyzer.calculate_aggregate_sentiment(
                    news_articles, days=7
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
            
            st.plotly_chart(fig, use_container_width=True)
        
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
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_news_sentiment(self):
        """Render news and sentiment analysis tab"""
        st.header("📰 News & Sentiment Analysis")
        
        symbol = st.session_state.get('selected_symbol', 'AAPL')
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            days_back = st.slider("Days of news:", 1, 30, 7)
            refresh_news = st.button("🔄 Refresh News", use_container_width=True)
        
        # Fetch news
        with st.spinner(f"📡 Fetching news for {symbol}..."):
            news_articles = self.news_aggregator.fetch_all_news(symbol)
        
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
        
        # Sentiment over time
        st.subheader("📈 Sentiment Trend")
        
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
        
        st.plotly_chart(fig, use_container_width=True)
        
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
                if st.button("📈 Open Position", use_container_width=True):
                    # Fetch current price
                    stock_data = self._fetch_stock_data(sim_symbol, '1d')
                    if stock_data is not None:
                        entry_price = stock_data['Close'].iloc[-1]
                        self.db.open_position(
                            symbol=sim_symbol,
                            shares=sim_shares,
                            entry_price=entry_price,
                            strategy="Manual Entry"
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
        
        # Positions table
        st.subheader("📊 Open Positions")
        
        positions_df = pd.DataFrame(portfolio['positions'])
        if not positions_df.empty:
            # Format for display
            display_df = positions_df[[
                'symbol', 'shares', 'entry_price', 'current_price', 
                'unrealized_pnl', 'unrealized_pnl_pct', 'days_held'
            ]].copy()
            
            display_df.columns = [
                'Symbol', 'Shares', 'Entry', 'Current', 'P&L', 'P&L %', 'Days'
            ]
            
            # Format currency and percentage
            display_df['Entry'] = display_df['Entry'].apply(lambda x: f"${x:.2f}")
            display_df['Current'] = display_df['Current'].apply(lambda x: f"${x:.2f}")
            display_df['P&L'] = display_df['P&L'].apply(lambda x: f"${x:.2f}")
            display_df['P&L %'] = display_df['P&L %'].apply(lambda x: f"{x:+.2f}%")
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        
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
                st.dataframe(trade_history, use_container_width=True)
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
        st.plotly_chart(chart, use_container_width=True)
        
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
        """Render ML predictions tab (kept from original)"""
        st.header("🔮 Machine Learning Predictions")
        st.info("🚧 ML prediction features coming soon! Integration with backtesting engine planned.")
    
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
        if st.button("� Run Backtest", type="primary", use_container_width=True):
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
                    
                    st.plotly_chart(fig, use_container_width=True)
            
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
                            use_container_width=True,
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
            st.checkbox("Email Alerts", value=False)
            st.checkbox("Telegram Alerts", value=False)
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
            <p>🚀 <strong>AI Stock Trading Dashboard</strong> - Professional Monthly Trading Signals</p>
            <p><em>⚠️ DISCLAIMER: For educational purposes only. Not financial advice. Trading involves risk.</em></p>
            <p>Built with Streamlit, yfinance, and advanced sentiment analysis</p>
        </div>
        """, unsafe_allow_html=True)
    
    def _fetch_stock_data(self, symbol: str, period: str) -> pd.DataFrame:
        """Fetch stock data from yfinance"""
        try:
            ticker = yf.Ticker(symbol)
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
        df['ADX'] = self.technical_indicators.calculate_adx(df)
        df['OBV'] = self.technical_indicators.calculate_obv(df)
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
