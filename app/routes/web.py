from flask import Blueprint, render_template

web = Blueprint('web', __name__)

@web.route('/')
def root():
    return {
        "message": "Movie API is running",
        "endpoints": {
            "search": "/api/movies/search?q=<query>",
            "movie": "/api/movies/<id>",
            "streaming": "/api/movies/<id>/streaming",
            "health": "/api/health",
            "web_interface": "/web"
        }
    }

@web.route('/web')
def serve_web():
    return render_template('index.html') 