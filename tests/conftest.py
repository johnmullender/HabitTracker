import os
import pytest

# Set flag BEFORE importing app
os.environ['FLASK_ENV'] = 'TESTING'

from app import app, db

# Create and destroy temporary database for tests
@pytest.fixture()
def client():
    app.config['TESTING']= True
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


# Create helper class to automatically log in test User
class AuthActions:
    def __init__(self, client):
        self._client = client

    def login(self, username, password):
        self._client.post('/register', data={'username': username, 'password': password})
        self._client.post('/login', data={'username': username, 'password': password})


# Use helper class for login
@pytest.fixture()
def auth(client):
    return AuthActions(client)