"""
Simple backtest example
"""

from kaytrade.data.data_loader import DataLoader
from kaytrade.data.preprocessor import DataPreprocessor
from kaytrade.signals.signal_generator import SignalGenerator
from kaytrade.signals.rule_based import MovingAverageCrossover
from kaytrade.execution.backtester import Backtester
from kaytrade.analytics.performance import PerformanceAnalyzer


def main():
    # Load data
    print("Loading data...")
    loader = DataLoader()
    data = loader.load_historical_data(
        symbols="AAPL",
        start_date="2020-01-01",
        end_date="2023-12-31"
    )
    
    # Preprocess data
    print("Preprocessing data...")
    preprocessor = DataPreprocessor()
    data = preprocessor.add_technical_indicators(data)
    
    # Generate signals
    print("Generating signals...")
    signal_generator = SignalGenerator()
    signal_generator.add_strategy(MovingAverageCrossover(fast_period=50, slow_period=200))
    
    signals_df = signal_generator.generate_signals(data)
    signals = signal_generator.aggregate_signals(signals_df)
    
    # Run backtest
    print("Running backtest...")
    backtester = Backtester(
        initial_capital=100000.0,
        commission=0.001,
        slippage=0.0005
    )
    
    results = backtester.run_backtest(
        data=data,
        signals=signals,
        position_sizing='equal_weight'
    )
    
    # Analyze performance
    print("\nPerformance Analysis:")
    print("=" * 50)
    
    analyzer = PerformanceAnalyzer()
    returns = results['Portfolio_Value'].pct_change().dropna()
    
    report = analyzer.generate_report(returns)
    print(report)
    
    # Display results
    print(f"\nFinal Portfolio Value: ${results['Portfolio_Value'].iloc[-1]:,.2f}")
    print(f"Initial Capital: $100,000.00")
    print(f"Total Return: {(results['Portfolio_Value'].iloc[-1] - 100000) / 100000 * 100:.2f}%")


if __name__ == "__main__":
    main()
