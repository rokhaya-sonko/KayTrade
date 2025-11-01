# Contributing to KayTrade

Thank you for your interest in contributing to KayTrade! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and constructive in all interactions. We aim to foster an inclusive and welcoming community.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (Python version, OS, etc.)
- Error messages or logs

### Suggesting Features

For feature requests:
- Describe the feature and its benefits
- Provide use cases
- Consider implementation complexity
- Check if similar features exist

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Test your changes**
5. **Commit with clear messages**
   ```bash
   git commit -m "Add feature: description"
   ```
6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Create a Pull Request**

## Development Setup

### Prerequisites
- Python 3.8+
- Git
- pip

### Setup Environment

```bash
# Clone repository
git clone https://github.com/rokhaya-sonko/KayTrade.git
cd KayTrade

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

## Code Style

### Python Style Guide
- Follow PEP 8
- Use meaningful variable names
- Add docstrings to functions and classes
- Keep functions focused and small
- Use type hints where appropriate

### Example

```python
def calculate_sharpe_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.02,
    periods_per_year: int = 252
) -> float:
    """
    Calculate Sharpe ratio
    
    Args:
        returns: Series of returns
        risk_free_rate: Annual risk-free rate
        periods_per_year: Number of periods per year
        
    Returns:
        Sharpe ratio
    """
    excess_returns = returns - (risk_free_rate / periods_per_year)
    return np.sqrt(periods_per_year) * excess_returns.mean() / excess_returns.std()
```

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_signals.py

# Run with coverage
python -m pytest --cov=kaytrade tests/
```

### Writing Tests

Create test files in the `tests/` directory:

```python
import pytest
from kaytrade.signals.rule_based import MovingAverageCrossover

def test_ma_crossover():
    strategy = MovingAverageCrossover(fast_period=20, slow_period=50)
    # Test implementation
    assert strategy.name == "MA_Crossover"
```

## Documentation

### Docstring Format

Use Google-style docstrings:

```python
def function_name(param1: type1, param2: type2) -> return_type:
    """
    Brief description
    
    Detailed description if needed.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When invalid input
    """
```

### Updating Documentation

- Update README.md for major features
- Update USAGE.md for new functionality
- Add examples to examples/ directory
- Update config/config.yaml if adding new settings

## Project Structure

```
KayTrade/
├── kaytrade/              # Main package
│   ├── data/              # Data modules
│   ├── signals/           # Signal generation
│   ├── portfolio/         # Portfolio management
│   ├── execution/         # Execution and backtesting
│   ├── analytics/         # Performance analytics
│   ├── brokers/           # Broker adapters
│   └── utils/             # Utilities
├── streamlit_app/         # Web interface
├── examples/              # Example scripts
├── tests/                 # Test suite
├── config/                # Configuration files
└── docs/                  # Documentation
```

## Areas for Contribution

### High Priority
- Additional ML models (LSTM, Transformers)
- More technical indicators
- Risk management features
- Real broker integrations
- Performance optimizations

### Medium Priority
- Additional data sources
- More execution algorithms
- Advanced portfolio optimization
- Visualization improvements
- Documentation enhancements

### Low Priority
- Code refactoring
- Test coverage improvements
- CI/CD setup
- Docker support

## Commit Messages

### Format
```
type: brief description

Detailed description if needed.

Fixes #issue_number
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Maintenance tasks

### Examples
```
feat: add LSTM strategy for signal generation

Implements LSTM-based strategy with configurable architecture
and training parameters.

Closes #123
```

## Review Process

### For Contributors
- Ensure all tests pass
- Update documentation
- Keep PRs focused
- Respond to feedback promptly

### For Reviewers
- Be constructive and respectful
- Test changes locally
- Verify documentation
- Check for edge cases

## Questions?

If you have questions:
- Check existing issues
- Review documentation
- Ask in discussions
- Create a new issue

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Thank You!

Your contributions help make KayTrade better for everyone. We appreciate your time and effort!
