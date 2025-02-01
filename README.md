# Movie Streaming Search API

A Flask-based RESTful API that allows users to search for movies and find which streaming services offer them. The application follows RESTful principles and includes both a backend API and a simple frontend interface.

## Features

- RESTful API architecture
- Search movies by title
- Filter results by year and streaming service
- Real-time search with debouncing
- Responsive web interface
- Input validation and sanitization
- Error handling and user feedback
- SQLite database integration
- Cross-Origin Resource Sharing (CORS) support
- Blueprint-based routing
- Configuration management for different environments

## Prerequisites

- Python 3.8+
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd movie-streaming-search
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python database.py
```

## Running the Application

1. Start the Flask server:
```bash
python app.py
```

2. Open a web browser and navigate to:
```
http://localhost:5000/web
```

## API Endpoints

### Root
- **URL**: `/`
- **Method**: `GET`
- **Description**: Get API information and available endpoints
- **Success Response**: `200 OK`
```json
{
    "message": "Movie API is running",
    "endpoints": {
        "search": "/api/movies/search?q=<query>",
        "movie": "/api/movies/<id>",
        "streaming": "/api/movies/<id>/streaming",
        "health": "/api/health",
        "web_interface": "/web"
    }
}
```

### Search Movies
- **URL**: `/api/movies/search`
- **Method**: `GET`
- **Query Parameters**:
  - `q` (required): Search query (minimum 2 characters)
  - `year` (optional): Filter by release year
  - `service` (optional): Filter by streaming service
- **Success Response**: `200 OK`
```json
{
    "results": [
        {
            "id": 1,
            "title": "The Matrix",
            "year": 1999,
            "streaming_services": ["Netflix", "Amazon Prime"]
        }
    ],
    "count": 1,
    "query": "matrix",
    "filters": {
        "year": null,
        "service": null
    }
}
```

### Get Movie
- **URL**: `/api/movies/<id>`
- **Method**: `GET`
- **Success Response**: `200 OK`
```json
{
    "id": 1,
    "title": "The Matrix",
    "year": 1999,
    "streaming_services": ["Netflix", "Amazon Prime"]
}
```

### Get Movie Streaming Services
- **URL**: `/api/movies/<id>/streaming`
- **Method**: `GET`
- **Success Response**: `200 OK`
```json
{
    "movie_id": 1,
    "title": "The Matrix",
    "streaming_services": ["Netflix", "Amazon Prime"]
}
```

### Health Check
- **URL**: `/api/health`
- **Method**: `GET`
- **Success Response**: `200 OK`
```json
{
    "status": "healthy",
    "database": "connected"
}
```

## Project Structure

```
movie-streaming-search/
├── app/
│   ├── __init__.py          # Application factory
│   ├── models/              # Database models
│   │   ├── __init__.py
│   │   └── movie.py        # Movie model and database operations
│   ├── routes/              # Route handlers
│   │   ├── __init__.py
│   │   ├── api.py          # API endpoints
│   │   └── web.py          # Web interface routes
│   ├── services/            # Application services
│   │   ├── __init__.py
│   │   └── database.py     # Database connection handling
│   └── templates/           # HTML templates
│       └── index.html      # Web interface template
├── app.py                   # Application entry point
├── config.py                # Configuration settings
├── tests.py                 # Test suite
├── requirements.txt         # Python dependencies
└── README.md               # Documentation
```

## Configuration

The application supports multiple environments through configuration classes:
- Development (default)
- Testing
- Production

Configuration can be set using environment variables:
```bash
export FLASK_ENV=development  # or testing, production
```

## Database Schema

1. **Movies**
   - `id` (Primary Key, AUTO_INCREMENT)
   - `title` (VARCHAR)
   - `release_year` (INTEGER)

2. **Streaming_Services**
   - `id` (Primary Key, AUTO_INCREMENT)
   - `service_name` (VARCHAR, UNIQUE)

3. **Movie_Streamings**
   - `movie_id` (Foreign Key)
   - `service_id` (Foreign Key)
   - Primary Key (movie_id, service_id)

## Error Handling

The API includes comprehensive error handling for:
- Invalid input validation (400)
- Resource not found (404)
- Database connection issues (500)
- Server errors (500)

Error responses follow a consistent format:
```json
{
    "error": "error_type",
    "message": "Detailed error message"
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
