# KayTrade

**Modular AI-powered framework for research, backtesting, and execution of trading strategies.**

KayTrade is an open-source electronic trading framework that includes data pipelines, ML signal generation, portfolio optimization, execution simulation, and interactive dashboards.

## Features

### 📊 Data Ingestion & Preprocessing
- Historical and live market data fetching (via yfinance, Alpha Vantage)
- Data caching for efficient retrieval
- Technical indicator calculation (SMA, EMA, RSI, MACD, Bollinger Bands)
- Feature engineering for ML models
- Data normalization and missing data handling

### 🎯 Signal Generation
- **Rule-Based Strategies:**
  - Moving Average Crossover
  - RSI Divergence
  - Bollinger Bands
  - Momentum Strategy
  - Mean Reversion
- **Machine Learning Models:**
  - Random Forest Classifier
  - XGBoost Classifier
  - Automated feature preparation
  - Model training and evaluation

### 💼 Portfolio Management
- Position sizing (equal weight, risk parity, Kelly criterion)
- Portfolio rebalancing
- Constraint management (max/min position sizes, leverage limits)
- Long-only or long/short positions
- Portfolio optimization (mean-variance, maximum Sharpe, risk parity)

### ⚙️ Execution Simulation
- Backtesting engine with realistic execution
- Transaction costs (commissions)
- Market impact modeling (slippage)
- VWAP and TWAP execution algorithms
- Multi-asset portfolio backtesting

### 📈 Performance Analytics
- Sharpe Ratio
- Sortino Ratio
- Maximum Drawdown
- Calmar Ratio
- Annual Return & Volatility
- Win Rate & Profit Factor
- Beta & Alpha (vs. benchmark)
- Information Ratio
- Portfolio Turnover

### 🔄 Paper Trading
- Paper broker for simulated trading
- Order management (market, limit orders)
- Position tracking
- Account monitoring
- Adapter architecture for broker integration (Alpaca, Interactive Brokers, etc.)

### 📱 Streamlit Dashboard
- Interactive web interface
- Real-time data visualization
- Strategy configuration and monitoring
- Portfolio performance tracking
- Performance analytics dashboard

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install from source

```bash
git clone https://github.com/rokhaya-sonko/KayTrade.git
cd KayTrade
pip install -r requirements.txt
pip install -e .
```

## Quick Start

### 1. Simple Backtest

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
signal_generator = SignalGenerator()
signal_generator.add_strategy(MovingAverageCrossover())
signals_df = signal_generator.generate_signals(data)
signals = signal_generator.aggregate_signals(signals_df)

# Run backtest
backtester = Backtester(initial_capital=100000)
results = backtester.run_backtest(data, signals)

# Analyze performance
analyzer = PerformanceAnalyzer()
returns = results['Portfolio_Value'].pct_change().dropna()
print(analyzer.generate_report(returns))
```

### 2. ML-Based Strategy

```python
from kaytrade.signals.ml_based import RandomForestStrategy

# Train ML model
strategy = RandomForestStrategy(n_estimators=100)
strategy.train(train_data)

# Generate signals
signals = strategy.generate_signals(test_data)
```

### 3. Launch Streamlit Dashboard

```bash
streamlit run streamlit_app/app.py
```

## Examples

See the `examples/` directory for more detailed examples:
- `simple_backtest.py` - Basic backtesting example
- `ml_strategy_example.py` - Machine learning strategy
- `multi_asset_backtest.py` - Multi-asset portfolio

## Configuration

Edit `config/config.yaml` to customize:
- Data sources and caching
- Trading parameters (capital, commission, slippage)
- Signal generation settings
- Portfolio constraints
- Performance analytics

## Project Structure

```
KayTrade/
├── kaytrade/              # Main package
│   ├── data/              # Data ingestion and preprocessing
│   ├── signals/           # Signal generation (rule-based & ML)
│   ├── portfolio/         # Portfolio management and optimization
│   ├── execution/         # Backtesting and execution algorithms
│   ├── analytics/         # Performance analytics
│   ├── brokers/           # Paper trading broker adapters
│   └── utils/             # Utilities (config, logging)
├── streamlit_app/         # Streamlit visualization app
├── examples/              # Example scripts
├── config/                # Configuration files
├── tests/                 # Unit tests
└── README.md              # This file
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This software is for educational and research purposes only. It is not intended for real trading or investment advice. Trading involves risk, and you should only trade with money you can afford to lose.

## Roadmap

- [ ] Add more ML models (LSTM, Transformer)
- [ ] Real-time data streaming
- [ ] Advanced risk management
- [ ] Integration with more brokers
- [ ] Reinforcement learning strategies
- [ ] Walk-forward optimization
- [ ] Monte Carlo simulation
- [ ] Factor models

## Author

Rokhaya Sonko

## Acknowledgments

Built with:
- pandas, numpy, scipy
- scikit-learn, xgboost
- yfinance
- streamlit, plotly
- And many other great open-source libraries
