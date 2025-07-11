from typing import List, Dict, Tuple
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import statistics
import math

class SpotifyDataProcessor:
    """Process and analyze Spotify data"""
    
    def __init__(self):
        pass
    
    def process_listening_history(self, recent_tracks: List[Dict]) -> Dict:
        """Process recent listening history into useful stats"""
        if not recent_tracks:
            return {}
        
        # Extract basic info
        total_tracks = len(recent_tracks)
        unique_tracks = len(set(track["track"]["id"] for track in recent_tracks))
        unique_artists = len(set(track["track"]["artists"][0]["id"] for track in recent_tracks))
        
        # Calculate listening patterns
        listening_by_hour = self._analyze_listening_by_hour(recent_tracks)
        listening_by_day = self._analyze_listening_by_day(recent_tracks)
        
        # Track repetition analysis
        track_plays = Counter(track["track"]["id"] for track in recent_tracks)
        most_played_tracks = track_plays.most_common(10)
        
        # Artist analysis
        artist_plays = Counter(track["track"]["artists"][0]["name"] for track in recent_tracks)
        top_artists = artist_plays.most_common(10)
        
        return {
            "total_tracks_played": total_tracks,
            "unique_tracks": unique_tracks,
            "unique_artists": unique_artists,
            "repetition_rate": (total_tracks - unique_tracks) / total_tracks if total_tracks > 0 else 0,
            "listening_by_hour": listening_by_hour,
            "listening_by_day": listening_by_day,
            "most_played_tracks": most_played_tracks,
            "top_artists": top_artists
        }
    
    def _analyze_listening_by_hour(self, tracks: List[Dict]) -> Dict[int, int]:
        """Analyze listening patterns by hour of day"""
        hour_counts = defaultdict(int)
        
        for track in tracks:
            played_at = datetime.fromisoformat(track["played_at"].replace('Z', '+00:00'))
            hour = played_at.hour
            hour_counts[hour] += 1
        
        return dict(hour_counts)
    
    def _analyze_listening_by_day(self, tracks: List[Dict]) -> Dict[str, int]:
        """Analyze listening patterns by day of week"""
        day_counts = defaultdict(int)
        
        for track in tracks:
            played_at = datetime.fromisoformat(track["played_at"].replace('Z', '+00:00'))
            day = played_at.strftime("%A")
            day_counts[day] += 1
        
        return dict(day_counts)
    
    def analyze_track_characteristics(self, tracks: List[Dict]) -> Dict:
        """Analyze track characteristics using available data (no audio features)"""
        if not tracks:
            return {}
        
        # Extract track data
        track_data = []
        for track in tracks:
            track_info = track.get("track", track)
            if track_info:
                track_data.append(track_info)
        
        if not track_data:
            return {}
        
        # Analyze popularity distribution
        popularities = [t.get("popularity", 0) for t in track_data if t.get("popularity") is not None]
        
        # Analyze track duration
        durations = [t.get("duration_ms", 0) for t in track_data if t.get("duration_ms")]
        duration_minutes = [d / (1000 * 60) for d in durations if d > 0]
        
        # Analyze explicitness
        explicit_count = sum(1 for t in track_data if t.get("explicit", False))
        
        # Release year analysis
        release_years = []
        for track in track_data:
            album = track.get("album", {})
            release_date = album.get("release_date", "")
            if release_date and len(release_date) >= 4:
                try:
                    year = int(release_date[:4])
                    release_years.append(year)
                except ValueError:
                    pass
        
        analysis = {
            "track_count": len(track_data),
            "avg_popularity": statistics.mean(popularities) if popularities else 0,
            "popularity_std": statistics.stdev(popularities) if len(popularities) > 1 else 0,
            "avg_duration_minutes": statistics.mean(duration_minutes) if duration_minutes else 0,
            "explicit_percentage": (explicit_count / len(track_data)) * 100 if track_data else 0,
        }
        
        if release_years:
            analysis.update({
                "avg_release_year": statistics.mean(release_years),
                "oldest_track_year": min(release_years),
                "newest_track_year": max(release_years),
                "year_range": max(release_years) - min(release_years)
            })
        
        return analysis
    
    def calculate_genre_diversity(self, artists: List[Dict]) -> Dict:
        """Calculate genre diversity score"""
        if not artists:
            return {"diversity_score": 0, "genre_distribution": {}}
        
        # Collect all genres
        all_genres = []
        for artist in artists:
            all_genres.extend(artist.get("genres", []))
        
        if not all_genres:
            return {"diversity_score": 0, "genre_distribution": {}}
        
        # Count genres
        genre_counts = Counter(all_genres)
        total_genres = len(all_genres)
        unique_genres = len(genre_counts)
        
        # Calculate diversity using Shannon entropy
        diversity_score = 0
        for count in genre_counts.values():
            p = count / total_genres
            diversity_score -= p * math.log2(p)
        
        # Normalize to 0-1 scale
        max_diversity = math.log2(unique_genres) if unique_genres > 1 else 1
        normalized_diversity = diversity_score / max_diversity if max_diversity > 0 else 0
        
        return {
            "diversity_score": normalized_diversity,
            "unique_genres": unique_genres,
            "total_genre_mentions": total_genres,
            "genre_distribution": dict(genre_counts.most_common(10))
        }
    
    def calculate_obscurity_score(self, artists: List[Dict], tracks: List[Dict]) -> Dict:
        """Calculate how obscure the user's music taste is"""
        if not artists and not tracks:
            return {"obscurity_score": 0}
        
        # Artist popularity (lower popularity = more obscure)
        artist_popularities = []
        for artist in artists:
            if artist.get("popularity") is not None:
                artist_popularities.append(artist["popularity"])
        
        # Track popularity
        track_popularities = []
        for track in tracks:
            track_data = track.get("track", track)
            if track_data.get("popularity") is not None:
                track_popularities.append(track_data["popularity"])
        
        # Calculate obscurity (inverse of popularity)
        avg_artist_obscurity = 0
        avg_track_obscurity = 0
        
        if artist_popularities:
            avg_artist_popularity = statistics.mean(artist_popularities)
            avg_artist_obscurity = (100 - avg_artist_popularity) / 100
        
        if track_popularities:
            avg_track_popularity = statistics.mean(track_popularities)
            avg_track_obscurity = (100 - avg_track_popularity) / 100
        
        # Combined obscurity score
        overall_obscurity = (avg_artist_obscurity + avg_track_obscurity) / 2
        
        return {
            "obscurity_score": overall_obscurity,
            "avg_artist_popularity": statistics.mean(artist_popularities) if artist_popularities else 0,
            "avg_track_popularity": statistics.mean(track_popularities) if track_popularities else 0,
            "artist_popularity_std": statistics.stdev(artist_popularities) if len(artist_popularities) > 1 else 0,
            "track_popularity_std": statistics.stdev(track_popularities) if len(track_popularities) > 1 else 0
        }
    
    def calculate_uniqueness_score(self, user_data: Dict) -> Dict:
        """Calculate overall uniqueness score combining multiple factors"""
        
        # Components of uniqueness
        genre_diversity = user_data.get("genre_diversity", {}).get("diversity_score", 0)
        obscurity_score = user_data.get("obscurity_score", {}).get("obscurity_score", 0)
        
        # Track characteristics diversity (since audio features are deprecated)
        track_characteristics = user_data.get("track_characteristics", {})
        characteristics_diversity = 0
        
        if track_characteristics:
            # Use year range and popularity std as diversity indicators
            year_range = track_characteristics.get("year_range", 0)
            popularity_std = track_characteristics.get("popularity_std", 0)
            
            # Normalize these values
            year_diversity = min(year_range / 50, 1.0)  # 50 years = max diversity
            popularity_diversity = popularity_std / 50  # Normalize popularity std
            
            characteristics_diversity = (year_diversity + popularity_diversity) / 2
        
        # Repetition penalty (listening to same tracks repeatedly reduces uniqueness)
        repetition_rate = user_data.get("listening_history", {}).get("repetition_rate", 0)
        repetition_penalty = 1 - repetition_rate
        
        # Calculate weighted uniqueness score (adjusted weights since no audio features)
        uniqueness_components = {
            "genre_diversity": genre_diversity * 0.4,  # Increased weight
            "obscurity": obscurity_score * 0.4,        # Increased weight
            "track_diversity": characteristics_diversity * 0.1,
            "listening_variety": repetition_penalty * 0.1
        }
        
        total_uniqueness = sum(uniqueness_components.values())
        
        return {
            "uniqueness_score": total_uniqueness,
            "components": uniqueness_components,
            "rating": self._get_uniqueness_rating(total_uniqueness),
            "note": "Calculated without audio features (deprecated by Spotify)"
        }
    
    def _get_uniqueness_rating(self, score: float) -> str:
        """Convert uniqueness score to human-readable rating"""
        if score >= 0.8:
            return "Extremely Unique"
        elif score >= 0.6:
            return "Very Unique"
        elif score >= 0.4:
            return "Moderately Unique"
        elif score >= 0.2:
            return "Somewhat Unique"
        else:
            return "Mainstream"
    
    def generate_insights(self, processed_data: Dict) -> List[str]:
        """Generate human-readable insights from the processed data"""
        insights = []
        
        # Listening habits
        history = processed_data.get("listening_history", {})
        if history:
            total_tracks = history.get("total_tracks_played", 0)
            unique_tracks = history.get("unique_tracks", 0)
            
            insights.append(f"You've listened to {total_tracks} tracks with {unique_tracks} unique songs")
            
            # Peak listening time
            listening_by_hour = history.get("listening_by_hour", {})
            if listening_by_hour:
                peak_hour = max(listening_by_hour.items(), key=lambda x: x[1])[0]
                insights.append(f"Your peak listening time is around {peak_hour}:00")
        
        # Genre diversity
        genre_info = processed_data.get("genre_diversity", {})
        if genre_info:
            diversity_score = genre_info.get("diversity_score", 0)
            unique_genres = genre_info.get("unique_genres", 0)
            insights.append(f"You listen to {unique_genres} different genres with a diversity score of {diversity_score:.2f}")
        
        # Uniqueness
        uniqueness = processed_data.get("uniqueness_score", {})
        if uniqueness:
            rating = uniqueness.get("rating", "Unknown")
            score = uniqueness.get("uniqueness_score", 0)
            insights.append(f"Your music taste is {rating} (uniqueness score: {score:.2f})")
        
        # Track characteristics (instead of audio features)
        track_chars = processed_data.get("track_characteristics", {})
        if track_chars:
            avg_popularity = track_chars.get("avg_popularity", 0)
            year_range = track_chars.get("year_range", 0)
            
            if avg_popularity < 30:
                insights.append("You prefer lesser-known tracks")
            elif avg_popularity > 70:
                insights.append("You enjoy popular mainstream music")
            
            if year_range > 30:
                insights.append("Your music spans multiple decades")
            
            explicit_pct = track_chars.get("explicit_percentage", 0)
            if explicit_pct > 50:
                insights.append("You listen to a lot of explicit content")
        
        return insights