"""
Rule-based trading strategies
"""

import pandas as pd
import numpy as np
from kaytrade.signals.signal_generator import BaseStrategy


class MovingAverageCrossover(BaseStrategy):
    """
    Moving Average Crossover Strategy
    """
    
    def __init__(self, fast_period: int = 50, slow_period: int = 200):
        """
        Initialize strategy
        
        Args:
            fast_period: Fast MA period
            slow_period: Slow MA period
        """
        super().__init__("MA_Crossover")
        self.fast_period = fast_period
        self.slow_period = slow_period
        
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate signals based on MA crossover"""
        fast_ma = data['Close'].rolling(window=self.fast_period).mean()
        slow_ma = data['Close'].rolling(window=self.slow_period).mean()
        
        signals = pd.Series(0, index=data.index)
        signals[fast_ma > slow_ma] = 1
        signals[fast_ma < slow_ma] = -1
        
        return signals


class RSIDivergence(BaseStrategy):
    """
    RSI Divergence Strategy
    """
    
    def __init__(self, period: int = 14, oversold: int = 30, overbought: int = 70):
        """
        Initialize strategy
        
        Args:
            period: RSI period
            oversold: Oversold threshold
            overbought: Overbought threshold
        """
        super().__init__("RSI_Divergence")
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
        
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate signals based on RSI"""
        # Calculate RSI
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        signals = pd.Series(0, index=data.index)
        signals[rsi < self.oversold] = 1  # Buy when oversold
        signals[rsi > self.overbought] = -1  # Sell when overbought
        
        return signals


class BollingerBands(BaseStrategy):
    """
    Bollinger Bands Strategy
    """
    
    def __init__(self, period: int = 20, std_dev: float = 2.0):
        """
        Initialize strategy
        
        Args:
            period: MA period
            std_dev: Number of standard deviations
        """
        super().__init__("Bollinger_Bands")
        self.period = period
        self.std_dev = std_dev
        
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate signals based on Bollinger Bands"""
        sma = data['Close'].rolling(window=self.period).mean()
        std = data['Close'].rolling(window=self.period).std()
        
        upper_band = sma + (std * self.std_dev)
        lower_band = sma - (std * self.std_dev)
        
        signals = pd.Series(0, index=data.index)
        signals[data['Close'] < lower_band] = 1  # Buy when price below lower band
        signals[data['Close'] > upper_band] = -1  # Sell when price above upper band
        
        return signals


class MomentumStrategy(BaseStrategy):
    """
    Momentum Strategy
    """
    
    def __init__(self, lookback: int = 20, threshold: float = 0.02):
        """
        Initialize strategy
        
        Args:
            lookback: Lookback period
            threshold: Momentum threshold
        """
        super().__init__("Momentum")
        self.lookback = lookback
        self.threshold = threshold
        
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate signals based on momentum"""
        momentum = data['Close'].pct_change(self.lookback)
        
        signals = pd.Series(0, index=data.index)
        signals[momentum > self.threshold] = 1  # Buy on positive momentum
        signals[momentum < -self.threshold] = -1  # Sell on negative momentum
        
        return signals


class MeanReversion(BaseStrategy):
    """
    Mean Reversion Strategy
    """
    
    def __init__(self, period: int = 20, threshold: float = 1.5):
        """
        Initialize strategy
        
        Args:
            period: Lookback period
            threshold: Z-score threshold
        """
        super().__init__("Mean_Reversion")
        self.period = period
        self.threshold = threshold
        
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate signals based on mean reversion"""
        mean = data['Close'].rolling(window=self.period).mean()
        std = data['Close'].rolling(window=self.period).std()
        z_score = (data['Close'] - mean) / std
        
        signals = pd.Series(0, index=data.index)
        signals[z_score < -self.threshold] = 1  # Buy when price is low
        signals[z_score > self.threshold] = -1  # Sell when price is high
        
        return signals


class RuleBasedStrategy:
    """
    Collection of rule-based strategies
    """
    
    @staticmethod
    def get_all_strategies():
        """Get all available rule-based strategies"""
        return [
            MovingAverageCrossover(),
            RSIDivergence(),
            BollingerBands(),
            MomentumStrategy(),
            MeanReversion(),
        ]
