"""
Paper trading broker for simulated trading
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
from abc import ABC, abstractmethod


class BrokerAdapter(ABC):
    """Base class for broker adapters"""
    
    @abstractmethod
    def get_account_info(self) -> Dict:
        """Get account information"""
        pass
    
    @abstractmethod
    def get_positions(self) -> Dict:
        """Get current positions"""
        pass
    
    @abstractmethod
    def place_order(self, symbol: str, quantity: int, order_type: str) -> Dict:
        """Place an order"""
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        pass
    
    @abstractmethod
    def get_quote(self, symbol: str) -> Dict:
        """Get current quote for a symbol"""
        pass


class PaperBroker(BrokerAdapter):
    """
    Paper trading broker for testing strategies without real money
    """
    
    def __init__(
        self,
        initial_capital: float = 100000.0,
        commission: float = 0.001,
        slippage: float = 0.0005
    ):
        """
        Initialize paper broker
        
        Args:
            initial_capital: Initial capital
            commission: Commission rate
            slippage: Slippage rate
        """
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.commission = commission
        self.slippage = slippage
        
        self.positions = {}  # {symbol: quantity}
        self.orders = {}  # {order_id: order_dict}
        self.order_history = []
        self.next_order_id = 1
        
    def get_account_info(self) -> Dict:
        """Get account information"""
        return {
            'cash': self.cash,
            'buying_power': self.cash,
            'portfolio_value': self._calculate_portfolio_value(),
            'initial_capital': self.initial_capital,
            'profit_loss': self._calculate_portfolio_value() - self.initial_capital
        }
    
    def get_positions(self) -> Dict:
        """Get current positions"""
        return self.positions.copy()
    
    def place_order(
        self,
        symbol: str,
        quantity: int,
        order_type: str = 'market',
        price: Optional[float] = None
    ) -> Dict:
        """
        Place an order
        
        Args:
            symbol: Stock symbol
            quantity: Number of shares (positive for buy, negative for sell)
            order_type: Order type ('market', 'limit')
            price: Limit price (for limit orders)
            
        Returns:
            Order confirmation
        """
        order_id = str(self.next_order_id)
        self.next_order_id += 1
        
        order = {
            'order_id': order_id,
            'symbol': symbol,
            'quantity': quantity,
            'order_type': order_type,
            'price': price,
            'status': 'pending',
            'timestamp': datetime.now()
        }
        
        self.orders[order_id] = order
        
        # Simulate immediate execution for market orders
        if order_type == 'market':
            self._execute_order(order_id)
        
        return order
    
    def _execute_order(self, order_id: str):
        """
        Execute an order
        
        Args:
            order_id: Order ID
        """
        order = self.orders.get(order_id)
        if not order:
            return
        
        symbol = order['symbol']
        quantity = order['quantity']
        
        # Get current price (in real implementation, fetch from data source)
        # For now, use a placeholder
        current_price = order.get('price', 100.0)
        
        # Apply slippage
        if quantity > 0:  # Buy
            execution_price = current_price * (1 + self.slippage)
        else:  # Sell
            execution_price = current_price * (1 - self.slippage)
        
        # Calculate cost
        cost = abs(quantity) * execution_price
        commission_cost = cost * self.commission
        total_cost = cost + commission_cost
        
        # Check if we have enough cash for buy orders
        if quantity > 0 and total_cost > self.cash:
            order['status'] = 'rejected'
            order['reason'] = 'Insufficient funds'
            return
        
        # Check if we have enough shares for sell orders
        current_position = self.positions.get(symbol, 0)
        if quantity < 0 and abs(quantity) > current_position:
            order['status'] = 'rejected'
            order['reason'] = 'Insufficient shares'
            return
        
        # Update position
        new_position = current_position + quantity
        if new_position == 0:
            self.positions.pop(symbol, None)
        else:
            self.positions[symbol] = new_position
        
        # Update cash
        if quantity > 0:  # Buy
            self.cash -= total_cost
        else:  # Sell
            self.cash += (cost - commission_cost)
        
        # Update order status
        order['status'] = 'filled'
        order['execution_price'] = execution_price
        order['commission'] = commission_cost
        order['total_cost'] = total_cost
        order['execution_time'] = datetime.now()
        
        # Add to history
        self.order_history.append(order.copy())
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order
        
        Args:
            order_id: Order ID
            
        Returns:
            True if cancelled successfully
        """
        order = self.orders.get(order_id)
        if not order:
            return False
        
        if order['status'] == 'pending':
            order['status'] = 'cancelled'
            return True
        
        return False
    
    def get_quote(self, symbol: str, data_source=None) -> Dict:
        """
        Get current quote for a symbol
        
        Args:
            symbol: Stock symbol
            data_source: Optional data source (e.g., yfinance)
            
        Returns:
            Quote information
        """
        # In a real implementation, fetch from data source
        # For now, return placeholder
        return {
            'symbol': symbol,
            'bid': 100.0,
            'ask': 100.1,
            'last': 100.05,
            'volume': 1000000,
            'timestamp': datetime.now()
        }
    
    def get_order(self, order_id: str) -> Optional[Dict]:
        """
        Get order information
        
        Args:
            order_id: Order ID
            
        Returns:
            Order information
        """
        return self.orders.get(order_id)
    
    def get_order_history(self) -> List[Dict]:
        """
        Get order history
        
        Returns:
            List of executed orders
        """
        return self.order_history.copy()
    
    def _calculate_portfolio_value(self, prices: Optional[Dict[str, float]] = None) -> float:
        """
        Calculate portfolio value
        
        Args:
            prices: Current prices for positions
            
        Returns:
            Total portfolio value
        """
        if prices is None:
            # Use placeholder prices
            prices = {symbol: 100.0 for symbol in self.positions.keys()}
        
        position_value = sum(
            quantity * prices.get(symbol, 0)
            for symbol, quantity in self.positions.items()
        )
        
        return self.cash + position_value
    
    def reset(self):
        """Reset broker to initial state"""
        self.cash = self.initial_capital
        self.positions = {}
        self.orders = {}
        self.order_history = []
        self.next_order_id = 1


class AlpacaPaperBroker(BrokerAdapter):
    """
    Alpaca paper trading broker adapter
    Note: Requires alpaca-trade-api package and API credentials
    """
    
    def __init__(self, api_key: str = "", secret_key: str = "", base_url: str = ""):
        """
        Initialize Alpaca paper broker
        
        Args:
            api_key: Alpaca API key
            secret_key: Alpaca secret key
            base_url: Alpaca base URL (paper trading URL)
        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = base_url
        
        # Note: In a real implementation, initialize Alpaca API client
        # try:
        #     import alpaca_trade_api as tradeapi
        #     self.api = tradeapi.REST(api_key, secret_key, base_url)
        # except ImportError:
        #     raise ImportError("alpaca-trade-api package is required")
    
    def get_account_info(self) -> Dict:
        """Get account information from Alpaca"""
        # Implementation would call Alpaca API
        # account = self.api.get_account()
        # return account._raw
        return {}
    
    def get_positions(self) -> Dict:
        """Get current positions from Alpaca"""
        # Implementation would call Alpaca API
        # positions = self.api.list_positions()
        # return {p.symbol: int(p.qty) for p in positions}
        return {}
    
    def place_order(self, symbol: str, quantity: int, order_type: str = 'market') -> Dict:
        """Place an order with Alpaca"""
        # Implementation would call Alpaca API
        # side = 'buy' if quantity > 0 else 'sell'
        # order = self.api.submit_order(
        #     symbol=symbol,
        #     qty=abs(quantity),
        #     side=side,
        #     type=order_type,
        #     time_in_force='gtc'
        # )
        # return order._raw
        return {}
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order with Alpaca"""
        # Implementation would call Alpaca API
        # try:
        #     self.api.cancel_order(order_id)
        #     return True
        # except:
        #     return False
        return False
    
    def get_quote(self, symbol: str) -> Dict:
        """Get current quote from Alpaca"""
        # Implementation would call Alpaca API
        # quote = self.api.get_latest_quote(symbol)
        # return quote._raw
        return {}
