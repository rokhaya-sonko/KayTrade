"""
Streamlit app for visualization and strategy monitoring
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kaytrade.data.data_loader import DataLoader
from kaytrade.data.preprocessor import DataPreprocessor
from kaytrade.signals.signal_generator import SignalGenerator
from kaytrade.signals.rule_based import MovingAverageCrossover, RSIDivergence, BollingerBands
from kaytrade.signals.ml_based import RandomForestStrategy, XGBoostStrategy
from kaytrade.portfolio.portfolio_manager import PortfolioManager
from kaytrade.execution.backtester import Backtester
from kaytrade.analytics.performance import PerformanceAnalyzer


# Page configuration
st.set_page_config(
    page_title="KayTrade - AI Trading Framework",
    page_icon="📈",
    layout="wide"
)

# Title
st.title("📈 KayTrade - AI-Powered Trading Framework")
st.markdown("---")

# Sidebar
st.sidebar.header("Configuration")

# Data configuration
st.sidebar.subheader("Data Settings")
symbols_input = st.sidebar.text_input("Symbols (comma-separated)", "AAPL,MSFT,GOOGL")
symbols = [s.strip() for s in symbols_input.split(",")]

start_date = st.sidebar.date_input(
    "Start Date",
    value=datetime.now() - timedelta(days=365*2)
)
end_date = st.sidebar.date_input(
    "End Date",
    value=datetime.now()
)

# Strategy configuration
st.sidebar.subheader("Strategy Settings")
strategy_type = st.sidebar.selectbox(
    "Strategy Type",
    ["Rule-Based", "ML-Based", "Hybrid"]
)

if strategy_type == "Rule-Based":
    rule_strategies = st.sidebar.multiselect(
        "Select Strategies",
        ["MA Crossover", "RSI", "Bollinger Bands"],
        default=["MA Crossover"]
    )
elif strategy_type == "ML-Based":
    ml_model = st.sidebar.selectbox(
        "ML Model",
        ["Random Forest", "XGBoost"]
    )

# Portfolio configuration
st.sidebar.subheader("Portfolio Settings")
initial_capital = st.sidebar.number_input(
    "Initial Capital ($)",
    min_value=1000,
    value=100000,
    step=1000
)

position_sizing = st.sidebar.selectbox(
    "Position Sizing",
    ["equal_weight", "risk_parity", "kelly"]
)

# Execution configuration
st.sidebar.subheader("Execution Settings")
commission = st.sidebar.number_input(
    "Commission (%)",
    min_value=0.0,
    max_value=1.0,
    value=0.1,
    step=0.01
) / 100

slippage = st.sidebar.number_input(
    "Slippage (%)",
    min_value=0.0,
    max_value=1.0,
    value=0.05,
    step=0.01
) / 100

# Run backtest button
run_backtest = st.sidebar.button("Run Backtest", type="primary")

# Main content
tab1, tab2, tab3, tab4 = st.tabs(["📊 Data", "📈 Strategy", "💼 Portfolio", "📉 Performance"])

# Tab 1: Data
with tab1:
    st.header("Market Data")
    
    if run_backtest or st.session_state.get('data_loaded'):
        with st.spinner("Loading data..."):
            # Load data
            loader = DataLoader()
            
            data_dict = {}
            for symbol in symbols:
                data = loader.load_historical_data(
                    symbol,
                    start_date.strftime("%Y-%m-%d"),
                    end_date.strftime("%Y-%m-%d")
                )
                data_dict[symbol] = data
            
            st.session_state['data_loaded'] = True
            st.session_state['data_dict'] = data_dict
        
        # Display data
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Price Data")
            selected_symbol = st.selectbox("Select Symbol", symbols)
            
            if selected_symbol in data_dict:
                df = data_dict[selected_symbol]
                
                # Price chart
                fig = go.Figure()
                fig.add_trace(go.Candlestick(
                    x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'],
                    name=selected_symbol
                ))
                fig.update_layout(
                    title=f"{selected_symbol} Price Chart",
                    xaxis_title="Date",
                    yaxis_title="Price ($)",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Volume")
            if selected_symbol in data_dict:
                df = data_dict[selected_symbol]
                
                # Volume chart
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=df.index,
                    y=df['Volume'],
                    name='Volume'
                ))
                fig.update_layout(
                    title=f"{selected_symbol} Volume",
                    xaxis_title="Date",
                    yaxis_title="Volume",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Statistics
        st.subheader("Summary Statistics")
        stats_df = pd.DataFrame()
        for symbol, df in data_dict.items():
            stats_df[symbol] = df['Close'].describe()
        st.dataframe(stats_df.T)

# Tab 2: Strategy
with tab2:
    st.header("Trading Signals")
    
    if run_backtest and 'data_dict' in st.session_state:
        with st.spinner("Generating signals..."):
            signal_generator = SignalGenerator()
            
            # Add strategies
            if strategy_type == "Rule-Based":
                if "MA Crossover" in rule_strategies:
                    signal_generator.add_strategy(MovingAverageCrossover())
                if "RSI" in rule_strategies:
                    signal_generator.add_strategy(RSIDivergence())
                if "Bollinger Bands" in rule_strategies:
                    signal_generator.add_strategy(BollingerBands())
            
            # Generate signals for first symbol
            preprocessor = DataPreprocessor()
            symbol = symbols[0]
            df = st.session_state['data_dict'][symbol].copy()
            df = preprocessor.add_technical_indicators(df)
            
            signals_df = signal_generator.generate_signals(df)
            aggregated_signals = signal_generator.aggregate_signals(signals_df)
            
            st.session_state['signals'] = aggregated_signals
            st.session_state['signals_df'] = signals_df
        
        # Display signals
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Signal Chart")
            fig = go.Figure()
            
            # Price
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['Close'],
                mode='lines',
                name='Price'
            ))
            
            # Buy signals
            buy_signals = aggregated_signals[aggregated_signals == 1]
            if len(buy_signals) > 0:
                fig.add_trace(go.Scatter(
                    x=buy_signals.index,
                    y=df.loc[buy_signals.index, 'Close'],
                    mode='markers',
                    marker=dict(size=10, color='green', symbol='triangle-up'),
                    name='Buy'
                ))
            
            # Sell signals
            sell_signals = aggregated_signals[aggregated_signals == -1]
            if len(sell_signals) > 0:
                fig.add_trace(go.Scatter(
                    x=sell_signals.index,
                    y=df.loc[sell_signals.index, 'Close'],
                    mode='markers',
                    marker=dict(size=10, color='red', symbol='triangle-down'),
                    name='Sell'
                ))
            
            fig.update_layout(
                title="Trading Signals",
                xaxis_title="Date",
                yaxis_title="Price ($)",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Signal Statistics")
            
            signal_counts = {
                'Buy Signals': (aggregated_signals == 1).sum(),
                'Sell Signals': (aggregated_signals == -1).sum(),
                'Hold Signals': (aggregated_signals == 0).sum()
            }
            
            st.metric("Total Buy Signals", signal_counts['Buy Signals'])
            st.metric("Total Sell Signals", signal_counts['Sell Signals'])
            st.metric("Total Hold Signals", signal_counts['Hold Signals'])

# Tab 3: Portfolio
with tab3:
    st.header("Portfolio Performance")
    
    if run_backtest and 'signals' in st.session_state:
        with st.spinner("Running backtest..."):
            # Run backtest
            backtester = Backtester(
                initial_capital=initial_capital,
                commission=commission,
                slippage=slippage
            )
            
            symbol = symbols[0]
            df = st.session_state['data_dict'][symbol]
            signals = st.session_state['signals']
            
            results = backtester.run_backtest(
                df,
                signals,
                position_sizing=position_sizing
            )
            
            st.session_state['results'] = results
            st.session_state['backtester'] = backtester
        
        # Display portfolio
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Portfolio Value")
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=results.index,
                y=results['Portfolio_Value'],
                mode='lines',
                name='Portfolio Value',
                fill='tozeroy'
            ))
            fig.add_hline(
                y=initial_capital,
                line_dash="dash",
                line_color="gray",
                annotation_text="Initial Capital"
            )
            fig.update_layout(
                title="Portfolio Value Over Time",
                xaxis_title="Date",
                yaxis_title="Value ($)",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Portfolio Metrics")
            
            final_value = results['Portfolio_Value'].iloc[-1]
            total_return = (final_value - initial_capital) / initial_capital
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric(
                    "Final Value",
                    f"${final_value:,.2f}",
                    f"{total_return*100:.2f}%"
                )
            with col_b:
                st.metric(
                    "Cash Balance",
                    f"${results['Cash'].iloc[-1]:,.2f}"
                )
            
            # Positions chart
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=results.index,
                y=results['Positions'],
                name='Active Positions'
            ))
            fig.update_layout(
                title="Active Positions Over Time",
                xaxis_title="Date",
                yaxis_title="Number of Positions",
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)

# Tab 4: Performance
with tab4:
    st.header("Performance Analytics")
    
    if 'results' in st.session_state:
        backtester = st.session_state['backtester']
        results = st.session_state['results']
        
        # Calculate performance metrics
        analyzer = PerformanceAnalyzer()
        returns = results['Portfolio_Value'].pct_change().dropna()
        
        metrics = analyzer.calculate_all_metrics(returns)
        
        # Display metrics
        st.subheader("Performance Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Return", f"{metrics['total_return']*100:.2f}%")
            st.metric("Annual Return", f"{metrics['annual_return']*100:.2f}%")
        
        with col2:
            st.metric("Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}")
            st.metric("Sortino Ratio", f"{metrics['sortino_ratio']:.2f}")
        
        with col3:
            st.metric("Max Drawdown", f"{metrics['max_drawdown']*100:.2f}%")
            st.metric("Calmar Ratio", f"{metrics['calmar_ratio']:.2f}")
        
        with col4:
            st.metric("Win Rate", f"{metrics['win_rate']*100:.2f}%")
            st.metric("Profit Factor", f"{metrics['profit_factor']:.2f}")
        
        # Returns distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Returns Distribution")
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=returns,
                nbinsx=50,
                name='Returns'
            ))
            fig.update_layout(
                title="Daily Returns Distribution",
                xaxis_title="Return",
                yaxis_title="Frequency",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Cumulative Returns")
            cumulative_returns = (1 + returns).cumprod()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=cumulative_returns.index,
                y=cumulative_returns,
                mode='lines',
                name='Cumulative Returns',
                fill='tozeroy'
            ))
            fig.update_layout(
                title="Cumulative Returns",
                xaxis_title="Date",
                yaxis_title="Cumulative Return",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Performance report
        st.subheader("Detailed Report")
        report = analyzer.generate_report(returns)
        st.text(report)

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using KayTrade Framework")
