import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import time

class SpotifyClient:
    """Handle all Spotify API interactions"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://api.spotify.com/v1"
        self.headers = {"Authorization": f"Bearer {access_token}"}
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make a request to Spotify API with error handling"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                # Rate limited - wait and retry
                retry_after = int(response.headers.get('Retry-After', 1))
                time.sleep(retry_after)
                return self._make_request(endpoint, params)
            raise e
    
    def get_user_profile(self) -> Dict:
        """Get current user's profile"""
        return self._make_request("me")
    
    def get_top_artists(self, time_range: str = "medium_term", limit: int = 50) -> List[Dict]:
        """Get user's top artists
        
        Args:
            time_range: 'short_term' (4 weeks), 'medium_term' (6 months), 'long_term' (all time)
            limit: Number of artists to return (max 50)
        """
        params = {"time_range": time_range, "limit": limit}
        data = self._make_request("me/top/artists", params)
        return data.get("items", [])
    
    def get_top_tracks(self, time_range: str = "medium_term", limit: int = 50) -> List[Dict]:
        """Get user's top tracks"""
        params = {"time_range": time_range, "limit": limit}
        data = self._make_request("me/top/tracks", params)
        return data.get("items", [])
    
    def get_recently_played(self, limit: int = 50, after: Optional[int] = None) -> List[Dict]:
        """Get recently played tracks
        
        Args:
            limit: Number of items to return (max 50)
            after: Unix timestamp to get tracks after this time
        """
        params = {"limit": limit}
        if after:
            params["after"] = after
        
        data = self._make_request("me/player/recently-played", params)
        return data.get("items", [])
    
    def get_all_recent_tracks(self, days_back: int = 30) -> List[Dict]:
        """Get all recent tracks for the specified number of days"""
        all_tracks = []
        after = int((datetime.now() - timedelta(days=days_back)).timestamp() * 1000)
        
        while True:
            tracks = self.get_recently_played(limit=50, after=after)
            
            if not tracks:
                break
                
            all_tracks.extend(tracks)
            
            # Update after timestamp to the last track's timestamp
            last_track_time = tracks[-1]["played_at"]
            after = int(datetime.fromisoformat(last_track_time.replace('Z', '+00:00')).timestamp() * 1000)
            
            # Avoid infinite loops
            if len(all_tracks) > 10000:
                break
        
        return all_tracks
    
    def get_audio_features(self, track_ids: List[str]) -> List[Dict]:
        """Get audio features for multiple tracks - DEPRECATED BY SPOTIFY"""
        # Audio features endpoint was deprecated by Spotify on Nov 27, 2024
        # Returning empty list to maintain compatibility
        print("Warning: Audio features endpoint has been deprecated by Spotify")
        return []
    
    def get_single_audio_features(self, track_id: str) -> Dict:
        """Get audio features for a single track - DEPRECATED BY SPOTIFY"""
        # Audio features endpoint was deprecated by Spotify on Nov 27, 2024
        # Returning empty dict to maintain compatibility
        print("Warning: Audio features endpoint has been deprecated by Spotify")
        return {}
    
    def get_artist_details(self, artist_ids: List[str]) -> List[Dict]:
        """Get details for multiple artists"""
        if not artist_ids:
            return []
        
        # Spotify API accepts max 50 artist IDs at once
        chunk_size = 50
        all_artists = []
        
        for i in range(0, len(artist_ids), chunk_size):
            chunk = artist_ids[i:i + chunk_size]
            ids_param = ",".join(chunk)
            
            data = self._make_request("artists", {"ids": ids_param})
            artists = data.get("artists", [])
            all_artists.extend(artists)
        
        return all_artists
    
    def search_artist(self, query: str, limit: int = 20) -> List[Dict]:
        """Search for artists"""
        params = {"q": query, "type": "artist", "limit": limit}
        data = self._make_request("search", params)
        return data.get("artists", {}).get("items", [])
    
    def get_user_playlists(self, limit: int = 50) -> List[Dict]:
        """Get user's playlists"""
        params = {"limit": limit}
        data = self._make_request("me/playlists", params)
        return data.get("items", [])