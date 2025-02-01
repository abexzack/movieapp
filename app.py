from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import sqlite3
from sqlite3 import Error
import re
from typing import Tuple, Optional

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Default database path
app.config['DATABASE'] = 'movie_streaming.db'

# Add basic logging
@app.before_request
def log_request_info():
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Body: %s', request.get_data())
    app.logger.debug('Path: %s', request.path)

def get_db_connection():
    try:
        conn = sqlite3.connect(app.config['DATABASE'])
        conn.row_factory = sqlite3.Row  # This enables column access by name: row['column_name']
        return conn
    except Error as e:
        print(f"Database connection error: {e}")
        return None

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        "message": "Movie API is running",
        "endpoints": {
            "search": "/api/movies/search?q=<query>",
            "streaming": "/api/movies/<movie_id>/streaming",
            "health": "/api/health"
        }
    })

def validate_search_query(query: str) -> Tuple[bool, Optional[str]]:
    """
    Validate the search query and return (is_valid, error_message)
    """
    if not query:
        return False, "Search query is required"
    
    if len(query) < 2:
        return False, "Search query must be at least 2 characters long"
    
    if len(query) > 100:
        return False, "Search query is too long (maximum 100 characters)"
    
    # Check for invalid characters
    if not re.match(r'^[a-zA-Z0-9\s\-:,.\']+$', query):
        return False, "Search query contains invalid characters"
    
    # Check for SQL injection attempts
    suspicious_patterns = ['--', ';', 'DROP', 'DELETE', 'UPDATE', 'INSERT']
    if any(pattern.lower() in query.lower() for pattern in suspicious_patterns):
        return False, "Invalid search query"
    
    return True, None

@app.route('/api/movies/search', methods=['GET'])
def search_movies():
    conn = None  # Initialize connection variable
    try:
        query = request.args.get('q', '').strip()
        
        # Add debug logging
        app.logger.debug(f"Search query: {query}")
        app.logger.debug(f"Using database: {app.config['DATABASE']}")
        
        # Validate input
        is_valid, error_message = validate_search_query(query)
        if not is_valid:
            return jsonify({
                "error": "Invalid input",
                "message": error_message
            }), 400

        # Get optional filters
        year = request.args.get('year')
        service = request.args.get('service')
        
        conn = get_db_connection()
        if not conn:
            return jsonify({
                "error": "Database error",
                "message": "Could not connect to database"
            }), 500

        cursor = conn.cursor()
        
        # Build the query dynamically based on filters
        query_parts = [
            "SELECT DISTINCT",
            "    m.id,",
            "    m.title,",
            "    m.release_year,",
            "    GROUP_CONCAT(DISTINCT s.service_name) as streaming_services",
            "FROM Movies m",
            "LEFT JOIN Movie_Streamings ms ON m.id = ms.movie_id",
            "LEFT JOIN Streaming_Services s ON ms.service_id = s.id",
            "WHERE LOWER(m.title) LIKE ?"
        ]
        params = [f'%{query.lower()}%']

        # Add year filter if provided
        if year:
            if year.isdigit():
                query_parts.append("AND m.release_year = ?")
                params.append(int(year))
            else:
                # Invalid year format, ignore the filter
                year = None

        # Add streaming service filter if provided
        if service:
            query_parts.append("AND EXISTS (")
            query_parts.append("    SELECT 1 FROM Movie_Streamings ms2")
            query_parts.append("    JOIN Streaming_Services s2 ON ms2.service_id = s2.id")
            query_parts.append("    WHERE ms2.movie_id = m.id")
            query_parts.append("    AND LOWER(s2.service_name) = ?")
            query_parts.append(")")
            params.append(service.lower())

        # Add group by and order by
        query_parts.extend([
            "GROUP BY m.id",
            "ORDER BY",
            "    CASE WHEN LOWER(m.title) = ? THEN 1",
            "         WHEN LOWER(m.title) LIKE ? THEN 2",
            "         ELSE 3 END,",
            "    m.release_year DESC"
        ])
        params.extend([query.lower(), f'{query.lower()}%'])

        # Execute the query
        cursor.execute(" ".join(query_parts), params)
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            streaming_services = (
                row['streaming_services'].split(',') 
                if row['streaming_services'] 
                else []
            )
            results.append({
                'id': row['id'],
                'title': row['title'],
                'year': row['release_year'],
                'streaming_services': streaming_services,
                'exact_match': row['title'].lower() == query.lower()
            })

        response_data = {
            "results": results,
            "count": len(results),
            "query": query,
            "filters": {
                "year": int(year) if year and year.isdigit() else None,
                "service": service if service else None
            }
        }

        # Add search metadata
        if len(results) == 0:
            response_data["suggestion"] = "Try using fewer words or check your spelling"
        
        # Add debug logging for results
        app.logger.debug(f"Found {len(results)} results")
        app.logger.debug(f"SQL Query: {' '.join(query_parts)}")
        app.logger.debug(f"SQL Params: {params}")
        
        return jsonify(response_data)

    except Error as e:
        app.logger.error(f"Database error: {e}")
        return jsonify({
            "error": "Server error",
            "message": "An unexpected error occurred while searching"
        }), 500
        
    finally:
        if conn:
            conn.close()

@app.route('/api/movies/<int:movie_id>/streaming', methods=['GET'])
def get_streaming_services(movie_id):
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                "error": "Database error",
                "message": "Could not connect to database"
            }), 500

        cursor = conn.cursor()
        
        # Get movie and its streaming services
        cursor.execute("""
            SELECT 
                m.id,
                m.title,
                GROUP_CONCAT(s.service_name) as streaming_services
            FROM Movies m
            LEFT JOIN Movie_Streamings ms ON m.id = ms.movie_id
            LEFT JOIN Streaming_Services s ON ms.service_id = s.id
            WHERE m.id = ?
            GROUP BY m.id
        """, (movie_id,))
        
        row = cursor.fetchone()
        
        if not row:
            return jsonify({
                "error": "Not found",
                "message": f"Movie with ID {movie_id} not found"
            }), 404

        streaming_services = row['streaming_services'].split(',') if row['streaming_services'] else []
        
        return jsonify({
            "movie_id": row['id'],
            "title": row['title'],
            "streaming_services": streaming_services
        })

    except Error as e:
        app.logger.error(f"Database error: {e}")
        return jsonify({
            "error": "Server error",
            "message": "An unexpected error occurred while fetching streaming services"
        }), 500
        
    finally:
        if conn:
            conn.close()

@app.route('/api/health', methods=['GET'])
def health_check():
    conn = get_db_connection()
    if conn:
        conn.close()
        return jsonify({"status": "healthy", "database": "connected"})
    return jsonify({"status": "unhealthy", "database": "disconnected"}), 500

@app.route('/web')
def serve_web():
    return send_file('index.html')

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({
        "error": "Not found",
        "message": "The requested resource was not found"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Server error",
        "message": "An unexpected error occurred. Please try again later."
    }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 