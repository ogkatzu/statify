from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    spotify_user_id = Column(String, primary_key=True, index=True)
    display_name = Column(String)
    email = Column(String)
    profile_image_url = Column(String)
    spotify_country = Column(String)
    follower_count = Column(Integer, default=0)
    premium_status = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    analyses = relationship("UserAnalysis", back_populates="user", cascade="all, delete-orphan")
    tokens = relationship("UserToken", back_populates="user", cascade="all, delete-orphan")

class UserToken(Base):
    __tablename__ = "user_tokens"
    
    user_id = Column(String, ForeignKey("users.spotify_user_id"), primary_key=True)
    access_token = Column(Text)  # Store encrypted
    refresh_token = Column(Text)  # Store encrypted
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="tokens")

class UserAnalysis(Base):
    __tablename__ = "user_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.spotify_user_id"), index=True)
    analysis_date = Column(DateTime, default=datetime.utcnow)
    
    # Scores
    uniqueness_score = Column(Float)
    uniqueness_rating = Column(String)
    genre_diversity_score = Column(Float)
    obscurity_score = Column(Float)
    
    # Listening stats
    total_tracks_played = Column(Integer)
    unique_tracks = Column(Integer)
    unique_artists = Column(Integer)
    unique_genres = Column(Integer)
    repetition_rate = Column(Float)
    
    # Track characteristics
    avg_popularity = Column(Float)
    avg_duration_minutes = Column(Float)
    explicit_percentage = Column(Float)
    avg_release_year = Column(Float)
    year_range = Column(Integer)
    
    # JSON data
    insights = Column(JSON)
    listening_by_hour = Column(JSON)
    listening_by_day = Column(JSON)
    genre_distribution = Column(JSON)
    uniqueness_components = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="analyses")
    top_artists = relationship("UserTopArtist", back_populates="analysis", cascade="all, delete-orphan")
    top_tracks = relationship("UserTopTrack", back_populates="analysis", cascade="all, delete-orphan")

class UserTopArtist(Base):
    __tablename__ = "user_top_artists"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.spotify_user_id"), index=True)
    analysis_id = Column(Integer, ForeignKey("user_analyses.id"), index=True)
    
    spotify_artist_id = Column(String, index=True)
    artist_name = Column(String)
    rank_position = Column(Integer)
    time_range = Column(String)  # short_term, medium_term, long_term
    popularity = Column(Integer)
    follower_count = Column(Integer)
    genres = Column(JSON)
    image_url = Column(String)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    analysis = relationship("UserAnalysis", back_populates="top_artists")

class UserTopTrack(Base):
    __tablename__ = "user_top_tracks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.spotify_user_id"), index=True)
    analysis_id = Column(Integer, ForeignKey("user_analyses.id"), index=True)
    
    spotify_track_id = Column(String, index=True)
    track_name = Column(String)
    artist_name = Column(String)
    album_name = Column(String)
    rank_position = Column(Integer)
    time_range = Column(String)  # short_term, medium_term, long_term
    popularity = Column(Integer)
    duration_ms = Column(Integer)
    explicit = Column(Boolean)
    release_date = Column(String)
    image_url = Column(String)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    analysis = relationship("UserAnalysis", back_populates="top_tracks")

class UserGenre(Base):
    __tablename__ = "user_genres"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.spotify_user_id"), index=True)
    analysis_id = Column(Integer, ForeignKey("user_analyses.id"), index=True)
    
    genre_name = Column(String, index=True)
    occurrence_count = Column(Integer)
    percentage = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)

# Analysis aggregation for trends
class UserTrend(Base):
    __tablename__ = "user_trends"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.spotify_user_id"), index=True)
    
    metric_name = Column(String)  # uniqueness_score, genre_diversity, etc.
    metric_value = Column(Float)
    change_from_previous = Column(Float)  # percentage change
    trend_direction = Column(String)  # up, down, stable
    
    # Time grouping
    year = Column(Integer)
    month = Column(Integer)
    week = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)