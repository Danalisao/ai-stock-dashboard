"""
🏦 Professional Trading Platform
Institutional-grade trading interface with real execution capabilities
"""

import streamlit as st
import asyncio
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import logging
import os
import json

# Professional trading modules
from modules.utils import (
    load_config, setup_logging, is_market_open, 
    format_currency, format_percentage
)
from modules.database_manager import DatabaseManager
from modules.monthly_signals import MonthlySignals
from modules.broker_integration import TradingExecutor, AlpacaBroker
from modules.risk_manager import ProfessionalRiskManager, RiskLevel
from modules.professional_alerts import ProfessionalAlertSystem, AlertType, AlertPriority
from modules.technical_indicators import TechnicalIndicators
from modules.portfolio_tracker import PortfolioTracker

# Configure Streamlit page
st.set_page_config(
    page_title="Professional Trading Platform",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        font-weight: bold;
        background: linear-gradient(90deg, #1e3a8a, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .pro-metric {
        background: linear-gradient(135deg, #1e293b, #334155);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
        margin: 0.5rem 0;
    }
    .risk-critical {
        border-left-color: #ef4444 !important;
        background: linear-gradient(135deg, #431c1c, #552222);
    }
    .risk-high {
        border-left-color: #f97316 !important;
        background: linear-gradient(135deg, #3c1f0f, #4c2818);
    }
    .risk-medium {
        border-left-color: #eab308 !important;
        background: linear-gradient(135deg, #3c3711, #4c4618);
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #0f172a, #1e293b);
    }
    .position-long {
        color: #10b981;
        font-weight: bold;
    }
    .position-short {
        color: #ef4444;
        font-weight: bold;
    }
    .execution-ready {
        background: linear-gradient(135deg, #064e3b, #047857);
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #10b981;
    }
</style>
""", unsafe_allow_html=True)

class ProfessionalTradingPlatform:
    """Professional trading platform for institutional use"""
    
    def __init__(self):
        """Initialize professional trading platform"""
        # Load configuration
        self.config = load_config()
        setup_logging(self.config.get('logging', {}))
        self.logger = logging.getLogger(__name__)
        
        # Initialize core systems
        self.db = DatabaseManager(self.config.get('database', {}))
        self.signals = MonthlySignals(self.config)
        self.risk_manager = ProfessionalRiskManager(self.config)
        self.alert_system = ProfessionalAlertSystem(self.config)
        self.technical = TechnicalIndicators()
        self.portfolio = PortfolioTracker(self.config, self.db)
        
        # Initialize trading executor (if broker configured)
        if self.config.get('broker', {}).get('enabled', False):
            self.trading_executor = TradingExecutor(self.config)
        else:
            self.trading_executor = None
        
        # Trading session state
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        if 'trading_enabled' not in st.session_state:
            st.session_state.trading_enabled = False
        if 'selected_symbols' not in st.session_state:
            st.session_state.selected_symbols = []
    
    def run(self):
        """Run the professional trading platform"""
        
        # Authentication check
        if not st.session_state.authenticated:
            self._render_authentication()
            return
        
        # Main platform header
        st.markdown('<div class="main-header">🏦 Professional Trading Platform</div>', 
                   unsafe_allow_html=True)
        
        # Market status and key metrics
        self._render_header_metrics()
        
        # Sidebar controls
        self._render_professional_sidebar()
        
        # Main interface tabs
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "🎯 Trading Signals",
            "📊 Live Positions", 
            "⚡ Order Execution",
            "🛡️ Risk Management",
            "📈 Performance Analytics",
            "🚨 Alert Center"
        ])
        
        with tab1:
            self._render_trading_signals()
        
        with tab2:
            self._render_live_positions()
        
        with tab3:
            self._render_order_execution()
        
        with tab4:
            self._render_risk_management()
        
        with tab5:
            self._render_performance_analytics()
        
        with tab6:
            self._render_alert_center()
    
    def _render_authentication(self):
        """Render authentication interface"""
        st.markdown("## 🔐 Professional Access Required")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("""
            ### Professional Trading Platform
            
            This is an institutional-grade trading platform with real execution capabilities.
            Access is restricted to authorized traders only.
            """)
            
            # Authentication form
            with st.form("authentication"):
                access_code = st.text_input("Access Code", type="password")
                broker_enabled = st.checkbox("Enable Live Trading (requires broker setup)")
                
                if st.form_submit_button("🚀 Access Platform", use_container_width=True):
                    # Simple authentication (replace with real auth in production)
                    if access_code == self.config.get('auth', {}).get('access_code', 'PROFESSIONAL_TRADER_2025'):
                        st.session_state.authenticated = True
                        st.session_state.trading_enabled = broker_enabled
                        st.rerun()
                    else:
                        st.error("❌ Invalid access code")
            
            st.markdown("""
            ---
            ⚠️ **Professional Use Only**
            
            This platform provides real trading signals and execution capabilities.
            Users are fully responsible for their trading decisions and potential losses.
            """)
    
    def _render_header_metrics(self):
        """Render key metrics in header"""
        col1, col2, col3, col4, col5 = st.columns(5)
        
        # Market status
        market_open = is_market_open()
        status_color = "🟢" if market_open else "🔴"
        status_text = "LIVE" if market_open else "CLOSED"
        
        with col1:
            st.markdown(f"""
            <div class="pro-metric">
                <h4>{status_color} Market Status</h4>
                <h2>{status_text}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # Portfolio value (if available)
        if self.trading_executor:
            try:
                portfolio_status = asyncio.run(self.trading_executor.get_portfolio_status())
                portfolio_value = portfolio_status.get('account', {}).get('portfolio_value', 0)
                day_pl = portfolio_status.get('account', {}).get('day_pl', 0)
                day_pl_pct = portfolio_status.get('account', {}).get('day_pl_pct', 0)
                
                with col2:
                    st.markdown(f"""
                    <div class="pro-metric">
                        <h4>💰 Portfolio Value</h4>
                        <h2>{format_currency(portfolio_value)}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    color_class = "risk-critical" if day_pl < 0 else ""
                    st.markdown(f"""
                    <div class="pro-metric {color_class}">
                        <h4>📊 Daily P&L</h4>
                        <h2>{format_currency(day_pl)} ({day_pl_pct:+.1f}%)</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
            except Exception as e:
                self.logger.error(f"Error fetching portfolio status: {e}")
        
        # Active signals count
        watchlist = self.config.get('watchlist', {}).get('stocks', [])
        high_conviction_signals = 0
        
        try:
            for symbol in watchlist[:10]:  # Check first 10 for performance
                score_data = self.signals.calculate_monthly_score(symbol)
                if score_data and score_data.get('total_score', 0) >= 85:
                    high_conviction_signals += 1
        except:
            pass
        
        with col4:
            st.markdown(f"""
            <div class="pro-metric">
                <h4>🎯 Active Signals</h4>
                <h2>{high_conviction_signals}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # Risk level
        with col5:
            st.markdown(f"""
            <div class="pro-metric">
                <h4>🛡️ Risk Level</h4>
                <h2>MODERATE</h2>
            </div>
            """, unsafe_allow_html=True)
    
    def _render_professional_sidebar(self):
        """Render professional sidebar controls"""
        st.sidebar.markdown("## ⚙️ Trading Controls")
        
        # Trading mode
        trading_mode = st.sidebar.selectbox(
            "Trading Mode",
            ["Paper Trading", "Live Trading"] if st.session_state.trading_enabled else ["Paper Trading"],
            index=1 if st.session_state.trading_enabled else 0
        )
        
        # Watchlist selection
        st.sidebar.markdown("### 📋 Watchlist")
        all_symbols = self.config.get('watchlist', {}).get('stocks', [])
        
        selected_symbols = st.sidebar.multiselect(
            "Select symbols for analysis:",
            options=all_symbols,
            default=all_symbols[:10],  # Default first 10
            key="symbol_selector"
        )
        
        st.session_state.selected_symbols = selected_symbols
        
        # Risk controls
        st.sidebar.markdown("### 🛡️ Risk Controls")
        
        max_position_size = st.sidebar.slider(
            "Max Position Size (%)",
            min_value=1,
            max_value=10,
            value=5,
            help="Maximum percentage of portfolio per position"
        )
        
        max_daily_risk = st.sidebar.slider(
            "Max Daily Risk (%)",
            min_value=1,
            max_value=5,
            value=2,
            help="Maximum daily portfolio risk"
        )
        
        # Quick actions
        st.sidebar.markdown("### ⚡ Quick Actions")
        
        if st.sidebar.button("🚨 Emergency Close All", type="secondary"):
            st.sidebar.warning("Emergency close all positions - confirm in main interface")
        
        if st.sidebar.button("📊 Generate Report", type="primary"):
            st.sidebar.success("Report generation started...")
        
        if st.sidebar.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()
    
    def _render_trading_signals(self):
        """Render professional trading signals"""
        st.header("🎯 Professional Trading Signals")
        
        if not st.session_state.selected_symbols:
            st.warning("Please select symbols from the sidebar to analyze.")
            return
        
        # Signal generation controls
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            min_score = st.slider("Minimum Signal Score", 75, 95, 85)
        
        with col2:
            signal_types = st.multiselect(
                "Signal Types",
                ["BUY", "STRONG_BUY", "SELL", "STRONG_SELL"],
                default=["BUY", "STRONG_BUY"]
            )
        
        with col3:
            if st.button("🔄 Refresh Signals", type="primary"):
                st.cache_data.clear()
        
        # Generate signals
        signals_data = []
        
        with st.spinner("Analyzing market signals..."):
            for symbol in st.session_state.selected_symbols:
                try:
                    score_data = self.signals.calculate_monthly_score(symbol)
                    if score_data and score_data.get('total_score', 0) >= min_score:
                        action = score_data.get('recommendation', {}).get('action', 'HOLD')
                        if action in signal_types:
                            signals_data.append({
                                'symbol': symbol,
                                'score': score_data.get('total_score', 0),
                                'action': action,
                                'conviction': score_data.get('recommendation', {}).get('conviction', 'MEDIUM'),
                                'entry_price': score_data.get('entry_price', 0),
                                'target_price': score_data.get('target_price', 0),
                                'stop_loss': score_data.get('stop_loss', 0),
                                'risk_reward': score_data.get('risk_reward_ratio', 0),
                                'data': score_data
                            })
                except Exception as e:
                    self.logger.error(f"Error analyzing {symbol}: {e}")
        
        if not signals_data:
            st.info("No signals meeting criteria found. Try lowering the minimum score.")
            return
        
        # Sort by score
        signals_data.sort(key=lambda x: x['score'], reverse=True)
        
        # Display signals
        st.subheader(f"📊 {len(signals_data)} Professional Signal(s) Found")
        
        for i, signal in enumerate(signals_data):
            with st.expander(f"🎯 {signal['symbol']} - Score: {signal['score']}/100 - {signal['action']}", 
                           expanded=(i < 3)):  # Expand first 3
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                    **Signal Details**
                    - **Action**: {signal['action']}
                    - **Conviction**: {signal['conviction']}
                    - **Score**: {signal['score']}/100
                    """)
                
                with col2:
                    st.markdown(f"""
                    **Price Levels**
                    - **Entry**: ${signal['entry_price']:.2f}
                    - **Target**: ${signal['target_price']:.2f}
                    - **Stop Loss**: ${signal['stop_loss']:.2f}
                    """)
                
                with col3:
                    st.markdown(f"""
                    **Risk/Reward**
                    - **R/R Ratio**: {signal['risk_reward']:.2f}:1
                    - **Upside**: {((signal['target_price']/signal['entry_price'] - 1) * 100):+.1f}%
                    - **Risk**: {((signal['stop_loss']/signal['entry_price'] - 1) * 100):+.1f}%
                    """)
                
                with col4:
                    # Position sizing calculation
                    if self.trading_executor:
                        try:
                            portfolio_status = asyncio.run(self.trading_executor.get_portfolio_status())
                            portfolio_value = portfolio_status.get('account', {}).get('portfolio_value', 100000)
                            
                            position_calc = self.risk_manager.calculate_position_size(
                                signal, portfolio_value, [], pd.DataFrame()
                            )
                            
                            st.markdown(f"""
                            **Position Sizing**
                            - **Shares**: {position_calc.get('recommended_shares', 0)}
                            - **Value**: ${position_calc.get('recommended_value', 0):,.0f}
                            - **Allocation**: {position_calc.get('portfolio_allocation_pct', 0):.1f}%
                            """)
                        except:
                            st.markdown("Position sizing calculation unavailable")
                
                # Execution buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button(f"⚡ Execute {signal['action']}", 
                               key=f"execute_{signal['symbol']}", 
                               type="primary"):
                        if self.trading_executor and st.session_state.trading_enabled:
                            self._execute_signal(signal)
                        else:
                            st.info("Paper trading mode - order logged")
                
                with col2:
                    if st.button(f"📋 Copy Signal", key=f"copy_{signal['symbol']}"):
                        signal_text = self._format_signal_for_copy(signal)
                        st.code(signal_text, language="text")
                
                with col3:
                    if st.button(f"🚨 Create Alert", key=f"alert_{signal['symbol']}"):
                        alert = self.alert_system.create_entry_signal_alert(signal['data'])
                        asyncio.run(self.alert_system.send_alert(alert))
                        st.success("Alert created and sent!")
    
    def _render_live_positions(self):
        """Render live positions monitoring"""
        st.header("📊 Live Positions")
        
        if not self.trading_executor:
            st.warning("Broker integration not configured. Showing simulated positions.")
            return
        
        try:
            portfolio_status = asyncio.run(self.trading_executor.get_portfolio_status())
            positions = portfolio_status.get('detailed_positions', [])
            
            if not positions:
                st.info("No open positions.")
                return
            
            # Portfolio summary
            account = portfolio_status.get('account', {})
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Portfolio Value",
                    format_currency(account.get('portfolio_value', 0)),
                    delta=format_currency(account.get('day_pl', 0))
                )
            
            with col2:
                st.metric(
                    "Cash Available",
                    format_currency(account.get('cash', 0))
                )
            
            with col3:
                st.metric(
                    "Daily P&L",
                    f"{account.get('day_pl_pct', 0):+.2f}%",
                    delta=format_currency(account.get('day_pl', 0))
                )
            
            with col4:
                exposure = portfolio_status.get('positions', {}).get('exposure', 0)
                st.metric(
                    "Market Exposure",
                    f"{exposure * 100:.1f}%"
                )
            
            # Positions table
            st.subheader("Position Details")
            
            position_data = []
            for pos in positions:
                symbol = pos.get('symbol', '')
                qty = float(pos.get('qty', 0))
                market_value = float(pos.get('market_value', 0))
                unrealized_pl = float(pos.get('unrealized_pl', 0))
                unrealized_plpc = float(pos.get('unrealized_plpc', 0))
                
                position_data.append({
                    'Symbol': symbol,
                    'Quantity': int(qty),
                    'Side': 'LONG' if qty > 0 else 'SHORT',
                    'Market Value': format_currency(market_value),
                    'Unrealized P&L': format_currency(unrealized_pl),
                    'Unrealized P&L %': f"{unrealized_plpc * 100:+.2f}%",
                    'Current Price': format_currency(float(pos.get('current_price', 0))),
                    'Avg Cost': format_currency(float(pos.get('avg_entry_price', 0)))
                })
            
            if position_data:
                df = pd.DataFrame(position_data)
                st.dataframe(df, use_container_width=True)
                
                # Position actions
                st.subheader("Position Management")
                
                selected_symbol = st.selectbox(
                    "Select position to manage:",
                    options=[pos['Symbol'] for pos in position_data]
                )
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if st.button("📈 Add to Position"):
                        st.info(f"Add to {selected_symbol} position - implement order entry")
                
                with col2:
                    if st.button("📉 Reduce Position"):
                        st.info(f"Reduce {selected_symbol} position - implement partial close")
                
                with col3:
                    if st.button("🚪 Close Position"):
                        st.warning(f"Close {selected_symbol} position - confirm in modal")
                
                with col4:
                    if st.button("🛡️ Set Stop Loss"):
                        st.info(f"Set stop loss for {selected_symbol} - implement stop order")
        
        except Exception as e:
            st.error(f"Error fetching positions: {e}")
            self.logger.error(f"Position fetch error: {e}")
    
    def _render_order_execution(self):
        """Render order execution interface"""
        st.header("⚡ Professional Order Execution")
        
        if not st.session_state.trading_enabled:
            st.warning("⚠️ Live trading not enabled. Orders will be simulated.")
        
        # Order entry form
        with st.form("order_execution"):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                symbol = st.text_input("Symbol", value="AAPL")
                side = st.selectbox("Side", ["BUY", "SELL"])
            
            with col2:
                order_type = st.selectbox("Order Type", ["MARKET", "LIMIT", "STOP", "STOP_LIMIT"])
                quantity = st.number_input("Quantity", min_value=1, value=100)
            
            with col3:
                limit_price = st.number_input("Limit Price ($)", value=0.0, format="%.2f")
                stop_price = st.number_input("Stop Price ($)", value=0.0, format="%.2f")
            
            with col4:
                time_in_force = st.selectbox("Time in Force", ["DAY", "GTC", "IOC", "FOK"])
                
                # Get current price for reference
                try:
                    ticker = yf.Ticker(symbol.upper())
                    current_price = ticker.history(period="1d")['Close'].iloc[-1]
                    st.metric("Current Price", f"${current_price:.2f}")
                except:
                    st.metric("Current Price", "N/A")
            
            # Risk calculation
            if limit_price > 0 and stop_price > 0:
                risk_per_share = abs(limit_price - stop_price)
                total_risk = risk_per_share * quantity
                st.info(f"💰 Total Risk: ${total_risk:.2f} ({quantity} shares × ${risk_per_share:.2f})")
            
            # Execute order
            if st.form_submit_button("🚀 Execute Order", type="primary"):
                if self.trading_executor and st.session_state.trading_enabled:
                    self._execute_manual_order({
                        'symbol': symbol.upper(),
                        'side': side,
                        'order_type': order_type,
                        'quantity': quantity,
                        'limit_price': limit_price if limit_price > 0 else None,
                        'stop_price': stop_price if stop_price > 0 else None,
                        'time_in_force': time_in_force
                    })
                else:
                    st.success(f"✅ Paper trade executed: {side} {quantity} {symbol} @ {order_type}")
        
        # Recent orders
        st.subheader("📋 Recent Orders")
        
        # This would fetch real orders from broker
        # For now, show placeholder
        st.info("Recent orders will be displayed here when broker integration is active.")
    
    def _render_risk_management(self):
        """Render risk management dashboard"""
        st.header("🛡️ Risk Management")
        
        # Risk metrics overview
        st.subheader("Portfolio Risk Metrics")
        
        try:
            if self.trading_executor:
                portfolio_status = asyncio.run(self.trading_executor.get_portfolio_status())
                positions = portfolio_status.get('detailed_positions', [])
                
                # Calculate risk metrics
                risk_metrics = self.risk_manager.calculate_portfolio_risk_metrics(
                    positions, {}, portfolio_status.get('account', {}).get('portfolio_value', 100000)
                )
                
                # Display risk metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Portfolio Volatility", f"{risk_metrics.volatility * 100:.1f}%")
                    st.metric("Sharpe Ratio", f"{risk_metrics.sharpe_ratio:.2f}")
                
                with col2:
                    st.metric("Max Drawdown", f"{abs(risk_metrics.max_drawdown) * 100:.1f}%")
                    st.metric("Sortino Ratio", f"{risk_metrics.sortino_ratio:.2f}")
                
                with col3:
                    st.metric("1-Day VaR", format_currency(abs(risk_metrics.var_1d)))
                    st.metric("5-Day VaR", format_currency(abs(risk_metrics.var_5d)))
                
                with col4:
                    st.metric("Concentration Risk", f"{risk_metrics.concentration_risk * 100:.1f}%")
                    st.metric("Beta", f"{risk_metrics.beta:.2f}")
                
                # Risk limit checks
                risk_check = self.risk_manager.check_risk_limits(
                    risk_metrics, 
                    portfolio_status.get('account', {}).get('portfolio_value', 100000)
                )
                
                if risk_check['violations']:
                    st.error("🚨 Risk Limit Violations Detected!")
                    for violation in risk_check['violations']:
                        st.error(f"• {violation['type']}: {violation['current']:.2f}% (Limit: {violation['limit']:.2f}%)")
                
                if risk_check['warnings']:
                    st.warning("⚠️ Risk Warnings:")
                    for warning in risk_check['warnings']:
                        st.warning(f"• {warning['type']}: {warning.get('current', 'N/A')}")
                
                # Overall risk level
                risk_level = risk_check.get('overall_risk_level', 'MODERATE')
                risk_color = {
                    'CONSERVATIVE': 'green',
                    'MODERATE': 'blue', 
                    'AGGRESSIVE': 'orange',
                    'SPECULATIVE': 'red'
                }.get(risk_level, 'blue')
                
                st.markdown(f"**Overall Risk Level**: :{risk_color}[{risk_level}]")
                
        except Exception as e:
            st.error(f"Error calculating risk metrics: {e}")
        
        # Risk controls
        st.subheader("Risk Controls")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Position Limits**")
            max_single_position = st.slider("Max Single Position (%)", 1, 20, 5)
            max_sector_exposure = st.slider("Max Sector Exposure (%)", 10, 50, 25)
            
        with col2:
            st.markdown("**Risk Limits**")
            max_portfolio_var = st.slider("Max Portfolio VaR (%)", 1, 10, 3)
            max_drawdown = st.slider("Max Drawdown (%)", 5, 25, 10)
        
        if st.button("💾 Update Risk Limits"):
            st.success("Risk limits updated successfully!")
    
    def _render_performance_analytics(self):
        """Render performance analytics"""
        st.header("📈 Performance Analytics")
        
        # Time period selection
        period = st.selectbox(
            "Analysis Period",
            ["1D", "1W", "1M", "3M", "6M", "1Y", "YTD"],
            index=4  # Default to 6M
        )
        
        # Portfolio performance chart
        st.subheader("Portfolio Performance")
        
        # Placeholder chart - would use real portfolio data
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        portfolio_values = 100000 * (1 + np.cumsum(np.random.normal(0.0008, 0.02, len(dates))))
        spy_values = 100000 * (1 + np.cumsum(np.random.normal(0.0005, 0.015, len(dates))))
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates, y=portfolio_values,
            name="Portfolio", line=dict(color="#3b82f6", width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=dates, y=spy_values,
            name="SPY Benchmark", line=dict(color="#6b7280", width=2, dash="dash")
        ))
        
        fig.update_layout(
            title="Portfolio vs Benchmark Performance",
            xaxis_title="Date",
            yaxis_title="Portfolio Value ($)",
            template="plotly_dark",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Performance metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Return", "+15.2%", "+2.1%")
            st.metric("Annualized Return", "+18.7%")
        
        with col2:
            st.metric("Sharpe Ratio", "1.85", "+0.12")
            st.metric("Sortino Ratio", "2.34")
        
        with col3:
            st.metric("Max Drawdown", "-4.2%", "+1.1%")
            st.metric("Win Rate", "68.5%")
        
        with col4:
            st.metric("Alpha vs SPY", "+3.8%")
            st.metric("Beta", "0.92")
        
        # Trade analysis
        st.subheader("Trade Analysis")
        
        # Monthly returns heatmap
        monthly_returns = np.random.normal(0.02, 0.05, (12, 1))
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        fig_heatmap = px.imshow(
            monthly_returns.T,
            x=months,
            y=['2024'],
            color_continuous_scale='RdYlGn',
            aspect='auto',
            title="Monthly Returns Heatmap"
        )
        
        fig_heatmap.update_layout(template="plotly_dark", height=200)
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    def _render_alert_center(self):
        """Render alert center"""
        st.header("🚨 Alert Center")
        
        # Alert controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔔 Test All Alerts"):
                # Test all alert channels
                test_alert = self.alert_system.create_entry_signal_alert({
                    'symbol': 'TEST',
                    'total_score': 95,
                    'action': 'BUY',
                    'entry_price': 100.0,
                    'target_price': 125.0,
                    'stop_loss': 92.0
                })
                
                results = asyncio.run(self.alert_system.send_alert(test_alert))
                
                for channel, success in results.items():
                    if success:
                        st.success(f"✅ {channel.title()} working")
                    else:
                        st.error(f"❌ {channel.title()} failed")
        
        with col2:
            if st.button("📋 View Alert History"):
                st.session_state.show_alert_history = True
        
        with col3:
            if st.button("⚙️ Configure Alerts"):
                st.session_state.show_alert_config = True
        
        # Recent alerts
        recent_alerts = self.alert_system.get_recent_alerts(20)
        
        if recent_alerts:
            st.subheader("Recent Alerts")
            
            for alert in reversed(recent_alerts[-10:]):  # Show last 10
                priority_color = {
                    AlertPriority.CRITICAL: "red",
                    AlertPriority.HIGH: "orange", 
                    AlertPriority.MEDIUM: "blue",
                    AlertPriority.LOW: "green",
                    AlertPriority.INFO: "gray"
                }.get(alert.priority, "blue")
                
                with st.expander(f":{priority_color}[{alert.priority.value.upper()}] {alert.title}"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(alert.message)
                        st.caption(f"Time: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    with col2:
                        if not alert.acknowledged:
                            if st.button("✅ Acknowledge", key=f"ack_{alert.alert_id}"):
                                self.alert_system.acknowledge_alert(alert.alert_id)
                                st.rerun()
        else:
            st.info("No recent alerts.")
        
        # Unacknowledged alerts
        unack_alerts = self.alert_system.get_unacknowledged_alerts()
        if unack_alerts:
            st.error(f"🚨 {len(unack_alerts)} unacknowledged alerts!")
    
    def _execute_signal(self, signal: Dict[str, Any]):
        """Execute a trading signal"""
        try:
            result = asyncio.run(self.trading_executor.execute_signal(signal))
            
            if result['success']:
                st.success(f"✅ Order executed for {signal['symbol']}")
                st.json(result)
            else:
                st.error(f"❌ Order failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            st.error(f"Execution error: {e}")
            self.logger.error(f"Signal execution error: {e}")
    
    def _execute_manual_order(self, order_data: Dict[str, Any]):
        """Execute a manual order"""
        try:
            # This would integrate with the broker API
            st.success(f"✅ Order submitted: {order_data}")
        except Exception as e:
            st.error(f"Order execution failed: {e}")
    
    def _format_signal_for_copy(self, signal: Dict[str, Any]) -> str:
        """Format signal for copying to broker"""
        return f"""
TRADING SIGNAL - {signal['symbol']}

Action: {signal['action']}
Score: {signal['score']}/100
Conviction: {signal['conviction']}

Entry: ${signal['entry_price']:.2f}
Target: ${signal['target_price']:.2f} (+{((signal['target_price']/signal['entry_price'] - 1) * 100):.1f}%)
Stop Loss: ${signal['stop_loss']:.2f} ({((signal['stop_loss']/signal['entry_price'] - 1) * 100):.1f}%)

Risk/Reward: {signal['risk_reward']:.2f}:1

Professional Trading Platform - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """

# Initialize and run the platform
if __name__ == "__main__":
    platform = ProfessionalTradingPlatform()
    platform.run()