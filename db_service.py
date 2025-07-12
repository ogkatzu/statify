from sqlalchemy.orm import Session
from models import User, UserToken, UserAnalysis, UserTopArtist, UserTopTrack
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import os
import base64
from typing import Optional, Dict, Any

# Token encryption (you should store this in environment variables)
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
if isinstance(ENCRYPTION_KEY, str):
    ENCRYPTION_KEY = ENCRYPTION_KEY.encode()
fernet = Fernet(ENCRYPTION_KEY)

class DatabaseService:
    def __init__(self, db: Session):
        self.db = db
    
    def encrypt_token(self, token: str) -> str:
        """Encrypt a token for storage"""
        return fernet.encrypt(token.encode()).decode()
    
    def decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt a token from storage"""
        return fernet.decrypt(encrypted_token.encode()).decode()
    
    def get_or_create_user(self, spotify_user_data: Dict[str, Any]) -> User:
        """Get existing user or create new one"""
        user_id = spotify_user_data["id"]
        user = self.db.query(User).filter(User.spotify_user_id == user_id).first()
        
        if not user:
            user = User(
                spotify_user_id=user_id,
                display_name=spotify_user_data.get("display_name", ""),
                email=spotify_user_data.get("email", ""),
                profile_image_url=spotify_user_data.get("images", [{}])[0].get("url", "") if spotify_user_data.get("images") else "",
                spotify_country=spotify_user_data.get("country", ""),
                follower_count=spotify_user_data.get("followers", {}).get("total", 0),
                premium_status=spotify_user_data.get("product") == "premium",
                created_at=datetime.utcnow(),
                last_login_at=datetime.utcnow()
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        else:
            # Update last login
            user.last_login_at = datetime.utcnow()
            self.db.commit()
        
        return user
    
    def store_user_tokens(self, user_id: str, access_token: str, refresh_token: str, expires_in: int):
        """Store or update user tokens"""
        # Remove existing tokens
        self.db.query(UserToken).filter(UserToken.user_id == user_id).delete()
        
        # Create new token record
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        token_record = UserToken(
            user_id=user_id,
            access_token=self.encrypt_token(access_token),
            refresh_token=self.encrypt_token(refresh_token) if refresh_token else None,
            expires_at=expires_at
        )
        
        self.db.add(token_record)
        self.db.commit()
    
    def get_user_tokens(self, user_id: str) -> Optional[UserToken]:
        """Get user tokens"""
        return self.db.query(UserToken).filter(UserToken.user_id == user_id).first()
    
    def is_token_valid(self, user_id: str) -> bool:
        """Check if user's token is still valid"""
        token = self.get_user_tokens(user_id)
        if not token:
            return False
        return datetime.utcnow() < token.expires_at
    
    def store_analysis(self, user_id: str, analysis_data: Dict[str, Any]) -> UserAnalysis:
        """Store user analysis results"""
        uniqueness = analysis_data.get("uniqueness_score", {})
        listening_history = analysis_data.get("listening_history", {})
        genre_diversity = analysis_data.get("genre_diversity", {})
        obscurity_score = analysis_data.get("obscurity_score", {})
        track_characteristics = analysis_data.get("track_characteristics", {})
        
        analysis = UserAnalysis(
            user_id=user_id,
            analysis_date=datetime.utcnow(),
            
            # Scores
            uniqueness_score=uniqueness.get("uniqueness_score", 0.0),
            uniqueness_rating=uniqueness.get("rating", ""),
            genre_diversity_score=genre_diversity.get("shannon_entropy", 0.0),
            obscurity_score=obscurity_score.get("obscurity_score", 0.0),
            
            # Listening stats
            total_tracks_played=listening_history.get("total_tracks_played", 0),
            unique_tracks=listening_history.get("unique_tracks", 0),
            unique_artists=listening_history.get("unique_artists", 0),
            unique_genres=genre_diversity.get("unique_genres", 0),
            repetition_rate=listening_history.get("repetition_rate", 0.0),
            
            # Track characteristics
            avg_popularity=track_characteristics.get("avg_popularity", 0.0),
            avg_duration_minutes=track_characteristics.get("avg_duration_minutes", 0.0),
            explicit_percentage=track_characteristics.get("explicit_percentage", 0.0),
            avg_release_year=track_characteristics.get("avg_release_year", 0.0),
            year_range=track_characteristics.get("year_range", 0),
            
            # JSON data
            insights=analysis_data.get("insights", []),
            listening_by_hour=listening_history.get("listening_by_hour", {}),
            listening_by_day=listening_history.get("listening_by_day", {}),
            genre_distribution=genre_diversity.get("genre_distribution", {}),
            uniqueness_components=uniqueness.get("components", {})
        )
        
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        
        # Store top artists and tracks
        self._store_top_items(analysis.id, user_id, analysis_data)
        
        return analysis
    
    def _store_top_items(self, analysis_id: int, user_id: str, analysis_data: Dict[str, Any]):
        """Store top artists and tracks for this analysis"""
        top_artists = analysis_data.get("top_artists", {})
        top_tracks = analysis_data.get("top_tracks", {})
        
        # Store top artists
        for time_range, artists in top_artists.items():
            for rank, artist in enumerate(artists, 1):
                artist_record = UserTopArtist(
                    user_id=user_id,
                    analysis_id=analysis_id,
                    spotify_artist_id=artist["id"],
                    artist_name=artist["name"],
                    rank_position=rank,
                    time_range=time_range,
                    popularity=artist.get("popularity", 0),
                    follower_count=artist.get("followers", {}).get("total", 0),
                    genres=artist.get("genres", []),
                    image_url=artist.get("images", [{}])[0].get("url", "") if artist.get("images") else ""
                )
                self.db.add(artist_record)
        
        # Store top tracks
        for time_range, tracks in top_tracks.items():
            for rank, track in enumerate(tracks, 1):
                track_record = UserTopTrack(
                    user_id=user_id,
                    analysis_id=analysis_id,
                    spotify_track_id=track["id"],
                    track_name=track["name"],
                    artist_name=track["artists"][0]["name"] if track.get("artists") else "",
                    album_name=track.get("album", {}).get("name", ""),
                    rank_position=rank,
                    time_range=time_range,
                    popularity=track.get("popularity", 0),
                    duration_ms=track.get("duration_ms", 0),
                    explicit=track.get("explicit", False),
                    release_date=track.get("album", {}).get("release_date", ""),
                    image_url=track.get("album", {}).get("images", [{}])[0].get("url", "") if track.get("album", {}).get("images") else ""
                )
                self.db.add(track_record)
        
        self.db.commit()
    
    def get_user_latest_analysis(self, user_id: str) -> Optional[UserAnalysis]:
        """Get user's most recent analysis"""
        return (self.db.query(UserAnalysis)
                .filter(UserAnalysis.user_id == user_id)
                .order_by(UserAnalysis.analysis_date.desc())
                .first())
    
    def get_user_analysis_history(self, user_id: str, limit: int = 10) -> list:
        """Get user's analysis history"""
        return (self.db.query(UserAnalysis)
                .filter(UserAnalysis.user_id == user_id)
                .order_by(UserAnalysis.analysis_date.desc())
                .limit(limit)
                .all())