# 🎵 Statify - Spotify Music Analytics

A comprehensive web application that analyzes your Spotify listening habits and provides insights into your unique music taste.

## ✨ Features

- **Spotify OAuth Integration** - Secure authentication with your Spotify account
- **Music Taste Analysis** - Deep dive into your listening patterns and preferences
- **Uniqueness Scoring** - Discover how unique your music taste is compared to others
- **Genre Diversity Analysis** - Explore your musical palette across different genres
- **Obscurity Metrics** - See how mainstream or underground your music taste is
- **Historical Tracking** - Keep track of how your music taste evolves over time
- **Interactive Dashboard** - Beautiful, responsive interface to explore your data
- **Data Persistence** - All your analyses are saved and can be compared over time

## 🏗️ Architecture

- **Frontend**: React 19 with Vite for fast development and modern UI
- **Backend**: FastAPI with Python for robust API development
- **Database**: PostgreSQL for reliable data persistence
- **Authentication**: Spotify OAuth 2.0 with secure token management
- **Deployment**: Docker-ready with PostgreSQL and pgAdmin containers

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- Spotify Developer Account

### 1. Clone and Setup

```bash
git clone <repository-url>
cd statify
```

### 2. Environment Configuration

Create a `.env` file in the root directory:

```env
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
DATABASE_URL=postgresql://statify_user:statify_password@localhost:5432/statify
ENCRYPTION_KEY=your_32_byte_encryption_key  # Optional, auto-generated if not set
```

### 3. Database Setup

Start the PostgreSQL database:

```bash
docker-compose up -d postgres
```

Optional: Start pgAdmin for database management:

```bash
docker-compose up -d  # Includes pgAdmin at http://localhost:5050
```

### 4. Backend Setup

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI backend:

```bash
python main.py
# or
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Frontend Setup

Install and start the React frontend:

```bash
cd frontend
npm install
npm run dev
```

### 6. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **pgAdmin** (optional): http://localhost:5050
- **API Docs**: http://localhost:8000/docs

## 🔧 Configuration

### Spotify App Setup

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new app
3. Add redirect URI: `http://127.0.0.1:8000/callback`
4. Copy Client ID and Secret to your `.env` file

### Database Configuration

The app uses PostgreSQL with the following default configuration:
- **Host**: localhost:5432
- **Database**: statify
- **User**: statify_user
- **Password**: statify_password

## 📊 API Endpoints

### Authentication
- `GET /login` - Initiate Spotify OAuth flow
- `GET /callback` - Handle OAuth callback
- `GET /validate-token` - Validate access token
- `POST /refresh-token` - Refresh expired tokens

### Analytics
- `GET /user/analysis` - Get comprehensive music analysis
- `GET /user/analysis-history` - Get historical analysis data
- `GET /user/top-artists` - Get top artists
- `GET /user/top-tracks` - Get top tracks
- `GET /user/recent-tracks` - Get recently played tracks

## 📁 Project Structure

```
statify/
├── main.py                 # FastAPI application entry point
├── spotify_client.py       # Spotify Web API client
├── data_processor.py       # Music data analysis logic
├── database.py            # Database connection and session management
├── models.py              # SQLAlchemy database models
├── db_service.py          # Database service layer
├── requirements.txt       # Python dependencies
├── docker-compose.yaml    # Docker services configuration
├── init.sql              # Database initialization script
├── .env                  # Environment variables (create this)
├── frontend/             # React frontend application
│   ├── src/
│   │   ├── App.jsx       # Main application component
│   │   └── App.css       # Application styles
│   ├── package.json      # Frontend dependencies
│   └── vite.config.js    # Vite configuration
└── README.md             # This file
```

## 🔒 Security Features

- **Token Encryption**: Access and refresh tokens are encrypted before database storage
- **Secure Sessions**: Persistent login with automatic token refresh
- **CORS Protection**: Configured for specific frontend origins
- **Environment Isolation**: Sensitive data stored in environment variables

## 🚀 Development

### Backend Development

```bash
# Start with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests
python test_db.py

# Check code quality
pip install black isort flake8
black . && isort . && flake8 .
```

### Frontend Development

```bash
cd frontend

# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

### Database Management

```bash
# Start database only
docker-compose up -d postgres

# View logs
docker-compose logs postgres

# Access database directly
docker exec -it statify_postgres psql -U statify_user -d statify

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

## 📈 Analytics Features

### Uniqueness Score
Combines multiple factors to determine how unique your music taste is:
- Genre diversity (Shannon entropy)
- Artist popularity distribution
- Track obscurity metrics
- Listening pattern analysis

### Genre Analysis
- Comprehensive genre mapping from artist data
- Diversity scoring using information theory
- Visual representation of your musical palette

### Temporal Analysis
- Listening patterns by hour and day
- Historical trend tracking
- Music taste evolution over time

### Insights Generation
AI-powered insights about your listening habits:
- Peak listening times
- Genre preferences
- Mainstream vs. underground tendencies
- Unique characteristics of your taste

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Commit: `git commit -am 'Add feature'`
5. Push: `git push origin feature-name`
6. Create a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Spotify Web API](https://developer.spotify.com/documentation/web-api/) for providing access to music data
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent Python web framework
- [React](https://reactjs.org/) for the frontend framework
- [PostgreSQL](https://www.postgresql.org/) for reliable data storage

## 📞 Support

If you encounter any issues or have questions:

1. Check the [API Documentation](http://localhost:8000/docs) when the server is running
2. Review the logs in the terminal where you started the servers
3. Ensure all environment variables are properly set
4. Verify that the database is running: `docker-compose ps`

---

**Made with ❤️ for music lovers who want to understand their unique taste**