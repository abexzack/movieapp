import unittest
import json
import sqlite3
from app import app
import os

class TestFlaskAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test database once for all tests"""
        cls.test_db = 'test_movie_streaming.db'
        app.config['DATABASE'] = cls.test_db  # Set the database path for the app
        
        # Create and populate test database
        conn = sqlite3.connect(cls.test_db)
        cursor = conn.cursor()
        
        # Create tables
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS Movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                release_year INTEGER NOT NULL
            );
            
            CREATE TABLE IF NOT EXISTS Streaming_Services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT NOT NULL UNIQUE
            );
            
            CREATE TABLE IF NOT EXISTS Movie_Streamings (
                movie_id INTEGER,
                service_id INTEGER,
                PRIMARY KEY (movie_id, service_id),
                FOREIGN KEY (movie_id) REFERENCES Movies(id),
                FOREIGN KEY (service_id) REFERENCES Streaming_Services(id)
            );
        """)
        
        conn.commit()
        conn.close()

    def setUp(self):
        """Set up test client and fresh data before each test"""
        app.config['TESTING'] = True
        self.client = app.test_client()
        
        # Clean and repopulate test data
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.executescript("""
            DELETE FROM Movie_Streamings;
            DELETE FROM Movies;
            DELETE FROM Streaming_Services;
            DELETE FROM sqlite_sequence;
        """)
        
        # Insert test data
        cursor.executescript("""
            INSERT INTO Movies (title, release_year) VALUES
                ('Test Movie 1', 2020),
                ('Test Movie 2', 2021),
                ('Another Movie', 2019);
                
            INSERT INTO Streaming_Services (service_name) VALUES
                ('Netflix'),
                ('Amazon Prime');
                
            INSERT INTO Movie_Streamings (movie_id, service_id) VALUES
                (1, 1),  -- Test Movie 1 on Netflix
                (1, 2),  -- Test Movie 1 on Amazon Prime
                (2, 1);  -- Test Movie 2 on Netflix
        """)
        
        conn.commit()
        conn.close()

    def test_health_check(self):
        """Test the health check endpoint"""
        response = self.client.get('/api/health')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['database'], 'connected')

    def test_search_basic(self):
        """Test basic search functionality"""
        response = self.client.get('/api/movies/search?q=Test')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['results']), 2, "Should find two test movies")
        self.assertTrue(any(movie['title'] == 'Test Movie 1' for movie in data['results']))
        self.assertTrue(any(movie['title'] == 'Test Movie 2' for movie in data['results']))

    def test_search_with_filters(self):
        """Test search with year and service filters"""
        response = self.client.get('/api/movies/search?q=Test&year=2020&service=netflix')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['results']), 1, "Should find exactly one movie")
        self.assertEqual(data['results'][0]['title'], 'Test Movie 1')
        self.assertEqual(data['results'][0]['year'], 2020)
        self.assertIn('Netflix', data['results'][0]['streaming_services'])

    def test_search_no_results(self):
        """Test search with no matching results"""
        response = self.client.get('/api/movies/search?q=NonexistentMovie')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['results']), 0)
        self.assertIn('suggestion', data)

    def test_search_validation(self):
        """Test search input validation"""
        # Test empty query
        response = self.client.get('/api/movies/search?q=')
        self.assertEqual(response.status_code, 400)
        
        # Test too short query
        response = self.client.get('/api/movies/search?q=a')
        self.assertEqual(response.status_code, 400)
        
        # Test invalid characters
        response = self.client.get('/api/movies/search?q=test;DROP%20TABLE')
        self.assertEqual(response.status_code, 400)

    def test_get_streaming_services(self):
        """Test getting streaming services for a specific movie"""
        response = self.client.get('/api/movies/1/streaming')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['movie_id'], 1)
        self.assertEqual(len(data['streaming_services']), 2)
        self.assertIn('Netflix', data['streaming_services'])
        self.assertIn('Amazon Prime', data['streaming_services'])

    def test_get_streaming_services_not_found(self):
        """Test getting streaming services for non-existent movie"""
        response = self.client.get('/api/movies/999/streaming')
        self.assertEqual(response.status_code, 404)

    def test_exact_match_ordering(self):
        """Test that exact matches appear first in results"""
        response = self.client.get('/api/movies/search?q=Test Movie 1')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(data['results']), 0, "Should have at least one result")
        self.assertTrue(data['results'][0]['exact_match'])
        self.assertEqual(data['results'][0]['title'], 'Test Movie 1')

    def test_invalid_year_filter(self):
        """Test search with invalid year filter"""
        response = self.client.get('/api/movies/search?q=Test&year=invalid')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        # Year should be None if it's not a valid integer
        self.assertIsNone(data['filters']['year'])
        # Verify we still get results despite invalid year
        self.assertGreater(len(data['results']), 0)

    def test_case_insensitive_search(self):
        """Test case insensitive search"""
        response = self.client.get('/api/movies/search?q=test')
        data_lower = json.loads(response.data)
        
        response = self.client.get('/api/movies/search?q=TEST')
        data_upper = json.loads(response.data)
        
        self.assertEqual(data_lower['results'], data_upper['results'])

    @classmethod
    def tearDownClass(cls):
        """Clean up test database after all tests"""
        try:
            os.remove(cls.test_db)
        except OSError:
            pass

if __name__ == '__main__':
    unittest.main() 