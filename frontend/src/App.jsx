import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [accessToken, setAccessToken] = useState(null)
  const [refreshToken, setRefreshToken] = useState(null)
  const [userData, setUserData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  // Initialize authentication state on app load
  useEffect(() => {
    // Check for token in localStorage first
    const storedToken = localStorage.getItem('spotify_access_token')
    const storedRefreshToken = localStorage.getItem('spotify_refresh_token')
    const storedUserData = localStorage.getItem('spotify_user_data')
    const tokenExpiry = localStorage.getItem('spotify_token_expiry')
    
    // Check if stored token is still valid
    if (storedToken && tokenExpiry) {
      const currentTime = new Date().getTime()
      const expiryTime = parseInt(tokenExpiry)
      
      if (currentTime < expiryTime) {
        // Token is still valid
        setAccessToken(storedToken)
        setRefreshToken(storedRefreshToken)
        setIsAuthenticated(true)
        
        // Load cached user data if available
        if (storedUserData) {
          try {
            setUserData(JSON.parse(storedUserData))
          } catch (e) {
            console.warn('Failed to parse stored user data')
            localStorage.removeItem('spotify_user_data')
          }
        }
      } else if (storedRefreshToken) {
        // Token expired but we have refresh token, try to refresh
        attemptTokenRefresh(storedRefreshToken)
      } else {
        // Clear expired token data
        clearStoredAuth()
      }
    }
    
    // Check for access token in URL (from OAuth callback)
    const urlParams = new URLSearchParams(window.location.search)
    const urlToken = urlParams.get('access_token')
    const urlRefreshToken = urlParams.get('refresh_token')
    const urlExpiresIn = urlParams.get('expires_in')
    
    if (urlToken) {
      // Store new token with proper expiry
      const expiresInSeconds = urlExpiresIn ? parseInt(urlExpiresIn) : 3600
      const expiryTime = new Date().getTime() + (expiresInSeconds * 1000)
      
      localStorage.setItem('spotify_access_token', urlToken)
      localStorage.setItem('spotify_token_expiry', expiryTime.toString())
      
      if (urlRefreshToken) {
        localStorage.setItem('spotify_refresh_token', urlRefreshToken)
      }
      
      setAccessToken(urlToken)
      setRefreshToken(urlRefreshToken)
      setIsAuthenticated(true)
      
      // Clean up URL
      window.history.replaceState({}, document.title, window.location.pathname)
    }
  }, [])

  // Attempt to refresh token
  const attemptTokenRefresh = async (refreshTokenToUse) => {
    try {
      const response = await fetch('http://localhost:8000/refresh-token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `refresh_token=${refreshTokenToUse}`
      })
      
      if (response.ok) {
        const data = await response.json()
        const expiryTime = new Date().getTime() + (data.expires_in * 1000)
        
        localStorage.setItem('spotify_access_token', data.access_token)
        localStorage.setItem('spotify_token_expiry', expiryTime.toString())
        
        if (data.refresh_token) {
          localStorage.setItem('spotify_refresh_token', data.refresh_token)
        }
        
        setAccessToken(data.access_token)
        setRefreshToken(data.refresh_token || refreshTokenToUse)
        setIsAuthenticated(true)
      } else {
        // Refresh failed, clear all auth data
        clearStoredAuth()
      }
    } catch (error) {
      console.error('Token refresh failed:', error)
      clearStoredAuth()
    }
  }

  // Clear stored authentication data
  const clearStoredAuth = () => {
    localStorage.removeItem('spotify_access_token')
    localStorage.removeItem('spotify_refresh_token')
    localStorage.removeItem('spotify_user_data')
    localStorage.removeItem('spotify_token_expiry')
  }

  // Login with Spotify
  const handleLogin = () => {
    window.location.href = 'http://localhost:8000/login'
  }

  // Logout function
  const handleLogout = () => {
    clearStoredAuth()
    setAccessToken(null)
    setRefreshToken(null)
    setUserData(null)
    setIsAuthenticated(false)
    setError(null)
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
      
      // Cache user data in localStorage
      localStorage.setItem('spotify_user_data', JSON.stringify(data))
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // Auto-fetch analysis when we get a token (only if we don't have cached data)
  useEffect(() => {
    if (accessToken && !userData) {
      fetchAnalysis()
    }
  }, [accessToken])

  // Login Screen
  if (!isAuthenticated) {
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
        <Dashboard userData={userData} onRefresh={fetchAnalysis} onLogout={handleLogout} />
      </div>
    )
  }

  return null
}

// Simple Dashboard Component
function Dashboard({ userData, onRefresh, onLogout }) {
  const uniqueness = userData.uniqueness_score || {}
  const profile = userData.user_profile || {}
  const listeningHistory = userData.listening_history || {}
  const genreDiversity = userData.genre_diversity || {}
  const obscurityScore = userData.obscurity_score || {}

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Hi {profile.name}! 👋</h1>
        <div className="header-actions">
          <button onClick={onRefresh} className="refresh-button">
            Refresh Data
          </button>
          <button onClick={onLogout} className="logout-button">
            Logout
          </button>
        </div>
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
                  {/* <div className="popularity-indicator">
                    {track.popularity > 70 ? '🔥' : track.popularity > 40 ? '⭐' : '💎'}
                  </div> */}
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