"""Initialize the Flask application and database.

This module creates the Flask application instance, configures
SQLAlchemy to use a SQLite database and registers the database models.
The use of SQLite is convenient because it is built into Python and
does not require a separate server. However, writes occur sequentially,
so heavy write loads can slow down【779944838122452†L12-L20】.  For this
project, which will be used to define CRM communication schedules,
SQLite is sufficient.

The application enables foreign‑key support for SQLite and
configures cascade behaviour on foreign keys so that deleting a
parent record automatically deletes dependent records; SQLite
implements this behaviour via the `ON DELETE CASCADE` clause【685663684588476†L559-L563】.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    """Factory function to create and configure the Flask app."""
    app = Flask(__name__)
    # Secret key for sessions/flash messages. Replace with a strong value in production.
    app.config['SECRET_KEY'] = 'dev'
    # SQLite database file. The database will be created automatically.
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///regua_comunicacao.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialise database
    db.init_app(app)

    # Enable SQLite foreign key enforcement each time a connection is created.
    # Without this pragma SQLite ignores foreign keys by default.【685663684588476†L559-L563】
    @app.before_request
    def before_request():
        from sqlalchemy import text
        db.session.execute(text('PRAGMA foreign_keys = ON'))

    # Import models so that they are registered with SQLAlchemy
    from . import models  # noqa: F401

    # Register routes
    from .routes import bp as routes_bp  # noqa: F401
    app.register_blueprint(routes_bp)

    # Create database tables if they do not exist
    with app.app_context():
        db.create_all()

    return app