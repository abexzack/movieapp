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

## API Documentation

### Authentication

Currently, the API is open and does not require authentication.

### Base URL

```
http://localhost:5000/api
```

### Response Format

All responses are in JSON format. Successful responses have a 200 status code and contain the requested data. Error responses include an error message and appropriate status code.

### Endpoints

#### 1. Search Movies

Search for movies with optional filters.

```
GET /api/movies/search
```

**Query Parameters:**
- `q` (required): Search query string
  - Minimum length: 2 characters
  - Example: `matrix`
- `year` (optional): Filter by release year
  - Format: YYYY
  - Example: `1999`
- `service` (optional): Filter by streaming service
  - Case insensitive
  - Example: `netflix`

**Success Response (200 OK):**
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
        "year": 1999,
        "service": "netflix"
    }
}
```

**Error Responses:**
- `400 Bad Request`: Invalid or missing query parameter
```json
{
    "error": "Invalid input",
    "message": "Search query must be at least 2 characters"
}
```

#### 2. Get Movie Details

Retrieve detailed information about a specific movie.

```
GET /api/movies/<id>
```

**URL Parameters:**
- `id`: Movie ID (integer)

**Success Response (200 OK):**
```json
{
    "id": 1,
    "title": "The Matrix",
    "year": 1999,
    "streaming_services": ["Netflix", "Amazon Prime"]
}
```

**Error Response:**
- `404 Not Found`: Movie not found
```json
{
    "error": "Not found",
    "message": "Movie with ID 1 not found"
}
```

#### 3. Get Movie Streaming Services

Get streaming service availability for a specific movie.

```
GET /api/movies/<id>/streaming
```

**URL Parameters:**
- `id`: Movie ID (integer)

**Success Response (200 OK):**
```json
{
    "movie_id": 1,
    "title": "The Matrix",
    "streaming_services": ["Netflix", "Amazon Prime"]
}
```

**Error Response:**
- `404 Not Found`: Movie not found
```json
{
    "error": "Not found",
    "message": "Movie with ID 1 not found"
}
```

#### 4. Health Check

Check API and database health status.

```
GET /api/health
```

**Success Response (200 OK):**
```json
{
    "status": "healthy",
    "database": "connected"
}
```

**Error Response:**
- `500 Server Error`: Database connection failed
```json
{
    "status": "unhealthy",
    "database": "disconnected"
}
```

### Common Error Responses

1. **400 Bad Request**
   - Invalid input parameters
   - Missing required fields
   - Validation failures

2. **404 Not Found**
   - Resource does not exist
   - Invalid endpoint

3. **500 Server Error**
   - Database connection issues
   - Internal server errors

### Rate Limiting

Currently, there are no rate limits implemented.

### Example Usage

#### Using cURL

```bash
# Search for movies
curl "http://localhost:5000/api/movies/search?q=matrix&year=1999&service=netflix"

# Get movie details
curl "http://localhost:5000/api/movies/1"

# Get streaming services
curl "http://localhost:5000/api/movies/1/streaming"

# Check health
curl "http://localhost:5000/api/health"
```

#### Using Python Requests

```python
import requests

# Search for movies
response = requests.get(
    "http://localhost:5000/api/movies/search",
    params={"q": "matrix", "year": 1999, "service": "netflix"}
)

# Get movie details
response = requests.get("http://localhost:5000/api/movies/1")

# Get streaming services
response = requests.get("http://localhost:5000/api/movies/1/streaming")
```

## Running Tests

The project uses Python's unittest framework with coverage reporting. Tests are organized into unit tests and integration tests.

### Test Structure
```
tests/
├── __init__.py
├── base.py                 # Base test class with common setup
├── run_tests.py           # Test runner with coverage
├── unit/                  # Unit tests
│   ├── __init__.py
│   └── test_movie_model.py
└── integration/           # Integration tests
    ├── __init__.py
    └── test_api.py
```

### Running Tests

1. Run all tests with coverage:
```bash
python -m tests.run_tests
```

2. Run specific test files:
```bash
python -m unittest tests/unit/test_movie_model.py
python -m unittest tests/integration/test_api.py
```

3. Run tests with verbose output:
```bash
python -m unittest -v
```

### Coverage Reports

After running tests with coverage, you can:

1. View coverage in terminal:
```bash
coverage report
```

2. Generate HTML coverage report:
```bash
coverage html
```
Then open `coverage_report/index.html` in your browser

### Test Categories

1. Unit Tests:
   - Movie model creation and serialization
   - Search functionality
   - Streaming service retrieval

2. Integration Tests:
   - API endpoints
   - Database interactions
   - Error handling

### Running Tests in Different Environments

```bash
# Development
FLASK_ENV=development python -m tests.run_tests

# Testing
FLASK_ENV=testing python -m tests.run_tests

# Production
FLASK_ENV=production python -m tests.run_tests
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
