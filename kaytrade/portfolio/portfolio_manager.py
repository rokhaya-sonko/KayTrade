"""
Portfolio management with position sizing, rebalancing, and constraints
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime


class PortfolioManager:
    """
    Manage portfolio positions, sizing, and rebalancing
    """
    
    def __init__(
        self,
        initial_capital: float = 100000.0,
        max_position_size: float = 0.2,
        min_position_size: float = 0.01,
        max_leverage: float = 1.0,
        long_only: bool = True
    ):
        """
        Initialize PortfolioManager
        
        Args:
            initial_capital: Initial capital
            max_position_size: Maximum position size as fraction of portfolio
            min_position_size: Minimum position size as fraction of portfolio
            max_leverage: Maximum leverage
            long_only: Whether to allow only long positions
        """
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.max_position_size = max_position_size
        self.min_position_size = min_position_size
        self.max_leverage = max_leverage
        self.long_only = long_only
        
        self.positions = {}  # {symbol: shares}
        self.cash = initial_capital
        self.portfolio_value = initial_capital
        self.history = []
        
    def calculate_position_size(
        self,
        signal: float,
        price: float,
        volatility: Optional[float] = None,
        method: str = 'equal_weight'
    ) -> int:
        """
        Calculate position size
        
        Args:
            signal: Trading signal (-1 to 1)
            price: Current price
            volatility: Asset volatility (optional)
            method: Position sizing method
            
        Returns:
            Number of shares to trade
        """
        if signal == 0:
            return 0
        
        portfolio_value = self.get_portfolio_value()
        
        if method == 'equal_weight':
            # Equal weight allocation
            target_value = portfolio_value * self.max_position_size * abs(signal)
            shares = int(target_value / price)
            
        elif method == 'risk_parity':
            # Risk parity allocation
            if volatility is None or volatility == 0:
                volatility = 0.2  # Default volatility
            
            # Inverse volatility weighting
            target_value = (portfolio_value * self.max_position_size * abs(signal)) / volatility
            shares = int(target_value / price)
            
        elif method == 'kelly':
            # Kelly criterion (simplified)
            # Note: In production, these should be estimated from historical performance
            win_rate = 0.55  # Conservative estimate
            win_loss_ratio = 1.5  # Conservative estimate
            kelly_fraction = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio
            kelly_fraction = max(0, min(kelly_fraction, self.max_position_size))
            
            target_value = portfolio_value * kelly_fraction * abs(signal)
            shares = int(target_value / price)
            
        else:
            raise ValueError(f"Unknown position sizing method: {method}")
        
        # Apply position size constraints
        min_value = portfolio_value * self.min_position_size
        max_value = portfolio_value * self.max_position_size
        
        target_value = shares * price
        if target_value < min_value and target_value > 0:
            shares = int(min_value / price)
        elif target_value > max_value:
            shares = int(max_value / price)
        
        # Apply direction
        if signal < 0 and not self.long_only:
            shares = -shares
        elif signal < 0 and self.long_only:
            shares = 0
        
        return shares
    
    def update_position(
        self,
        symbol: str,
        shares: int,
        price: float,
        timestamp: Optional[datetime] = None
    ):
        """
        Update position for a symbol
        
        Args:
            symbol: Stock symbol
            shares: Number of shares to add (negative to reduce)
            price: Execution price
            timestamp: Transaction timestamp
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Update position
        current_shares = self.positions.get(symbol, 0)
        new_shares = current_shares + shares
        
        # Update cash
        cost = shares * price
        self.cash -= cost
        
        # Update position
        if new_shares == 0:
            self.positions.pop(symbol, None)
        else:
            self.positions[symbol] = new_shares
        
        # Record transaction
        self.history.append({
            'timestamp': timestamp,
            'symbol': symbol,
            'shares': shares,
            'price': price,
            'cost': cost,
            'cash': self.cash,
            'portfolio_value': self.get_portfolio_value()
        })
    
    def get_position(self, symbol: str) -> int:
        """
        Get current position for a symbol
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Number of shares
        """
        return self.positions.get(symbol, 0)
    
    def get_portfolio_value(self, prices: Optional[Dict[str, float]] = None) -> float:
        """
        Get current portfolio value
        
        Args:
            prices: Current prices for all positions
            
        Returns:
            Total portfolio value
        """
        if prices is None:
            # Use last known value if prices not provided
            return self.portfolio_value
        
        position_value = sum(
            shares * prices.get(symbol, 0)
            for symbol, shares in self.positions.items()
        )
        
        self.portfolio_value = self.cash + position_value
        return self.portfolio_value
    
    def get_positions(self) -> Dict[str, int]:
        """
        Get all current positions
        
        Returns:
            Dictionary of positions
        """
        return self.positions.copy()
    
    def get_weights(self, prices: Dict[str, float]) -> Dict[str, float]:
        """
        Get portfolio weights
        
        Args:
            prices: Current prices
            
        Returns:
            Dictionary of weights
        """
        portfolio_value = self.get_portfolio_value(prices)
        
        weights = {}
        for symbol, shares in self.positions.items():
            position_value = shares * prices.get(symbol, 0)
            weights[symbol] = position_value / portfolio_value if portfolio_value > 0 else 0
        
        return weights
    
    def rebalance(
        self,
        target_weights: Dict[str, float],
        prices: Dict[str, float],
        timestamp: Optional[datetime] = None
    ):
        """
        Rebalance portfolio to target weights
        
        Args:
            target_weights: Target weights for each symbol
            prices: Current prices
            timestamp: Rebalancing timestamp
        """
        portfolio_value = self.get_portfolio_value(prices)
        current_weights = self.get_weights(prices)
        
        for symbol, target_weight in target_weights.items():
            current_weight = current_weights.get(symbol, 0)
            weight_diff = target_weight - current_weight
            
            if abs(weight_diff) > 0.01:  # Only rebalance if difference > 1%
                target_value = portfolio_value * target_weight
                current_shares = self.get_position(symbol)
                current_value = current_shares * prices.get(symbol, 0)
                
                value_diff = target_value - current_value
                shares_to_trade = int(value_diff / prices.get(symbol, 1))
                
                if shares_to_trade != 0:
                    self.update_position(symbol, shares_to_trade, prices[symbol], timestamp)
    
    def check_constraints(self, prices: Dict[str, float]) -> bool:
        """
        Check if portfolio satisfies constraints
        
        Args:
            prices: Current prices
            
        Returns:
            True if constraints are satisfied
        """
        weights = self.get_weights(prices)
        
        # Check position size constraints
        for weight in weights.values():
            if weight > self.max_position_size:
                return False
        
        # Check leverage constraint
        total_weight = sum(abs(w) for w in weights.values())
        if total_weight > self.max_leverage:
            return False
        
        # Check long-only constraint
        if self.long_only:
            if any(shares < 0 for shares in self.positions.values()):
                return False
        
        return True
    
    def get_history(self) -> pd.DataFrame:
        """
        Get transaction history
        
        Returns:
            DataFrame with transaction history
        """
        return pd.DataFrame(self.history)
    
    def reset(self):
        """Reset portfolio to initial state"""
        self.current_capital = self.initial_capital
        self.positions = {}
        self.cash = self.initial_capital
        self.portfolio_value = self.initial_capital
        self.history = []
