import pytest
import os
from unittest.mock import MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from cryptography.fernet import Fernet

# Set test environment variables
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SPOTIFY_CLIENT_ID"] = "test_client_id"
os.environ["SPOTIFY_CLIENT_SECRET"] = "test_client_secret"
os.environ["FRONTEND_URL"] = "http://localhost:3000"
os.environ["BACKEND_URL"] = "http://localhost:8000"
os.environ["ENCRYPTION_KEY"] = Fernet.generate_key().decode()

from database import get_db, Base
from main import app


@pytest.fixture(scope="session")
def test_engine():
    """Create a test database engine"""
    engine = create_engine(
        "sqlite:///./test.db",
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    # Cleanup
    os.remove("./test.db") if os.path.exists("./test.db") else None


@pytest.fixture(scope="function")
def test_db(test_engine):
    """Create a test database session"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client with dependency override"""
    def override_get_db():
        try:
            yield test_db
        finally:
            test_db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def mock_spotify_response():
    """Mock Spotify API response data"""
    return {
        "user_profile": {
            "id": "test_user_123",
            "display_name": "Test User",
            "email": "test@example.com",
            "images": [{"url": "http://example.com/image.jpg"}],
            "country": "US",
            "followers": {"total": 100},
            "product": "premium"
        },
        "top_artists": {
            "items": [
                {
                    "id": "artist_1",
                    "name": "Test Artist 1",
                    "popularity": 80,
                    "genres": ["pop", "rock"],
                    "images": [{"url": "http://example.com/artist1.jpg"}],
                    "followers": {"total": 1000000}
                },
                {
                    "id": "artist_2", 
                    "name": "Test Artist 2",
                    "popularity": 75,
                    "genres": ["jazz", "blues"],
                    "images": [{"url": "http://example.com/artist2.jpg"}],
                    "followers": {"total": 500000}
                }
            ]
        },
        "top_tracks": {
            "items": [
                {
                    "id": "track_1",
                    "name": "Test Track 1",
                    "popularity": 85,
                    "duration_ms": 240000,
                    "artists": [{"id": "artist_1", "name": "Test Artist 1"}],
                    "album": {
                        "id": "album_1",
                        "name": "Test Album 1",
                        "images": [{"url": "http://example.com/album1.jpg"}]
                    }
                }
            ]
        },
        "recent_tracks": {
            "items": [
                {
                    "track": {
                        "id": "track_1",
                        "name": "Test Track 1",
                        "artists": [{"id": "artist_1", "name": "Test Artist 1"}],
                        "popularity": 85
                    },
                    "played_at": "2024-01-01T12:00:00Z"
                }
            ]
        }
    }


@pytest.fixture
def sample_listening_data():
    """Sample listening history data for testing"""
    return [
        {
            "track": {
                "id": "track_1",
                "name": "Test Track 1",
                "artists": [{"id": "artist_1", "name": "Artist 1"}],
                "popularity": 80
            },
            "played_at": "2024-01-01T12:00:00Z"
        },
        {
            "track": {
                "id": "track_2", 
                "name": "Test Track 2",
                "artists": [{"id": "artist_2", "name": "Artist 2"}],
                "popularity": 60
            },
            "played_at": "2024-01-01T14:30:00Z"
        },
        {
            "track": {
                "id": "track_1",  # Repeat track
                "name": "Test Track 1",
                "artists": [{"id": "artist_1", "name": "Artist 1"}],
                "popularity": 80
            },
            "played_at": "2024-01-01T16:15:00Z"
        }
    ]