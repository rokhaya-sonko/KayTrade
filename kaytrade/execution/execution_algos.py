"""
Execution algorithms (VWAP, TWAP)
"""

import pandas as pd
import numpy as np
from typing import List, Optional, Dict
from datetime import datetime, timedelta


class VWAPExecution:
    """
    Volume Weighted Average Price execution algorithm
    """
    
    def __init__(self, target_shares: int, duration_minutes: int = 60):
        """
        Initialize VWAP execution
        
        Args:
            target_shares: Total shares to execute
            duration_minutes: Execution duration in minutes
        """
        self.target_shares = target_shares
        self.duration_minutes = duration_minutes
        self.executed_shares = 0
        self.executions = []
        
    def calculate_slice_size(
        self,
        volume: float,
        total_volume: float,
        remaining_shares: int
    ) -> int:
        """
        Calculate slice size based on volume profile
        
        Args:
            volume: Current period volume
            total_volume: Total expected volume
            remaining_shares: Remaining shares to execute
            
        Returns:
            Number of shares to execute in this slice
        """
        if total_volume == 0:
            return 0
        
        volume_fraction = volume / total_volume
        slice_size = int(remaining_shares * volume_fraction)
        
        return min(slice_size, remaining_shares)
    
    def execute(
        self,
        data: pd.DataFrame,
        start_time: datetime
    ) -> List[Dict]:
        """
        Execute VWAP order
        
        Args:
            data: DataFrame with intraday data (must include Volume)
            start_time: Execution start time
            
        Returns:
            List of execution records
        """
        # Filter data for execution window
        end_time = start_time + timedelta(minutes=self.duration_minutes)
        exec_data = data[(data.index >= start_time) & (data.index < end_time)]
        
        if exec_data.empty or 'Volume' not in exec_data.columns:
            return []
        
        # Calculate total expected volume
        total_volume = exec_data['Volume'].sum()
        
        # Execute slices
        remaining_shares = self.target_shares
        
        for timestamp, row in exec_data.iterrows():
            if remaining_shares <= 0:
                break
            
            slice_size = self.calculate_slice_size(
                row['Volume'],
                total_volume,
                remaining_shares
            )
            
            if slice_size > 0:
                execution = {
                    'timestamp': timestamp,
                    'shares': slice_size,
                    'price': row['Close'],
                    'value': slice_size * row['Close']
                }
                
                self.executions.append(execution)
                self.executed_shares += slice_size
                remaining_shares -= slice_size
        
        return self.executions
    
    def get_average_price(self) -> float:
        """
        Get volume-weighted average execution price
        
        Returns:
            VWAP execution price
        """
        if not self.executions:
            return 0.0
        
        total_value = sum(e['value'] for e in self.executions)
        total_shares = sum(e['shares'] for e in self.executions)
        
        if total_shares == 0:
            return 0.0
        
        return total_value / total_shares
    
    def get_execution_summary(self) -> Dict:
        """
        Get execution summary
        
        Returns:
            Dictionary with execution metrics
        """
        return {
            'target_shares': self.target_shares,
            'executed_shares': self.executed_shares,
            'fill_rate': self.executed_shares / self.target_shares if self.target_shares > 0 else 0,
            'average_price': self.get_average_price(),
            'num_slices': len(self.executions)
        }


class TWAPExecution:
    """
    Time Weighted Average Price execution algorithm
    """
    
    def __init__(self, target_shares: int, duration_minutes: int = 60, num_slices: int = 10):
        """
        Initialize TWAP execution
        
        Args:
            target_shares: Total shares to execute
            duration_minutes: Execution duration in minutes
            num_slices: Number of execution slices
        """
        self.target_shares = target_shares
        self.duration_minutes = duration_minutes
        self.num_slices = num_slices
        self.slice_size = target_shares // num_slices
        self.executed_shares = 0
        self.executions = []
        
    def execute(
        self,
        data: pd.DataFrame,
        start_time: datetime
    ) -> List[Dict]:
        """
        Execute TWAP order
        
        Args:
            data: DataFrame with intraday data
            start_time: Execution start time
            
        Returns:
            List of execution records
        """
        # Calculate time interval between slices
        interval_minutes = self.duration_minutes / self.num_slices
        
        # Execute slices
        remaining_shares = self.target_shares
        
        for i in range(self.num_slices):
            exec_time = start_time + timedelta(minutes=i * interval_minutes)
            
            # Find closest data point
            if exec_time not in data.index:
                # Find nearest time
                time_diffs = abs(data.index - exec_time)
                nearest_idx = time_diffs.argmin()
                exec_time = data.index[nearest_idx]
            
            if exec_time not in data.index:
                continue
            
            # Determine slice size (handle remainder in last slice)
            if i == self.num_slices - 1:
                slice_size = remaining_shares
            else:
                slice_size = min(self.slice_size, remaining_shares)
            
            if slice_size > 0:
                price = data.loc[exec_time, 'Close']
                
                execution = {
                    'timestamp': exec_time,
                    'shares': slice_size,
                    'price': price,
                    'value': slice_size * price
                }
                
                self.executions.append(execution)
                self.executed_shares += slice_size
                remaining_shares -= slice_size
        
        return self.executions
    
    def get_average_price(self) -> float:
        """
        Get time-weighted average execution price
        
        Returns:
            TWAP execution price
        """
        if not self.executions:
            return 0.0
        
        total_value = sum(e['value'] for e in self.executions)
        total_shares = sum(e['shares'] for e in self.executions)
        
        if total_shares == 0:
            return 0.0
        
        return total_value / total_shares
    
    def get_execution_summary(self) -> Dict:
        """
        Get execution summary
        
        Returns:
            Dictionary with execution metrics
        """
        return {
            'target_shares': self.target_shares,
            'executed_shares': self.executed_shares,
            'fill_rate': self.executed_shares / self.target_shares if self.target_shares > 0 else 0,
            'average_price': self.get_average_price(),
            'num_slices': len(self.executions),
            'planned_slices': self.num_slices
        }


class ExecutionSimulator:
    """
    Simulate order execution with market impact
    """
    
    def __init__(
        self,
        market_impact_coef: float = 0.1,
        temporary_impact_coef: float = 0.5
    ):
        """
        Initialize execution simulator
        
        Args:
            market_impact_coef: Market impact coefficient
            temporary_impact_coef: Temporary impact coefficient
        """
        self.market_impact_coef = market_impact_coef
        self.temporary_impact_coef = temporary_impact_coef
    
    def calculate_market_impact(
        self,
        shares: int,
        avg_daily_volume: float,
        volatility: float
    ) -> float:
        """
        Calculate market impact
        
        Args:
            shares: Number of shares to trade
            avg_daily_volume: Average daily volume
            volatility: Price volatility
            
        Returns:
            Market impact as fraction of price
        """
        if avg_daily_volume == 0:
            return 0.0
        
        participation_rate = abs(shares) / avg_daily_volume
        impact = self.market_impact_coef * volatility * np.sqrt(participation_rate)
        
        return impact
    
    def simulate_execution(
        self,
        shares: int,
        price: float,
        avg_daily_volume: float,
        volatility: float,
        is_buy: bool
    ) -> Dict:
        """
        Simulate order execution
        
        Args:
            shares: Number of shares
            price: Current price
            avg_daily_volume: Average daily volume
            volatility: Price volatility
            is_buy: Whether this is a buy order
            
        Returns:
            Execution result
        """
        # Calculate market impact
        impact = self.calculate_market_impact(shares, avg_daily_volume, volatility)
        
        # Apply impact to price
        if is_buy:
            execution_price = price * (1 + impact)
        else:
            execution_price = price * (1 - impact)
        
        # Calculate total cost
        total_cost = shares * execution_price
        impact_cost = abs(shares * (execution_price - price))
        
        return {
            'shares': shares,
            'price': price,
            'execution_price': execution_price,
            'impact': impact,
            'impact_cost': impact_cost,
            'total_cost': total_cost
        }
