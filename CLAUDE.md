# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Database Setup
- **Start database**: `docker-compose up -d postgres` (starts PostgreSQL)
- **Start with pgAdmin**: `docker-compose up -d` (includes database admin interface)
- **Install Python dependencies**: `pip install -r requirements.txt`

### Backend (FastAPI)
- **Start development server**: `python main.py` or `uvicorn main:app --reload --host 0.0.0.0 --port 8000`
- **Install dependencies**: `pip install -r requirements.txt`

### Frontend (React + Vite)
- **Start development server**: `cd frontend && npm run dev` (runs on http://localhost:5173)
- **Build for production**: `cd frontend && npm run build`
- **Lint code**: `cd frontend && npm run lint`
- **Preview production build**: `cd frontend && npm run preview`
- **Install dependencies**: `cd frontend && npm install`

### Environment Setup
- Create `.env` file in root with:
  - `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET`
  - `DATABASE_URL=postgresql://statify_user:statify_password@localhost:5432/statify`
  - `ENCRYPTION_KEY` for token encryption (optional, auto-generated if not set)
- Backend runs on port 8000, frontend on port 5173
- Database runs on port 5432, pgAdmin on port 5050
- OAuth callback configured for `http://127.0.0.1:8000/callback`

## Architecture Overview

This is a **Spotify music analytics application** with a Python FastAPI backend and React frontend.

### Backend Structure
- **main.py**: FastAPI application with OAuth flow and comprehensive analysis endpoint
- **spotify_client.py**: `SpotifyClient` class handling all Spotify Web API interactions with rate limiting  
- **data_processor.py**: `SpotifyDataProcessor` class for analyzing user music data and generating insights
- **database.py**: Database connection and session management
- **models.py**: SQLAlchemy database models for users, tokens, analyses, and trends
- **db_service.py**: Database service layer for user management and data persistence

### Key Features
- **OAuth Integration**: Spotify OAuth 2.0 flow with automatic token handling and database persistence
- **Comprehensive Analysis**: `/user/analysis` endpoint provides full music taste analysis including:
  - Listening history patterns (by hour/day)
  - Top artists/tracks across different time ranges
  - Genre diversity analysis using Shannon entropy
  - Obscurity scoring based on popularity metrics
  - Uniqueness scoring combining multiple factors
  - Generated insights and personalized recommendations
- **Data Persistence**: User profiles, tokens, and analysis results stored in PostgreSQL
- **Analysis History**: Track user's music taste evolution over time
- **Secure Token Storage**: Encrypted token storage for enhanced security

### Data Processing Pipeline
1. **SpotifyClient** fetches data from Spotify API (top artists, tracks, recent listening history)
2. **SpotifyDataProcessor** analyzes patterns, calculates metrics, and generates insights
3. **DatabaseService** stores user data, tokens, and analysis results in PostgreSQL
4. **Frontend** visualizes data with interactive charts and detailed breakdowns

### Frontend Components
- **App.jsx**: Main application with OAuth handling, loading states, and dashboard
- **Dashboard component**: Comprehensive music analytics visualization including:
  - Circular progress indicator for uniqueness score
  - Stats overview tiles
  - Top artists/tracks grids with images and popularity indicators
  - Genre bubble visualization
  - Categorized insights with icons

### Important Notes
- **Audio Features Deprecated**: Spotify deprecated audio features endpoint (Nov 27, 2024). Code handles this gracefully with fallback analysis using track metadata
- **Rate Limiting**: SpotifyClient includes automatic retry logic for rate-limited requests
- **CORS Configuration**: Backend configured for localhost:5173 frontend development
- **Responsive Design**: Frontend uses CSS Grid and Flexbox for responsive layouts

### API Endpoints
- `GET /login`: Initiates Spotify OAuth flow
- `GET /callback`: Handles OAuth callback, stores user/tokens in DB, redirects to frontend
- `GET /validate-token`: Validates if access token is still valid
- `POST /refresh-token`: Refreshes expired access tokens
- `GET /user/analysis`: Main endpoint for comprehensive music analysis (stores results in DB)
- `GET /user/analysis-history`: Retrieves user's historical analysis data
- `GET /user/top-artists`, `/user/top-tracks`, `/user/recent-tracks`: Individual data endpoints

### Dependencies
- **Backend**: FastAPI, uvicorn, requests, python-dotenv, SQLAlchemy, psycopg2-binary, cryptography
- **Frontend**: React 19, Vite, recharts (for potential future chart enhancements)
- **Database**: PostgreSQL 15, pgAdmin 4 (via Docker)