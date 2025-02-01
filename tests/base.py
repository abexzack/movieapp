import unittest
import sqlite3
from app import create_app
from app.services.database import get_db

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test app and database before each test"""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Initialize test database
        self._init_test_db()
        
    def tearDown(self):
        """Clean up after each test"""
        self.app_context.pop()
    
    def _init_test_db(self):
        """Initialize test database with sample data"""
        conn = get_db()
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

            CREATE TABLE IF NOT EXISTS Movie_Search_History (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                movie_id INTEGER NOT NULL,
                search_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (movie_id) REFERENCES Movies(id)
            );
        """)
        
        # Clear existing data
        cursor.executescript("""
            DELETE FROM Movie_Search_History;
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

            -- Add some search history data
            INSERT INTO Movie_Search_History (movie_id) VALUES
                (1), (1), (1), -- Test Movie 1 searched 3 times
                (2), (2),      -- Test Movie 2 searched 2 times
                (3);           -- Another Movie searched once
        """)
        
        conn.commit()
    
    @classmethod
    def setUpClass(cls):
        """Set up any necessary test fixtures before running tests"""
        # Ensure test database is created
        app = create_app('testing')
        with app.app_context():
            conn = get_db()
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
    
    @classmethod
    def tearDownClass(cls):
        """Clean up any test fixtures after running tests"""
        import os
        try:
            os.remove('test_movie_streaming.db')
        except OSError:
            pass 