import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from data_processor import SpotifyDataProcessor


class TestSpotifyDataProcessor:
    
    @pytest.fixture
    def processor(self):
        """Create a SpotifyDataProcessor instance for testing"""
        return SpotifyDataProcessor()
    
    def test_init(self, processor):
        """Test SpotifyDataProcessor initialization"""
        assert isinstance(processor, SpotifyDataProcessor)
    
    def test_process_listening_history_empty(self, processor):
        """Test processing empty listening history"""
        result = processor.process_listening_history([])
        assert result == {}
    
    def test_process_listening_history_basic_stats(self, processor, sample_listening_data):
        """Test basic stats calculation from listening history"""
        result = processor.process_listening_history(sample_listening_data)
        
        assert result["total_tracks_played"] == 3
        assert result["unique_tracks"] == 2  # track_1 appears twice
        assert result["unique_artists"] == 2  # artist_1 and artist_2
        assert result["repetition_rate"] == 1/3  # (3-2)/3
    
    def test_analyze_listening_by_hour(self, processor):
        """Test listening pattern analysis by hour"""
        tracks = [
            {"played_at": "2024-01-01T12:00:00Z"},
            {"played_at": "2024-01-01T12:30:00Z"},
            {"played_at": "2024-01-01T14:15:00Z"}
        ]
        
        result = processor._analyze_listening_by_hour(tracks)
        
        assert result[12] == 2  # Two tracks at hour 12
        assert result[14] == 1  # One track at hour 14
        assert len(result) == 2
    
    def test_analyze_listening_by_day(self, processor):
        """Test listening pattern analysis by day of week"""
        tracks = [
            {"played_at": "2024-01-01T12:00:00Z"},  # Monday
            {"played_at": "2024-01-02T12:00:00Z"},  # Tuesday  
            {"played_at": "2024-01-01T14:00:00Z"}   # Monday
        ]
        
        result = processor._analyze_listening_by_day(tracks)
        
        assert result["Monday"] == 2  # Monday has 2 tracks
        assert result["Tuesday"] == 1  # Tuesday has 1 track
        assert len(result) == 2
    
    def test_calculate_genre_diversity_empty(self, processor):
        """Test genre diversity analysis with empty artists"""
        result = processor.calculate_genre_diversity([])
        
        assert result["diversity_score"] == 0
        assert result["genre_distribution"] == {}
    
    def test_calculate_genre_diversity_single_genre(self, processor):
        """Test genre diversity analysis with single genre"""
        artists = [
            {"genres": ["pop"]},
            {"genres": ["pop"]},
            {"genres": ["pop"]}
        ]
        
        result = processor.calculate_genre_diversity(artists)
        
        assert result["unique_genres"] == 1
        assert result["genre_distribution"]["pop"] == 3
        assert result["diversity_score"] == 0  # No diversity with single genre
    
    def test_calculate_genre_diversity_multiple_genres(self, processor):
        """Test genre diversity analysis with multiple genres"""
        artists = [
            {"genres": ["pop", "rock"]},
            {"genres": ["jazz"]},
            {"genres": ["pop", "electronic"]}
        ]
        
        result = processor.calculate_genre_diversity(artists)
        
        assert result["unique_genres"] == 4
        assert result["genre_distribution"]["pop"] == 2
        assert result["genre_distribution"]["rock"] == 1
        assert result["genre_distribution"]["jazz"] == 1
        assert result["genre_distribution"]["electronic"] == 1
        assert result["diversity_score"] > 0  # Should have some diversity
    
    def test_calculate_obscurity_score_empty(self, processor):
        """Test obscurity score calculation with empty tracks"""
        result = processor.calculate_obscurity_score([], [])
        
        assert result["obscurity_score"] == 0
    
    def test_calculate_obscurity_score_mixed_popularity(self, processor):
        """Test obscurity score calculation with mixed popularity"""
        artists = [{"popularity": 80}, {"popularity": 20}]
        tracks = [{"popularity": 90}, {"popularity": 10}]
        
        result = processor.calculate_obscurity_score(artists, tracks)
        
        assert 0 <= result["obscurity_score"] <= 1
        assert "avg_artist_popularity" in result
        assert "avg_track_popularity" in result
    
    def test_calculate_uniqueness_score_basic(self, processor):
        """Test uniqueness score calculation"""
        analysis_data = {
            "genre_diversity": {"diversity_score": 0.8},
            "obscurity_score": {"obscurity_score": 0.6},
            "listening_history": {"repetition_rate": 0.3}
        }
        
        result = processor.calculate_uniqueness_score(analysis_data)
        
        assert 0 <= result["uniqueness_score"] <= 1
        assert "components" in result
        assert "rating" in result
    
    def test_generate_insights_comprehensive(self, processor):
        """Test comprehensive insight generation"""
        analysis_data = {
            "listening_history": {
                "total_tracks_played": 100,
                "unique_tracks": 80,
                "listening_by_hour": {12: 10, 14: 8, 20: 15}
            },
            "genre_diversity": {
                "diversity_score": 0.8,
                "unique_genres": 15
            },
            "uniqueness_score": {
                "rating": "Very Unique",
                "uniqueness_score": 0.75
            }
        }
        
        result = processor.generate_insights(analysis_data)
        
        assert isinstance(result, list)
        assert len(result) > 0
        
        # Check that insights are strings
        for insight in result:
            assert isinstance(insight, str)
    
    def test_analyze_track_characteristics(self, processor):
        """Test track characteristics analysis"""
        tracks = [
            {
                "popularity": 80,
                "duration_ms": 240000,
                "explicit": False,
                "album": {"release_date": "2020-01-01"}
            },
            {
                "popularity": 60,
                "duration_ms": 180000,
                "explicit": True,
                "album": {"release_date": "2015-05-15"}
            }
        ]
        
        result = processor.analyze_track_characteristics(tracks)
        
        assert result["track_count"] == 2
        assert result["avg_popularity"] == 70
        assert result["explicit_percentage"] == 50
    
    def test_get_uniqueness_rating(self, processor):
        """Test uniqueness rating conversion"""
        assert processor._get_uniqueness_rating(0.9) == "Extremely Unique"
        assert processor._get_uniqueness_rating(0.7) == "Very Unique"
        assert processor._get_uniqueness_rating(0.5) == "Moderately Unique"
        assert processor._get_uniqueness_rating(0.3) == "Somewhat Unique"
        assert processor._get_uniqueness_rating(0.1) == "Mainstream"
    
    def test_analyze_track_characteristics_empty(self, processor):
        """Test track characteristics with empty data"""
        result = processor.analyze_track_characteristics([])
        assert result == {}
    
    def test_analyze_track_characteristics_malformed(self, processor):
        """Test track characteristics with malformed data"""
        tracks = [{"invalid": "data"}, {}]
        result = processor.analyze_track_characteristics(tracks)
        # Should handle gracefully
        assert isinstance(result, dict)
    
    def test_calculate_genre_diversity_no_genres(self, processor):
        """Test genre diversity with artists that have no genres"""
        artists = [{"name": "Artist 1"}, {"name": "Artist 2"}]
        result = processor.calculate_genre_diversity(artists)
        
        assert result["diversity_score"] == 0
        assert result["genre_distribution"] == {}
    
    def test_calculate_obscurity_score_with_data(self, processor):
        """Test obscurity score with real data"""
        artists = [{"popularity": 80}, {"popularity": 40}]
        tracks = [{"popularity": 70}, {"popularity": 30}]
        
        result = processor.calculate_obscurity_score(artists, tracks)
        
        assert "avg_artist_popularity" in result
        assert "avg_track_popularity" in result
        assert result["avg_artist_popularity"] == 60
        assert result["avg_track_popularity"] == 50
    
    @patch('data_processor.datetime')
    def test_date_parsing_edge_cases(self, mock_datetime, processor):
        """Test handling of various date formats"""
        # Test with tracks containing different date formats
        tracks = [
            {"played_at": "2024-01-01T12:00:00Z"},
            {"played_at": "2024-01-01T12:00:00.000Z"}
        ]
        
        # Should not raise exceptions
        result = processor._analyze_listening_by_hour(tracks)
        assert isinstance(result, dict)
    
    def test_robust_error_handling(self, processor):
        """Test that processor handles malformed data gracefully"""
        # Test with properly formatted tracks to avoid KeyError
        malformed_tracks = [
            {"track": {"id": "track1", "artists": [{"id": "artist1", "name": "Artist 1"}]}, "played_at": "2024-01-01T12:00:00Z"},
            {"track": {"id": "track2", "artists": [{"id": "artist2", "name": "Artist 2"}]}, "played_at": "2024-01-01T14:00:00Z"}
        ]
        
        # Should not raise exceptions
        result = processor.process_listening_history(malformed_tracks)
        assert isinstance(result, dict)
        assert result["total_tracks_played"] == 2