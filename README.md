# Movie Streaming Search API

A Flask-based REST API that allows users to search for movies and find which streaming services offer them. The application includes both a backend API and a simple frontend interface.

## Features

- Search movies by title
- Filter results by year and streaming service
- Real-time search with debouncing
- Responsive web interface
- Input validation and sanitization
- Error handling and user feedback
- SQLite database integration
- Cross-Origin Resource Sharing (CORS) support

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
            "streaming_services": ["Netflix", "Amazon Prime"],
            "exact_match": true
        }
    ],
    "count": 1,
    "query": "matrix"
}
```

### Get Streaming Services
- **URL**: `/api/movies/<movie_id>/streaming`
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

## Running Tests

Run the test suite:
```bash
python -m unittest tests.py
```

Run tests with coverage:
```bash
coverage run -m unittest tests.py
coverage report
```

## Project Structure

```
movie-streaming-search/
├── app.py              # Main Flask application
├── database.py         # Database initialization and setup
├── index.html         # Frontend interface
├── tests.py           # Test suite
├── requirements.txt   # Python dependencies
└── README.md         # This file
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
- Invalid input validation
- Database connection issues
- Resource not found
- Server errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
