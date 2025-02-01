from tests.base import BaseTestCase
from app.models.movie import Movie

class TestMovieModel(BaseTestCase):
    def test_movie_creation(self):
        """Test creating a movie object"""
        movie = Movie(1, "Test Movie", 2020)
        self.assertEqual(movie.title, "Test Movie")
        self.assertEqual(movie.release_year, 2020)
    
    def test_movie_to_dict(self):
        """Test movie serialization"""
        movie = Movie(1, "Test Movie", 2020)
        data = movie.to_dict(include_streaming=False)
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['title'], "Test Movie")
        self.assertEqual(data['year'], 2020)
    
    def test_get_streaming_services(self):
        """Test fetching streaming services for a movie"""
        movie = Movie.get_by_id(1)
        services = movie.streaming_services
        self.assertIn("Netflix", services)
        self.assertIn("Amazon Prime", services)
    
    def test_search_movies(self):
        """Test movie search functionality"""
        results = Movie.search("Test")
        self.assertEqual(len(results), 2)
        self.assertTrue(any(m.title == "Test Movie 1" for m in results))
        
        # Test with year filter
        results = Movie.search("Test", year=2020)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Test Movie 1")
        
        # Test with service filter
        results = Movie.search("Test", service="Netflix")
        self.assertTrue(all("Netflix" in m.streaming_services for m in results)) 