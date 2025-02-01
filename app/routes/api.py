from flask import Blueprint, request, jsonify
from app.models.movie import Movie
from typing import Optional
from flask import current_app
from app.services.database import get_db

api = Blueprint('api', __name__)

@api.route('/movies/search')
def search_movies():
    query = request.args.get('q', '').strip()
    year = request.args.get('year', type=int)
    service = request.args.get('service')

    if not query:
        return jsonify({
            "error": "Invalid input",
            "message": "Search query is required"
        }), 400

    if len(query) < 2:
        return jsonify({
            "error": "Invalid input",
            "message": "Search query must be at least 2 characters"
        }), 400

    movies = Movie.search(query, year, service)
    
    return jsonify({
        "results": [movie.to_dict() for movie in movies],
        "count": len(movies),
        "query": query,
        "filters": {
            "year": year,
            "service": service
        }
    })

@api.route('/movies/<int:movie_id>')
def get_movie(movie_id: int):
    movie = Movie.get_by_id(movie_id)
    if not movie:
        return jsonify({
            "error": "Not found",
            "message": f"Movie with ID {movie_id} not found"
        }), 404
    
    return jsonify(movie.to_dict())

@api.route('/movies/<int:movie_id>/streaming')
def get_movie_streaming(movie_id: int):
    movie = Movie.get_by_id(movie_id)
    if not movie:
        return jsonify({
            "error": "Not found",
            "message": f"Movie with ID {movie_id} not found"
        }), 404
    
    return jsonify({
        "movie_id": movie.id,
        "title": movie.title,
        "streaming_services": movie.streaming_services
    })

@api.route('/health')
def health_check():
    db = get_db()
    if db:
        return jsonify({
            "status": "healthy",
            "database": "connected"
        })
    return jsonify({
        "status": "unhealthy",
        "database": "disconnected"
    }), 500

@api.route('/movies/trending')
def get_trending_movies():
    """Get most searched/popular movies"""
    try:
        movies = Movie.get_trending(limit=10)  # Get top 10 trending movies
        return jsonify({
            "results": [movie.to_dict() for movie in movies],
            "count": len(movies)
        })
    except Exception as e:
        current_app.logger.error(f"Error fetching trending movies: {e}")
        return jsonify({
            "error": "Server error",
            "message": "Failed to fetch trending movies"
        }), 500

@api.route('/services')
def get_streaming_services():
    """Get all available streaming services"""
    try:
        cursor = get_db().cursor()
        cursor.execute("SELECT service_name FROM Streaming_Services ORDER BY service_name")
        services = [row['service_name'] for row in cursor.fetchall()]
        
        return jsonify({
            "services": services
        })
    except Exception as e:
        current_app.logger.error(f"Error fetching streaming services: {e}")
        return jsonify({
            "error": "Server error",
            "message": "Failed to fetch streaming services"
        }), 500 