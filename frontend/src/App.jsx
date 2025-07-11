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

      {/* Hero Section - Uniqueness Score */}
      <div className="hero-section">
        <div className="hero-card">
          <div className="hero-content">
            <h2>Your Music DNA</h2>
            <div className="uniqueness-display">
              <div className="score-circle">
                <svg className="progress-ring" width="200" height="200">
                  <circle
                    className="progress-ring-background"
                    cx="100"
                    cy="100"
                    r="85"
                  />
                  <circle
                    className="progress-ring-progress"
                    cx="100"
                    cy="100"
                    r="85"
                    style={{
                      strokeDasharray: `${2 * Math.PI * 85}`,
                      strokeDashoffset: `${2 * Math.PI * 85 * (1 - (uniqueness.uniqueness_score || 0))}`
                    }}
                  />
                </svg>
                <div className="score-text">
                  <span className="score-number">{(uniqueness.uniqueness_score * 100).toFixed(0)}%</span>
                  <span className="score-label">Unique</span>
                </div>
              </div>
              <div className="score-details">
                <h3>{uniqueness.rating}</h3>
                <p>Your music taste is more unique than most listeners</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="stats-overview">
        <div className="stat-tile">
          <div className="stat-icon">🎵</div>
          <div className="stat-content">
            <h3>{listeningHistory.total_tracks_played || 0}</h3>
            <p>Total Tracks</p>
          </div>
        </div>
        <div className="stat-tile">
          <div className="stat-icon">🎤</div>
          <div className="stat-content">
            <h3>{listeningHistory.unique_artists || 0}</h3>
            <p>Unique Artists</p>
          </div>
        </div>
        <div className="stat-tile">
          <div className="stat-icon">🎼</div>
          <div className="stat-content">
            <h3>{genreDiversity.unique_genres || 0}</h3>
            <p>Genres</p>
          </div>
        </div>
        <div className="stat-tile">
          <div className="stat-icon">💎</div>
          <div className="stat-content">
            <h3>{(obscurityScore.obscurity_score * 100).toFixed(0)}%</h3>
            <p>Obscurity</p>
          </div>
        </div>
      </div>

      {/* Top Content Grid */}
      <div className="content-grid">
        {/* Top Artists */}
        <div className="content-section">
          <h2>🔥 Your Top Artists</h2>
          <div className="artists-list">
            {userData.top_artists?.short_term?.slice(0, 8).map((artist, index) => (
              <div key={artist.id} className="artist-item">
                <div className="rank">#{index + 1}</div>
                <img src={artist.images[0]?.url} alt={artist.name} className="artist-image" />
                <div className="artist-details">
                  <h4>{artist.name}</h4>
                  <p>{artist.genres?.[0] || 'Artist'}</p>
                </div>
                <div className="popularity-bar">
                  <div 
                    className="popularity-fill" 
                    style={{ width: `${artist.popularity}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Songs */}
        <div className="content-section">
          <h2>🎧 Your Top Songs</h2>
          <div className="songs-list">
            {userData.top_tracks?.short_term?.slice(0, 8).map((track, index) => (
              <div key={track.id} className="song-item">
                <div className="rank">#{index + 1}</div>
                <img src={track.album.images[0]?.url} alt={track.name} className="song-image" />
                <div className="song-details">
                  <h4>{track.name}</h4>
                  <p>{track.artists[0].name}</p>
                  <span className="album-name">{track.album.name}</span>
                </div>
                <div className="song-stats">
                  <div className="duration">
                    {Math.floor(track.duration_ms / 60000)}:{String(Math.floor((track.duration_ms % 60000) / 1000)).padStart(2, '0')}
                  </div>
                  <div className="popularity-indicator">
                    {track.popularity > 70 ? '🔥' : track.popularity > 40 ? '⭐' : '💎'}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Genre Distribution */}
      <div className="genre-section">
        <h2>Your Musical Palette</h2>
        <div className="genre-visualization">
          {Object.entries(genreDiversity.genre_distribution || {}).slice(0, 8).map(([genre, count], index) => {
            const maxCount = Math.max(...Object.values(genreDiversity.genre_distribution || {}));
            const size = Math.max(80 + (count / maxCount) * 60, 80);
            
            return (
              <div 
                key={genre} 
                className="genre-bubble" 
                style={{
                  '--size': size,
                  '--delay': `${index * 0.1}s`
                }}
              >
                <span className="genre-name">{genre.replace(/\s+/g, ' ')}</span>
                <span className="genre-count">{count}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Insights */}
      <div className="insights-section">
        <h2>🔍 Your Music Insights</h2>
        <div className="insights-container">
          {userData.insights?.map((insight, index) => {
            // Determine insight type based on content
            let icon = '💡';
            let category = 'General';
            
            if (insight.includes('tracks') || insight.includes('songs')) {
              icon = '🎵';
              category = 'Listening Habits';
            } else if (insight.includes('genre') || insight.includes('diversity')) {
              icon = '🎨';
              category = 'Musical Diversity';
            } else if (insight.includes('unique') || insight.includes('mainstream')) {
              icon = '💎';
              category = 'Taste Profile';
            } else if (insight.includes('time') || insight.includes('hour')) {
              icon = '⏰';
              category = 'Listening Patterns';
            } else if (insight.includes('explicit') || insight.includes('content')) {
              icon = '🔞';
              category = 'Content Preferences';
            } else if (insight.includes('decades') || insight.includes('year')) {
              icon = '📅';
              category = 'Musical Timeline';
            }

            return (
              <div 
                key={index} 
                className="insight-item" 
                style={{ '--delay': `${index * 0.15}s` }}
              >
                <div className="insight-header">
                  <div className="insight-icon">{icon}</div>
                  <span className="insight-category">{category}</span>
                </div>
                <p className="insight-text">{insight}</p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  )
}

export default App