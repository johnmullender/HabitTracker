from app import User

def test_register_user(client):
    # Create a User
    client.post('/register', data={'username': 'tester', 'password': '123'})

    # Check database to see if they exist
    assert User.query.filter_by(username='tester').count() == 1


def test_register_duplicate(client):
    # Register a dummy user
    client.post('/register', data={'username': 'tester', 'password': '123'})

    # Register a duplicate
    response = client.post('/register', data={'username': 'tester', 'password': '123'}, follow_redirects=True)

    # Should flash error message
    assert b"An account with that username already exists" in response.data


def test_login_happy(client):
    # Create a User
    client.post('/register', data={'username': 'tester', 'password': '123'})

    # Attempt to login with CORRECT credentials
    response = client.post('/login', data={'username': 'tester', 'password': '123'})

    # Should redirect (302) to dashboard
    assert response.status_code == 302


def test_login_sad(client):
    # Create a User
    client.post('/register', data={'username': 'tester', 'password': '123'})

    # Attempt to login with INCORRECT credentials
    response = client.post('/login', data={'username': 'tester', 'password': 'WRONG_PASS'})

    # Should stay on login page and show error
    assert response.status_code == 200


def test_unauthorized_access(client):
    response = client.get('/', follow_redirects= True)
    assert b"Create An Account" in response.data


def test_special_char_registration(client):
    # Test basic special characters
    response = client.post('/register', data={'username': 'test!@#^&%$&^', 'password': '123'}, follow_redirects=True)
    assert b'Username must consist only of letters and numbers' in response.data
    assert db.session.query(User).count() == 0


def test_sql_injection_registration(client):
    # Test SQL injection
    response = client.post('/register', data= {'username': "DROP TABLE users:--", 'password': '123'}, follow_redirects=True)
    assert b'Username must consist only of letters and numbers' in response.data
    assert db.session.query(User).count() == 0


def test_xss_registration(client):
    # Test malicious username attempt
    response = client.post('/register', data={"username": '<script>', 'password': '123'}, follow_redirects=True)
    assert b'Username must consist only of letters and numbers' in response.data
    assert db.session.query(User).count() == 0


def test_whitespace_registration(client):
    # Test whitespace username attempt
    response = client.post('/register', data={'username': '        ', 'password': '123'}, follow_redirects=True)
    assert b'Username must consist only of letters and numbers' in response.data
    assert db.session.query(User).count() == 0

