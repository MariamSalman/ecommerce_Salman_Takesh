from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()

"""
The `db` object is an instance of `SQLAlchemy` used for interacting with the database in a Flask application.

It provides an interface for querying and manipulating database tables. Typically, it is used for:

1. Defining models that represent tables in the database.
2. Performing CRUD operations (Create, Read, Update, Delete).
3. Managing the session lifecycle (commit, rollback, etc.).

Usage:
- The `db` object is usually initialized in the main application file using `db.init_app(app)`, where `app` is the Flask application instance.
- It is used for creating tables, querying records, and handling relationships between models.

For example:
    - `db.create_all()` is used to create all tables based on the defined models.
    - `db.session.add()` is used to add new records to the database.
    - `db.session.commit()` is used to commit transactions to the database.
"""
