# Quantdle Python Client Examples

This directory contains comprehensive examples demonstrating how to use the Quantdle Python client to download and analyze financial market data.

## 📁 Available Examples

### 🐍 Python Script: `quantdle_examples.py`
A complete Python script with 7 comprehensive examples covering all major features of the Quantdle client. Run it directly from the command line.

### 📓 Jupyter Notebook: `quantdle_examples.ipynb`
An interactive Jupyter notebook with the same examples as the Python script, perfect for experimentation and learning.

## 🚀 Quick Start

### Prerequisites

1. **Install the Quantdle package:**
   ```bash
   pip install quantdle
   ```

2. **Optional - For polars support:**
   ```bash
   pip install quantdle[polars]
   ```

3. **Set your API credentials:**
   ```bash
   export QDL_API_KEY='your-api-key'
   export QDL_API_KEY_ID='your-api-key-id'
   ```

### Running the Examples

#### Option 1: Python Script
```bash
cd examples
python quantdle_examples.py
```

#### Option 2: Jupyter Notebook
```bash
cd examples
jupyter notebook quantdle_examples.ipynb
```

## 📊 Examples Overview

### 1. **Basic Data Download**
- Simple data retrieval for a single symbol
- Understanding DataFrame structure
- Basic statistics and data inspection

### 2. **Multiple Symbols and Timeframes**
- Efficient batch downloads
- Working with different assets
- Comparing latest prices across symbols

### 3. **Pandas vs Polars DataFrames**
- Performance comparison
- Memory efficiency for large datasets
- Advanced operations with polars

### 4. **Symbol Discovery and Information**
- Finding available symbols for your account
- Getting symbol metadata and availability
- Data coverage information

### 5. **Advanced Data Analysis**
- Technical indicators (Moving Averages, RSI)
- Trading signal generation
- Statistical analysis and performance metrics

### 6. **Error Handling Best Practices**
- Robust error handling patterns
- Retry logic implementation
- Production-ready code examples

### 7. **Large Date Range Downloads**
- Automatic chunking for big datasets
- Performance optimization techniques
- Parallel download configuration

## 🎯 Key Features Demonstrated

- ✅ **Security**: Environment variable usage for API credentials
- ✅ **Performance**: Parallel downloads and chunking strategies
- ✅ **Flexibility**: Multiple output formats (pandas/polars)
- ✅ **Robustness**: Comprehensive error handling
- ✅ **Analysis**: Real-world technical analysis examples
- ✅ **Best Practices**: Production-ready code patterns

## 📈 Sample Output

The examples will download various financial instruments including:

- **EURUSD** - Major forex pair
- **GBPUSD** - Major forex pair  
- **XAUUSD** - Gold spot price
- **BTCUSD** - Bitcoin cryptocurrency

## 🛠️ Customization

The examples are designed to be easily customizable:

1. **Change symbols**: Modify the `symbols_config` list
2. **Adjust timeframes**: Use M1, M5, M15, M30, H1, H4, or D1
3. **Modify date ranges**: Change start_date and end_date parameters
4. **Performance tuning**: Adjust max_workers and chunk_size_years

## 🔧 Troubleshooting

### Common Issues

1. **Missing API credentials**
   ```
   ⚠️  Please set QDL_API_KEY and QDL_API_KEY_ID environment variables
   ```
   **Solution**: Set your API credentials as environment variables

2. **Polars not available**
   ```
   ⚠️  Polars not available. Install with: pip install quantdle[polars]
   ```
   **Solution**: Install polars support or use pandas format

3. **Invalid symbol errors**
   ```
   ❌ Error downloading SYMBOL: API request failed
   ```
   **Solution**: Check available symbols for your account using `get_available_symbols()`

## 📚 Additional Resources

- 📖 [Main README](../README.md) - Project overview and installation
- 🌐 [Quantdle Documentation](https://docs.quantdle.com) - Complete API reference
- 🐛 [GitHub Issues](https://github.com/quantdle/quantdle-python/issues) - Bug reports and feature requests
- 💬 [Support](https://quantdle.com/support) - Community help and questions

## 🤝 Contributing

Found an issue or want to improve the examples? Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your improvements
4. Submit a pull request

---

**Happy trading!** 📈 