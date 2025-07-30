"""
Shared test fixtures and configuration for pytest
"""

import pytest
import requests
from unittest.mock import Mock
import pandas as pd
from quantdle.client import Client
from quantdle.symbols import SymbolsAPI
from quantdle.data_downloader import DataDownloader


@pytest.fixture
def mock_session():
    """Mock requests session for testing"""
    return Mock(spec=requests.Session)


@pytest.fixture
def test_host():
    """Test API host"""
    return "https://api.test.com"


@pytest.fixture
def test_api_key():
    """Test API key"""
    return "test_api_key"


@pytest.fixture
def test_api_key_id():
    """Test API key ID"""
    return "test_api_key_id"


@pytest.fixture
def client(test_api_key, test_api_key_id, test_host):
    """Client instance for testing"""
    return Client(api_key=test_api_key, api_key_id=test_api_key_id, host=test_host)


@pytest.fixture
def symbols_api(mock_session, test_host):
    """SymbolsAPI instance for testing"""
    return SymbolsAPI(mock_session, test_host)


@pytest.fixture
def data_downloader(mock_session, test_host):
    """DataDownloader instance for testing"""
    return DataDownloader(mock_session, test_host)


@pytest.fixture
def sample_symbols():
    """Sample symbol list for testing"""
    return ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "BTCUSD"]


@pytest.fixture
def sample_symbol_info():
    """Sample symbol info for testing"""
    return {
        "symbol": "EURUSD",
        "available_from": "2004-01-01",
        "available_to": "2025-06-30"
    }


@pytest.fixture
def sample_market_data():
    """Sample market data for testing"""
    return [
        {
            "timestamp": "2023-01-01T00:00:00",
            "open": 1.0500,
            "high": 1.0520,
            "low": 1.0480,
            "close": 1.0510,
            "volume": 1000
        },
        {
            "timestamp": "2023-01-01T01:00:00", 
            "open": 1.0510,
            "high": 1.0530,
            "low": 1.0495,
            "close": 1.0525,
            "volume": 1200
        },
        {
            "timestamp": "2023-01-01T02:00:00",
            "open": 1.0525,
            "high": 1.0545,
            "low": 1.0515,
            "close": 1.0535,
            "volume": 800
        }
    ]


@pytest.fixture
def sample_dataframe(sample_market_data):
    """Sample pandas DataFrame for testing"""
    df = pd.DataFrame(sample_market_data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df


@pytest.fixture
def mock_successful_response():
    """Mock successful HTTP response"""
    response = Mock()
    response.raise_for_status.return_value = None
    response.status_code = 200
    return response


@pytest.fixture
def mock_api_response(mock_successful_response):
    """Factory for creating mock API responses"""
    def _create_response(data):
        mock_successful_response.json.return_value = data
        return mock_successful_response
    return _create_response


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test (may be slow)"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their location"""
    for item in items:
        # Mark all tests in test_integration.py as integration tests
        if "test_integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        else:
            # All other tests are unit tests
            item.add_marker(pytest.mark.unit)


# Custom fixtures for specific test scenarios
@pytest.fixture
def mock_zip_response():
    """Mock ZIP file response for testing data downloads"""
    import io
    import zipfile
    import json
    
    def _create_zip_response(data):
        # Create in-memory ZIP file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            zf.writestr('data.json', json.dumps(data))
        
        response = Mock()
        response.raise_for_status.return_value = None
        response.content = zip_buffer.getvalue()
        return response
    
    return _create_zip_response


@pytest.fixture(autouse=True)
def suppress_warnings():
    """Suppress specific warnings during testing"""
    import warnings
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=DeprecationWarning)


# Performance testing fixtures
@pytest.fixture
def large_dataset():
    """Generate large dataset for performance testing"""
    import datetime
    
    data = []
    base_date = datetime.datetime(2023, 1, 1)
    
    for i in range(10000):  # 10k records
        data.append({
            "timestamp": (base_date + datetime.timedelta(hours=i)).isoformat(),
            "open": 1.0 + (i % 100) * 0.0001,
            "high": 1.0 + (i % 100) * 0.0001 + 0.002,
            "low": 1.0 + (i % 100) * 0.0001 - 0.001,
            "close": 1.0 + (i % 100) * 0.0001 + 0.0005,
            "volume": 1000 + (i % 500)
        })
    
    return data 