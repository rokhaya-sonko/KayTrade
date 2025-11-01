"""
Portfolio optimization using various methods
"""

import pandas as pd
import numpy as np
from scipy.optimize import minimize
from typing import Dict, List, Optional


class PortfolioOptimizer:
    """
    Optimize portfolio weights using different methods
    """
    
    def __init__(self, risk_free_rate: float = 0.02):
        """
        Initialize PortfolioOptimizer
        
        Args:
            risk_free_rate: Risk-free rate for Sharpe ratio calculation
        """
        self.risk_free_rate = risk_free_rate
        
    def calculate_returns(self, prices: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate returns from prices
        
        Args:
            prices: DataFrame with prices
            
        Returns:
            DataFrame with returns
        """
        return prices.pct_change().dropna()
    
    def calculate_mean_returns(self, returns: pd.DataFrame) -> pd.Series:
        """
        Calculate mean returns
        
        Args:
            returns: DataFrame with returns
            
        Returns:
            Series with mean returns
        """
        return returns.mean()
    
    def calculate_covariance(self, returns: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate covariance matrix
        
        Args:
            returns: DataFrame with returns
            
        Returns:
            Covariance matrix
        """
        return returns.cov()
    
    def optimize_mean_variance(
        self,
        returns: pd.DataFrame,
        target_return: Optional[float] = None,
        max_weight: float = 0.3,
        min_weight: float = 0.0,
        long_only: bool = True
    ) -> Dict[str, float]:
        """
        Optimize portfolio using mean-variance optimization
        
        Args:
            returns: DataFrame with returns
            target_return: Target return (None for maximum Sharpe)
            max_weight: Maximum weight per asset
            min_weight: Minimum weight per asset
            long_only: Whether to allow only long positions
            
        Returns:
            Dictionary with optimal weights
        """
        mean_returns = self.calculate_mean_returns(returns)
        cov_matrix = self.calculate_covariance(returns)
        
        n_assets = len(mean_returns)
        
        # Objective function: minimize portfolio variance
        def portfolio_variance(weights):
            return np.dot(weights, np.dot(cov_matrix, weights))
        
        # Constraints
        constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
        
        if target_return is not None:
            constraints.append({
                'type': 'eq',
                'fun': lambda x: np.dot(x, mean_returns) - target_return
            })
        
        # Bounds
        if long_only:
            bounds = tuple((min_weight, max_weight) for _ in range(n_assets))
        else:
            bounds = tuple((-max_weight, max_weight) for _ in range(n_assets))
        
        # Initial guess: equal weights
        x0 = np.array([1.0 / n_assets] * n_assets)
        
        # Optimize
        result = minimize(
            portfolio_variance,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if result.success:
            weights = dict(zip(returns.columns, result.x))
            return weights
        else:
            raise ValueError("Optimization failed")
    
    def optimize_maximum_sharpe(
        self,
        returns: pd.DataFrame,
        max_weight: float = 0.3,
        min_weight: float = 0.0,
        long_only: bool = True
    ) -> Dict[str, float]:
        """
        Optimize portfolio for maximum Sharpe ratio
        
        Args:
            returns: DataFrame with returns
            max_weight: Maximum weight per asset
            min_weight: Minimum weight per asset
            long_only: Whether to allow only long positions
            
        Returns:
            Dictionary with optimal weights
        """
        mean_returns = self.calculate_mean_returns(returns)
        cov_matrix = self.calculate_covariance(returns)
        
        n_assets = len(mean_returns)
        
        # Objective function: minimize negative Sharpe ratio
        def negative_sharpe(weights):
            portfolio_return = np.dot(weights, mean_returns)
            portfolio_std = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
            return -(portfolio_return - self.risk_free_rate) / portfolio_std
        
        # Constraints
        constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
        
        # Bounds
        if long_only:
            bounds = tuple((min_weight, max_weight) for _ in range(n_assets))
        else:
            bounds = tuple((-max_weight, max_weight) for _ in range(n_assets))
        
        # Initial guess: equal weights
        x0 = np.array([1.0 / n_assets] * n_assets)
        
        # Optimize
        result = minimize(
            negative_sharpe,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if result.success:
            weights = dict(zip(returns.columns, result.x))
            return weights
        else:
            raise ValueError("Optimization failed")
    
    def optimize_risk_parity(
        self,
        returns: pd.DataFrame,
        max_weight: float = 0.3,
        min_weight: float = 0.0
    ) -> Dict[str, float]:
        """
        Optimize portfolio using risk parity
        
        Args:
            returns: DataFrame with returns
            max_weight: Maximum weight per asset
            min_weight: Minimum weight per asset
            
        Returns:
            Dictionary with optimal weights
        """
        cov_matrix = self.calculate_covariance(returns)
        n_assets = len(returns.columns)
        
        # Calculate inverse volatility weights
        volatilities = np.sqrt(np.diag(cov_matrix))
        inv_vol = 1.0 / volatilities
        weights = inv_vol / np.sum(inv_vol)
        
        # Apply constraints
        weights = np.clip(weights, min_weight, max_weight)
        weights = weights / np.sum(weights)
        
        return dict(zip(returns.columns, weights))
    
    def optimize_equal_weight(
        self,
        assets: List[str]
    ) -> Dict[str, float]:
        """
        Create equal-weighted portfolio
        
        Args:
            assets: List of asset symbols
            
        Returns:
            Dictionary with equal weights
        """
        n_assets = len(assets)
        weight = 1.0 / n_assets
        return {asset: weight for asset in assets}
    
    def optimize_minimum_variance(
        self,
        returns: pd.DataFrame,
        max_weight: float = 0.3,
        min_weight: float = 0.0,
        long_only: bool = True
    ) -> Dict[str, float]:
        """
        Optimize portfolio for minimum variance
        
        Args:
            returns: DataFrame with returns
            max_weight: Maximum weight per asset
            min_weight: Minimum weight per asset
            long_only: Whether to allow only long positions
            
        Returns:
            Dictionary with optimal weights
        """
        return self.optimize_mean_variance(
            returns,
            target_return=None,
            max_weight=max_weight,
            min_weight=min_weight,
            long_only=long_only
        )
