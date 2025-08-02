"""
Tests for quantdle.client module
"""

import pytest
import requests
from unittest.mock import Mock, patch
from quantdle.client import Client


class TestClient:
    """Test cases for Client class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.client = Client(api_key="test_api_key", api_key_id="test_api_key_id", host="https://api.test.com")
    
    def test_init_default_host(self):
        """Test Client initialization with default host"""
        client = Client(api_key="test_key", api_key_id="test_key_id")
        assert client.api_key == "test_key"
        assert client.api_key_id == "test_key_id"
        assert client._Client__host == "https://hist.quantdle.com/v1"
        assert isinstance(client._Client__session, requests.Session)
        assert client._Client__session.headers['x-api-key'] == 'test_key'
    
    def test_init_custom_host(self):
        """Test Client initialization with custom host"""
        client = Client(api_key="test_key", api_key_id="test_key_id", host="https://custom.api.com")
        assert client._Client__host == "https://custom.api.com"
    
    def test_init_session_headers(self):
        """Test that session is properly configured with headers"""
        client = Client(api_key="test_key", api_key_id="test_key_id")
        assert 'x-api-key' in client._Client__session.headers
        assert client._Client__session.headers['x-api-key'] == 'test_key'
        assert 'x-api-key-id' in client._Client__session.headers
        assert client._Client__session.headers['x-api-key-id'] == 'test_key_id'
    
    def test_symbols_api_initialization(self):
        """Test that SymbolsAPI is properly initialized"""
        assert hasattr(self.client, '_Client__symbols_api')
        assert self.client._Client__symbols_api._SymbolsAPI__session == self.client._Client__session
        assert self.client._Client__symbols_api._SymbolsAPI__host == self.client._Client__host
    
    def test_data_downloader_initialization(self):
        """Test that DataDownloader is properly initialized"""
        assert hasattr(self.client, '_Client__data_downloader')
        assert self.client._Client__data_downloader._DataDownloader__session == self.client._Client__session
        assert self.client._Client__data_downloader._DataDownloader__host == self.client._Client__host
    
    def test_get_available_symbols_delegation(self):
        """Test that get_available_symbols delegates to SymbolsAPI"""
        expected_symbols = ["EURUSD", "GBPUSD", "USDJPY"]
        
        with patch.object(self.client._Client__symbols_api, 'get_available_symbols') as mock_method:
            mock_method.return_value = expected_symbols
            
            result = self.client.get_available_symbols()
            
            mock_method.assert_called_once_with()
            assert result == expected_symbols
    
    def test_get_symbol_info_delegation(self):
        """Test that get_symbol_info delegates to SymbolsAPI"""
        expected_info = {
            "symbol": "EURUSD",
            "available_from": "2004-01-01",
            "available_to": "2025-06-30"
        }
        
        with patch.object(self.client._Client__symbols_api, 'get_symbol_info') as mock_method:
            mock_method.return_value = expected_info
            
            result = self.client.get_symbol_info("EURUSD")
            
            mock_method.assert_called_once_with("EURUSD")
            assert result == expected_info
    
    def test_download_data_delegation(self):
        """Test that download_data delegates to DataDownloader"""
        import pandas as pd
        expected_df = pd.DataFrame({
            'timestamp': ['2023-01-01'],
            'open': [1.0],
            'high': [1.1],
            'low': [0.9],
            'close': [1.05],
            'volume': [100]
        })
        
        with patch.object(self.client._Client__data_downloader, '_download_data') as mock_method:
            mock_method.return_value = expected_df
            
            result = self.client.download_data(
                "EURUSD", "H1", "2023-01-01", "2023-01-02"
            )
            
            mock_method.assert_called_once_with(
                symbol="EURUSD", 
                timeframe="H1", 
                start_date="2023-01-01", 
                end_date="2023-01-02",
                output_format="pandas", 
                max_workers=4, 
                show_progress=True
            )
            assert result.equals(expected_df)
    
    def test_download_data_custom_parameters(self):
        """Test download_data with custom parameters"""
        import pandas as pd
        expected_df = pd.DataFrame()
        
        with patch.object(self.client._Client__data_downloader, '_download_data') as mock_method:
            mock_method.return_value = expected_df
            
            result = self.client.download_data(
                "EURUSD", "D1", "2020-01-01", "2023-01-01",
                max_workers=5, show_progress=False, output_format="polars"
            )
            
            mock_method.assert_called_once_with(
                symbol="EURUSD", 
                timeframe="D1", 
                start_date="2020-01-01", 
                end_date="2023-01-01",
                output_format="polars", 
                max_workers=5, 
                show_progress=False
            )
    
    def test_symbols_api_property(self):
        """Test symbols_api property access"""
        symbols_api = self.client._Client__symbols_api
        assert symbols_api == self.client._Client__symbols_api
    
    def test_data_downloader_property(self):
        """Test data_downloader property access"""
        data_downloader = self.client._Client__data_downloader
        assert data_downloader == self.client._Client__data_downloader
    
    def test_context_manager_protocol(self):
        """Test that Client can be used as context manager"""
        with Client(api_key="test_key", api_key_id="test_key_id") as client:
            assert isinstance(client, Client)
            assert hasattr(client._Client__session, 'close')
    
    def test_session_close_on_exit(self):
        """Test that session is closed when exiting context manager"""
        client = Client(api_key="test_key", api_key_id="test_key_id")
        
        with patch.object(client._Client__session, 'close') as mock_close:
            with client:
                pass
            mock_close.assert_called_once()
    
    def test_str_representation(self):
        """Test string representation of Client"""
        client_str = str(self.client)
        assert "Client" in client_str
    
    def test_repr_representation(self):
        """Test repr representation of Client"""
        client_repr = repr(self.client)
        assert "Client" in client_repr


class TestClientIntegration:
    """Integration tests for Client"""
    
    def test_end_to_end_workflow(self):
        """Test a complete workflow using mocked responses"""
        client = Client(api_key="test_key", api_key_id="test_key_id", host="https://api.test.com")
        
        # Mock symbols API
        expected_symbols = ["EURUSD", "GBPUSD"]
        expected_info = {
            "symbol": "EURUSD",
            "available_from": "2004-01-01",
            "available_to": "2025-06-30"
        }
        
        # Mock data download
        import pandas as pd
        expected_df = pd.DataFrame({
            'timestamp': pd.to_datetime(['2023-01-01']),
            'open': [1.0],
            'high': [1.1],
            'low': [0.9],
            'close': [1.05],
            'volume': [100]
        })
        
        with patch.object(client._Client__symbols_api, 'get_available_symbols') as mock_symbols, \
             patch.object(client._Client__symbols_api, 'get_symbol_info') as mock_info, \
             patch.object(client._Client__data_downloader, '_download_data') as mock_download:
            
            mock_symbols.return_value = expected_symbols
            mock_info.return_value = expected_info
            mock_download.return_value = expected_df
            
            # Test complete workflow
            symbols = client.get_available_symbols()
            assert symbols == expected_symbols
            
            symbol_info = client.get_symbol_info("EURUSD")
            assert symbol_info == expected_info
            
            data = client.download_data("EURUSD", "H1", "2023-01-01", "2023-01-02")
            assert data.equals(expected_df)
    
    def test_error_propagation(self):
        """Test that errors from underlying modules are properly propagated"""
        client = Client(api_key="test_key", api_key_id="test_key_id")
        
        # Test symbols API error propagation
        with patch.object(client._Client__symbols_api, 'get_available_symbols') as mock_symbols:
            mock_symbols.side_effect = Exception("API Error")
            
            with pytest.raises(Exception) as exc_info:
                client.get_available_symbols()
            
            assert "API Error" in str(exc_info.value)
        
        # Test data downloader error propagation
        with patch.object(client._Client__data_downloader, '_download_data') as mock_download:
            mock_download.side_effect = Exception("Download Error")
            
            with pytest.raises(Exception) as exc_info:
                client.download_data("EURUSD", "H1", "2023-01-01", "2023-01-02")
            
            assert "Download Error" in str(exc_info.value)
    
    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires test API credentials")
    def test_real_api_integration(self):
        """Test with real API (requires test credentials)"""
        client = Client(api_key="real_test_key", api_key_id="real_test_key_id", host="https://test-api.quantdle.com")
        
        # Test real API calls
        symbols = client.get_available_symbols()
        assert isinstance(symbols, list)
        
        if symbols:
            info = client.get_symbol_info(symbols[0])
            assert "symbol" in info
            assert "available_from" in info
            assert "available_to" in info
            
            # Small data download test
            df = client.download_data(
                symbols[0], "D1", "2023-01-01", "2023-01-05",
                show_progress=False
            )
            assert hasattr(df, 'columns')  # Works for both pandas and polars 