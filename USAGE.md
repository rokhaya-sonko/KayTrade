# KayTrade Usage Guide

This guide provides detailed instructions on how to use the KayTrade framework.

## Table of Contents
1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Data Loading](#data-loading)
4. [Signal Generation](#signal-generation)
5. [Portfolio Management](#portfolio-management)
6. [Backtesting](#backtesting)
7. [Performance Analysis](#performance-analysis)
8. [Streamlit Dashboard](#streamlit-dashboard)
9. [Advanced Usage](#advanced-usage)

## Installation

### Requirements
- Python 3.8+
- pip

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Install Package

```bash
pip install -e .
```

## Quick Start

Here's a simple example to get you started:

```python
from kaytrade.data.data_loader import DataLoader
from kaytrade.signals.signal_generator import SignalGenerator
from kaytrade.signals.rule_based import MovingAverageCrossover
from kaytrade.execution.backtester import Backtester
from kaytrade.analytics.performance import PerformanceAnalyzer

# Load data
loader = DataLoader()
data = loader.load_historical_data("AAPL", "2020-01-01", "2023-12-31")

# Generate signals
signal_gen = SignalGenerator()
signal_gen.add_strategy(MovingAverageCrossover())
signals_df = signal_gen.generate_signals(data)
signals = signal_gen.aggregate_signals(signals_df)

# Run backtest
backtester = Backtester(initial_capital=100000)
results = backtester.run_backtest(data, signals)

# Analyze performance
analyzer = PerformanceAnalyzer()
returns = results['Portfolio_Value'].pct_change().dropna()
print(analyzer.generate_report(returns))
```

## Data Loading

### Load Historical Data

```python
from kaytrade.data.data_loader import DataLoader

loader = DataLoader(cache_dir="./data_cache")

# Single symbol
data = loader.load_historical_data(
    symbols="AAPL",
    start_date="2020-01-01",
    end_date="2023-12-31",
    interval="1d"
)

# Multiple symbols
data = loader.load_historical_data(
    symbols=["AAPL", "MSFT", "GOOGL"],
    start_date="2020-01-01",
    end_date="2023-12-31"
)
```

### Load Live Data

```python
# Get recent data
live_data = loader.load_live_data("AAPL", period="5d")
```

### Preprocessing

```python
from kaytrade.data.preprocessor import DataPreprocessor

preprocessor = DataPreprocessor()

# Add technical indicators
data = preprocessor.add_technical_indicators(data)

# Create features for ML
data = preprocessor.create_features(data, lookback=20)

# Normalize data
data = preprocessor.normalize_data(data, columns=['Close', 'Volume'])
```

## Signal Generation

### Rule-Based Strategies

```python
from kaytrade.signals.signal_generator import SignalGenerator
from kaytrade.signals.rule_based import (
    MovingAverageCrossover,
    RSIDivergence,
    BollingerBands,
    MomentumStrategy,
    MeanReversion
)

signal_gen = SignalGenerator()

# Add strategies
signal_gen.add_strategy(MovingAverageCrossover(fast_period=50, slow_period=200))
signal_gen.add_strategy(RSIDivergence(period=14, oversold=30, overbought=70))
signal_gen.add_strategy(BollingerBands(period=20, std_dev=2.0))

# Generate signals
signals_df = signal_gen.generate_signals(data)

# Aggregate signals
signals = signal_gen.aggregate_signals(signals_df, method='majority')
```

### Machine Learning Strategies

```python
from kaytrade.signals.ml_based import RandomForestStrategy, XGBoostStrategy

# Create and train strategy
strategy = RandomForestStrategy(n_estimators=100, max_depth=10)
strategy.train(train_data, test_size=0.2)

# Generate signals
signals = strategy.generate_signals(test_data)
```

## Portfolio Management

### Basic Portfolio Operations

```python
from kaytrade.portfolio.portfolio_manager import PortfolioManager

portfolio = PortfolioManager(
    initial_capital=100000,
    max_position_size=0.2,
    min_position_size=0.01,
    long_only=True
)

# Calculate position size
shares = portfolio.calculate_position_size(
    signal=1.0,
    price=150.0,
    method='equal_weight'
)

# Update position
portfolio.update_position('AAPL', shares, 150.0)

# Get current positions
positions = portfolio.get_positions()
portfolio_value = portfolio.get_portfolio_value(prices)
```

### Portfolio Optimization

```python
from kaytrade.portfolio.optimizer import PortfolioOptimizer

optimizer = PortfolioOptimizer(risk_free_rate=0.02)

# Optimize for maximum Sharpe ratio
weights = optimizer.optimize_maximum_sharpe(returns_df)

# Risk parity optimization
weights = optimizer.optimize_risk_parity(returns_df)

# Mean-variance optimization
weights = optimizer.optimize_mean_variance(returns_df, target_return=0.15)
```

## Backtesting

### Single Asset Backtest

```python
from kaytrade.execution.backtester import Backtester

backtester = Backtester(
    initial_capital=100000,
    commission=0.001,  # 0.1%
    slippage=0.0005    # 0.05%
)

results = backtester.run_backtest(
    data=data,
    signals=signals,
    position_sizing='equal_weight'
)
```

### Multi-Asset Backtest

```python
# Prepare data and signals for multiple assets
data_dict = {
    'AAPL': aapl_data,
    'MSFT': msft_data,
    'GOOGL': googl_data
}

signals_dict = {
    'AAPL': aapl_signals,
    'MSFT': msft_signals,
    'GOOGL': googl_signals
}

# Run multi-asset backtest
results = backtester.run_multi_asset_backtest(
    data=data_dict,
    signals=signals_dict,
    weights={'AAPL': 0.33, 'MSFT': 0.33, 'GOOGL': 0.34},
    rebalance_frequency='monthly'
)
```

## Performance Analysis

### Calculate Metrics

```python
from kaytrade.analytics.performance import PerformanceAnalyzer

analyzer = PerformanceAnalyzer(risk_free_rate=0.02)
returns = results['Portfolio_Value'].pct_change().dropna()

# Calculate all metrics
metrics = analyzer.calculate_all_metrics(returns)

# Individual metrics
sharpe = analyzer.calculate_sharpe_ratio(returns)
sortino = analyzer.calculate_sortino_ratio(returns)
max_dd = analyzer.calculate_max_drawdown(returns)
```

### Generate Report

```python
# Generate comprehensive report
report = analyzer.generate_report(returns, benchmark_returns)
print(report)
```

## Streamlit Dashboard

Launch the interactive dashboard:

```bash
streamlit run streamlit_app/app.py
```

The dashboard provides:
- Data visualization
- Strategy configuration
- Portfolio monitoring
- Performance analytics
- Interactive charts

## Advanced Usage

### VWAP/TWAP Execution

```python
from kaytrade.execution.execution_algos import VWAPExecution, TWAPExecution

# VWAP execution
vwap = VWAPExecution(target_shares=1000, duration_minutes=60)
executions = vwap.execute(intraday_data, start_time)
avg_price = vwap.get_average_price()

# TWAP execution
twap = TWAPExecution(target_shares=1000, duration_minutes=60, num_slices=10)
executions = twap.execute(intraday_data, start_time)
avg_price = twap.get_average_price()
```

### Paper Trading

```python
from kaytrade.brokers.paper_broker import PaperBroker

broker = PaperBroker(initial_capital=100000)

# Place orders
order = broker.place_order('AAPL', 10, 'market')

# Get account info
account = broker.get_account_info()
positions = broker.get_positions()

# Get order history
history = broker.get_order_history()
```

### Configuration

Edit `config/config.yaml` to customize settings:

```yaml
data:
  default_source: yfinance
  cache_dir: ./data_cache

trading:
  initial_capital: 100000.0
  commission: 0.001
  slippage: 0.0005

portfolio:
  optimization_method: mean_variance
  max_leverage: 1.0
```

Load configuration in your code:

```python
from kaytrade.utils.config import Config

config = Config()
initial_capital = config.get('trading.initial_capital')
commission = config.get('trading.commission')
```

## Examples

Check the `examples/` directory for complete examples:

1. **simple_backtest.py** - Basic backtesting workflow
2. **ml_strategy_example.py** - Machine learning strategy
3. **multi_asset_backtest.py** - Multi-asset portfolio optimization

Run examples:

```bash
python examples/simple_backtest.py
python examples/ml_strategy_example.py
python examples/multi_asset_backtest.py
```

## Tips and Best Practices

1. **Data Quality**: Always preprocess and validate your data before use
2. **Overfitting**: Be careful with ML models - use proper train/test splits
3. **Transaction Costs**: Include realistic commission and slippage in backtests
4. **Risk Management**: Set appropriate position size limits
5. **Diversification**: Use multiple strategies and assets
6. **Walk-Forward**: Test strategies on out-of-sample data
7. **Monitoring**: Regularly monitor strategy performance

## Troubleshooting

### Data Loading Issues

If you encounter data loading errors:
- Check your internet connection
- Verify symbol names are correct
- Try using cache: `use_cache=True`

### Memory Issues

For large datasets:
- Use smaller date ranges
- Process data in chunks
- Clear cache periodically

### Performance Issues

To improve performance:
- Use vectorized operations
- Cache preprocessed data
- Reduce number of indicators
- Use simpler models for initial tests

## Support

For issues and questions:
- Check the [GitHub Issues](https://github.com/rokhaya-sonko/KayTrade/issues)
- Read the documentation
- Review example scripts

## Next Steps

1. Explore different strategies
2. Optimize parameters
3. Test on multiple assets
4. Implement risk management
5. Deploy to paper trading
6. Monitor and iterate
