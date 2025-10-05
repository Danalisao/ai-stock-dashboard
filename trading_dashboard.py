"""
🎯 Trading Dashboard - Détection de Pépites
Dashboard professionnel affichant uniquement les meilleures opportunités de trading

Ce dashboard est conçu pour les traders qui veulent des signaux clairs et actionnables.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import logging
from pathlib import Path

from modules.utils import load_config, setup_logging, format_currency, format_percentage
from modules.opportunity_scanner import OpportunityScanner
from modules.alert_manager import AlertManager
from modules.database_manager import DatabaseManager
from modules.technical_indicators import TechnicalIndicators
import yfinance as yf

# Configure page
st.set_page_config(
    page_title="Trading Dashboard - Détecteur de Pépites",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        font-weight: bold;
        background: linear-gradient(90deg, #FFD700, #FFA500, #FF6B6B);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    .opportunity-card {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        border-radius: 15px;
        padding: 1.5rem;
        border: 2px solid #FFD700;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
    }
    .score-badge-high {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem;
        border-radius: 15px;
    }
    .score-badge-medium {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem;
        border-radius: 15px;
    }
    .metric-positive {
        color: #38ef7d;
        font-weight: bold;
    }
    .metric-negative {
        color: #f5576c;
        font-weight: bold;
    }
    .trade-params {
        background: rgba(0,0,0,0.3);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #FFD700;
    }
</style>
""", unsafe_allow_html=True)


class TradingDashboard:
    """Dashboard for displaying golden trading opportunities"""
    
    def __init__(self):
        """Initialize dashboard"""
        self.config = load_config()
        setup_logging(self.config.get('logging', {}))
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.scanner = OpportunityScanner(self.config)
        self.alert_manager = AlertManager(self.config)
        self.db = DatabaseManager(self.config.get('database', {}))
        self.technical_indicators = TechnicalIndicators()
    
    def run(self):
        """Run the dashboard"""
        # Header
        st.markdown('<h1 class="main-header">💎 DÉTECTEUR DE PÉPITES MENSUELLES 💎</h1>', 
                   unsafe_allow_html=True)
        
        st.markdown("""
        <div style='text-align: center; font-size: 1.2rem; color: #FFD700; margin-bottom: 2rem;'>
        <b>Outil de Décision Trading Professionnel</b><br>
        <i>Seules les meilleures opportunités sont affichées ici (Score ≥ 85, R/R ≥ 2.5)</i>
        </div>
        """, unsafe_allow_html=True)
        
        # Sidebar controls
        self._render_sidebar()
        
        # Main content
        tab1, tab2, tab3, tab4 = st.tabs([
            "💎 Pépites Détectées", 
            "📊 Analyse Détaillée", 
            "📈 Graphiques",
            "⚙️ Scanner"
        ])
        
        with tab1:
            self._render_opportunities_tab()
        
        with tab2:
            self._render_analysis_tab()
        
        with tab3:
            self._render_charts_tab()
        
        with tab4:
            self._render_scanner_tab()
    
    def _render_sidebar(self):
        """Render sidebar controls"""
        with st.sidebar:
            st.image("https://img.icons8.com/color/96/000000/diamond.png", width=80)
            st.title("Contrôles")
            
            # Scan controls
            st.subheader("🔍 Scanner")
            
            if st.button("🚀 Lancer Scan Complet", use_container_width=True):
                with st.spinner("Scan en cours... (peut prendre 1-2 minutes)"):
                    opportunities = self.scanner.scan_all_opportunities()
                    st.session_state['opportunities'] = opportunities
                    st.session_state['last_scan'] = datetime.now()
                    
                    if opportunities:
                        st.success(f"✅ {len(opportunities)} pépites détectées!")
                        
                        # Send alerts
                        if st.session_state.get('auto_alert', False):
                            for opp in opportunities:
                                self._send_opportunity_alert(opp)
                    else:
                        st.warning("❌ Aucune opportunité trouvée")
            
            # Auto-alert toggle
            st.session_state['auto_alert'] = st.checkbox(
                "📢 Alertes automatiques", 
                value=st.session_state.get('auto_alert', True)
            )
            
            # Last scan info
            if 'last_scan' in st.session_state:
                last_scan = st.session_state['last_scan']
                st.info(f"Dernier scan: {last_scan.strftime('%H:%M:%S')}")
            
            st.divider()
            
            # Filters
            st.subheader("🎚️ Filtres")
            min_score = st.slider("Score minimum", 80, 100, 85)
            min_rr = st.slider("R/R minimum", 1.5, 5.0, 2.5, 0.5)
            
            st.session_state['min_score'] = min_score
            st.session_state['min_rr'] = min_rr
            
            st.divider()
            
            # Stats
            if 'opportunities' in st.session_state:
                opps = st.session_state['opportunities']
                st.subheader("📊 Statistiques")
                st.metric("Pépites trouvées", len(opps))
                
                if opps:
                    avg_score = sum(o['score'] for o in opps) / len(opps)
                    st.metric("Score moyen", f"{avg_score:.1f}")
                    
                    avg_rr = sum(o['risk_reward'] for o in opps) / len(opps)
                    st.metric("R/R moyen", f"1:{avg_rr:.2f}")
    
    def _render_opportunities_tab(self):
        """Render main opportunities tab"""
        if 'opportunities' not in st.session_state or not st.session_state['opportunities']:
            st.info("👆 Cliquez sur 'Lancer Scan Complet' pour détecter les pépites")
            
            # Show example of what will be displayed
            st.markdown("""
            ### Ce que vous verrez ici:
            - 🎯 **Score 85-100**: Opportunités avec tous les indicateurs alignés
            - ⚖️ **Risk/Reward ≥ 2.5**: Minimum 2.5$ de gain pour 1$ de risque
            - 📊 **Volume confirmé**: Volume supérieur à 1.3x la moyenne
            - 💪 **Confiance élevée**: Tous les composants au-dessus de 70/100
            - 🎯 **Prix clairs**: Entrée, Take Profit, Stop Loss précis
            """)
            return
        
        # Filter opportunities
        opportunities = self._filter_opportunities(st.session_state['opportunities'])
        
        if not opportunities:
            st.warning("Aucune opportunité ne correspond aux filtres sélectionnés")
            return
        
        # Display count
        st.markdown(f"### 🌟 {len(opportunities)} Pépites Détectées")
        
        # Display each opportunity
        for i, opp in enumerate(opportunities, 1):
            self._render_opportunity_card(opp, i)
    
    def _render_opportunity_card(self, opp: dict, index: int):
        """Render a single opportunity card"""
        # Card container
        with st.container():
            # Score badge color
            badge_class = "score-badge-high" if opp['score'] >= 90 else "score-badge-medium"
            
            col1, col2, col3 = st.columns([1, 2, 2])
            
            with col1:
                # Score badge
                st.markdown(f"""
                <div class="{badge_class}">
                    {opp['score']:.1f}
                </div>
                <div style='text-align: center; margin-top: 0.5rem; font-size: 1.1rem;'>
                    <b>{opp['recommendation']}</b>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Stock info
                st.markdown(f"""
                ### {index}. {opp['symbol']} - {opp['name']}
                **Conviction:** {opp['conviction']}  
                **Prix actuel:** ${opp['current_price']:.2f}  
                **Volatilité:** {opp['volatility']:.1f}% | **Volume:** {opp['volume_ratio']:.1f}x
                """)
            
            with col3:
                # Trading parameters
                target_class = "metric-positive"
                stop_class = "metric-negative"
                
                st.markdown(f"""
                <div class='trade-params'>
                <b>🎯 PARAMÈTRES DE TRADE:</b><br>
                🟢 <b>Entrée:</b> ${opp['entry_price']:.2f}<br>
                <span class='{target_class}'>🎯 Take Profit: ${opp['target_price']:.2f} (+{opp['target_pct']:.1f}%)</span><br>
                <span class='{stop_class}'>🛑 Stop Loss: ${opp['stop_loss']:.2f} (-{opp['stop_loss_pct']:.1f}%)</span><br>
                ⚖️ <b>Risk/Reward: 1:{opp['risk_reward']:.2f}</b><br>
                💼 <b>Position: {opp['position_size']}</b>
                </div>
                """, unsafe_allow_html=True)
            
            # Score breakdown
            with st.expander(f"📊 Détails de l'analyse - {opp['symbol']}"):
                col_a, col_b, col_c, col_d, col_e = st.columns(5)
                
                col_a.metric("Trend", f"{opp['trend_score']:.0f}/100")
                col_b.metric("Momentum", f"{opp['momentum_score']:.0f}/100")
                col_c.metric("Sentiment", f"{opp['sentiment_score']:.0f}/100")
                col_d.metric("Divergence", f"{opp['divergence_score']:.0f}/100")
                col_e.metric("Volume", f"{opp['volume_score']:.0f}/100")
                
                st.markdown(f"**Description:** {opp['description']}")
                st.markdown(f"**Confiance:** {opp['confidence']*100:.0f}%")
                
                # Action buttons
                btn_col1, btn_col2, btn_col3 = st.columns(3)
                
                with btn_col1:
                    if st.button(f"📈 Voir Graphique", key=f"chart_{opp['symbol']}"):
                        st.session_state['selected_symbol'] = opp['symbol']
                        st.rerun()
                
                with btn_col2:
                    if st.button(f"📢 Envoyer Alerte", key=f"alert_{opp['symbol']}"):
                        self._send_opportunity_alert(opp)
                        st.success(f"✅ Alerte envoyée pour {opp['symbol']}")
                
                with btn_col3:
                    if st.button(f"📋 Copier Message", key=f"copy_{opp['symbol']}"):
                        msg = self.scanner.generate_alert_message(opp)
                        st.code(msg, language=None)
            
            st.divider()
    
    def _render_analysis_tab(self):
        """Render detailed analysis tab"""
        if 'opportunities' not in st.session_state or not st.session_state['opportunities']:
            st.info("Lancez un scan d'abord")
            return
        
        opportunities = self._filter_opportunities(st.session_state['opportunities'])
        
        if not opportunities:
            st.warning("Aucune opportunité")
            return
        
        # Create DataFrame
        df = self.scanner.export_opportunities_to_dataframe(opportunities)
        
        # Display table
        st.markdown("### 📊 Table Récapitulative")
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
        
        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Télécharger CSV",
            data=csv,
            file_name=f"opportunites_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )
        
        # Charts
        st.markdown("### 📈 Visualisations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Score distribution
            fig = px.histogram(
                df, 
                x='score', 
                nbins=20,
                title="Distribution des Scores",
                labels={'score': 'Score', 'count': 'Nombre'}
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Risk/Reward distribution
            fig = px.scatter(
                df,
                x='score',
                y='risk_reward',
                size='volume_ratio',
                color='confidence',
                hover_data=['symbol', 'recommendation'],
                title="Score vs Risk/Reward",
                labels={
                    'score': 'Score',
                    'risk_reward': 'Risk/Reward',
                    'volume_ratio': 'Volume Ratio',
                    'confidence': 'Confiance'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Top opportunities by score
        st.markdown("### 🏆 Top 10 par Score")
        top_10 = df.nlargest(10, 'score')[['symbol', 'name', 'score', 'risk_reward', 'target_pct']]
        st.dataframe(top_10, use_container_width=True, hide_index=True)
    
    def _render_charts_tab(self):
        """Render charts tab"""
        if 'opportunities' not in st.session_state or not st.session_state['opportunities']:
            st.info("Lancez un scan d'abord")
            return
        
        opportunities = st.session_state['opportunities']
        
        # Symbol selection
        symbols = [opp['symbol'] for opp in opportunities]
        selected_symbol = st.selectbox(
            "Sélectionnez une action",
            symbols,
            index=0 if not st.session_state.get('selected_symbol') 
                  else symbols.index(st.session_state.get('selected_symbol')) 
                  if st.session_state.get('selected_symbol') in symbols else 0
        )
        
        # Find opportunity data
        opp = next((o for o in opportunities if o['symbol'] == selected_symbol), None)
        
        if not opp:
            st.error("Opportunité non trouvée")
            return
        
        # Display opportunity summary
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Score", f"{opp['score']:.1f}/100")
        col2.metric("Prix", f"${opp['current_price']:.2f}")
        col3.metric("Take Profit", f"+{opp['target_pct']:.1f}%")
        col4.metric("Risk/Reward", f"1:{opp['risk_reward']:.2f}")
        
        # Fetch data and create chart
        with st.spinner(f"Chargement des données pour {selected_symbol}..."):
            ticker = yf.Ticker(selected_symbol)
            data = ticker.history(period='3mo')
            
            if data.empty:
                st.error("Impossible de charger les données")
                return
            
            # Calculate indicators
            indicators = self.technical_indicators.calculate_all_indicators(data)
            
            # Create candlestick chart with entry/TP/SL lines
            fig = go.Figure()
            
            # Candlestick
            fig.add_trace(go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name=selected_symbol
            ))
            
            # Add entry/TP/SL lines
            last_date = data.index[-1]
            future_date = last_date + pd.Timedelta(days=30)
            
            # Entry line
            fig.add_hline(
                y=opp['entry_price'],
                line_dash="dash",
                line_color="blue",
                annotation_text=f"Entrée: ${opp['entry_price']:.2f}"
            )
            
            # Take profit line
            fig.add_hline(
                y=opp['target_price'],
                line_dash="dash",
                line_color="green",
                annotation_text=f"TP: ${opp['target_price']:.2f} (+{opp['target_pct']:.1f}%)"
            )
            
            # Stop loss line
            fig.add_hline(
                y=opp['stop_loss'],
                line_dash="dash",
                line_color="red",
                annotation_text=f"SL: ${opp['stop_loss']:.2f} (-{opp['stop_loss_pct']:.1f}%)"
            )
            
            # Add moving averages if available
            if 'SMA_20' in indicators:
                fig.add_trace(go.Scatter(
                    x=data.index,
                    y=indicators['SMA_20'],
                    mode='lines',
                    name='SMA 20',
                    line=dict(color='orange', width=1)
                ))
            
            if 'SMA_50' in indicators:
                fig.add_trace(go.Scatter(
                    x=data.index,
                    y=indicators['SMA_50'],
                    mode='lines',
                    name='SMA 50',
                    line=dict(color='purple', width=1)
                ))
            
            fig.update_layout(
                title=f"{selected_symbol} - Plan de Trade",
                yaxis_title="Prix ($)",
                xaxis_title="Date",
                height=600,
                template="plotly_dark"
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    def _render_scanner_tab(self):
        """Render scanner configuration tab"""
        st.markdown("### ⚙️ Configuration du Scanner")
        
        st.markdown("""
        Le scanner analyse automatiquement **120+ actions** avec les critères suivants:
        
        **Critères de Sélection Stricts:**
        - ✅ Score global ≥ 85/100
        - ✅ Risk/Reward ≥ 2.5
        - ✅ Confiance ≥ 70%
        - ✅ Volume ≥ 1.3x la moyenne
        - ✅ Tous les composants ≥ 70/100
        - ✅ Volatilité entre 15% et 80%
        
        **Seules les pépites répondant à TOUS ces critères sont affichées.**
        """)
        
        st.divider()
        
        # Scanner status
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Watchlist")
            st.info(f"**{len(self.scanner.EXTENDED_WATCHLIST)}** actions surveillées")
            
            # Show some symbols
            with st.expander("Voir la liste complète"):
                symbols_df = pd.DataFrame([
                    {'Symbol': k, 'Nom': v} 
                    for k, v in list(self.scanner.EXTENDED_WATCHLIST.items())[:50]
                ])
                st.dataframe(symbols_df, hide_index=True, use_container_width=True)
        
        with col2:
            st.markdown("### 🎯 Critères")
            st.metric("Score minimum", "85/100")
            st.metric("Risk/Reward minimum", "2.5")
            st.metric("Confiance minimum", "70%")
            st.metric("Volume minimum", "1.3x")
    
    def _filter_opportunities(self, opportunities):
        """Filter opportunities based on sidebar filters"""
        min_score = st.session_state.get('min_score', 85)
        min_rr = st.session_state.get('min_rr', 2.5)
        
        filtered = [
            opp for opp in opportunities
            if opp['score'] >= min_score and opp['risk_reward'] >= min_rr
        ]
        
        return filtered
    
    def _send_opportunity_alert(self, opp: dict):
        """Send alert for an opportunity"""
        message = self.scanner.generate_alert_message(opp)
        priority = 'CRITICAL' if opp['score'] >= 90 else 'HIGH'
        
        self.alert_manager.send_alert(
            alert_type='GOLDEN_OPPORTUNITY',
            symbol=opp['symbol'],
            message=message,
            priority=priority,
            value=opp['score'],
            data=opp
        )


def main():
    """Main entry point"""
    dashboard = TradingDashboard()
    dashboard.run()


if __name__ == '__main__':
    main()
