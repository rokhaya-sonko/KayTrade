"""
Machine Learning-based trading strategies
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
from typing import List, Optional
from kaytrade.signals.signal_generator import BaseStrategy


class MLStrategy(BaseStrategy):
    """
    Base class for ML-based strategies
    """
    
    def __init__(self, name: str, model=None):
        """
        Initialize ML strategy
        
        Args:
            name: Strategy name
            model: ML model instance
        """
        super().__init__(name)
        self.model = model
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare features for ML model
        
        Args:
            data: DataFrame with market data
            
        Returns:
            DataFrame with features
        """
        df = data.copy()
        
        # Price-based features
        df['Returns'] = df['Close'].pct_change()
        df['Log_Returns'] = np.log(df['Close'] / df['Close'].shift(1))
        
        # Moving averages
        df['SMA_5'] = df['Close'].rolling(window=5).mean()
        df['SMA_10'] = df['Close'].rolling(window=10).mean()
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        
        # Exponential moving averages
        df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
        df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
        
        # MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        sma_20 = df['Close'].rolling(window=20).mean()
        std_20 = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = sma_20 + (std_20 * 2)
        df['BB_Lower'] = sma_20 - (std_20 * 2)
        df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / sma_20
        
        # Volatility
        df['Volatility'] = df['Returns'].rolling(window=20).std()
        
        # Volume features
        if 'Volume' in df.columns:
            df['Volume_Change'] = df['Volume'].pct_change()
            df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
        
        # Momentum
        df['Momentum_5'] = df['Close'].pct_change(5)
        df['Momentum_10'] = df['Close'].pct_change(10)
        df['Momentum_20'] = df['Close'].pct_change(20)
        
        return df.dropna()
    
    def prepare_target(self, data: pd.DataFrame, horizon: int = 1) -> pd.Series:
        """
        Prepare target variable
        
        Args:
            data: DataFrame with market data
            horizon: Prediction horizon
            
        Returns:
            Series with target labels
        """
        future_returns = data['Close'].pct_change(horizon).shift(-horizon)
        target = pd.Series(0, index=data.index)
        target[future_returns > 0.01] = 1  # Buy signal
        target[future_returns < -0.01] = -1  # Sell signal
        
        return target
    
    def train(
        self,
        data: pd.DataFrame,
        feature_columns: Optional[List[str]] = None,
        test_size: float = 0.2
    ):
        """
        Train the ML model
        
        Args:
            data: DataFrame with market data
            feature_columns: List of feature columns (None = auto-select)
            test_size: Test set size
        """
        # Prepare features and target
        features_df = self.prepare_features(data)
        target = self.prepare_target(features_df)
        
        # Align features and target
        valid_idx = features_df.index.intersection(target.index)
        features_df = features_df.loc[valid_idx]
        target = target.loc[valid_idx]
        
        # Select feature columns
        if feature_columns is None:
            feature_columns = [col for col in features_df.columns 
                             if col not in ['Open', 'High', 'Low', 'Close', 'Volume', 'Symbol']]
        
        X = features_df[feature_columns]
        y = target
        
        # Remove any remaining NaN values
        mask = ~(X.isna().any(axis=1) | y.isna())
        X = X[mask]
        y = y[mask]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, shuffle=False
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        self.is_trained = True
        self.feature_columns = feature_columns
        
        # Evaluate (results can be logged externally if needed)
        self.train_score = self.model.score(X_train_scaled, y_train)
        self.test_score = self.model.score(X_test_scaled, y_test)
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate signals using ML model"""
        if not self.is_trained:
            raise ValueError("Model must be trained before generating signals")
        
        features_df = self.prepare_features(data)
        X = features_df[self.feature_columns]
        X_scaled = self.scaler.transform(X)
        
        predictions = self.model.predict(X_scaled)
        signals = pd.Series(predictions, index=features_df.index)
        
        # Reindex to match original data
        return signals.reindex(data.index, fill_value=0)


class RandomForestStrategy(MLStrategy):
    """
    Random Forest-based strategy
    """
    
    def __init__(self, n_estimators: int = 100, max_depth: int = 10):
        """
        Initialize Random Forest strategy
        
        Args:
            n_estimators: Number of trees
            max_depth: Maximum tree depth
        """
        model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=42
        )
        super().__init__("RandomForest", model)


class XGBoostStrategy(MLStrategy):
    """
    XGBoost-based strategy
    """
    
    def __init__(self, n_estimators: int = 100, max_depth: int = 6):
        """
        Initialize XGBoost strategy
        
        Args:
            n_estimators: Number of boosting rounds
            max_depth: Maximum tree depth
        """
        model = xgb.XGBClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=0.1,
            random_state=42,
            eval_metric='logloss'
        )
        super().__init__("XGBoost", model)
