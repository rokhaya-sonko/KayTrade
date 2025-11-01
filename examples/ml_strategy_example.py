"""
Machine learning strategy example
"""

from kaytrade.data.data_loader import DataLoader
from kaytrade.data.preprocessor import DataPreprocessor
from kaytrade.signals.ml_based import RandomForestStrategy, XGBoostStrategy
from kaytrade.execution.backtester import Backtester
from kaytrade.analytics.performance import PerformanceAnalyzer


def main():
    # Load data
    print("Loading data...")
    loader = DataLoader()
    data = loader.load_historical_data(
        symbols="AAPL",
        start_date="2019-01-01",
        end_date="2023-12-31"
    )
    
    # Split data for training and testing
    split_date = "2022-01-01"
    train_data = data[data.index < split_date]
    test_data = data[data.index >= split_date]
    
    # Train ML model
    print("Training ML model...")
    strategy = RandomForestStrategy(n_estimators=100, max_depth=10)
    strategy.train(train_data, test_size=0.2)
    
    # Generate signals on test data
    print("Generating signals...")
    signals = strategy.generate_signals(test_data)
    
    # Run backtest
    print("Running backtest...")
    backtester = Backtester(
        initial_capital=100000.0,
        commission=0.001,
        slippage=0.0005
    )
    
    results = backtester.run_backtest(
        data=test_data,
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
