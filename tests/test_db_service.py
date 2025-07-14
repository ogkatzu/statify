import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from db_service import DatabaseService
from models import User, UserToken, UserAnalysis


class TestDatabaseService:
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database session"""
        return Mock(spec=Session)
    
    @pytest.fixture
    def db_service(self, mock_db):
        """Create a DatabaseService instance with mock database"""
        return DatabaseService(mock_db)
    
    @pytest.fixture
    def sample_spotify_user_data(self):
        """Sample Spotify user data for testing"""
        return {
            "id": "spotify_user_123",
            "display_name": "Test User",
            "email": "test@example.com",
            "images": [{"url": "http://example.com/avatar.jpg"}],
            "country": "US",
            "followers": {"total": 150},
            "product": "premium"
        }
    
    def test_init(self, mock_db, db_service):
        """Test DatabaseService initialization"""
        assert db_service.db == mock_db
    
    @patch('db_service.fernet')
    def test_encrypt_token(self, mock_fernet, db_service):
        """Test token encryption"""
        mock_fernet.encrypt.return_value = b"encrypted_token"
        
        result = db_service.encrypt_token("test_token")
        
        assert result == "encrypted_token"
        mock_fernet.encrypt.assert_called_once_with("test_token".encode())
    
    @patch('db_service.fernet')
    def test_decrypt_token(self, mock_fernet, db_service):
        """Test token decryption"""
        mock_fernet.decrypt.return_value = b"decrypted_token"
        
        result = db_service.decrypt_token("encrypted_token")
        
        assert result == "decrypted_token"
        mock_fernet.decrypt.assert_called_once_with("encrypted_token".encode())
    
    def test_get_or_create_user_existing(self, mock_db, db_service, sample_spotify_user_data):
        """Test getting existing user"""
        # Mock existing user
        existing_user = Mock(spec=User)
        existing_user.last_login_at = datetime.utcnow()
        mock_db.query.return_value.filter.return_value.first.return_value = existing_user
        
        result = db_service.get_or_create_user(sample_spotify_user_data)
        
        assert result == existing_user
        mock_db.query.assert_called_once_with(User)
        mock_db.commit.assert_called_once()
        # User should not be added since it already exists
        mock_db.add.assert_not_called()
    
    def test_get_or_create_user_new(self, mock_db, db_service, sample_spotify_user_data):
        """Test creating new user"""
        # Mock no existing user
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = db_service.get_or_create_user(sample_spotify_user_data)
        
        # Should create and add new user
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called()
        mock_db.refresh.assert_called_once()
        assert isinstance(result, User)
    
    def test_get_or_create_user_minimal_data(self, mock_db, db_service):
        """Test creating user with minimal data"""
        minimal_data = {"id": "user123"}
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = db_service.get_or_create_user(minimal_data)
        
        mock_db.add.assert_called_once()
        assert isinstance(result, User)
    
    def test_store_user_tokens(self, mock_db, db_service):
        """Test storing user tokens"""
        user_id = "test_user_123"
        
        # Mock delete query for existing tokens
        mock_db.query.return_value.filter.return_value.delete.return_value = 0
        
        with patch.object(db_service, 'encrypt_token', return_value="encrypted_access"):
            db_service.store_user_tokens(
                user_id, 
                "access_token", 
                "refresh_token", 
                expires_in=3600
            )
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    def test_store_user_tokens_delete_existing(self, mock_db, db_service):
        """Test that existing tokens are deleted before storing new ones"""
        user_id = "test_user_123"
        
        # Mock delete query for existing tokens
        mock_db.query.return_value.filter.return_value.delete.return_value = 1
        
        with patch.object(db_service, 'encrypt_token', return_value="encrypted_token"):
            db_service.store_user_tokens(
                user_id,
                "new_access_token",
                "new_refresh_token",
                expires_in=3600
            )
        
        # Should delete existing and add new
        mock_db.query.return_value.filter.return_value.delete.assert_called_once()
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    def test_get_user_tokens(self, mock_db, db_service):
        """Test retrieving user tokens"""
        user_id = "test_user_123"
        mock_token = Mock(spec=UserToken)
        mock_token.access_token = "encrypted_access"
        mock_token.refresh_token = "encrypted_refresh"
        mock_token.expires_at = datetime.utcnow() + timedelta(hours=1)
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_token
        
        result = db_service.get_user_tokens(user_id)
        
        assert result == mock_token
        mock_db.query.assert_called_once_with(UserToken)
    
    def test_get_user_tokens_not_found(self, mock_db, db_service):
        """Test retrieving tokens when none exist"""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = db_service.get_user_tokens("nonexistent_user")
        
        assert result is None
    
    def test_store_analysis(self, mock_db, db_service):
        """Test storing analysis results"""
        user_id = "test_user_123"
        
        analysis_data = {
            "uniqueness_score": {"uniqueness_score": 0.75, "rating": "Very Unique"},
            "obscurity_score": {"obscurity_score": 0.6},
            "genre_diversity": {"shannon_entropy": 0.8, "unique_genres": 10}
        }
        
        # Mock refresh method
        mock_db.refresh = Mock()
        
        result = db_service.store_analysis(user_id, analysis_data)
        
        mock_db.add.assert_called()
        mock_db.commit.assert_called()
        assert isinstance(result, UserAnalysis)
    
    def test_get_user_analysis_history(self, mock_db, db_service):
        """Test retrieving user analysis history"""
        user_id = 1
        mock_analyses = [Mock(spec=UserAnalysis), Mock(spec=UserAnalysis)]
        mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = mock_analyses
        
        result = db_service.get_user_analysis_history(user_id, limit=10)
        
        assert result == mock_analyses
        mock_db.query.assert_called_once_with(UserAnalysis)
    
    def test_get_user_analysis_history_default_limit(self, mock_db, db_service):
        """Test retrieving analysis history with default limit"""
        user_id = "test_user_123"
        mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
        
        result = db_service.get_user_analysis_history(user_id)
        
        # Should use default limit of 10
        mock_db.query.return_value.filter.return_value.order_by.return_value.limit.assert_called_with(10)
    
    def test_is_token_valid_true(self, mock_db, db_service):
        """Test token validation when token is valid"""
        user_id = "test_user_123"
        mock_token = Mock(spec=UserToken)
        mock_token.expires_at = datetime.utcnow() + timedelta(hours=1)
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_token
        
        result = db_service.is_token_valid(user_id)
        
        assert result is True
    
    def test_is_token_valid_false(self, mock_db, db_service):
        """Test token validation when token is expired"""
        user_id = "test_user_123"
        mock_token = Mock(spec=UserToken)
        mock_token.expires_at = datetime.utcnow() - timedelta(hours=1)
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_token
        
        result = db_service.is_token_valid(user_id)
        
        assert result is False
    
    def test_get_user_latest_analysis(self, mock_db, db_service):
        """Test retrieving user's latest analysis"""
        user_id = "test_user_123"
        mock_analysis = Mock(spec=UserAnalysis)
        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = mock_analysis
        
        result = db_service.get_user_latest_analysis(user_id)
        
        assert result == mock_analysis
        mock_db.query.assert_called_once_with(UserAnalysis)
    
    def test_get_user_latest_analysis_not_found(self, mock_db, db_service):
        """Test retrieving latest analysis when none exists"""
        user_id = "test_user_123"
        mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None
        
        result = db_service.get_user_latest_analysis(user_id)
        
        assert result is None
    
    def test_store_top_items_private_method(self, mock_db, db_service):
        """Test the private _store_top_items method"""
        analysis_id = 1
        user_id = "test_user_123"
        analysis_data = {
            "top_artists": {
                "short_term": [{"id": "artist1", "name": "Artist 1", "popularity": 80}]
            },
            "top_tracks": {
                "short_term": [{"id": "track1", "name": "Track 1", "artists": [{"name": "Artist 1"}]}]
            }
        }
        
        db_service._store_top_items(analysis_id, user_id, analysis_data)
        
        # Should add records for both artist and track
        assert mock_db.add.call_count >= 2
        mock_db.commit.assert_called_once()
    
    def test_encrypt_decrypt_token_integration(self, mock_db, db_service):
        """Test token encryption and decryption work together"""
        original_token = "test_access_token_123"
        
        encrypted = db_service.encrypt_token(original_token)
        decrypted = db_service.decrypt_token(encrypted)
        
        assert decrypted == original_token
        assert encrypted != original_token
    
    def test_database_error_handling(self, mock_db, db_service, sample_spotify_user_data):
        """Test handling of database errors"""
        # Mock database error
        mock_db.commit.side_effect = Exception("Database error")
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Should handle the error gracefully
        with pytest.raises(Exception):
            db_service.get_or_create_user(sample_spotify_user_data)
    
    def test_token_expiry_check_no_token(self, mock_db, db_service):
        """Test token validity check when no token exists"""
        user_id = "test_user_123"
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = db_service.is_token_valid(user_id)
        
        assert result is False
    
    @patch('db_service.datetime')
    def test_store_analysis_with_timestamp(self, mock_datetime, mock_db, db_service):
        """Test that analysis is stored with correct timestamp"""
        fixed_time = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.utcnow.return_value = fixed_time
        
        user_id = "test_user_123"
        analysis_data = {"uniqueness_score": {"uniqueness_score": 0.8}}
        
        # Mock refresh method
        mock_db.refresh = Mock()
        
        result = db_service.store_analysis(user_id, analysis_data)
        
        # Check that analysis_date is set correctly
        call_args = mock_db.add.call_args[0][0]
        assert call_args.analysis_date == fixed_time