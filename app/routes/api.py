from flask import Blueprint, request, jsonify
from app.models.movie import Movie
from typing import Optional

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
    from app.services.database import get_db
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