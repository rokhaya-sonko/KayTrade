"""
Main signal generator class
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from abc import ABC, abstractmethod


class BaseStrategy(ABC):
    """Base class for trading strategies"""
    
    def __init__(self, name: str):
        """
        Initialize strategy
        
        Args:
            name: Strategy name
        """
        self.name = name
        
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals
        
        Args:
            data: DataFrame with market data
            
        Returns:
            Series with signals (1: buy, -1: sell, 0: hold)
        """
        pass


class SignalGenerator:
    """
    Generate trading signals using multiple strategies
    """
    
    def __init__(self):
        """Initialize SignalGenerator"""
        self.strategies = {}
        
    def add_strategy(self, strategy: BaseStrategy):
        """
        Add a strategy to the generator
        
        Args:
            strategy: Strategy instance
        """
        self.strategies[strategy.name] = strategy
        
    def generate_signals(
        self,
        data: pd.DataFrame,
        strategy_names: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Generate signals from all or selected strategies
        
        Args:
            data: DataFrame with market data
            strategy_names: List of strategy names to use (None = all)
            
        Returns:
            DataFrame with signals from each strategy
        """
        if strategy_names is None:
            strategy_names = list(self.strategies.keys())
        
        signals = pd.DataFrame(index=data.index)
        
        for name in strategy_names:
            if name in self.strategies:
                strategy = self.strategies[name]
                signals[name] = strategy.generate_signals(data)
        
        return signals
    
    def aggregate_signals(
        self,
        signals: pd.DataFrame,
        method: str = 'majority'
    ) -> pd.Series:
        """
        Aggregate signals from multiple strategies
        
        Args:
            signals: DataFrame with signals from multiple strategies
            method: Aggregation method ('majority', 'average', 'unanimous')
            
        Returns:
            Series with aggregated signals
        """
        if method == 'majority':
            # Majority vote
            return signals.mode(axis=1)[0]
        elif method == 'average':
            # Average of signals
            return signals.mean(axis=1).apply(
                lambda x: 1 if x > 0.33 else (-1 if x < -0.33 else 0)
            )
        elif method == 'unanimous':
            # All strategies must agree
            def unanimous(row):
                if all(row == 1):
                    return 1
                elif all(row == -1):
                    return -1
                else:
                    return 0
            return signals.apply(unanimous, axis=1)
        else:
            raise ValueError(f"Unknown aggregation method: {method}")
    
    def get_strategy(self, name: str) -> Optional[BaseStrategy]:
        """
        Get a strategy by name
        
        Args:
            name: Strategy name
            
        Returns:
            Strategy instance or None
        """
        return self.strategies.get(name)
    
    def list_strategies(self) -> List[str]:
        """
        List all registered strategies
        
        Returns:
            List of strategy names
        """
        return list(self.strategies.keys())
