# Unit Tests for Spotify Stats API

This directory contains comprehensive unit tests for the backend components of the Spotify Stats API.

## Test Structure

- `conftest.py` - Pytest configuration and fixtures
- `test_spotify_client.py` - Tests for SpotifyClient class ✅
- `test_data_processor.py` - Tests for SpotifyDataProcessor class 
- `test_db_service.py` - Tests for DatabaseService class
- `test_main.py` - Tests for FastAPI endpoints

## Running Tests

### Quick Test Run (Working Tests Only)
```bash
python test_runner.py
```

### All Tests
```bash
python -m pytest tests/ -v
```

### Specific Test File
```bash
python -m pytest tests/test_spotify_client.py -v
```

### With Coverage Report
```bash
python -m pytest tests/ --cov=. --cov-report=html
```

## Test Coverage

✅ **All 71 tests passing** with **69% overall coverage**:

- ✅ **SpotifyClient**: 14 tests, 57% line coverage
  - API request handling, rate limiting, authentication, data retrieval, error handling

- ✅ **SpotifyDataProcessor**: 20 tests, 88% line coverage  
  - Listening history analysis, genre diversity, obscurity scoring, uniqueness calculation, insights generation

- ✅ **DatabaseService**: 22 tests, 100% line coverage
  - User management, token storage/encryption, analysis persistence, database operations

- ✅ **FastAPI Endpoints**: 15 tests, 39% line coverage
  - Authentication flow, token validation, CORS, error handling, basic API functionality

## Dependencies

All test dependencies are included in `requirements.txt`:
- pytest
- pytest-asyncio
- pytest-cov
- httpx
- pytest-mock

## Test Database

Tests use SQLite in-memory database for isolation. Test environment variables are automatically configured.

## Notes

- Tests are designed to be independent and can run in any order
- Mock objects are used to avoid external API calls
- Test fixtures provide sample data for consistent testing
- Coverage reports are generated in `htmlcov/` directory