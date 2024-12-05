from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy instance
db = SQLAlchemy()

"""
The `db` object is an instance of `SQLAlchemy`, which is used for interacting with the database in Flask applications.
It provides an ORM (Object Relational Mapping) interface that allows you to define models (tables) and perform CRUD operations 
without writing raw SQL queries.

This instance is later bound to a Flask application using `db.init_app(app)` and can be used to manage database sessions.

How to use `db`:

1. **Model Definition**: 
    - You define classes that represent database tables. These classes inherit from `db.Model`.
    
2. **Performing Queries**: 
    - You can query the database and manipulate data using Python objects.
    
3. **Managing Transactions**: 
    - `db.session` manages all database transactions (commit, rollback, etc.).

Example Usage:

1. **Model Definition**:
    - Define models by inheriting from `db.Model` and specifying columns using `db.Column`.

2. **Performing CRUD Operations**:
    - Add new records: `db.session.add(instance)`
    - Query records: `Model.query.all()`, `Model.query.filter_by(...)`
    - Commit changes: `db.session.commit()`

Example Code:

```python
# Example of defining a model in SQLAlchemy

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    name = db.Column(db.String(100), nullable=False)  # String column for user name
    email = db.Column(db.String(100), unique=True, nullable=False)  # Unique email field
    
    def __repr__(self):
        return f"<User {self.name}>"

# Example of creating the database and adding a record
def init_db():
    # This will create all tables defined in the models
    db.create_all()

    # Creating a new User record
    new_user = User(name="John Doe", email="johndoe@example.com")
    db.session.add(new_user)  # Add the new record to the session
    db.session.commit()  # Commit the session to save changes

# Example of querying the database
def get_all_users():
    users = User.query.all()  # Retrieve all User records
    return users
