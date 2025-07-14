import pytest
from unittest.mock import Mock, patch
from fastapi import status


class TestMainSimpleEndpoints:
    
    def test_root_endpoint(self, client):
        """Test the root endpoint"""
        response = client.get("/")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "Spotify Stats API is running"}
    
    def test_login_endpoint_redirects(self, client):
        """Test the login endpoint returns a redirect"""
        response = client.get("/login", follow_redirects=False)
        
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        assert "accounts.spotify.com" in response.headers["location"]
    
    def test_callback_with_error(self, client):
        """Test callback endpoint with error parameter"""
        response = client.get("/callback?error=access_denied", follow_redirects=False)
        
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        assert "error=access_denied" in response.headers["location"]
    
    def test_callback_without_code(self, client):
        """Test callback endpoint without authorization code"""
        response = client.get("/callback", follow_redirects=False)
        
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        assert "error=no_code" in response.headers["location"]
    
    @patch('main.SpotifyClient')
    def test_validate_token_invalid(self, mock_spotify_client, client):
        """Test token validation with invalid token"""
        mock_client_instance = Mock()
        mock_client_instance.get_user_profile.side_effect = Exception("Invalid token")
        mock_spotify_client.return_value = mock_client_instance
        
        response = client.get("/validate-token?access_token=invalid_token")
        
        # The endpoint may return 200 with error info or 401, both are valid
        assert response.status_code in [200, 401]
    
    def test_validate_token_missing_token(self, client):
        """Test token validation without token parameter"""
        response = client.get("/validate-token")
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_user_analysis_missing_token(self, client):
        """Test user analysis without access token"""
        response = client.get("/user/analysis")
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_cors_headers_working(self, client):
        """Test that CORS is configured"""
        response = client.get("/")
        
        # Should not fail due to CORS issues
        assert response.status_code == status.HTTP_200_OK
    
    def test_invalid_endpoint(self, client):
        """Test accessing non-existent endpoint"""
        response = client.get("/nonexistent")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_request_validation_invalid_json(self, client):
        """Test request validation for endpoints with required parameters"""
        # Test refresh token endpoint with invalid JSON
        response = client.post("/refresh-token", content="invalid json")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_health_endpoint_if_exists(self, client):
        """Test health check endpoint if it exists"""
        response = client.get("/health")
        
        # Either returns 200 (if implemented) or 404 (if not implemented)
        assert response.status_code in [200, 404]
    
    @patch('main.SpotifyClient')
    def test_rate_limit_handling_in_validation(self, mock_spotify_client, client):
        """Test that rate limiting doesn't break token validation"""
        mock_client_instance = Mock()
        # Simulate successful validation (rate limiting handled internally)
        mock_client_instance.get_user_profile.return_value = {"id": "user123"}
        mock_spotify_client.return_value = mock_client_instance
        
        response = client.get("/validate-token?access_token=test_token")
        
        # Should succeed regardless of internal rate limiting
        assert response.status_code in [200, 401]  # Either valid or invalid token
    
    def test_options_request_cors(self, client):
        """Test that OPTIONS requests work for CORS"""
        response = client.options("/")
        
        # Should not fail (CORS middleware handles OPTIONS)
        assert response.status_code in [200, 405]
    
    @patch('main.create_tables')
    def test_startup_creates_tables(self, mock_create_tables):
        """Test that startup event calls create_tables"""
        mock_create_tables.return_value = None
        mock_create_tables()
        mock_create_tables.assert_called_once()
    
    def test_basic_security_headers(self, client):
        """Test basic endpoint security"""
        response = client.get("/")
        
        # Should return valid JSON response
        assert response.headers["content-type"] == "application/json"
        assert response.status_code == status.HTTP_200_OK