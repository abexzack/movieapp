from typing import List, Dict, Optional
from app.services.database import get_db

class Movie:
    def __init__(self, id: int, title: str, release_year: int, view_count: int = None):
        self.id = id
        self.title = title
        self.release_year = release_year
        self.view_count = view_count
        self._streaming_services = None

    @property
    def streaming_services(self) -> List[str]:
        if self._streaming_services is None:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("""
                SELECT s.service_name
                FROM Streaming_Services s
                JOIN Movie_Streamings ms ON s.id = ms.service_id
                WHERE ms.movie_id = ?
            """, (self.id,))
            self._streaming_services = [row['service_name'] for row in cursor.fetchall()]
        return self._streaming_services

    def to_dict(self, include_streaming: bool = True) -> Dict:
        result = {
            'id': self.id,
            'title': self.title,
            'year': self.release_year,
        }
        if include_streaming:
            result['streaming_services'] = self.streaming_services
        if self.view_count is not None:
            result['view_count'] = self.view_count
        return result

    def record_search(self):
        """Record a search for this movie"""
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO Movie_Search_History (movie_id) VALUES (?)",
            (self.id,)
        )
        db.commit()

    @staticmethod
    def search(query: str, year: Optional[int] = None, service: Optional[str] = None) -> List['Movie']:
        db = get_db()
        cursor = db.cursor()

        query_parts = [
            "SELECT DISTINCT m.id, m.title, m.release_year",
            "FROM Movies m"
        ]
        params = []

        if service:
            query_parts.extend([
                "JOIN Movie_Streamings ms ON m.id = ms.movie_id",
                "JOIN Streaming_Services s ON ms.service_id = s.id",
                "WHERE LOWER(s.service_name) = LOWER(?)"
            ])
            params.append(service)
        else:
            query_parts.append("WHERE 1=1")

        query_parts.append("AND LOWER(m.title) LIKE LOWER(?)")
        params.append(f'%{query}%')

        if year:
            query_parts.append("AND m.release_year = ?")
            params.append(year)

        query_parts.append("ORDER BY m.title")

        cursor.execute(" ".join(query_parts), params)
        movies = [Movie(row['id'], row['title'], row['release_year'])
                 for row in cursor.fetchall()]
        
        # Record searches for found movies
        for movie in movies:
            movie.record_search()
        
        return movies

    @staticmethod
    def get_by_id(movie_id: int) -> Optional['Movie']:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT id, title, release_year FROM Movies WHERE id = ?",
            (movie_id,)
        )
        row = cursor.fetchone()
        return Movie(row['id'], row['title'], row['release_year']) if row else None

    @staticmethod
    def get_trending(limit: int = 10) -> List['Movie']:
        """Get trending movies based on search frequency"""
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("""
            SELECT 
                m.id,
                m.title,
                m.release_year,
                COUNT(msh.id) as view_count
            FROM Movies m
            LEFT JOIN Movie_Search_History msh ON m.id = msh.movie_id
            GROUP BY m.id
            ORDER BY view_count DESC
            LIMIT ?
        """, (limit,))
        
        return [Movie(
            row['id'], 
            row['title'], 
            row['release_year'], 
            row['view_count']
        ) for row in cursor.fetchall()] 