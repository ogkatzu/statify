import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
import time
from spotify_client import SpotifyClient


class TestSpotifyClient:
    
    @pytest.fixture
    def client(self):
        """Create a SpotifyClient instance for testing"""
        return SpotifyClient("test_access_token")
    
    def test_init(self, client):
        """Test SpotifyClient initialization"""
        assert client.access_token == "test_access_token"
        assert client.base_url == "https://api.spotify.com/v1"
        assert client.headers == {"Authorization": "Bearer test_access_token"}
    
    @patch('spotify_client.requests.get')
    def test_make_request_success(self, mock_get, client):
        """Test successful API request"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "data"}
        mock_get.return_value = mock_response
        
        result = client._make_request("me")
        
        assert result == {"test": "data"}
        mock_get.assert_called_once_with(
            "https://api.spotify.com/v1/me",
            headers={"Authorization": "Bearer test_access_token"},
            params=None
        )
    
    @patch('spotify_client.requests.get')
    def test_make_request_with_params(self, mock_get, client):
        """Test API request with parameters"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_get.return_value = mock_response
        
        params = {"limit": 10, "time_range": "short_term"}
        result = client._make_request("me/top/artists", params)
        
        assert result == {"items": []}
        mock_get.assert_called_once_with(
            "https://api.spotify.com/v1/me/top/artists",
            headers={"Authorization": "Bearer test_access_token"},
            params=params
        )
    
    @patch('spotify_client.time.sleep')
    @patch('spotify_client.requests.get')
    def test_make_request_rate_limit_retry(self, mock_get, mock_sleep, client):
        """Test rate limit handling with retry"""
        # First call returns 429, second call succeeds
        rate_limit_response = Mock()
        rate_limit_response.status_code = 429
        rate_limit_response.headers = {"Retry-After": "2"}
        rate_limit_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        
        success_response = Mock()
        success_response.status_code = 200
        success_response.json.return_value = {"success": True}
        
        mock_get.side_effect = [rate_limit_response, success_response]
        
        result = client._make_request("me")
        
        assert result == {"success": True}
        assert mock_get.call_count == 2
        mock_sleep.assert_called_once_with(2)
    
    @patch('spotify_client.requests.get')
    def test_make_request_http_error(self, mock_get, client):
        """Test handling of HTTP errors (non-429)"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_get.return_value = mock_response
        
        with pytest.raises(requests.exceptions.HTTPError):
            client._make_request("me")
    
    @patch.object(SpotifyClient, '_make_request')
    def test_get_user_profile(self, mock_make_request, client):
        """Test get_user_profile method"""
        expected_data = {"id": "user123", "display_name": "Test User"}
        mock_make_request.return_value = expected_data
        
        result = client.get_user_profile()
        
        assert result == expected_data
        mock_make_request.assert_called_once_with("me")
    
    @patch.object(SpotifyClient, '_make_request')
    def test_get_top_artists_default_params(self, mock_make_request, client):
        """Test get_top_artists with default parameters"""
        expected_data = {"items": [{"id": "artist1", "name": "Artist 1"}]}
        mock_make_request.return_value = expected_data
        
        result = client.get_top_artists()
        
        assert result == [{"id": "artist1", "name": "Artist 1"}]
        mock_make_request.assert_called_once_with(
            "me/top/artists", 
            {"time_range": "medium_term", "limit": 50}
        )
    
    @patch.object(SpotifyClient, '_make_request')
    def test_get_top_artists_custom_params(self, mock_make_request, client):
        """Test get_top_artists with custom parameters"""
        expected_data = {"items": [{"id": "artist1", "name": "Artist 1"}]}
        mock_make_request.return_value = expected_data
        
        result = client.get_top_artists(time_range="short_term", limit=20)
        
        assert result == [{"id": "artist1", "name": "Artist 1"}]
        mock_make_request.assert_called_once_with(
            "me/top/artists", 
            {"time_range": "short_term", "limit": 20}
        )
    
    @patch.object(SpotifyClient, '_make_request')
    def test_get_top_tracks_default_params(self, mock_make_request, client):
        """Test get_top_tracks with default parameters"""
        expected_data = {"items": [{"id": "track1", "name": "Track 1"}]}
        mock_make_request.return_value = expected_data
        
        result = client.get_top_tracks()
        
        assert result == [{"id": "track1", "name": "Track 1"}]
        mock_make_request.assert_called_once_with(
            "me/top/tracks", 
            {"time_range": "medium_term", "limit": 50}
        )
    
    @patch.object(SpotifyClient, '_make_request')
    def test_get_top_tracks_custom_params(self, mock_make_request, client):
        """Test get_top_tracks with custom parameters"""
        expected_data = {"items": [{"id": "track1", "name": "Track 1"}]}
        mock_make_request.return_value = expected_data
        
        result = client.get_top_tracks(time_range="long_term", limit=10)
        
        assert result == [{"id": "track1", "name": "Track 1"}]
        mock_make_request.assert_called_once_with(
            "me/top/tracks", 
            {"time_range": "long_term", "limit": 10}
        )
    
    @patch.object(SpotifyClient, '_make_request')
    def test_get_recently_played_default_params(self, mock_make_request, client):
        """Test get_recently_played with default parameters"""
        expected_data = {"items": [{"track": {"id": "track1"}, "played_at": "2024-01-01T12:00:00Z"}]}
        mock_make_request.return_value = expected_data
        
        result = client.get_recently_played()
        
        assert result == [{"track": {"id": "track1"}, "played_at": "2024-01-01T12:00:00Z"}]
        mock_make_request.assert_called_once_with(
            "me/player/recently-played", 
            {"limit": 50}
        )
    
    @patch.object(SpotifyClient, '_make_request')
    def test_get_recently_played_custom_params(self, mock_make_request, client):
        """Test get_recently_played with custom parameters"""
        expected_data = {"items": []}
        mock_make_request.return_value = expected_data
        
        result = client.get_recently_played(limit=25, after=1640995200000)
        
        assert result == []
        mock_make_request.assert_called_once_with(
            "me/player/recently-played", 
            {"limit": 25, "after": 1640995200000}
        )
    
    @patch.object(SpotifyClient, '_make_request')
    def test_empty_response_handling(self, mock_make_request, client):
        """Test handling of empty responses"""
        mock_make_request.return_value = {}
        
        # Test methods that use .get("items", [])
        assert client.get_top_artists() == []
        assert client.get_top_tracks() == []
        assert client.get_recently_played() == []
    
    def test_headers_format(self, client):
        """Test that authorization headers are properly formatted"""
        expected_headers = {"Authorization": "Bearer test_access_token"}
        assert client.headers == expected_headers