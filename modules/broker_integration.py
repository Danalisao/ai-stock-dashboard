"""
🏦 Broker Integration Module
Professional API integration for real trading execution
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import requests
import json

class OrderType(Enum):
    """Order types for professional trading"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    TRAILING_STOP = "trailing_stop"

class OrderSide(Enum):
    """Order sides"""
    BUY = "buy"
    SELL = "sell"

class OrderStatus(Enum):
    """Order status"""
    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

@dataclass
class Order:
    """Professional order representation"""
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: int
    price: Optional[float] = None
    stop_price: Optional[float] = None
    time_in_force: str = "DAY"
    order_id: Optional[str] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: int = 0
    average_fill_price: Optional[float] = None
    commission: float = 0.0
    created_at: Optional[datetime] = None
    filled_at: Optional[datetime] = None

class BrokerAPI:
    """Abstract base class for broker integrations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.base_url = config.get('base_url', '')
        self.api_key = config.get('api_key', '')
        self.secret = config.get('secret', '')
        self.paper_trading = config.get('paper_trading', True)
        
    async def place_order(self, order: Order) -> Dict[str, Any]:
        """Place an order"""
        raise NotImplementedError
        
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        raise NotImplementedError
        
    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get order status"""
        raise NotImplementedError
        
    async def get_positions(self) -> List[Dict[str, Any]]:
        """Get current positions"""
        raise NotImplementedError
        
    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        raise NotImplementedError

class AlpacaBroker(BrokerAPI):
    """Alpaca API integration for professional trading"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        if self.paper_trading:
            self.base_url = "https://paper-api.alpaca.markets"
        else:
            self.base_url = "https://api.alpaca.markets"
            
        self.headers = {
            'APCA-API-KEY-ID': self.api_key,
            'APCA-API-SECRET-KEY': self.secret,
            'Content-Type': 'application/json'
        }
        
    async def place_order(self, order: Order) -> Dict[str, Any]:
        """Place order with Alpaca"""
        url = f"{self.base_url}/v2/orders"
        
        payload = {
            'symbol': order.symbol,
            'side': order.side.value,
            'type': order.order_type.value,
            'qty': order.quantity,
            'time_in_force': order.time_in_force
        }
        
        if order.price:
            payload['limit_price'] = order.price
        if order.stop_price:
            payload['stop_price'] = order.stop_price
            
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            order.order_id = result.get('id')
            order.created_at = datetime.now()
            
            self.logger.info(f"Order placed: {order.symbol} {order.side.value} {order.quantity}")
            return {'success': True, 'order_id': order.order_id, 'data': result}
            
        except Exception as e:
            self.logger.error(f"Failed to place order: {e}")
            return {'success': False, 'error': str(e)}
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel order"""
        url = f"{self.base_url}/v2/orders/{order_id}"
        
        try:
            response = requests.delete(url, headers=self.headers)
            response.raise_for_status()
            self.logger.info(f"Order cancelled: {order_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to cancel order {order_id}: {e}")
            return False
    
    async def get_positions(self) -> List[Dict[str, Any]]:
        """Get current positions"""
        url = f"{self.base_url}/v2/positions"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to get positions: {e}")
            return []
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        url = f"{self.base_url}/v2/account"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to get account info: {e}")
            return {}

class IBKRBroker(BrokerAPI):
    """Interactive Brokers integration (placeholder for institutional trading)"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # IBKR requires TWS API or IB Gateway
        self.logger.warning("IBKR integration requires TWS/Gateway setup")
    
    async def place_order(self, order: Order) -> Dict[str, Any]:
        """Place order with IBKR (requires TWS API setup)"""
        # This would integrate with the IBKR TWS API
        self.logger.info("IBKR order placement - implement TWS API integration")
        return {'success': False, 'error': 'TWS API integration required'}

class TradingExecutor:
    """Professional trading execution engine"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize broker based on config
        broker_type = config.get('broker', {}).get('type', 'alpaca')
        broker_config = config.get('broker', {})
        
        if broker_type == 'alpaca':
            self.broker = AlpacaBroker(broker_config)
        elif broker_type == 'ibkr':
            self.broker = IBKRBroker(broker_config)
        else:
            raise ValueError(f"Unsupported broker: {broker_type}")
        
        # Risk management parameters
        self.max_position_size = config.get('risk', {}).get('max_position_size_pct', 5) / 100
        self.max_daily_loss = config.get('risk', {}).get('max_daily_loss_pct', 3) / 100
        self.max_portfolio_risk = config.get('risk', {}).get('max_portfolio_risk_pct', 10) / 100
        
    async def execute_signal(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute trading signal with professional risk management
        
        Args:
            signal: Trading signal from monthly signals
            
        Returns:
            Execution result
        """
        symbol = signal['symbol']
        action = signal['action']
        entry_price = signal.get('entry_price')
        stop_loss = signal.get('stop_loss')
        take_profit = signal.get('target_price')
        conviction = signal.get('conviction', 'MEDIUM')
        
        # Get account info for position sizing
        account = await self.broker.get_account_info()
        if not account:
            return {'success': False, 'error': 'Cannot get account info'}
        
        portfolio_value = float(account.get('portfolio_value', 0))
        buying_power = float(account.get('buying_power', 0))
        
        # Calculate position size based on risk
        risk_amount = portfolio_value * self.max_position_size
        if stop_loss and entry_price:
            risk_per_share = abs(entry_price - stop_loss)
            max_shares = int(risk_amount / risk_per_share)
        else:
            # Use percentage of portfolio if no stop loss
            max_shares = int((portfolio_value * self.max_position_size) / entry_price)
        
        # Adjust based on conviction level
        conviction_multiplier = {
            'LOW': 0.5,
            'MEDIUM': 1.0,
            'HIGH': 1.5,
            'VERY_HIGH': 2.0
        }.get(conviction, 1.0)
        
        shares = int(max_shares * conviction_multiplier)
        shares = max(1, min(shares, max_shares))  # At least 1 share
        
        # Create orders
        orders = []
        
        if action in ['BUY', 'STRONG_BUY']:
            # Main entry order
            entry_order = Order(
                symbol=symbol,
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
                quantity=shares,
                price=entry_price,
                time_in_force="DAY"
            )
            
            result = await self.broker.place_order(entry_order)
            if result['success']:
                orders.append(entry_order)
                
                # Place protective stop loss
                if stop_loss:
                    stop_order = Order(
                        symbol=symbol,
                        side=OrderSide.SELL,
                        order_type=OrderType.STOP,
                        quantity=shares,
                        stop_price=stop_loss,
                        time_in_force="GTC"
                    )
                    await self.broker.place_order(stop_order)
                    orders.append(stop_order)
                
                # Place take profit order
                if take_profit:
                    profit_order = Order(
                        symbol=symbol,
                        side=OrderSide.SELL,
                        order_type=OrderType.LIMIT,
                        quantity=shares // 2,  # Take profit on half position
                        price=take_profit,
                        time_in_force="GTC"
                    )
                    await self.broker.place_order(profit_order)
                    orders.append(profit_order)
        
        elif action in ['SELL', 'STRONG_SELL']:
            # Check if we have position to sell
            positions = await self.broker.get_positions()
            current_position = next((p for p in positions if p['symbol'] == symbol), None)
            
            if current_position:
                position_qty = int(current_position['qty'])
                if position_qty > 0:
                    sell_order = Order(
                        symbol=symbol,
                        side=OrderSide.SELL,
                        order_type=OrderType.MARKET,
                        quantity=position_qty
                    )
                    result = await self.broker.place_order(sell_order)
                    if result['success']:
                        orders.append(sell_order)
        
        return {
            'success': len(orders) > 0,
            'orders': orders,
            'position_size': shares,
            'risk_amount': risk_amount,
            'conviction': conviction
        }
    
    async def get_portfolio_status(self) -> Dict[str, Any]:
        """Get comprehensive portfolio status"""
        account = await self.broker.get_account_info()
        positions = await self.broker.get_positions()
        
        if not account:
            return {'error': 'Cannot retrieve account information'}
        
        # Calculate portfolio metrics
        portfolio_value = float(account.get('portfolio_value', 0))
        cash = float(account.get('cash', 0))
        day_pl = float(account.get('unrealized_pl', 0))
        total_pl = float(account.get('total_pl', 0))
        
        # Position analysis
        long_value = sum(float(p.get('market_value', 0)) for p in positions if float(p.get('qty', 0)) > 0)
        short_value = sum(abs(float(p.get('market_value', 0))) for p in positions if float(p.get('qty', 0)) < 0)
        
        return {
            'account': {
                'portfolio_value': portfolio_value,
                'cash': cash,
                'buying_power': float(account.get('buying_power', 0)),
                'day_pl': day_pl,
                'day_pl_pct': (day_pl / portfolio_value * 100) if portfolio_value > 0 else 0,
                'total_pl': total_pl,
                'total_pl_pct': (total_pl / portfolio_value * 100) if portfolio_value > 0 else 0
            },
            'positions': {
                'total_positions': len(positions),
                'long_value': long_value,
                'short_value': short_value,
                'net_value': long_value - short_value,
                'exposure': (long_value + short_value) / portfolio_value if portfolio_value > 0 else 0
            },
            'risk': {
                'available_risk': max(0, (self.max_portfolio_risk * portfolio_value) - abs(day_pl)),
                'daily_risk_used': abs(day_pl) / (self.max_daily_loss * portfolio_value) if portfolio_value > 0 else 0,
                'portfolio_risk_used': abs(day_pl) / (self.max_portfolio_risk * portfolio_value) if portfolio_value > 0 else 0
            },
            'detailed_positions': positions
        }