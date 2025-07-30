#!/usr/bin/env python3
"""
Quantdle Python Client - Comprehensive Examples

This script demonstrates how to use the Quantdle Python client to download 
historical financial market data.

Features demonstrated:
- Basic data downloading
- Working with different symbols and timeframes  
- Using pandas vs polars DataFrames
- Handling large date ranges
- Advanced configuration options
- Symbol discovery and information
- Error handling best practices
- Data analysis examples

Requirements:
- quantdle Python package: pip install quantdle
- Optional for polars support: pip install quantdle[polars]
"""

import os
from datetime import datetime, timedelta
import quantdle as qdl
import pandas as pd


# ============================================================================
# Configuration & Setup
# ============================================================================

def setup_client():
    """
    Initialize the Quantdle client with your API credentials.
    
    For security, it's recommended to store credentials as environment variables:
    - QDL_API_KEY: Your Quantdle API key
    - QDL_API_KEY_ID: Your Quantdle API key ID
    """
    
    # Option 1: Use environment variables (recommended)
    api_key = os.getenv('QDL_API_KEY')
    api_key_id = os.getenv('QDL_API_KEY_ID')
    
    if not api_key or not api_key_id:
        print("Please set QDL_API_KEY and QDL_API_KEY_ID environment variables")
        print("   Example:")
        print("   export QDL_API_KEY='your-api-key'")
        print("   export QDL_API_KEY_ID='your-api-key-id'")
        return None
    
    # Option 2: Direct assignment (not recommended for production)
    # api_key = "your-api-key"
    # api_key_id = "your-api-key-id"
    
    client = qdl.Client(api_key=api_key, api_key_id=api_key_id)
    print("Quantdle client initialized successfully!")
    return client


# ============================================================================
# Example 1: Basic Data Download
# ============================================================================

def example_basic_download(client):
    """
    Demonstrate basic data downloading for a single symbol and timeframe.
    """
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Data Download")
    print("="*60)
    
    try:
        # Download 1 month of EURUSD hourly data
        print("Downloading EURUSD H1 data for January 2024...")
        
        df = client.download_data(
            symbol="EURUSD",
            timeframe="H1", 
            start_date="2024-01-01",
            end_date="2024-01-31"
        )
        
        print(f"Downloaded {len(df):,} data points")
        print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        print("\nSample data:")
        print(df.head(10))
        
        print("\nBasic statistics:")
        print(df[['open', 'high', 'low', 'close', 'volume']].describe())
        
        return df
        
    except Exception as e:
        print(f"Error downloading data: {e}")
        return None


# ============================================================================
# Example 2: Multiple Symbols and Timeframes
# ============================================================================

def example_multiple_symbols(client):
    """
    Download data for multiple symbols and timeframes efficiently.
    """
    print("\n" + "="*60)
    print("EXAMPLE 2: Multiple Symbols and Timeframes")
    print("="*60)
    
    # Define the symbols and timeframes we want to download
    symbols_config = [
        {"symbol": "EURUSD", "timeframe": "D1", "name": "EUR/USD Daily"},
        {"symbol": "GBPUSD", "timeframe": "H4", "name": "GBP/USD 4-Hour"},
        {"symbol": "XAUUSD", "timeframe": "H1", "name": "Gold 1-Hour"},
    ]
    
    # Download data for the last 30 days
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    datasets = {}
    
    for config in symbols_config:
        try:
            print(f"\nDownloading {config['name']} ({config['symbol']} {config['timeframe']})...")
            
            df = client.download_data(
                symbol=config["symbol"],
                timeframe=config["timeframe"],
                start_date=start_date,
                end_date=end_date,
                show_progress=True
            )
            
            datasets[config["symbol"]] = df
            print(f"Downloaded {len(df):,} data points for {config['name']}")
            
        except Exception as e:
            print(f"Error downloading {config['symbol']}: {e}")
    
    # Compare closing prices
    if datasets:
        print(f"\nLatest closing prices:")
        for symbol, df in datasets.items():
            if not df.empty:
                latest = df.iloc[-1]
                print(f"   {symbol}: {latest['close']:.5f} (Volume: {latest['volume']:,})")
    
    return datasets


# ============================================================================
# Example 3: Using Polars DataFrames
# ============================================================================

def example_polars_dataframes(client):
    """
    Demonstrate using polars DataFrames for better performance with large datasets.
    Note: Requires polars: pip install quantdle[polars]
    """
    print("\n" + "="*60)
    print("EXAMPLE 3: Using Polars DataFrames")
    print("="*60)
    
    try:
        # Check if polars is available
        import polars as pl
        print("Polars is available")
        
        print("Downloading XAUUSD data as Polars DataFrame...")
        
        df = client.download_data(
            symbol="XAUUSD",
            timeframe="H1",
            start_date="2024-01-01",
            end_date="2024-01-15",
            output_format="polars"
        )
        
        print(f"Downloaded {len(df):,} data points as Polars DataFrame")
        print(f"DataFrame info: {df.shape[0]} rows × {df.shape[1]} columns")
        
        # Demonstrate some polars operations
        print("\nPolars DataFrame operations:")
        
        # Calculate daily returns
        daily_returns = df.with_columns([
            (pl.col("close").pct_change() * 100).alias("return_pct")
        ])
        
        print("Sample with returns:")
        print(daily_returns.head(10))
        
        # Calculate some statistics using polars
        stats = df.select([
            pl.col("high").max().alias("max_high"),
            pl.col("low").min().alias("min_low"),
            pl.col("volume").mean().alias("avg_volume"),
            pl.col("close").std().alias("price_volatility")
        ])
        
        print("\nStatistical summary:")
        print(stats)
        
        return df
        
    except ImportError:
        print("Polars not available. Install with: pip install quantdle[polars]")
        print("Falling back to pandas DataFrame...")
        
        df = client.download_data(
            symbol="XAUUSD",
            timeframe="H1",
            start_date="2024-01-01",
            end_date="2024-01-15",
            output_format="pandas"  # Use pandas instead
        )
        
        print(f"Downloaded {len(df):,} data points as Pandas DataFrame")
        return df
        
    except Exception as e:
        print(f"Error downloading XAUUSD data: {e}")
        return None


# ============================================================================
# Example 4: Large Date Range with Chunking
# ============================================================================

def example_large_date_range(client):
    """
    Download data for a large date range, demonstrating automatic chunking.
    """
    print("\n" + "="*60)
    print("EXAMPLE 4: Large Date Range Download")
    print("="*60)
    
    try:
        print("Downloading 2 years of EURUSD daily data...")
        print("(This demonstrates automatic chunking for large requests)")
        
        df = client.download_data(
            symbol="EURUSD",
            timeframe="D1",
            start_date="2022-01-01", 
            end_date="2023-12-31",
            max_workers=6,           # Increase parallel downloads
            show_progress=True,      # Show progress bars
            chunk_size_years=1       # Use 1-year chunks
        )
        
        print(f"Downloaded {len(df):,} daily candles")
        print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        
        # Analyze the data
        print("\nYearly summary:")
        df['year'] = pd.to_datetime(df['timestamp']).dt.year
        yearly_stats = df.groupby('year').agg({
            'high': 'max',
            'low': 'min', 
            'close': ['first', 'last'],
            'volume': 'mean'
        }).round(5)
        
        print(yearly_stats)
        
        # Calculate yearly returns
        yearly_returns = df.groupby('year')['close'].agg(['first', 'last'])
        yearly_returns['return_pct'] = ((yearly_returns['last'] / yearly_returns['first']) - 1) * 100
        
        print("\nYearly returns:")
        for year, row in yearly_returns.iterrows():
            print(f"   {year}: {row['return_pct']:.2f}%")
        
        return df
        
    except Exception as e:
        print(f"Error downloading large dataset: {e}")
        return None


# ============================================================================
# Example 5: Symbol Discovery and Information
# ============================================================================

def example_symbol_discovery(client):
    """
    Discover available symbols and get information about them.
    """
    print("\n" + "="*60)
    print("EXAMPLE 5: Symbol Discovery and Information")
    print("="*60)
    
    try:
        # Get all available symbols
        print("Discovering available symbols...")
        symbols = client.get_available_symbols()
        
        print(f"Found {len(symbols)} available symbols")
        print(f"Sample symbols: {symbols[:10]}")
        
        # Get detailed information for some popular symbols
        popular_symbols = ['EURUSD', 'GBPUSD', 'XAUUSD', 'BTCUSD']
        
        print("\nSymbol Information:")
        print("-" * 80)
        
        symbol_info = {}
        for symbol in popular_symbols:
            if symbol in symbols:
                try:
                    info = client.get_symbol_info(symbol)
                    symbol_info[symbol] = info
                    
                    print(f" {symbol}:")
                    print(f"   Available from: {info.get('available_from', 'N/A')}")
                    print(f"   Available to: {info.get('available_to', 'N/A')}")
                    print(f"   Data points: {info.get('data_points', 'N/A'):,}")
                    print()
                    
                except Exception as e:
                    print(f"Could not get info for {symbol}: {e}")
            else:
                print(f"{symbol} not available in your account")
        
        return symbols, symbol_info
        
    except Exception as e:
        print(f"Error discovering symbols: {e}")
        return None, None


# ============================================================================
# Example 6: Advanced Data Analysis
# ============================================================================

def example_data_analysis(df):
    """
    Perform advanced analysis on downloaded data.
    """
    if df is None or df.empty:
        print("No data available for analysis")
        return
        
    print("\n" + "="*60)
    print("EXAMPLE 6: Advanced Data Analysis")
    print("="*60)
    
    # Ensure timestamp is datetime
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.set_index('timestamp')
    
    print("Technical Analysis Examples:")
    
    # Calculate moving averages
    df['MA_20'] = df['close'].rolling(window=20).mean()
    df['MA_50'] = df['close'].rolling(window=50).mean()
    
    # Calculate daily returns
    df['daily_return'] = df['close'].pct_change()
    
    # Calculate volatility (20-day rolling standard deviation)
    df['volatility'] = df['daily_return'].rolling(window=20).std() * 100
    
    # RSI calculation (simplified)
    def calculate_rsi(prices, window=14):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    df['RSI'] = calculate_rsi(df['close'])
    
    # Print latest technical indicators
    latest = df.iloc[-1]
    print(f"\nLatest Technical Indicators:")
    print(f"   Price: {latest['close']:.5f}")
    print(f"   20-day MA: {latest['MA_20']:.5f}")
    print(f"   50-day MA: {latest['MA_50']:.5f}")
    print(f"   Daily Return: {latest['daily_return']*100:.2f}%")
    print(f"   Volatility (20d): {latest['volatility']:.2f}%")
    print(f"   RSI: {latest['RSI']:.1f}")
    
    # Trading signals
    print(f"\nSimple Trading Signals:")
    
    if latest['MA_20'] > latest['MA_50']:
        print("   Bullish: 20-day MA above 50-day MA")
    else:
        print("   Bearish: 20-day MA below 50-day MA")
        
    if latest['RSI'] > 70:
        print("   Overbought: RSI > 70")
    elif latest['RSI'] < 30:
        print("   Oversold: RSI < 30")
    else:
        print("   Normal: RSI in neutral zone")
    
    # Statistical summary
    print(f"\nStatistical Summary (last 100 periods):")
    recent_data = df.tail(100)
    summary_stats = {
        'Avg Daily Return': f"{recent_data['daily_return'].mean()*100:.3f}%",
        'Volatility': f"{recent_data['daily_return'].std()*100:.2f}%",
        'Max Drawdown': f"{((recent_data['close'] / recent_data['close'].cummax()) - 1).min()*100:.2f}%",
        'Sharpe Ratio': f"{(recent_data['daily_return'].mean() / recent_data['daily_return'].std()) * (252**0.5):.2f}"
    }
    
    for metric, value in summary_stats.items():
        print(f"   {metric}: {value}")


# ============================================================================
# Example 7: Error Handling Best Practices  
# ============================================================================

def example_error_handling(client):
    """
    Demonstrate proper error handling when working with the API.
    """
    print("\n" + "="*60)
    print("EXAMPLE 7: Error Handling Best Practices")
    print("="*60)
    
    # Test with invalid symbol
    print("Testing error handling with invalid symbol...")
    try:
        df = client.download_data(
            symbol="INVALID_SYMBOL",
            timeframe="H1",
            start_date="2024-01-01",
            end_date="2024-01-02"
        )
        print("This should have failed!")
    except Exception as e:
        print(f"Properly caught error: {e}")
    
    # Test with invalid date range
    print("\nTesting with invalid date range...")
    try:
        df = client.download_data(
            symbol="EURUSD",
            timeframe="H1", 
            start_date="2025-01-01",  # Future date
            end_date="2025-01-02"
        )
        print("This should have failed!")
    except Exception as e:
        print(f"Properly caught error: {e}")
    
    # Test with robust error handling function
    print("\nRobust download function example:")
    
    def robust_download(client, symbol, timeframe, start_date, end_date, max_retries=3):
        """Download data with retry logic and proper error handling."""
        for attempt in range(max_retries):
            try:
                print(f"   Attempt {attempt + 1}/{max_retries} for {symbol}...")
                df = client.download_data(
                    symbol=symbol,
                    timeframe=timeframe,
                    start_date=start_date,
                    end_date=end_date,
                    show_progress=False
                )
                print(f"   Success! Downloaded {len(df):,} records")
                return df
                
            except Exception as e:
                print(f"   Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    print(f"   All {max_retries} attempts failed for {symbol}")
                    return None
                else:
                    print(f"   Retrying in 1 second...")
                    import time
                    time.sleep(1)
        
        return None
    
    # Test the robust function
    df = robust_download(client, "EURUSD", "H1", "2024-01-01", "2024-01-02")


# ============================================================================
# Main Execution
# ============================================================================

def main():
    """
    Run all examples in sequence.
    """
    print("Quantdle Python Client - Comprehensive Examples")
    print("=" * 60)
    
    # Initialize client
    client = setup_client()
    if not client:
        return
    
    # Run examples
    try:
        # Basic examples
        basic_df = example_basic_download(client)
        datasets = example_multiple_symbols(client)
        polars_df = example_polars_dataframes(client)
        large_df = example_large_date_range(client)
        
        # Discovery and information
        symbols, symbol_info = example_symbol_discovery(client)
        
        # Advanced analysis (use the first available dataset)
        analysis_df = basic_df if basic_df is not None else None
        if analysis_df is None and datasets:
            analysis_df = next(iter(datasets.values()))
        
        example_data_analysis(analysis_df)
        
        # Error handling
        example_error_handling(client)
        
        print("\n" + "="*60)
        print("All examples completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError running examples: {e}")
    
    finally:
        # Clean up (if client has context manager support)
        if hasattr(client, '__exit__'):
            client.__exit__(None, None, None)


if __name__ == "__main__":
    main() 