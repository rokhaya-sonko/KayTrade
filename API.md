# KayTrade API Reference

Complete API documentation for KayTrade framework.

## Table of Contents
- [Data Module](#data-module)
- [Signals Module](#signals-module)
- [Portfolio Module](#portfolio-module)
- [Execution Module](#execution-module)
- [Analytics Module](#analytics-module)
- [Brokers Module](#brokers-module)
- [Utils Module](#utils-module)

---

## Data Module

### DataLoader

Load historical and live market data.

```python
from kaytrade.data.data_loader import DataLoader

loader = DataLoader(cache_dir="./data_cache")
```

#### Methods

##### `load_historical_data(symbols, start_date, end_date, interval='1d', use_cache=True)`
Load historical market data.

**Parameters:**
- `symbols` (str or list): Stock symbol(s)
- `start_date` (str): Start date (YYYY-MM-DD)
- `end_date` (str): End date (YYYY-MM-DD)
- `interval` (str): Data interval (1d, 1h, etc.)
- `use_cache` (bool): Use cached data if available

**Returns:** DataFrame with OHLCV data

##### `load_live_data(symbols, period='1d')`
Load live/recent market data.

**Parameters:**
- `symbols` (str or list): Stock symbol(s)
- `period` (str): Time period (1d, 5d, 1mo, etc.)

**Returns:** DataFrame with recent data

### DataPreprocessor

Preprocess market data.

```python
from kaytrade.data.preprocessor import DataPreprocessor

preprocessor = DataPreprocessor()
```

#### Methods

##### `add_technical_indicators(data, indicators=None)`
Add technical indicators to data.

**Parameters:**
- `data` (DataFrame): Market data
- `indicators` (list): List of indicators to add

**Returns:** DataFrame with indicators

##### `create_features(data, lookback=20)`
Create features for ML models.

**Parameters:**
- `data` (DataFrame): Market data
- `lookback` (int): Lookback period

**Returns:** DataFrame with features

---

## Signals Module

### SignalGenerator

Generate and aggregate trading signals.

```python
from kaytrade.signals.signal_generator import SignalGenerator

signal_gen = SignalGenerator()
```

#### Methods

##### `add_strategy(strategy)`
Add a strategy to the generator.

**Parameters:**
- `strategy` (BaseStrategy): Strategy instance

##### `generate_signals(data, strategy_names=None)`
Generate signals from strategies.

**Parameters:**
- `data` (DataFrame): Market data
- `strategy_names` (list): Strategies to use

**Returns:** DataFrame with signals

##### `aggregate_signals(signals, method='majority')`
Aggregate signals from multiple strategies.

**Parameters:**
- `signals` (DataFrame): Signals from strategies
- `method` (str): Aggregation method

**Returns:** Series with aggregated signals

### Rule-Based Strategies

#### MovingAverageCrossover

```python
from kaytrade.signals.rule_based import MovingAverageCrossover

strategy = MovingAverageCrossover(fast_period=50, slow_period=200)
```

#### RSIDivergence

```python
from kaytrade.signals.rule_based import RSIDivergence

strategy = RSIDivergence(period=14, oversold=30, overbought=70)
```

#### BollingerBands

```python
from kaytrade.signals.rule_based import BollingerBands

strategy = BollingerBands(period=20, std_dev=2.0)
```

### ML-Based Strategies

#### RandomForestStrategy

```python
from kaytrade.signals.ml_based import RandomForestStrategy

strategy = RandomForestStrategy(n_estimators=100, max_depth=10)
strategy.train(train_data)
signals = strategy.generate_signals(test_data)
```

#### XGBoostStrategy

```python
from kaytrade.signals.ml_based import XGBoostStrategy

strategy = XGBoostStrategy(n_estimators=100, max_depth=6)
```

---

## Portfolio Module

### PortfolioManager

Manage portfolio positions and sizing.

```python
from kaytrade.portfolio.portfolio_manager import PortfolioManager

portfolio = PortfolioManager(
    initial_capital=100000,
    max_position_size=0.2,
    min_position_size=0.01,
    long_only=True
)
```

#### Methods

##### `calculate_position_size(signal, price, volatility=None, method='equal_weight')`
Calculate position size.

**Parameters:**
- `signal` (float): Trading signal (-1 to 1)
- `price` (float): Current price
- `volatility` (float): Asset volatility
- `method` (str): Position sizing method

**Returns:** Number of shares

##### `update_position(symbol, shares, price, timestamp=None)`
Update position for a symbol.

**Parameters:**
- `symbol` (str): Stock symbol
- `shares` (int): Number of shares to add
- `price` (float): Execution price
- `timestamp` (datetime): Transaction timestamp

##### `get_portfolio_value(prices=None)`
Get current portfolio value.

**Parameters:**
- `prices` (dict): Current prices

**Returns:** Total portfolio value

### PortfolioOptimizer

Optimize portfolio weights.

```python
from kaytrade.portfolio.optimizer import PortfolioOptimizer

optimizer = PortfolioOptimizer(risk_free_rate=0.02)
```

#### Methods

##### `optimize_maximum_sharpe(returns, max_weight=0.3, min_weight=0.0)`
Optimize for maximum Sharpe ratio.

**Parameters:**
- `returns` (DataFrame): Returns data
- `max_weight` (float): Maximum weight per asset
- `min_weight` (float): Minimum weight per asset

**Returns:** Dictionary with optimal weights

##### `optimize_risk_parity(returns, max_weight=0.3, min_weight=0.0)`
Optimize using risk parity.

**Returns:** Dictionary with weights

---

## Execution Module

### Backtester

Backtest trading strategies.

```python
from kaytrade.execution.backtester import Backtester

backtester = Backtester(
    initial_capital=100000,
    commission=0.001,
    slippage=0.0005
)
```

#### Methods

##### `run_backtest(data, signals, position_sizing='equal_weight')`
Run single-asset backtest.

**Parameters:**
- `data` (DataFrame): Market data
- `signals` (Series): Trading signals
- `position_sizing` (str): Position sizing method

**Returns:** DataFrame with results

##### `run_multi_asset_backtest(data, signals, weights=None, rebalance_frequency='monthly')`
Run multi-asset backtest.

**Parameters:**
- `data` (dict): Dictionary of DataFrames
- `signals` (dict): Dictionary of signal Series
- `weights` (dict): Target weights
- `rebalance_frequency` (str): Rebalancing frequency

**Returns:** DataFrame with results

### Execution Algorithms

#### VWAPExecution

```python
from kaytrade.execution.execution_algos import VWAPExecution

vwap = VWAPExecution(target_shares=1000, duration_minutes=60)
executions = vwap.execute(intraday_data, start_time)
avg_price = vwap.get_average_price()
```

#### TWAPExecution

```python
from kaytrade.execution.execution_algos import TWAPExecution

twap = TWAPExecution(target_shares=1000, duration_minutes=60, num_slices=10)
```

---

## Analytics Module

### PerformanceAnalyzer

Analyze strategy performance.

```python
from kaytrade.analytics.performance import PerformanceAnalyzer

analyzer = PerformanceAnalyzer(risk_free_rate=0.02)
```

#### Methods

##### `calculate_sharpe_ratio(returns, periods_per_year=252)`
Calculate Sharpe ratio.

**Returns:** float

##### `calculate_sortino_ratio(returns, periods_per_year=252)`
Calculate Sortino ratio.

**Returns:** float

##### `calculate_max_drawdown(returns)`
Calculate maximum drawdown.

**Returns:** float

##### `calculate_all_metrics(returns, benchmark_returns=None)`
Calculate all performance metrics.

**Parameters:**
- `returns` (Series): Strategy returns
- `benchmark_returns` (Series): Benchmark returns

**Returns:** Dictionary with all metrics

##### `generate_report(returns, benchmark_returns=None)`
Generate performance report.

**Returns:** Formatted string report

---

## Brokers Module

### PaperBroker

Paper trading broker.

```python
from kaytrade.brokers.paper_broker import PaperBroker

broker = PaperBroker(initial_capital=100000)
```

#### Methods

##### `get_account_info()`
Get account information.

**Returns:** Dictionary with account details

##### `place_order(symbol, quantity, order_type='market', price=None)`
Place an order.

**Parameters:**
- `symbol` (str): Stock symbol
- `quantity` (int): Number of shares
- `order_type` (str): Order type
- `price` (float): Limit price

**Returns:** Order confirmation

##### `get_positions()`
Get current positions.

**Returns:** Dictionary of positions

---

## Utils Module

### Config

Configuration management.

```python
from kaytrade.utils.config import Config

config = Config()
```

#### Methods

##### `get(key, default=None)`
Get configuration value.

**Parameters:**
- `key` (str): Configuration key
- `default`: Default value

**Returns:** Configuration value

##### `set(key, value)`
Set configuration value.

### Logger

Setup logging.

```python
from kaytrade.utils.logger import setup_logger

logger = setup_logger(
    name="kaytrade",
    level="INFO",
    log_file="./logs/kaytrade.log"
)
```

---

## Signal Values

Trading signals use the following convention:
- `1`: Buy signal
- `-1`: Sell signal
- `0`: Hold/No signal

## Position Sizing Methods

Available methods:
- `equal_weight`: Equal allocation to all positions
- `risk_parity`: Inverse volatility weighting
- `kelly`: Kelly criterion

## Aggregation Methods

Signal aggregation methods:
- `majority`: Majority vote
- `average`: Average of signals
- `unanimous`: All strategies must agree

## Return Calculations

- All returns are calculated as simple returns by default
- Annualization uses 252 trading days per year
- Risk-free rate should be annual rate

---

For more examples, see the `examples/` directory.
