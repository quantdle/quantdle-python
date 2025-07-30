"""
Integration tests for the Quantdle client
"""

import pytest
import pandas as pd
from unittest.mock import patch, Mock

from quantdle import Client


class TestQuantdleIntegration:
    """Integration tests for the complete Quantdle system"""
    
    def test_complete_workflow(self):
        """Test the complete workflow from symbols to data download"""
        client = Client(api_key="test_key", api_key_id="test_key_id", host="https://api.test.com")
        
        # Mock complete workflow
        mock_symbols = ["EURUSD", "GBPUSD"]
        mock_info = {"symbol": "EURUSD", "available_from": "2004-01-01", "available_to": "2025-06-30"}
        mock_data = [{"date": "2023-01-01", "time": "00:00:00", "open": 1.0, "high": 1.1, "low": 0.9, "close": 1.05, "volume": 100}]
        
        with patch.object(client._Client__symbols_api, 'get_available_symbols') as mock_get_symbols, \
             patch.object(client._Client__symbols_api, 'get_symbol_info') as mock_get_info, \
             patch.object(client._Client__data_downloader, '_DataDownloader__download_chunk') as mock_download:
            
            mock_get_symbols.return_value = mock_symbols
            mock_get_info.return_value = mock_info
            mock_download.return_value = mock_data
            
            # Test complete workflow
            symbols = client.get_available_symbols()
            assert symbols == mock_symbols
            
            info = client.get_symbol_info("EURUSD")
            assert info == mock_info
            
            df = client.download_data("EURUSD", "H1", "2023-01-01", "2023-01-02", show_progress=False)
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 1 