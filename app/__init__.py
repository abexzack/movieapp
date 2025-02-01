from flask import Flask
from flask_cors import CORS
from config import config
from app.services.database import close_db

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    CORS(app)

    # Register database teardown
    app.teardown_appcontext(close_db)

    # Register blueprints
    from app.routes.api import api
    from app.routes.web import web
    
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(web)

    # Register error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return {
            "error": "Not found",
            "message": "The requested resource was not found"
        }, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {
            "error": "Server error",
            "message": "An unexpected error occurred. Please try again later."
        }, 500

    return app 