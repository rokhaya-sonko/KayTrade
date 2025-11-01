"""
Performance analytics: Sharpe, Sortino, drawdown, turnover, etc.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional


class PerformanceAnalyzer:
    """
    Analyze trading strategy performance
    """
    
    def __init__(self, risk_free_rate: float = 0.02):
        """
        Initialize PerformanceAnalyzer
        
        Args:
            risk_free_rate: Annual risk-free rate
        """
        self.risk_free_rate = risk_free_rate
        
    def calculate_sharpe_ratio(
        self,
        returns: pd.Series,
        periods_per_year: int = 252
    ) -> float:
        """
        Calculate Sharpe ratio
        
        Args:
            returns: Series of returns
            periods_per_year: Number of periods per year (252 for daily)
            
        Returns:
            Sharpe ratio
        """
        if len(returns) == 0:
            return 0.0
        
        excess_returns = returns - (self.risk_free_rate / periods_per_year)
        
        if excess_returns.std() == 0:
            return 0.0
        
        sharpe = np.sqrt(periods_per_year) * excess_returns.mean() / excess_returns.std()
        
        return sharpe
    
    def calculate_sortino_ratio(
        self,
        returns: pd.Series,
        periods_per_year: int = 252
    ) -> float:
        """
        Calculate Sortino ratio
        
        Args:
            returns: Series of returns
            periods_per_year: Number of periods per year
            
        Returns:
            Sortino ratio
        """
        if len(returns) == 0:
            return 0.0
        
        excess_returns = returns - (self.risk_free_rate / periods_per_year)
        downside_returns = excess_returns[excess_returns < 0]
        
        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0.0
        
        sortino = np.sqrt(periods_per_year) * excess_returns.mean() / downside_returns.std()
        
        return sortino
    
    def calculate_max_drawdown(self, returns: pd.Series) -> float:
        """
        Calculate maximum drawdown
        
        Args:
            returns: Series of returns
            
        Returns:
            Maximum drawdown (as negative percentage)
        """
        if len(returns) == 0:
            return 0.0
        
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        
        return drawdown.min()
    
    def calculate_calmar_ratio(
        self,
        returns: pd.Series,
        periods_per_year: int = 252
    ) -> float:
        """
        Calculate Calmar ratio
        
        Args:
            returns: Series of returns
            periods_per_year: Number of periods per year
            
        Returns:
            Calmar ratio
        """
        if len(returns) == 0:
            return 0.0
        
        annual_return = self.calculate_annual_return(returns, periods_per_year)
        max_drawdown = abs(self.calculate_max_drawdown(returns))
        
        if max_drawdown == 0:
            return 0.0
        
        return annual_return / max_drawdown
    
    def calculate_annual_return(
        self,
        returns: pd.Series,
        periods_per_year: int = 252
    ) -> float:
        """
        Calculate annualized return
        
        Args:
            returns: Series of returns
            periods_per_year: Number of periods per year
            
        Returns:
            Annualized return
        """
        if len(returns) == 0:
            return 0.0
        
        total_return = (1 + returns).prod() - 1
        n_periods = len(returns)
        
        if n_periods < periods_per_year:
            # Annualize if less than a year
            annual_return = (1 + total_return) ** (periods_per_year / n_periods) - 1
        else:
            annual_return = total_return * (periods_per_year / n_periods)
        
        return annual_return
    
    def calculate_annual_volatility(
        self,
        returns: pd.Series,
        periods_per_year: int = 252
    ) -> float:
        """
        Calculate annualized volatility
        
        Args:
            returns: Series of returns
            periods_per_year: Number of periods per year
            
        Returns:
            Annualized volatility
        """
        if len(returns) == 0:
            return 0.0
        
        return returns.std() * np.sqrt(periods_per_year)
    
    def calculate_turnover(
        self,
        positions: pd.DataFrame,
        portfolio_values: pd.Series
    ) -> float:
        """
        Calculate portfolio turnover
        
        Args:
            positions: DataFrame with position changes
            portfolio_values: Series with portfolio values
            
        Returns:
            Average turnover rate
        """
        if positions.empty or len(portfolio_values) == 0:
            return 0.0
        
        # Calculate trade values
        if 'cost' in positions.columns:
            trade_values = positions['cost'].abs()
        else:
            return 0.0
        
        # Calculate average portfolio value
        avg_portfolio_value = portfolio_values.mean()
        
        if avg_portfolio_value == 0:
            return 0.0
        
        # Calculate turnover
        total_traded = trade_values.sum()
        n_periods = len(portfolio_values)
        
        turnover = total_traded / (avg_portfolio_value * n_periods)
        
        return turnover
    
    def calculate_information_ratio(
        self,
        returns: pd.Series,
        benchmark_returns: pd.Series
    ) -> float:
        """
        Calculate information ratio
        
        Args:
            returns: Strategy returns
            benchmark_returns: Benchmark returns
            
        Returns:
            Information ratio
        """
        if len(returns) == 0 or len(benchmark_returns) == 0:
            return 0.0
        
        # Align series
        aligned_returns, aligned_benchmark = returns.align(benchmark_returns, join='inner')
        
        if len(aligned_returns) == 0:
            return 0.0
        
        # Calculate active returns
        active_returns = aligned_returns - aligned_benchmark
        
        if active_returns.std() == 0:
            return 0.0
        
        ir = active_returns.mean() / active_returns.std()
        
        return ir * np.sqrt(252)  # Annualized
    
    def calculate_beta(
        self,
        returns: pd.Series,
        benchmark_returns: pd.Series
    ) -> float:
        """
        Calculate beta
        
        Args:
            returns: Strategy returns
            benchmark_returns: Benchmark returns
            
        Returns:
            Beta
        """
        if len(returns) == 0 or len(benchmark_returns) == 0:
            return 0.0
        
        # Align series
        aligned_returns, aligned_benchmark = returns.align(benchmark_returns, join='inner')
        
        if len(aligned_returns) < 2:
            return 0.0
        
        # Calculate beta
        covariance = np.cov(aligned_returns, aligned_benchmark)[0, 1]
        benchmark_variance = np.var(aligned_benchmark)
        
        if benchmark_variance == 0:
            return 0.0
        
        beta = covariance / benchmark_variance
        
        return beta
    
    def calculate_alpha(
        self,
        returns: pd.Series,
        benchmark_returns: pd.Series,
        periods_per_year: int = 252
    ) -> float:
        """
        Calculate alpha
        
        Args:
            returns: Strategy returns
            benchmark_returns: Benchmark returns
            periods_per_year: Number of periods per year
            
        Returns:
            Alpha
        """
        if len(returns) == 0 or len(benchmark_returns) == 0:
            return 0.0
        
        # Align series
        aligned_returns, aligned_benchmark = returns.align(benchmark_returns, join='inner')
        
        if len(aligned_returns) == 0:
            return 0.0
        
        # Calculate beta
        beta = self.calculate_beta(aligned_returns, aligned_benchmark)
        
        # Calculate returns
        strategy_return = aligned_returns.mean() * periods_per_year
        benchmark_return = aligned_benchmark.mean() * periods_per_year
        
        # Calculate alpha
        alpha = strategy_return - (self.risk_free_rate + beta * (benchmark_return - self.risk_free_rate))
        
        return alpha
    
    def calculate_win_rate(self, returns: pd.Series) -> float:
        """
        Calculate win rate
        
        Args:
            returns: Series of returns
            
        Returns:
            Win rate (percentage of positive returns)
        """
        if len(returns) == 0:
            return 0.0
        
        winning_periods = (returns > 0).sum()
        total_periods = len(returns)
        
        return winning_periods / total_periods
    
    def calculate_profit_factor(self, returns: pd.Series) -> float:
        """
        Calculate profit factor
        
        Args:
            returns: Series of returns
            
        Returns:
            Profit factor (gross profit / gross loss)
        """
        if len(returns) == 0:
            return 0.0
        
        gains = returns[returns > 0].sum()
        losses = abs(returns[returns < 0].sum())
        
        if losses == 0:
            return np.inf if gains > 0 else 0.0
        
        return gains / losses
    
    def calculate_all_metrics(
        self,
        returns: pd.Series,
        benchmark_returns: Optional[pd.Series] = None,
        positions: Optional[pd.DataFrame] = None,
        portfolio_values: Optional[pd.Series] = None
    ) -> Dict:
        """
        Calculate all performance metrics
        
        Args:
            returns: Strategy returns
            benchmark_returns: Benchmark returns (optional)
            positions: Position history (optional)
            portfolio_values: Portfolio values (optional)
            
        Returns:
            Dictionary with all metrics
        """
        metrics = {
            'total_return': (1 + returns).prod() - 1,
            'annual_return': self.calculate_annual_return(returns),
            'annual_volatility': self.calculate_annual_volatility(returns),
            'sharpe_ratio': self.calculate_sharpe_ratio(returns),
            'sortino_ratio': self.calculate_sortino_ratio(returns),
            'max_drawdown': self.calculate_max_drawdown(returns),
            'calmar_ratio': self.calculate_calmar_ratio(returns),
            'win_rate': self.calculate_win_rate(returns),
            'profit_factor': self.calculate_profit_factor(returns),
        }
        
        if benchmark_returns is not None:
            metrics['beta'] = self.calculate_beta(returns, benchmark_returns)
            metrics['alpha'] = self.calculate_alpha(returns, benchmark_returns)
            metrics['information_ratio'] = self.calculate_information_ratio(returns, benchmark_returns)
        
        if positions is not None and portfolio_values is not None:
            metrics['turnover'] = self.calculate_turnover(positions, portfolio_values)
        
        return metrics
    
    def generate_report(
        self,
        returns: pd.Series,
        benchmark_returns: Optional[pd.Series] = None,
        positions: Optional[pd.DataFrame] = None,
        portfolio_values: Optional[pd.Series] = None
    ) -> str:
        """
        Generate performance report
        
        Args:
            returns: Strategy returns
            benchmark_returns: Benchmark returns (optional)
            positions: Position history (optional)
            portfolio_values: Portfolio values (optional)
            
        Returns:
            Formatted performance report
        """
        metrics = self.calculate_all_metrics(returns, benchmark_returns, positions, portfolio_values)
        
        report = "Performance Report\n"
        report += "=" * 50 + "\n\n"
        
        report += f"Total Return:        {metrics['total_return']:>10.2%}\n"
        report += f"Annual Return:       {metrics['annual_return']:>10.2%}\n"
        report += f"Annual Volatility:   {metrics['annual_volatility']:>10.2%}\n"
        report += f"Sharpe Ratio:        {metrics['sharpe_ratio']:>10.2f}\n"
        report += f"Sortino Ratio:       {metrics['sortino_ratio']:>10.2f}\n"
        report += f"Max Drawdown:        {metrics['max_drawdown']:>10.2%}\n"
        report += f"Calmar Ratio:        {metrics['calmar_ratio']:>10.2f}\n"
        report += f"Win Rate:            {metrics['win_rate']:>10.2%}\n"
        report += f"Profit Factor:       {metrics['profit_factor']:>10.2f}\n"
        
        if 'beta' in metrics:
            report += f"\nBeta:                {metrics['beta']:>10.2f}\n"
            report += f"Alpha:               {metrics['alpha']:>10.2%}\n"
            report += f"Information Ratio:   {metrics['information_ratio']:>10.2f}\n"
        
        if 'turnover' in metrics:
            report += f"\nTurnover:            {metrics['turnover']:>10.2f}\n"
        
        return report
