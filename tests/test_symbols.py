"""
Tests for quantdle.symbols module
"""

import pytest
import requests
from unittest.mock import Mock, patch
from quantdle.symbols import SymbolsAPI


class TestSymbolsAPI:
    """Test cases for SymbolsAPI class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_session = Mock(spec=requests.Session)
        self.host = "https://api.test.com"
        self.symbols_api = SymbolsAPI(self.mock_session, self.host)
    
    def test_init(self):
        """Test SymbolsAPI initialization"""
        assert self.symbols_api._SymbolsAPI__session == self.mock_session
        assert self.symbols_api._SymbolsAPI__host == self.host
    
    def test_make_request_success(self):
        """Test successful API request"""
        # Mock successful response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"test": "data"}
        self.mock_session.request.return_value = mock_response
        
        result = self.symbols_api._SymbolsAPI__make_request("GET", "/test", {"param": "value"})
        
        # Verify request was made correctly
        self.mock_session.request.assert_called_once_with(
            method="GET",
            url="https://api.test.com/test",
            params={"param": "value"},
            timeout=30
        )
        
        # Verify response
        assert result == {"test": "data"}
        mock_response.raise_for_status.assert_called_once()
        mock_response.json.assert_called_once()
    
    def test_make_request_http_error(self):
        """Test API request with HTTP error"""
        # Mock HTTP error
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        self.mock_session.request.return_value = mock_response
        
        with pytest.raises(Exception) as exc_info:
            self.symbols_api._SymbolsAPI__make_request("GET", "/test")
        
        assert "API request failed" in str(exc_info.value)
        assert "404 Not Found" in str(exc_info.value)
    
    def test_make_request_connection_error(self):
        """Test API request with connection error"""
        # Mock connection error
        self.mock_session.request.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        with pytest.raises(Exception) as exc_info:
            self.symbols_api._SymbolsAPI__make_request("GET", "/test")
        
        assert "API request failed" in str(exc_info.value)
        assert "Connection failed" in str(exc_info.value)
    
    def test_get_available_symbols_success(self):
        """Test successful get_available_symbols"""
        expected_symbols = ["EURUSD", "GBPUSD", "USDJPY"]
        
        with patch.object(self.symbols_api, '_SymbolsAPI__make_request') as mock_request:
            mock_request.return_value = {"symbols": expected_symbols}
            
            result = self.symbols_api.get_available_symbols()
            
            mock_request.assert_called_once_with('GET', '/symbols')
            assert result == expected_symbols
    
    def test_get_available_symbols_empty(self):
        """Test get_available_symbols with empty response"""
        with patch.object(self.symbols_api, '_SymbolsAPI__make_request') as mock_request:
            mock_request.return_value = {"symbols": []}
            
            result = self.symbols_api.get_available_symbols()
            
            assert result == []
    
    def test_get_symbol_info_success(self):
        """Test successful get_symbol_info"""
        expected_info = {
            "symbol": "EURUSD",
            "available_from": "2004-01-01",
            "available_to": "2025-06-30"
        }
        
        with patch.object(self.symbols_api, '_SymbolsAPI__make_request') as mock_request:
            mock_request.return_value = expected_info
            
            result = self.symbols_api.get_symbol_info("EURUSD")
            
            mock_request.assert_called_once_with('GET', '/symbols/EURUSD/range')
            assert result == expected_info
    
    def test_get_symbol_info_different_symbols(self):
        """Test get_symbol_info with different symbols"""
        symbols_to_test = ["EURUSD", "GBPUSD", "XAUUSD"]
        
        for symbol in symbols_to_test:
            with patch.object(self.symbols_api, '_SymbolsAPI__make_request') as mock_request:
                expected_info = {
                    "symbol": symbol,
                    "available_from": "2020-01-01",
                    "available_to": "2025-12-31"
                }
                mock_request.return_value = expected_info
                
                result = self.symbols_api.get_symbol_info(symbol)
                
                mock_request.assert_called_once_with('GET', f'/symbols/{symbol}/range')
                assert result == expected_info
    
    def test_get_symbol_info_api_error(self):
        """Test get_symbol_info with API error"""
        with patch.object(self.symbols_api, '_SymbolsAPI__make_request') as mock_request:
            mock_request.side_effect = Exception("API error")
            
            with pytest.raises(Exception) as exc_info:
                self.symbols_api.get_symbol_info("INVALID")
            
            assert "API error" in str(exc_info.value)


class TestSymbolsAPIIntegration:
    """Integration tests for SymbolsAPI (these would typically use a test API)"""
    
    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires test API credentials")
    def test_real_api_call(self):
        """Test with real API (requires test credentials)"""
        # This would be used with test API credentials
        session = requests.Session()
        symbols_api = SymbolsAPI(session, "https://test-api.quantdle.com")
        
        # Test real API call
        symbols = symbols_api.get_available_symbols()
        assert isinstance(symbols, list)
        
        if symbols:
            info = symbols_api.get_symbol_info(symbols[0])
            assert "symbol" in info
            assert "available_from" in info
            assert "available_to" in info 