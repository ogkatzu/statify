import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [accessToken, setAccessToken] = useState(null)
  const [userData, setUserData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // Check for access token in URL (from OAuth callback)
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search)
    const token = urlParams.get('access_token')
    if (token) {
      setAccessToken(token)
      // Clean up URL
      window.history.replaceState({}, document.title, window.location.pathname)
    }
  }, [])

  // Login with Spotify
  const handleLogin = () => {
    window.location.href = 'http://localhost:8000/login'
  }

  // Fetch user analysis
  const fetchAnalysis = async () => {
    if (!accessToken) return

    setLoading(true)
    setError(null)

    try {
      const response = await fetch(`http://localhost:8000/user/analysis?access_token=${accessToken}&days_back=30`)
      
      if (!response.ok) {
        throw new Error('Failed to fetch analysis')
      }

      const data = await response.json()
      setUserData(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // Auto-fetch analysis when we get a token
  useEffect(() => {
    if (accessToken) {
      fetchAnalysis()
    }
  }, [accessToken])

  // Login Screen
  if (!accessToken) {
    return (
      <div className="app">
        <div className="login-container">
          <h1>🎵 Spotify Stats</h1>
          <p>Discover your unique music taste</p>
          <button onClick={handleLogin} className="login-button">
            Connect with Spotify
          </button>
        </div>
      </div>
    )
  }

  // Loading Screen
  if (loading) {
    return (
      <div className="app">
        <div className="loading-container">
          <div className="spinner"></div>
          <h2>Analyzing your music taste...</h2>
          <p>This might take a moment</p>
        </div>
      </div>
    )
  }

  // Error Screen
  if (error) {
    return (
      <div className="app">
        <div className="error-container">
          <h2>Oops! Something went wrong</h2>
          <p>{error}</p>
          <button onClick={fetchAnalysis} className="retry-button">
            Try Again
          </button>
        </div>
      </div>
    )
  }

  // Dashboard Screen
  if (userData) {
    return (
      <div className="app">
        <Dashboard userData={userData} onRefresh={fetchAnalysis} />
      </div>
    )
  }

  return null
}

// Simple Dashboard Component
function Dashboard({ userData, onRefresh }) {
  const uniqueness = userData.uniqueness_score || {}
  const profile = userData.user_profile || {}
  const listeningHistory = userData.listening_history || {}
  const genreDiversity = userData.genre_diversity || {}
  const obscurityScore = userData.obscurity_score || {}

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Hi {profile.name}! 👋</h1>
        <button onClick={onRefresh} className="refresh-button">
          Refresh Data
        </button>
      </header>

      <div className="stats-grid">
        {/* Uniqueness Score */}
        <div className="stat-card highlight">
          <h3>Your Music Uniqueness</h3>
          <div className="uniqueness-score">
            <span className="score">{(uniqueness.uniqueness_score * 100).toFixed(0)}%</span>
            <span className="rating">{uniqueness.rating}</span>
          </div>
        </div>

        {/* Listening Stats */}
        <div className="stat-card">
          <h3>Listening Activity</h3>
          <div className="stats-list">
            <div className="stat-item">
              <span>Total Tracks</span>
              <span>{listeningHistory.total_tracks_played || 0}</span>
            </div>
            <div className="stat-item">
              <span>Unique Songs</span>
              <span>{listeningHistory.unique_tracks || 0}</span>
            </div>
            <div className="stat-item">
              <span>Unique Artists</span>
              <span>{listeningHistory.unique_artists || 0}</span>
            </div>
          </div>
        </div>

        {/* Genre Diversity */}
        <div className="stat-card">
          <h3>Genre Diversity</h3>
          <div className="stats-list">
            <div className="stat-item">
              <span>Diversity Score</span>
              <span>{(genreDiversity.diversity_score * 100).toFixed(0)}%</span>
            </div>
            <div className="stat-item">
              <span>Unique Genres</span>
              <span>{genreDiversity.unique_genres || 0}</span>
            </div>
          </div>
        </div>

        {/* Obscurity Score */}
        <div className="stat-card">
          <h3>Music Obscurity</h3>
          <div className="stats-list">
            <div className="stat-item">
              <span>Obscurity Score</span>
              <span>{(obscurityScore.obscurity_score * 100).toFixed(0)}%</span>
            </div>
            <div className="stat-item">
              <span>Avg Artist Popularity</span>
              <span>{obscurityScore.avg_artist_popularity?.toFixed(0) || 0}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Top Artists */}
      <div className="section">
        <h2>Your Top Artists</h2>
        <div className="artists-grid">
          {userData.top_artists?.short_term?.slice(0, 6).map((artist, index) => (
            <div key={artist.id} className="artist-card">
              <img src={artist.images[0]?.url} alt={artist.name} />
              <div className="artist-info">
                <h4>{artist.name}</h4>
                <p>#{index + 1}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Insights */}
      <div className="section">
        <h2>Insights About Your Music Taste</h2>
        <div className="insights">
          {userData.insights?.map((insight, index) => (
            <div key={index} className="insight-card">
              <p>{insight}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default App