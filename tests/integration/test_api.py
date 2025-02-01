from tests.base import BaseTestCase
import json

class TestAPIEndpoints(BaseTestCase):
    def test_health_check(self):
        """Test the health check endpoint"""
        response = self.client.get('/api/health')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'healthy')
    
    def test_search_endpoint(self):
        """Test the movie search endpoint"""
        # Test basic search
        response = self.client.get('/api/movies/search?q=Test')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['results']), 2)
        
        # Test with filters
        response = self.client.get('/api/movies/search?q=Test&year=2020&service=netflix')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['results']), 1)
    
    def test_get_movie(self):
        """Test getting a specific movie"""
        response = self.client.get('/api/movies/1')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['title'], 'Test Movie 1')
        
        # Test non-existent movie
        response = self.client.get('/api/movies/999')
        self.assertEqual(response.status_code, 404)
    
    def test_get_movie_streaming(self):
        """Test getting movie streaming services"""
        response = self.client.get('/api/movies/1/streaming')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Netflix', data['streaming_services']) 