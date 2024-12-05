from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()

"""
The `db` object is an instance of `SQLAlchemy` used for interacting with the database in a Flask application.

It provides an interface for querying and manipulating database tables. Typically, it is used for:

1. Defining models that represent tables in the database.
2. Performing CRUD operations.
3. Managing the session lifecycle.
"""
