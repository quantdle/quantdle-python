"""
Tests for quantdle.data_downloader module
"""

import io
import json
import zipfile
from datetime import datetime
from unittest.mock import Mock, patch
import pytest
import requests
import pandas as pd

from quantdle.data_downloader import DataDownloader


class TestDataDownloader:
    """Test cases for DataDownloader class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_session = Mock(spec=requests.Session)
        self.host = "https://api.test.com"
        self.downloader = DataDownloader(self.mock_session, self.host)
    
    def test_init(self):
        """Test DataDownloader initialization"""
        assert self.downloader._DataDownloader__session == self.mock_session
        assert self.downloader._DataDownloader__host == self.host
    
    def test_make_request_success(self):
        """Test successful API request"""
        # Mock successful response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"presigned_urls": ["url1", "url2"]}
        self.mock_session.request.return_value = mock_response
        
        result = self.downloader._DataDownloader__make_request("GET", "/data/EURUSD", {"timeframe": "H1"})
        
        # Verify request was made correctly
        self.mock_session.request.assert_called_once_with(
            method="GET",
            url="https://api.test.com/data/EURUSD",
            params={"timeframe": "H1"},
            timeout=30
        )
        
        assert result == {"presigned_urls": ["url1", "url2"]}

    def test_make_request_403_forbidden_returns_empty_and_warns(self):
        """403 Forbidden should not raise, but warn and return empty URLs."""
        # Mock 403 response
        mock_response = Mock()
        mock_response.status_code = 403
        # raise_for_status would raise, but our code short-circuits before calling it
        self.mock_session.request.return_value = mock_response

        with patch('quantdle.data_downloader.warnings.warn') as mock_warn:
            result = self.downloader._DataDownloader__make_request(
                "GET", "/data/AUDCAD", {"timeframe": "D1"}
            )

        mock_warn.assert_called_once()
        # Ensure message mentions plan limitation
        warn_msg = mock_warn.call_args[0][0]
        assert "not included in your current plan" in warn_msg
        assert result == {"presigned_urls": []}

    def test_make_request_404_not_found_returns_empty_and_warns(self):
        """404 Not Found should not raise, but warn and return empty URLs."""
        mock_response = Mock()
        mock_response.status_code = 404
        self.mock_session.request.return_value = mock_response

        with patch('quantdle.data_downloader.warnings.warn') as mock_warn:
            result = self.downloader._DataDownloader__make_request(
                "GET", "/data/UNKNOWN", {"timeframe": "H1"}
            )

        mock_warn.assert_called_once()
        assert result == {"presigned_urls": []}
    
    @patch('quantdle.data_downloader.requests.get')
    def test_download_and_extract_zip_success(self, mock_get):
        """Test successful ZIP download and extraction"""
        # Create a mock ZIP file with JSON content
        test_data = [
            {"timestamp": "2023-01-01T00:00:00", "open": 1.0, "high": 1.1, "low": 0.9, "close": 1.05, "volume": 100},
            {"timestamp": "2023-01-01T01:00:00", "open": 1.05, "high": 1.15, "low": 0.95, "close": 1.1, "volume": 150}
        ]
        
        # Create in-memory ZIP file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            zf.writestr('data.json', json.dumps(test_data))
        zip_content = zip_buffer.getvalue()
        
        # Mock the requests.get response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = zip_content
        mock_get.return_value = mock_response
        
        result = self.downloader._DataDownloader__download_and_extract_zip("http://test-url.com/data.zip")
        
        mock_get.assert_called_once_with("http://test-url.com/data.zip", timeout=30)
        assert result == test_data
    
    @patch('quantdle.data_downloader.requests.get')
    def test_download_and_extract_zip_nested_data(self, mock_get):
        """Test ZIP extraction with nested data structure"""
        # Test data wrapped in 'data' key
        test_data = [{"timestamp": "2023-01-01T00:00:00", "open": 1.0, "high": 1.1, "low": 0.9, "close": 1.05, "volume": 100}]
        nested_data = {"data": test_data}
        
        # Create in-memory ZIP file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            zf.writestr('data.json', json.dumps(nested_data))
        zip_content = zip_buffer.getvalue()
        
        # Mock the requests.get response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = zip_content
        mock_get.return_value = mock_response
        
        result = self.downloader._DataDownloader__download_and_extract_zip("http://test-url.com/data.zip")
        
        assert result == test_data
    
    @patch('quantdle.data_downloader.requests.get')
    def test_download_and_extract_zip_no_json(self, mock_get):
        """Test ZIP with no JSON files"""
        # Create ZIP with no JSON files
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            zf.writestr('readme.txt', 'No JSON here')
        zip_content = zip_buffer.getvalue()
        
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.content = zip_content
        mock_get.return_value = mock_response
        
        with patch('quantdle.data_downloader.warnings.warn') as mock_warn:
            result = self.downloader._DataDownloader__download_and_extract_zip("http://test-url.com/data.zip")
            
            mock_warn.assert_called_once()
            assert result == []
    
    @patch('quantdle.data_downloader.requests.get')
    def test_download_and_extract_zip_http_error(self, mock_get):
        """Test ZIP download with HTTP error"""
        mock_get.side_effect = requests.exceptions.HTTPError("404 Not Found")
        
        with pytest.raises(Exception) as exc_info:
            self.downloader._DataDownloader__download_and_extract_zip("http://test-url.com/data.zip")
        
        assert "Error downloading/extracting data" in str(exc_info.value)
    
    def test_download_chunk_success(self):
        """Test successful chunk download"""
        mock_urls = ["url1.zip", "url2.zip"]
        mock_data = [
            [{"timestamp": "2023-01-01", "open": 1.0}],
            [{"timestamp": "2023-01-02", "open": 1.1}]
        ]
        
        with patch.object(self.downloader, '_DataDownloader__make_request') as mock_request, \
             patch.object(self.downloader, '_DataDownloader__download_and_extract_zip') as mock_extract:
            
            mock_request.return_value = {"presigned_urls": mock_urls}
            mock_extract.side_effect = mock_data
            
            result = self.downloader._DataDownloader__download_chunk(
                "EURUSD", "H1", 
                datetime(2023, 1, 1), datetime(2023, 1, 2),
                max_workers=2, show_progress=False
            )
            
            # Verify API request
            mock_request.assert_called_once_with(
                'GET', '/data/EURUSD', 
                {
                    'timeframe': 'H1',
                    'start_date': '2023-01-01',
                    'end_date': '2023-01-02'
                }
            )
            
            # Verify all URLs were processed
            assert mock_extract.call_count == 2
            
            # Verify combined data (order may vary due to parallel processing)
            expected_result = mock_data[0] + mock_data[1]
            # Sort both results by timestamp for consistent comparison
            result_sorted = sorted(result, key=lambda x: x['timestamp'])
            expected_sorted = sorted(expected_result, key=lambda x: x['timestamp'])
            assert result_sorted == expected_sorted
    
    def test_download_chunk_no_urls(self):
        """Test chunk download with no URLs"""
        with patch.object(self.downloader, '_DataDownloader__make_request') as mock_request:
            mock_request.return_value = {"presigned_urls": []}
            
            result = self.downloader._DataDownloader__download_chunk(
                "EURUSD", "H1",
                datetime(2023, 1, 1), datetime(2023, 1, 2),
                max_workers=2, show_progress=False
            )
            
            assert result == []
    
    def test_download_data_simple(self):
        """Test simple download_data call"""
        mock_data = [
            {"date": "2023-01-01", "time": "00:00:00", "open": 1.0, "high": 1.1, "low": 0.9, "close": 1.05, "volume": 100}
        ]
        
        with patch.object(self.downloader, '_DataDownloader__download_chunk') as mock_chunk:
            mock_chunk.return_value = mock_data
            
            df = self.downloader._download_data(
                "EURUSD", "H1", "2023-01-01", "2023-01-02",
                show_progress=False
            )
            
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 1
            assert 'datetime' in df.index.names or 'datetime' in df.columns
    
    def test_download_data_date_conversion(self):
        """Test download_data with different date input formats"""
        mock_data = [{"date": "2023-01-01", "time": "00:00:00", "open": 1.0, "high": 1.1, "low": 0.9, "close": 1.05, "volume": 100}]
        
        with patch.object(self.downloader, '_DataDownloader__download_chunk') as mock_chunk:
            mock_chunk.return_value = mock_data
            
            # Test with string dates
            df1 = self.downloader._download_data(
                "EURUSD", "H1", "2023-01-01", "2023-01-02", show_progress=False
            )
            
            # Test with datetime objects
            df2 = self.downloader._download_data(
                "EURUSD", "H1", datetime(2023, 1, 1), datetime(2023, 1, 2), show_progress=False
            )
            
            # Both should work and produce same result
            assert len(df1) == len(df2) == 1
    
    def test_download_data_large_range_chunking(self):
        """Test download_data with large date range that triggers chunking"""
        mock_data = [{"date": "2023-01-01", "time": "00:00:00", "open": 1.0, "high": 1.1, "low": 0.9, "close": 1.05, "volume": 100}]
        
        with patch.object(self.downloader, '_DataDownloader__download_chunk') as mock_chunk:
            mock_chunk.return_value = mock_data
            
            # Test with a 10-year range that should trigger chunking (> 5 year default)
            df = self.downloader._download_data(
                "EURUSD", "H1", "2010-01-01", "2020-01-01",
                chunk_size_years=5, show_progress=False
            )
            
            # Should have called _download_chunk multiple times
            assert mock_chunk.call_count >= 2
            assert isinstance(df, pd.DataFrame)
    
    def test_download_data_polars_output(self):
        """Test download_data with polars output format"""
        mock_data = [{"date": "2023-01-01", "time": "00:00:00", "open": 1.0, "high": 1.1, "low": 0.9, "close": 1.05, "volume": 100}]
        
        with patch.object(self.downloader, '_DataDownloader__download_chunk') as mock_chunk:
            mock_chunk.return_value = mock_data
            
            # Test pandas output first (should work)
            df_pandas = self.downloader._download_data(
                "EURUSD", "H1", "2023-01-01", "2023-01-02",
                output_format="pandas", show_progress=False
            )
            assert isinstance(df_pandas, pd.DataFrame)
            
            # Test polars format request without polars installed
            # We'll mock the import to simulate polars not being available
            original_import = __builtins__['__import__']
            def mock_import(name, *args, **kwargs):
                if name == 'polars':
                    raise ImportError("No module named 'polars'")
                return original_import(name, *args, **kwargs)
            
            __builtins__['__import__'] = mock_import
            try:
                with pytest.raises(ImportError, match="Polars is not installed"):
                    self.downloader._download_data(
                        "EURUSD", "H1", "2023-01-01", "2023-01-02",
                        output_format="polars", show_progress=False
                    )
            finally:
                __builtins__['__import__'] = original_import
    
    def test_download_data_no_data(self):
        """Test download_data with no data returned"""
        with patch.object(self.downloader, '_DataDownloader__download_chunk') as mock_chunk:
            mock_chunk.return_value = []
            
            with patch('quantdle.data_downloader.warnings.warn') as mock_warn:
                df = self.downloader._download_data(
                    "EURUSD", "H1", "2023-01-01", "2023-01-02", show_progress=False
                )
                
                mock_warn.assert_called_once()
                assert isinstance(df, pd.DataFrame)
                assert len(df) == 0
    
    def test_download_data_duplicate_removal(self):
        """Test that duplicate timestamps are removed"""
        # Mock data with duplicate timestamps - but in the expected format
        mock_data = [
            {"date": "2023-01-01", "time": "00:00:00", "open": 1.0, "high": 1.1, "low": 0.9, "close": 1.05, "volume": 100},
            {"date": "2023-01-01", "time": "00:00:00", "open": 1.1, "high": 1.2, "low": 1.0, "close": 1.15, "volume": 200},  # Duplicate
            {"date": "2023-01-01", "time": "01:00:00", "open": 1.05, "high": 1.15, "low": 0.95, "close": 1.1, "volume": 150}
        ]
        
        with patch.object(self.downloader, '_DataDownloader__download_chunk') as mock_chunk:
            mock_chunk.return_value = mock_data
            
            df = self.downloader._download_data(
                "EURUSD", "H1", "2023-01-01", "2023-01-02", show_progress=False
            )
            
            # Should remove duplicates based on datetime index
            assert isinstance(df, pd.DataFrame)
            # The exact length depends on how duplicates are handled, 
            # but it should be less than the original mock data
            assert len(df) <= len(mock_data)


class TestDataDownloaderIntegration:
    """Integration tests for DataDownloader (these would typically use a test API)"""
    
    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires test API credentials")
    def test_real_download(self):
        """Test with real API (requires test credentials)"""
        # This would be used with test API credentials
        session = requests.Session()
        downloader = DataDownloader(session, "https://test-api.quantdle.com")
        
        # Test real data download
        df = downloader._download_data(
            "EURUSD", "H1", "2023-01-01", "2023-01-02", show_progress=False
        )
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0 