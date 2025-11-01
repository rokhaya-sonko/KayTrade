"""
Multi-asset portfolio backtest example
"""

from kaytrade.data.data_loader import DataLoader
from kaytrade.data.preprocessor import DataPreprocessor
from kaytrade.signals.signal_generator import SignalGenerator
from kaytrade.signals.rule_based import MovingAverageCrossover, RSIDivergence
from kaytrade.portfolio.optimizer import PortfolioOptimizer
from kaytrade.execution.backtester import Backtester
from kaytrade.analytics.performance import PerformanceAnalyzer


def main():
    # Define symbols
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN"]
    
    # Load data
    print("Loading data...")
    loader = DataLoader()
    
    data_dict = {}
    for symbol in symbols:
        data = loader.load_historical_data(
            symbols=symbol,
            start_date="2020-01-01",
            end_date="2023-12-31"
        )
        data_dict[symbol] = data
    
    # Preprocess data
    print("Preprocessing data...")
    preprocessor = DataPreprocessor()
    for symbol in symbols:
        data_dict[symbol] = preprocessor.add_technical_indicators(data_dict[symbol])
    
    # Generate signals for each asset
    print("Generating signals...")
    signal_generator = SignalGenerator()
    signal_generator.add_strategy(MovingAverageCrossover())
    signal_generator.add_strategy(RSIDivergence())
    
    signals_dict = {}
    for symbol in symbols:
        signals_df = signal_generator.generate_signals(data_dict[symbol])
        signals_dict[symbol] = signal_generator.aggregate_signals(signals_df)
    
    # Optimize portfolio weights
    print("Optimizing portfolio...")
    optimizer = PortfolioOptimizer(risk_free_rate=0.02)
    
    # Create price DataFrame for optimization
    prices_df = pd.DataFrame({
        symbol: data['Close'] for symbol, data in data_dict.items()
    })
    
    returns_df = optimizer.calculate_returns(prices_df)
    weights = optimizer.optimize_maximum_sharpe(returns_df)
    
    print("Optimal weights:")
    for symbol, weight in weights.items():
        print(f"  {symbol}: {weight*100:.2f}%")
    
    # Run backtest
    print("\nRunning backtest...")
    backtester = Backtester(
        initial_capital=100000.0,
        commission=0.001,
        slippage=0.0005
    )
    
    results = backtester.run_multi_asset_backtest(
        data=data_dict,
        signals=signals_dict,
        weights=weights,
        position_sizing='equal_weight',
        rebalance_frequency='monthly'
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
    import pandas as pd
    main()
