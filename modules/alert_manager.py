"""
🚨 Alert Manager
Multi-channel alert system (Desktop, Email, Telegram, Audio)
"""

import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class AlertManager:
    """Manage multi-channel alerts for trading signals"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize alert manager
        
        Args:
            config: Configuration dictionary
        """
        self.config = config.get('alerts', {})
        self.email_config = config.get('email', {})
        self.telegram_config = config.get('telegram', {})
        self.logger = logging.getLogger(__name__)
        
        # Initialize channels
        self.channels = self.config.get('channels', {})
        self.enabled = self.config.get('enabled', True)
        
        # Initialize Telegram bot
        self.telegram_bot = None
        if self.channels.get('telegram', False):
            self._init_telegram()
        
        # Initialize audio
        self.audio_enabled = self.channels.get('audio', False)
        if self.audio_enabled:
            self._init_audio()
    
    def _init_telegram(self):
        """Initialize Telegram (pure synchronous, no async)"""
        try:
            bot_token = os.getenv('TELEGRAM_BOT_TOKEN') or self.telegram_config.get('bot_token')
            self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID') or self.telegram_config.get('chat_id')
            
            if bot_token and self.telegram_chat_id:
                # Store token for direct API calls (no async library)
                self.telegram_bot_token = bot_token
                self.telegram_bot = True  # Flag to indicate Telegram is configured
                self.logger.info("Telegram bot initialized")
            else:
                self.logger.warning("Telegram bot token or chat ID not found")
                self.telegram_bot = None
                
        except Exception as e:
            self.logger.error(f"Error initializing Telegram: {e}")
            self.telegram_bot = None
    
    def _init_audio(self):
        """Initialize audio system"""
        try:
            import pygame
            pygame.mixer.init()
            self.logger.info("Audio system initialized")
        except Exception as e:
            self.logger.error(f"Error initializing audio: {e}")
            self.audio_enabled = False
    
    def send_alert(self, alert_type: str, symbol: str, message: str, 
                   priority: str = 'MEDIUM', value: Optional[float] = None,
                   data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Send alert through appropriate channels based on priority
        
        Args:
            alert_type: Type of alert (e.g., 'PRICE_ALERT', 'SIGNAL', 'NEWS')
            symbol: Stock symbol
            message: Alert message
            priority: Priority level (CRITICAL, HIGH, MEDIUM, LOW)
            value: Optional numeric value
            data: Optional additional data
            
        Returns:
            True if any alert was sent successfully
        """
        if not self.enabled:
            return False
        
        success = False
        
        try:
            # Determine which channels to use based on priority
            channels_to_use = self._get_channels_for_priority(priority)
            
            # Format message
            formatted_message = self._format_message(alert_type, symbol, message, priority, value, data)
            
            # Send through each channel
            for channel in channels_to_use:
                if channel == 'desktop' and self.channels.get('desktop', True):
                    if self._send_desktop_notification(symbol, message, priority):
                        success = True
                
                elif channel == 'email' and self.channels.get('email', False):
                    if self._send_email(alert_type, symbol, formatted_message, priority):
                        success = True
                
                elif channel == 'telegram' and self.channels.get('telegram', False):
                    if self._send_telegram(formatted_message):
                        success = True
                
                elif channel == 'audio' and self.channels.get('audio', False):
                    if self._play_alert_sound(priority):
                        success = True
            
            # Log alert
            self.logger.info(f"Alert sent: {alert_type} - {symbol} - {priority}")
            
        except Exception as e:
            self.logger.error(f"Error sending alert: {e}")
        
        return success
    
    def send_opportunity_alert(self, opportunity: Dict[str, Any]) -> bool:
        """
        Send trading opportunity alert with smart channel fallback
        Priority: Telegram > Email > Desktop/Audio
        
        Args:
            opportunity: Opportunity data from Gemini AI
            
        Returns:
            True if alert sent successfully through any channel
        """
        try:
            symbol = opportunity.get('ticker', 'N/A')
            risk_level = opportunity.get('risk_level', 'medium')
            confidence = opportunity.get('confidence', 0)
            reasoning = opportunity.get('reasoning', '')
            catalysts = opportunity.get('explosion_catalysts', [])
            
            # Format opportunity message
            catalysts_str = '\n  • '.join(catalysts[:3]) if catalysts else 'Multiple factors'
            
            message = f"""
💎 TRADING OPPORTUNITY DETECTED 💎

📊 Symbol: {symbol}
🎯 Risk Level: {risk_level.upper()}
📈 Confidence: {confidence}%

💡 Reasoning:
{reasoning}

⚡ Catalysts:
  • {catalysts_str}

🚀 Source: Gemini AI Discovery
"""
            
            # Try Telegram first (HIGH priority)
            if self.channels.get('telegram', False) and self.telegram_bot:
                if self._send_telegram(message):
                    self.logger.info(f"✅ Telegram alert sent for {symbol} ({risk_level} risk)")
                    return True
                else:
                    self.logger.warning(f"⚠️ Telegram failed for {symbol}, trying email...")
            
            # Fallback to Email (MEDIUM priority)
            if self.channels.get('email', False):
                if self._send_email('OPPORTUNITY', symbol, message, 'HIGH'):
                    self.logger.info(f"✅ Email alert sent for {symbol} ({risk_level} risk)")
                    return True
                else:
                    self.logger.warning(f"⚠️ Email failed for {symbol}, trying desktop...")
            
            # Fallback to Desktop + Audio (LOW priority)
            success = False
            if self.channels.get('desktop', True):
                if self._send_desktop_notification(
                    f"Trading Opportunity: {symbol}",
                    f"{risk_level.upper()} risk • {confidence}% confidence\n{reasoning[:100]}...",
                    'HIGH'
                ):
                    success = True
                    self.logger.info(f"✅ Desktop alert sent for {symbol}")
            
            if self.channels.get('audio', False):
                if self._play_alert_sound('HIGH'):
                    success = True
                    self.logger.info(f"✅ Audio alert played for {symbol}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending opportunity alert: {e}")
            return False
    
    def _get_channels_for_priority(self, priority: str) -> List[str]:
        """Determine which channels to use based on priority"""
        priority_upper = priority.upper()
        
        if priority_upper == 'CRITICAL':
            return ['desktop', 'email', 'telegram', 'audio']
        elif priority_upper == 'HIGH':
            return ['desktop', 'telegram', 'audio']
        elif priority_upper == 'MEDIUM':
            return ['desktop']
        else:  # LOW
            return []  # Log only
    
    def _format_message(self, alert_type: str, symbol: str, message: str,
                        priority: str, value: Optional[float], 
                        data: Optional[Dict[str, Any]]) -> str:
        """Format alert message with details"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        formatted = f"""
🚨 STOCK ALERT - {priority} 🚨
━━━━━━━━━━━━━━━━━━━━━━
📊 Symbol: {symbol}
⚡ Type: {alert_type}
🕐 Time: {timestamp}

📋 Message:
{message}
"""
        
        if value is not None:
            formatted += f"\n💰 Value: {value}"
        
        if data:
            formatted += "\n\n📈 Details:"
            for key, val in data.items():
                formatted += f"\n  • {key}: {val}"
        
        formatted += "\n━━━━━━━━━━━━━━━━━━━━━━"
        
        return formatted
    
    def _send_desktop_notification(self, title: str, message: str, priority: str) -> bool:
        """Send desktop notification"""
        try:
            from plyer import notification
            
            # Choose icon based on priority
            if priority == 'CRITICAL':
                app_icon = None  # Could add custom icon path
            elif priority == 'HIGH':
                app_icon = None
            else:
                app_icon = None
            
            notification.notify(
                title=f"📈 {title}",
                message=message[:200],  # Limit message length
                app_name="Stock Dashboard",
                timeout=10 if priority in ['CRITICAL', 'HIGH'] else 5
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending desktop notification: {e}")
            return False
    
    def _send_email(self, alert_type: str, symbol: str, message: str, priority: str) -> bool:
        """Send email alert"""
        try:
            sender_email = os.getenv('GMAIL_EMAIL') or self.email_config.get('sender_email')
            sender_password = os.getenv('GMAIL_APP_PASSWORD') or self.email_config.get('sender_password')
            recipient_email = self.email_config.get('recipient_email') or sender_email
            
            if not all([sender_email, sender_password, recipient_email]):
                self.logger.warning("Email credentials not configured")
                return False
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[{priority}] Stock Alert: {symbol} - {alert_type}"
            msg['From'] = sender_email
            msg['To'] = recipient_email
            
            # HTML version
            html_body = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .header {{ background-color: #{'#d32f2f' if priority == 'CRITICAL' else '#1976d2'}; color: white; padding: 20px; }}
                    .content {{ padding: 20px; }}
                    .footer {{ background-color: #f5f5f5; padding: 10px; text-align: center; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🚨 Stock Alert</h1>
                </div>
                <div class="content">
                    <pre>{message}</pre>
                </div>
                <div class="footer">
                    <p>AI Stock Dashboard - Automated Alert System</p>
                </div>
            </body>
            </html>
            """
            
            part = MIMEText(html_body, 'html')
            msg.attach(part)
            
            # Send email
            smtp_server = self.email_config.get('smtp_server', 'smtp.gmail.com')
            smtp_port = self.email_config.get('smtp_port', 587)
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
            
            self.logger.info(f"Email alert sent to {recipient_email}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending email: {e}")
            return False
    
    def _send_telegram(self, message: str) -> bool:
        """Send Telegram message (pure synchronous, no async warnings)"""
        try:
            if not self.telegram_bot or not self.telegram_chat_id:
                return False
            
            # Use Telegram HTTP API directly with requests (100% synchronous)
            import requests
            
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            
            # Escape Markdown special characters for safety
            # Or use HTML parse_mode which is more forgiving
            payload = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'HTML'  # More forgiving than Markdown
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            self.logger.info("Telegram alert sent")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending Telegram message: {e}")
            return False
    
    def _play_alert_sound(self, priority: str) -> bool:
        """Play alert sound"""
        try:
            if not self.audio_enabled:
                return False
            
            import pygame
            
            # Map priority to sound file
            sound_files = {
                'CRITICAL': 'assets/sounds/critical_alert.mp3',
                'HIGH': 'assets/sounds/high_alert.mp3',
                'MEDIUM': 'assets/sounds/alert.mp3'
            }
            
            sound_file = sound_files.get(priority, sound_files['MEDIUM'])
            
            # Check if file exists
            if os.path.exists(sound_file):
                sound = pygame.mixer.Sound(sound_file)
                sound.play()
                return True
            else:
                # Use system beep as fallback
                import sys
                if sys.platform == 'darwin':  # macOS
                    os.system('afplay /System/Library/Sounds/Glass.aiff')
                elif sys.platform == 'win32':  # Windows
                    import winsound
                    winsound.Beep(1000, 500)
                else:  # Linux
                    os.system('beep')
                return True
            
        except Exception as e:
            self.logger.error(f"Error playing alert sound: {e}")
            return False
    
    # ==================== Specific Alert Types ====================
    
    def alert_price_move(self, symbol: str, current_price: float, 
                         change_pct: float, direction: str) -> bool:
        """Alert for significant price movement"""
        emoji = "🚀" if direction == "up" else "📉"
        message = f"{emoji} {symbol} moved {direction} {abs(change_pct):.2f}% to ${current_price:.2f}"
        
        priority = 'HIGH' if abs(change_pct) >= 10 else 'MEDIUM'
        
        return self.send_alert(
            alert_type='PRICE_MOVE',
            symbol=symbol,
            message=message,
            priority=priority,
            value=current_price,
            data={'change_pct': change_pct, 'direction': direction}
        )
    
    def alert_volume_surge(self, symbol: str, volume_ratio: float) -> bool:
        """Alert for volume surge"""
        message = f"📊 {symbol} volume surge detected: {volume_ratio:.1f}x average"
        
        priority = 'HIGH' if volume_ratio >= 3.0 else 'MEDIUM'
        
        return self.send_alert(
            alert_type='VOLUME_SURGE',
            symbol=symbol,
            message=message,
            priority=priority,
            value=volume_ratio
        )
    
    def alert_rsi_level(self, symbol: str, rsi: float, condition: str) -> bool:
        """Alert for RSI overbought/oversold"""
        if condition == 'oversold':
            message = f"💹 {symbol} RSI oversold: {rsi:.1f} - Potential buy opportunity"
            priority = 'MEDIUM'
        else:
            message = f"⚠️ {symbol} RSI overbought: {rsi:.1f} - Consider taking profits"
            priority = 'MEDIUM'
        
        return self.send_alert(
            alert_type='RSI_ALERT',
            symbol=symbol,
            message=message,
            priority=priority,
            value=rsi
        )
    
    def alert_macd_crossover(self, symbol: str, crossover_type: str) -> bool:
        """Alert for MACD crossover"""
        if crossover_type == 'bullish':
            message = f"📈 {symbol} MACD bullish crossover - Momentum turning positive"
            priority = 'MEDIUM'
        else:
            message = f"📉 {symbol} MACD bearish crossover - Momentum turning negative"
            priority = 'MEDIUM'
        
        return self.send_alert(
            alert_type='MACD_CROSSOVER',
            symbol=symbol,
            message=message,
            priority=priority
        )
    
    def alert_golden_cross(self, symbol: str) -> bool:
        """Alert for golden cross (SMA 50 crosses above SMA 200)"""
        message = f"⭐ {symbol} GOLDEN CROSS - SMA 50 crossed above SMA 200! Strong bullish signal"
        
        return self.send_alert(
            alert_type='GOLDEN_CROSS',
            symbol=symbol,
            message=message,
            priority='HIGH'
        )
    
    def alert_death_cross(self, symbol: str) -> bool:
        """Alert for death cross (SMA 50 crosses below SMA 200)"""
        message = f"💀 {symbol} DEATH CROSS - SMA 50 crossed below SMA 200! Strong bearish signal"
        
        return self.send_alert(
            alert_type='DEATH_CROSS',
            symbol=symbol,
            message=message,
            priority='HIGH'
        )
    
    def alert_sentiment_shift(self, symbol: str, old_sentiment: float, 
                              new_sentiment: float) -> bool:
        """Alert for significant sentiment change"""
        change = new_sentiment - old_sentiment
        direction = "positive" if change > 0 else "negative"
        
        message = f"📰 {symbol} sentiment shifted {direction}: {old_sentiment:.2f} → {new_sentiment:.2f}"
        
        priority = 'HIGH' if abs(change) >= 0.5 else 'MEDIUM'
        
        return self.send_alert(
            alert_type='SENTIMENT_SHIFT',
            symbol=symbol,
            message=message,
            priority=priority,
            data={'old_sentiment': old_sentiment, 'new_sentiment': new_sentiment}
        )
    
    def alert_monthly_signal(self, symbol: str, score: float, recommendation: str) -> bool:
        """Alert for monthly trading signal"""
        emoji = "🟢" if "BUY" in recommendation else "🔴" if "SELL" in recommendation else "⚖️"
        
        message = f"{emoji} {symbol} Monthly Signal: {recommendation}\nScore: {score:.1f}/100"
        
        # Priority based on score extremes
        if score >= 85 or score <= 15:
            priority = 'CRITICAL'
        elif score >= 75 or score <= 25:
            priority = 'HIGH'
        else:
            priority = 'MEDIUM'
        
        return self.send_alert(
            alert_type='MONTHLY_SIGNAL',
            symbol=symbol,
            message=message,
            priority=priority,
            value=score,
            data={'recommendation': recommendation}
        )
    
    def alert_news_spike(self, symbol: str, article_count: int) -> bool:
        """Alert for news spike"""
        message = f"📰 {symbol} news spike: {article_count} articles in the last hour"
        
        priority = 'HIGH' if article_count >= 20 else 'MEDIUM'
        
        return self.send_alert(
            alert_type='NEWS_SPIKE',
            symbol=symbol,
            message=message,
            priority=priority,
            value=article_count
        )
    
    def test_alerts(self) -> Dict[str, bool]:
        """Test all alert channels"""
        results = {}
        
        # Test desktop
        if self.channels.get('desktop', True):
            results['desktop'] = self._send_desktop_notification(
                "Test Alert",
                "This is a test notification from Stock Dashboard",
                "MEDIUM"
            )
        
        # Test email
        if self.channels.get('email', False):
            results['email'] = self._send_email(
                "TEST",
                "TEST",
                "This is a test email alert",
                "MEDIUM"
            )
        
        # Test Telegram
        if self.channels.get('telegram', False):
            results['telegram'] = self._send_telegram("🧪 Test message from Stock Dashboard")
        
        # Test audio
        if self.channels.get('audio', False):
            results['audio'] = self._play_alert_sound("MEDIUM")
        
        return results
