import sqlite3
from flask import current_app

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(current_app.config['DATABASE'])
    cursor = conn.cursor()
    
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

        -- Insert default streaming services if they don't exist
        INSERT OR IGNORE INTO Streaming_Services (service_name) VALUES
            ('Netflix'),
            ('Amazon Prime'),
            ('Disney+'),
            ('Hulu'),
            ('HBO Max');
    """)
    
    conn.commit()
    conn.close() 