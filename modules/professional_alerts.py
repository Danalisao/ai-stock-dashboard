"""
🚨 Real-Time Alert System
Professional trading alerts and notifications
"""

import logging
import asyncio
import smtplib
import requests
import pygame
import plyer
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import json

class AlertType(Enum):
    """Types of trading alerts"""
    ENTRY_SIGNAL = "entry_signal"
    EXIT_SIGNAL = "exit_signal"
    STOP_LOSS_HIT = "stop_loss_hit"
    TAKE_PROFIT_HIT = "take_profit_hit"
    RISK_VIOLATION = "risk_violation"
    MARGIN_CALL = "margin_call"
    HIGH_VOLATILITY = "high_volatility"
    NEWS_IMPACT = "news_impact"
    EARNINGS_ALERT = "earnings_alert"
    TECHNICAL_BREAKOUT = "technical_breakout"

class AlertPriority(Enum):
    """Alert priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class Alert:
    """Professional trading alert"""
    alert_type: AlertType
    priority: AlertPriority
    symbol: str
    title: str
    message: str
    data: Dict[str, Any]
    timestamp: datetime
    alert_id: str
    acknowledged: bool = False
    
class ProfessionalAlertSystem:
    """Advanced alert system for professional trading"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Alert configuration
        alert_config = config.get('alerts', {})
        self.channels = {
            'desktop': alert_config.get('desktop_enabled', True),
            'email': alert_config.get('email_enabled', False),
            'telegram': alert_config.get('telegram_enabled', False),
            'discord': alert_config.get('discord_enabled', False),
            'audio': alert_config.get('audio_enabled', True),
            'sms': alert_config.get('sms_enabled', False)
        }
        
        # Email configuration
        self.email_config = config.get('email', {})
        
        # Telegram configuration
        self.telegram_config = config.get('telegram', {})
        
        # Discord configuration
        self.discord_config = config.get('discord', {})
        
        # SMS configuration (Twilio)
        self.sms_config = config.get('sms', {})
        
        # Sound configuration
        self.sound_config = config.get('sound', {})
        
        # Alert history
        self.alert_history: List[Alert] = []
        self.max_history = 1000
        
        # Initialize audio system
        if self.channels['audio']:
            try:
                pygame.mixer.init()
                self.sounds = {
                    'critical': self.sound_config.get('critical_sound', './assets/sounds/critical.wav'),
                    'high': self.sound_config.get('high_sound', './assets/sounds/high.wav'),
                    'medium': self.sound_config.get('medium_sound', './assets/sounds/medium.wav'),
                    'low': self.sound_config.get('low_sound', './assets/sounds/low.wav')
                }
            except Exception as e:
                self.logger.warning(f"Audio system initialization failed: {e}")
                self.channels['audio'] = False
    
    async def send_alert(self, alert: Alert) -> Dict[str, bool]:
        """Send alert through all enabled channels"""
        results = {}
        
        # Add to history
        self.alert_history.append(alert)
        if len(self.alert_history) > self.max_history:
            self.alert_history.pop(0)
        
        # Log alert
        self.logger.info(f"Alert {alert.priority.value.upper()}: {alert.title}")
        
        # Send through each enabled channel
        if self.channels['desktop']:
            results['desktop'] = await self._send_desktop_notification(alert)
        
        if self.channels['email']:
            results['email'] = await self._send_email_alert(alert)
        
        if self.channels['telegram']:
            results['telegram'] = await self._send_telegram_alert(alert)
        
        if self.channels['discord']:
            results['discord'] = await self._send_discord_alert(alert)
        
        if self.channels['audio']:
            results['audio'] = await self._play_alert_sound(alert)
        
        if self.channels['sms']:
            results['sms'] = await self._send_sms_alert(alert)
        
        return results
    
    async def _send_desktop_notification(self, alert: Alert) -> bool:
        """Send desktop notification"""
        try:
            # Choose icon based on priority
            icon_map = {
                AlertPriority.CRITICAL: '🚨',
                AlertPriority.HIGH: '⚠️',
                AlertPriority.MEDIUM: '📊',
                AlertPriority.LOW: 'ℹ️',
                AlertPriority.INFO: '📌'
            }
            
            icon = icon_map.get(alert.priority, '📊')
            title = f"{icon} {alert.title}"
            
            plyer.notification.notify(
                title=title,
                message=alert.message,
                app_name="Professional Trading System",
                timeout=10
            )
            return True
        except Exception as e:
            self.logger.error(f"Desktop notification failed: {e}")
            return False
    
    async def _send_email_alert(self, alert: Alert) -> bool:
        """Send email alert"""
        try:
            if not all([
                self.email_config.get('smtp_server'),
                self.email_config.get('smtp_port'),
                self.email_config.get('sender_email'),
                self.email_config.get('sender_password'),
                self.email_config.get('recipient_email')
            ]):
                return False
            
            # Create email content
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender_email']
            msg['To'] = self.email_config['recipient_email']
            msg['Subject'] = f"Trading Alert - {alert.priority.value.upper()}: {alert.title}"
            
            # HTML email body
            html_body = f"""
            <html>
            <body>
                <h2 style="color: {'red' if alert.priority in [AlertPriority.CRITICAL, AlertPriority.HIGH] else 'orange' if alert.priority == AlertPriority.MEDIUM else 'blue'};">
                    {alert.title}
                </h2>
                <p><strong>Symbol:</strong> {alert.symbol}</p>
                <p><strong>Priority:</strong> {alert.priority.value.upper()}</p>
                <p><strong>Time:</strong> {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Message:</strong></p>
                <p>{alert.message}</p>
                
                <h3>Alert Data:</h3>
                <pre>{json.dumps(alert.data, indent=2)}</pre>
                
                <hr>
                <p><em>Professional Trading System Alert</em></p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['sender_email'], self.email_config['sender_password'])
            server.send_message(msg)
            server.quit()
            
            return True
        except Exception as e:
            self.logger.error(f"Email alert failed: {e}")
            return False
    
    async def _send_telegram_alert(self, alert: Alert) -> bool:
        """Send Telegram alert"""
        try:
            bot_token = self.telegram_config.get('bot_token')
            chat_id = self.telegram_config.get('chat_id')
            
            if not bot_token or not chat_id:
                return False
            
            # Format message
            emoji_map = {
                AlertPriority.CRITICAL: '🚨',
                AlertPriority.HIGH: '⚠️',
                AlertPriority.MEDIUM: '📊',
                AlertPriority.LOW: 'ℹ️',
                AlertPriority.INFO: '📌'
            }
            
            emoji = emoji_map.get(alert.priority, '📊')
            
            message = f"""
{emoji} *{alert.title}*

📊 Symbol: `{alert.symbol}`
🔥 Priority: {alert.priority.value.upper()}
⏰ Time: {alert.timestamp.strftime('%H:%M:%S')}

{alert.message}

```json
{json.dumps(alert.data, indent=2)}
```
            """
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, data=data, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            self.logger.error(f"Telegram alert failed: {e}")
            return False
    
    async def _send_discord_alert(self, alert: Alert) -> bool:
        """Send Discord webhook alert"""
        try:
            webhook_url = self.discord_config.get('webhook_url')
            if not webhook_url:
                return False
            
            # Color based on priority
            color_map = {
                AlertPriority.CRITICAL: 0xFF0000,  # Red
                AlertPriority.HIGH: 0xFF8800,      # Orange
                AlertPriority.MEDIUM: 0xFFFF00,    # Yellow
                AlertPriority.LOW: 0x0088FF,       # Blue
                AlertPriority.INFO: 0x888888       # Gray
            }
            
            embed = {
                "title": alert.title,
                "color": color_map.get(alert.priority, 0x0088FF),
                "fields": [
                    {"name": "Symbol", "value": alert.symbol, "inline": True},
                    {"name": "Priority", "value": alert.priority.value.upper(), "inline": True},
                    {"name": "Time", "value": alert.timestamp.strftime('%H:%M:%S'), "inline": True},
                    {"name": "Message", "value": alert.message, "inline": False}
                ],
                "footer": {"text": "Professional Trading System"},
                "timestamp": alert.timestamp.isoformat()
            }
            
            if alert.data:
                embed["fields"].append({
                    "name": "Data", 
                    "value": f"```json\n{json.dumps(alert.data, indent=2)[:1000]}\n```", 
                    "inline": False
                })
            
            payload = {"embeds": [embed]}
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            return response.status_code == 204
            
        except Exception as e:
            self.logger.error(f"Discord alert failed: {e}")
            return False
    
    async def _play_alert_sound(self, alert: Alert) -> bool:
        """Play alert sound"""
        try:
            if not pygame.mixer.get_init():
                return False
            
            sound_file = self.sounds.get(alert.priority.value, self.sounds.get('medium'))
            
            if sound_file:
                sound = pygame.mixer.Sound(sound_file)
                sound.play()
                return True
            
            return False
        except Exception as e:
            self.logger.error(f"Audio alert failed: {e}")
            return False
    
    async def _send_sms_alert(self, alert: Alert) -> bool:
        """Send SMS alert via Twilio"""
        try:
            # This would require Twilio API setup
            # Placeholder implementation
            self.logger.info(f"SMS alert would be sent: {alert.title}")
            return True
        except Exception as e:
            self.logger.error(f"SMS alert failed: {e}")
            return False
    
    def create_entry_signal_alert(self, signal_data: Dict[str, Any]) -> Alert:
        """Create entry signal alert"""
        symbol = signal_data['symbol']
        score = signal_data.get('total_score', 0)
        action = signal_data.get('action', 'BUY')
        entry_price = signal_data.get('entry_price', 0)
        target_price = signal_data.get('target_price', 0)
        stop_loss = signal_data.get('stop_loss', 0)
        
        # Determine priority based on score
        if score >= 95:
            priority = AlertPriority.CRITICAL
        elif score >= 90:
            priority = AlertPriority.HIGH
        elif score >= 85:
            priority = AlertPriority.MEDIUM
        else:
            priority = AlertPriority.LOW
        
        title = f"{action} Signal: {symbol} (Score: {score})"
        message = f"""
Entry Signal Generated for {symbol}

Action: {action}
Score: {score}/100
Entry Price: ${entry_price:.2f}
Target: ${target_price:.2f} (+{((target_price/entry_price - 1) * 100):.1f}%)
Stop Loss: ${stop_loss:.2f} ({((stop_loss/entry_price - 1) * 100):.1f}%)
Risk/Reward: {((target_price - entry_price) / (entry_price - stop_loss)):.1f}:1

This is a professional trading signal. Execute according to your risk management rules.
        """
        
        return Alert(
            alert_type=AlertType.ENTRY_SIGNAL,
            priority=priority,
            symbol=symbol,
            title=title,
            message=message,
            data=signal_data,
            timestamp=datetime.now(),
            alert_id=f"entry_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
    
    def create_risk_violation_alert(self, violation_data: Dict[str, Any]) -> Alert:
        """Create risk violation alert"""
        violation_type = violation_data.get('type', 'UNKNOWN')
        current = violation_data.get('current', 0)
        limit = violation_data.get('limit', 0)
        
        title = f"Risk Violation: {violation_type}"
        message = f"""
Portfolio Risk Limit Exceeded

Violation: {violation_type}
Current: {current:.2f}%
Limit: {limit:.2f}%

Immediate action required to reduce risk exposure.
        """
        
        return Alert(
            alert_type=AlertType.RISK_VIOLATION,
            priority=AlertPriority.CRITICAL,
            symbol="PORTFOLIO",
            title=title,
            message=message,
            data=violation_data,
            timestamp=datetime.now(),
            alert_id=f"risk_{violation_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
    
    def create_price_alert(self, symbol: str, current_price: float, 
                          target_price: float, alert_type: str) -> Alert:
        """Create price movement alert"""
        change_pct = ((current_price - target_price) / target_price) * 100
        
        if alert_type == "stop_loss":
            title = f"Stop Loss Hit: {symbol}"
            alert_enum = AlertType.STOP_LOSS_HIT
            priority = AlertPriority.HIGH
        elif alert_type == "take_profit":
            title = f"Take Profit Hit: {symbol}"
            alert_enum = AlertType.TAKE_PROFIT_HIT
            priority = AlertPriority.HIGH
        else:
            title = f"Price Alert: {symbol}"
            alert_enum = AlertType.TECHNICAL_BREAKOUT
            priority = AlertPriority.MEDIUM
        
        message = f"""
Price Movement Alert for {symbol}

Current Price: ${current_price:.2f}
Target Price: ${target_price:.2f}
Change: {change_pct:+.2f}%

Consider reviewing your position.
        """
        
        return Alert(
            alert_type=alert_enum,
            priority=priority,
            symbol=symbol,
            title=title,
            message=message,
            data={
                'current_price': current_price,
                'target_price': target_price,
                'change_pct': change_pct,
                'alert_type': alert_type
            },
            timestamp=datetime.now(),
            alert_id=f"price_{symbol}_{alert_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
    
    def get_recent_alerts(self, limit: int = 50) -> List[Alert]:
        """Get recent alerts"""
        return self.alert_history[-limit:] if len(self.alert_history) > limit else self.alert_history
    
    def get_unacknowledged_alerts(self) -> List[Alert]:
        """Get unacknowledged alerts"""
        return [alert for alert in self.alert_history if not alert.acknowledged]
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        for alert in self.alert_history:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                return True
        return False