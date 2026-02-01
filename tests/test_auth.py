from app import User, db, app
import pytest

### Test basic User registration ###
def test_register_user(client):
    # Create a User
    client.post('/register', data={'username': 'tester', 'password': '12345678'})

    # Check database to see if they exist
    assert User.query.filter_by(username='tester').count() == 1


### Test duplicate registration does not go through ###
def test_register_duplicate(client):
    # Register a dummy user
    client.post('/register', data={'username': 'tester', 'password': '12345678'})

    # Register a duplicate
    response = client.post('/register', data={'username': 'tester', 'password': '12345678'}, follow_redirects=True)

    # Should flash error message
    assert b"An account with that username already exists" in response.data


### Test regular login ###
def test_login_happy(client):
    # Create a User
    client.post('/register', data={'username': 'tester', 'password': '12345678'})

    # Attempt to login with CORRECT credentials
    response = client.post('/login', data={'username': 'tester', 'password': '12345678'})

    # Should redirect (302) to dashboard
    assert response.status_code == 302


### Test wrong password login ###
def test_login_sad(client):
    # Create a User
    client.post('/register', data={'username': 'tester', 'password': '12345678'})

    # Attempt to login with INCORRECT credentials
    response = client.post('/login', data={'username': 'tester', 'password': 'WRONG_PASS'})

    # Should stay on login page and show error
    assert response.status_code == 200


### Test invalid usernames ###
@pytest.mark.parametrize('test_username', ['test^&^%$#$$%^&%', 'DROP TABLE users:--',
                                            '<script>', '          ', 'a' * 40])
def test_invalid_usernames(client, test_username):
    response = client.post('/register', data={'username': test_username, 'password': '12345678'}, follow_redirects= True)
    assert b'Username must consist only of letters and numbers. Max 30 characters' in response.data
    assert db.session.query(User).count() == 0


### Test user is able to log in with case-insensitive username ###
def test_case_insensitive_login(client):
    client.post('/register', data={'username': 'TestUser', 'password': '12345678'})
    # User attempts to login with lowercase username
    response = client.post('/login', data={'username': 'testuser', 'password': '12345678'}, follow_redirects=True)
    assert b'Welcome' in response.data
    assert db.session.query(User).count() == 1


### Test invalid passwords ###
@pytest.mark.parametrize('test_password', ['1', 'a' * 65, '               '])
def test_invalid_passwords(client, test_password):
    response = client.post('/register', data={'username': 'tester', 'password': test_password}, follow_redirects= True)
    assert b'Password must be between 8 and 64 characters long. Password cannot be all whitespace' in response.data
    assert db.session.query(User).count() == 0


### Test to ensure password hashing in database ###
def test_password_hashing(client):
    client.post('/register', data={'username': 'tester', 'password': 'password123'})
    user = User.query.filter_by(username='tester').first()
    assert user.password != 'password123'
    assert ":" in user.password


### Test user is not able to access homepage w/ invalid session ID ###
def test_invalid_session_id(client):
    # Give dummy user invalid session id
    with client.session_transaction() as sess:
        sess['user_id'] = 99999

    # Make sure user gets redirected to register page
    response = client.post('/', follow_redirects= True)
    assert b'Create An Account To Get Started!' in response.data

    # Ensure invalid key is removed from session
    with client.session_transaction() as sess:
        assert 'user_id' not in sess


### Test user cannot access home page after log out ###
def test_logout_cannot_access_home(client, auth):
    # Log in test user
    auth.login('tester', '12345678')

    # Log test user out
    client.get('/logout', follow_redirects= True)

    # Logged out user attempts to access home page
    response = client.get('/', follow_redirects= True)
    assert b'Create An Account To Get Started!' in response.data


### Test user cannot access home page without logging in ###
def test_unauthorized_access(client):
    response = client.get('/', follow_redirects= True)
    assert b"Create An Account" in response.data


### Test attempts to gain unauthorized access to various routes ###
@pytest.mark.parametrize('route', ['/profile/tester', 'search', '/follow/tester', '/unfollow/tester'])
def test_unauthorized_access(client, route):
    response= client.post(route, follow_redirects= True)
    assert b'Create An Account To Get Started!' in response.data