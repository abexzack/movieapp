import sqlite3
from sqlite3 import Error

# Sample data
MOVIES = [
    ("The Matrix", 1999),
    ("Inception", 2010),
    ("Interstellar", 2014),
    ("The Dark Knight", 2008),
    ("Pulp Fiction", 1994),
    ("The Shawshank Redemption", 1994),
    ("Forrest Gump", 1994),
    ("Avatar", 2009),
    ("Titanic", 1997),
    ("The Lord of the Rings: The Fellowship of the Ring", 2001)
]

STREAMING_SERVICES = [
    "Netflix",
    "Amazon Prime",
    "HBO Max",
    "Disney+",
    "Hulu",
    "Apple TV+"
]

# Movie-Streaming service relationships (movie_index, service_index)
MOVIE_STREAMING_RELATIONS = [
    (0, 0),  # Matrix on Netflix
    (0, 1),  # Matrix on Amazon Prime
    (1, 2),  # Inception on HBO Max
    (1, 1),  # Inception on Amazon Prime
    (2, 0),  # Interstellar on Netflix
    (2, 4),  # Interstellar on Hulu
    (3, 2),  # Dark Knight on HBO Max
    (4, 0),  # Pulp Fiction on Netflix
    (5, 1),  # Shawshank on Amazon Prime
    (6, 3),  # Forrest Gump on Disney+
    (7, 3),  # Avatar on Disney+
    (8, 1),  # Titanic on Amazon Prime
    (9, 2)   # LOTR on HBO Max
]

def create_database():
    try:
        connection = sqlite3.connect('movie_streaming.db')
        cursor = connection.cursor()
        
        # Create Movies table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                release_year INTEGER NOT NULL
            )
        """)
        
        # Create Streaming_Services table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Streaming_Services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT NOT NULL UNIQUE
            )
        """)
        
        # Create Movie_Streamings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Movie_Streamings (
                movie_id INTEGER,
                service_id INTEGER,
                PRIMARY KEY (movie_id, service_id),
                FOREIGN KEY (movie_id) REFERENCES Movies(id),
                FOREIGN KEY (service_id) REFERENCES Streaming_Services(id)
            )
        """)
        
        print("Database and tables created successfully")
        return connection
            
    except Error as e:
        print(f"Error: {e}")
        return None

def populate_database(connection):
    try:
        cursor = connection.cursor()
        
        # Clear existing data
        cursor.execute("DELETE FROM Movie_Streamings")
        cursor.execute("DELETE FROM Movies")
        cursor.execute("DELETE FROM Streaming_Services")
        
        # Reset auto-increment counters
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('Movies', 'Streaming_Services')")
        
        # Insert Movies
        movie_insert_query = "INSERT INTO Movies (title, release_year) VALUES (?, ?)"
        cursor.executemany(movie_insert_query, MOVIES)
        
        # Insert Streaming Services
        service_insert_query = "INSERT INTO Streaming_Services (service_name) VALUES (?)"
        cursor.executemany(service_insert_query, [(service,) for service in STREAMING_SERVICES])
        
        # Insert Movie-Streaming relationships
        relation_insert_query = """
            INSERT INTO Movie_Streamings (movie_id, service_id)
            SELECT 
                (SELECT id FROM Movies LIMIT 1 OFFSET ?),
                (SELECT id FROM Streaming_Services LIMIT 1 OFFSET ?)
        """
        cursor.executemany(relation_insert_query, MOVIE_STREAMING_RELATIONS)
        
        connection.commit()
        print("Data inserted successfully")
        
    except Error as e:
        print(f"Error: {e}")
        connection.rollback()

def test_query(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT 
                m.title, 
                m.release_year, 
                GROUP_CONCAT(s.service_name) as streaming_services
            FROM Movies m
            LEFT JOIN Movie_Streamings ms ON m.id = ms.movie_id
            LEFT JOIN Streaming_Services s ON ms.service_id = s.id
            GROUP BY m.id
            LIMIT 5
        """)
        results = cursor.fetchall()
        print("\nSample data:")
        for row in results:
            print(f"{row[0]} ({row[1]}) - Available on: {row[2]}")
            
    except Error as e:
        print(f"Error querying data: {e}")

def main():
    connection = create_database()
    if connection:
        populate_database(connection)
        test_query(connection)
        connection.close()
        print("\nDatabase connection closed.")

if __name__ == "__main__":
    main() 