from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
import requests
import os
from urllib.parse import urlencode
import base64
from dotenv import load_dotenv

# Import our new classes
from spotify_client import SpotifyClient
from data_processor import SpotifyDataProcessor

load_dotenv()

app = FastAPI(title="Spotify Stats API")

# Spotify configuration
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = "http://localhost:8000/callback"
SPOTIFY_SCOPE = "user-read-private user-read-email user-top-read user-read-recently-played user-library-read"

@app.get("/")
async def root():
    return {"message": "Spotify Stats API is running"}

@app.get("/login")
async def login():
    """Redirect user to Spotify authorization"""
    params = {
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "scope": SPOTIFY_SCOPE,
        "show_dialog": "true"
    }
    
    auth_url = f"https://accounts.spotify.com/authorize?{urlencode(params)}"
    return RedirectResponse(url=auth_url)

@app.get("/callback")
async def callback(code: str = None, error: str = None):
    """Handle Spotify OAuth callback"""
    if error:
        raise HTTPException(status_code=400, detail=f"Spotify auth error: {error}")
    
    if not code:
        raise HTTPException(status_code=400, detail="No authorization code received")
    
    # Exchange code for access token
    auth_header = base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
    
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": SPOTIFY_REDIRECT_URI
    }
    
    response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
    
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get access token")
    
    token_data = response.json()
    access_token = token_data["access_token"]
    
    # Get user profile to test the token
    client = SpotifyClient(access_token)
    user_data = client.get_user_profile()
    
    return {
        "message": "Successfully authenticated with Spotify",
        "user": {
            "id": user_data["id"],
            "name": user_data["display_name"],
            "email": user_data["email"]
        },
        "access_token": access_token  # Don't return this in production
    }

# New comprehensive analysis endpoint
@app.get("/user/analysis")
async def get_user_analysis(access_token: str, days_back: int = 30):
    """Get comprehensive user music analysis"""
    try:
        client = SpotifyClient(access_token)
        processor = SpotifyDataProcessor()
        
        # Gather all data
        print("Fetching user data...")
        user_profile = client.get_user_profile()
        
        print("Fetching top artists...")
        top_artists_short = client.get_top_artists("short_term", 50)
        top_artists_medium = client.get_top_artists("medium_term", 50)
        top_artists_long = client.get_top_artists("long_term", 50)
        
        print("Fetching top tracks...")
        top_tracks_short = client.get_top_tracks("short_term", 50)
        top_tracks_medium = client.get_top_tracks("medium_term", 50)
        top_tracks_long = client.get_top_tracks("long_term", 50)
        
        print("Fetching recent listening history...")
        recent_tracks = client.get_all_recent_tracks(days_back)
        
        # Get audio features for top tracks (limit to prevent issues)
        print("Note: Audio features endpoint deprecated by Spotify")
        # Skip audio features since they're no longer available
        
        # Process all the data
        print("Processing data...")
        analysis = {
            "user_profile": {
                "id": user_profile["id"],
                "name": user_profile["display_name"],
                "followers": user_profile.get("followers", {}).get("total", 0)
            },
            "listening_history": processor.process_listening_history(recent_tracks),
            "top_artists": {
                "short_term": top_artists_short[:10],
                "medium_term": top_artists_medium[:10],
                "long_term": top_artists_long[:10]
            },
            "top_tracks": {
                "short_term": top_tracks_short[:10],
                "medium_term": top_tracks_medium[:10],
                "long_term": top_tracks_long[:10]
            },
            "track_characteristics": processor.analyze_track_characteristics(
                top_tracks_short + top_tracks_medium + top_tracks_long
            ),
            "genre_diversity": processor.calculate_genre_diversity(
                top_artists_short + top_artists_medium + top_artists_long
            ),
            "obscurity_score": processor.calculate_obscurity_score(
                top_artists_short + top_artists_medium + top_artists_long,
                top_tracks_short + top_tracks_medium + top_tracks_long
            )
        }
        
        # Calculate overall uniqueness
        analysis["uniqueness_score"] = processor.calculate_uniqueness_score(analysis)
        
        # Generate insights
        analysis["insights"] = processor.generate_insights(analysis)
        
        return analysis
        
    except Exception as e:
        print(f"Full error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/user/test-audio-features")
async def test_audio_features(access_token: str):
    """Test audio features with a single track"""
    try:
        client = SpotifyClient(access_token)
        
        # Get just one top track
        top_tracks = client.get_top_tracks("short_term", 1)
        
        if not top_tracks:
            return {"error": "No top tracks found"}
        
        track_id = top_tracks[0]["id"]
        print(f"Testing with track ID: {track_id}")
        
        # Test audio features for single track
        audio_features = client.get_audio_features([track_id])
        
        return {
            "track": {
                "name": top_tracks[0]["name"],
                "artist": top_tracks[0]["artists"][0]["name"],
                "id": track_id
            },
            "audio_features": audio_features
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")

# Keep your existing simple endpoints for testing
@app.get("/user/top-artists")
async def get_top_artists(access_token: str, limit: int = 20, time_range: str = "medium_term"):
    """Get user's top artists"""
    client = SpotifyClient(access_token)
    artists = client.get_top_artists(time_range, limit)
    return {"artists": artists}

@app.get("/user/top-tracks")
async def get_top_tracks(access_token: str, limit: int = 20, time_range: str = "medium_term"):
    """Get user's top tracks"""
    client = SpotifyClient(access_token)
    tracks = client.get_top_tracks(time_range, limit)
    return {"tracks": tracks}

@app.get("/user/recent-tracks")
async def get_recent_tracks(access_token: str, limit: int = 50):
    """Get user's recently played tracks"""
    client = SpotifyClient(access_token)
    tracks = client.get_recently_played(limit)
    return {"tracks": tracks}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)