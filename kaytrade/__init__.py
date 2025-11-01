"""
KayTrade: AI-powered electronic trading framework
"""

__version__ = "0.1.0"
__author__ = "Rokhaya Sonko"

from kaytrade.data.data_loader import DataLoader
from kaytrade.signals.signal_generator import SignalGenerator
from kaytrade.portfolio.portfolio_manager import PortfolioManager
from kaytrade.execution.backtester import Backtester
from kaytrade.analytics.performance import PerformanceAnalyzer

__all__ = [
    "DataLoader",
    "SignalGenerator",
    "PortfolioManager",
    "Backtester",
    "PerformanceAnalyzer",
]
