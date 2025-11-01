"""
Backtesting engine with slippage and transaction costs
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Callable
from datetime import datetime
from kaytrade.portfolio.portfolio_manager import PortfolioManager
from kaytrade.analytics.performance import PerformanceAnalyzer


class Backtester:
    """
    Backtest trading strategies with realistic execution simulation
    """
    
    def __init__(
        self,
        initial_capital: float = 100000.0,
        commission: float = 0.001,
        slippage: float = 0.0005,
        use_vwap: bool = False,
        use_twap: bool = False
    ):
        """
        Initialize Backtester
        
        Args:
            initial_capital: Initial capital
            commission: Commission rate (e.g., 0.001 = 0.1%)
            slippage: Slippage rate (e.g., 0.0005 = 0.05%)
            use_vwap: Use VWAP execution
            use_twap: Use TWAP execution
        """
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.use_vwap = use_vwap
        self.use_twap = use_twap
        
        self.portfolio_manager = PortfolioManager(initial_capital=initial_capital)
        self.results = None
        
    def calculate_execution_price(
        self,
        price: float,
        signal: float,
        volume: Optional[float] = None
    ) -> float:
        """
        Calculate execution price with slippage
        
        Args:
            price: Market price
            signal: Trading signal (1: buy, -1: sell)
            volume: Trading volume (for VWAP)
            
        Returns:
            Execution price
        """
        # Apply slippage
        if signal > 0:  # Buy
            execution_price = price * (1 + self.slippage)
        elif signal < 0:  # Sell
            execution_price = price * (1 - self.slippage)
        else:
            execution_price = price
        
        return execution_price
    
    def calculate_transaction_cost(self, trade_value: float) -> float:
        """
        Calculate transaction cost
        
        Args:
            trade_value: Value of trade
            
        Returns:
            Transaction cost
        """
        return abs(trade_value) * self.commission
    
    def run_backtest(
        self,
        data: pd.DataFrame,
        signals: pd.Series,
        position_sizing: str = 'equal_weight',
        rebalance_frequency: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Run backtest
        
        Args:
            data: DataFrame with market data
            signals: Series with trading signals
            position_sizing: Position sizing method
            rebalance_frequency: Rebalancing frequency (None, 'daily', 'weekly', 'monthly')
            
        Returns:
            DataFrame with backtest results
        """
        # Reset portfolio
        self.portfolio_manager.reset()
        
        # Results tracking
        results = []
        
        # Get unique symbols if multiple
        if 'Symbol' in data.columns:
            symbols = data['Symbol'].unique()
        else:
            symbols = ['ASSET']
        
        # Iterate through time periods
        dates = data.index.unique()
        
        for i, date in enumerate(dates):
            if isinstance(data.index, pd.MultiIndex):
                day_data = data.loc[date]
            else:
                day_data = data.loc[data.index == date]
            
            # Get signals for this date
            if date in signals.index:
                signal = signals.loc[date]
            else:
                signal = 0
            
            # Process each symbol
            for symbol in symbols:
                if 'Symbol' in day_data.columns:
                    symbol_data = day_data[day_data['Symbol'] == symbol]
                else:
                    symbol_data = day_data
                
                if symbol_data.empty:
                    continue
                
                price = symbol_data['Close'].iloc[0] if len(symbol_data) > 0 else 0
                volume = symbol_data['Volume'].iloc[0] if 'Volume' in symbol_data.columns else None
                
                # Calculate position size
                shares = self.portfolio_manager.calculate_position_size(
                    signal=signal,
                    price=price,
                    method=position_sizing
                )
                
                # Get current position
                current_shares = self.portfolio_manager.get_position(symbol)
                shares_to_trade = shares - current_shares
                
                # Execute trade
                if shares_to_trade != 0:
                    execution_price = self.calculate_execution_price(
                        price, np.sign(shares_to_trade), volume
                    )
                    
                    # Apply transaction costs
                    trade_value = abs(shares_to_trade * execution_price)
                    transaction_cost = self.calculate_transaction_cost(trade_value)
                    
                    # Update portfolio
                    self.portfolio_manager.update_position(
                        symbol=symbol,
                        shares=shares_to_trade,
                        price=execution_price,
                        timestamp=date
                    )
                    
                    # Deduct transaction cost
                    self.portfolio_manager.cash -= transaction_cost
            
            # Calculate portfolio value
            prices = {}
            for symbol in symbols:
                if 'Symbol' in day_data.columns:
                    symbol_data = day_data[day_data['Symbol'] == symbol]
                else:
                    symbol_data = day_data
                
                if not symbol_data.empty:
                    prices[symbol] = symbol_data['Close'].iloc[0]
                elif symbol in prices:
                    # Keep last known price if no data for this day
                    pass
                else:
                    # Skip if no price data available
                    continue
            
            if not prices:
                # No price data available, skip this period
                continue
            
            portfolio_value = self.portfolio_manager.get_portfolio_value(prices)
            
            # Record results
            results.append({
                'Date': date,
                'Portfolio_Value': portfolio_value,
                'Cash': self.portfolio_manager.cash,
                'Signal': signal,
                'Positions': len(self.portfolio_manager.positions)
            })
        
        # Convert to DataFrame
        self.results = pd.DataFrame(results)
        self.results.set_index('Date', inplace=True)
        
        return self.results
    
    def run_multi_asset_backtest(
        self,
        data: Dict[str, pd.DataFrame],
        signals: Dict[str, pd.Series],
        weights: Optional[Dict[str, float]] = None,
        position_sizing: str = 'equal_weight',
        rebalance_frequency: str = 'monthly'
    ) -> pd.DataFrame:
        """
        Run backtest with multiple assets
        
        Args:
            data: Dictionary of DataFrames (symbol -> data)
            signals: Dictionary of Series (symbol -> signals)
            weights: Target weights for each asset
            position_sizing: Position sizing method
            rebalance_frequency: Rebalancing frequency
            
        Returns:
            DataFrame with backtest results
        """
        # Reset portfolio
        self.portfolio_manager.reset()
        
        # Get all dates
        all_dates = set()
        for df in data.values():
            all_dates.update(df.index)
        all_dates = sorted(all_dates)
        
        # Results tracking
        results = []
        last_rebalance = None
        
        for date in all_dates:
            # Check if rebalancing is needed
            should_rebalance = False
            if rebalance_frequency and last_rebalance is not None:
                if rebalance_frequency == 'daily':
                    should_rebalance = True
                elif rebalance_frequency == 'weekly':
                    should_rebalance = (date - last_rebalance).days >= 7
                elif rebalance_frequency == 'monthly':
                    should_rebalance = (date - last_rebalance).days >= 30
            elif last_rebalance is None:
                should_rebalance = True
            
            # Get prices for all assets
            prices = {}
            for symbol, df in data.items():
                if date in df.index:
                    prices[symbol] = df.loc[date, 'Close']
            
            # Rebalance if needed
            if should_rebalance and weights:
                self.portfolio_manager.rebalance(weights, prices, date)
                last_rebalance = date
            
            # Process signals for each asset
            for symbol, signal_series in signals.items():
                if date not in signal_series.index or symbol not in prices:
                    continue
                
                signal = signal_series.loc[date]
                price = prices[symbol]
                
                # Calculate position size
                shares = self.portfolio_manager.calculate_position_size(
                    signal=signal,
                    price=price,
                    method=position_sizing
                )
                
                # Get current position
                current_shares = self.portfolio_manager.get_position(symbol)
                shares_to_trade = shares - current_shares
                
                # Execute trade
                if shares_to_trade != 0:
                    execution_price = self.calculate_execution_price(
                        price, np.sign(shares_to_trade)
                    )
                    
                    # Apply transaction costs
                    trade_value = abs(shares_to_trade * execution_price)
                    transaction_cost = self.calculate_transaction_cost(trade_value)
                    
                    # Update portfolio
                    self.portfolio_manager.update_position(
                        symbol=symbol,
                        shares=shares_to_trade,
                        price=execution_price,
                        timestamp=date
                    )
                    
                    # Deduct transaction cost
                    self.portfolio_manager.cash -= transaction_cost
            
            # Calculate portfolio value
            portfolio_value = self.portfolio_manager.get_portfolio_value(prices)
            
            # Record results
            results.append({
                'Date': date,
                'Portfolio_Value': portfolio_value,
                'Cash': self.portfolio_manager.cash,
                'Positions': len(self.portfolio_manager.positions)
            })
        
        # Convert to DataFrame
        self.results = pd.DataFrame(results)
        self.results.set_index('Date', inplace=True)
        
        return self.results
    
    def get_results(self) -> Optional[pd.DataFrame]:
        """Get backtest results"""
        return self.results
    
    def get_portfolio_history(self) -> pd.DataFrame:
        """Get portfolio transaction history"""
        return self.portfolio_manager.get_history()
    
    def analyze_performance(self, benchmark_returns: Optional[pd.Series] = None) -> Dict:
        """
        Analyze backtest performance
        
        Args:
            benchmark_returns: Benchmark returns for comparison
            
        Returns:
            Dictionary with performance metrics
        """
        if self.results is None:
            raise ValueError("No backtest results available")
        
        analyzer = PerformanceAnalyzer()
        
        # Calculate returns
        returns = self.results['Portfolio_Value'].pct_change().dropna()
        
        # Calculate metrics
        metrics = analyzer.calculate_all_metrics(returns, benchmark_returns)
        
        return metrics
