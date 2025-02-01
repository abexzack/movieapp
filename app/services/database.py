import sqlite3
from flask import current_app, g
from sqlite3 import Error

def get_db():
    if 'db' not in g:
        try:
            g.db = sqlite3.connect(current_app.config['DATABASE'])
            g.db.row_factory = sqlite3.Row
        except Error as e:
            current_app.logger.error(f"Database connection error: {e}")
            return None
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close() 