import pytest
from app import app
from flask import session
from flask_login import current_user

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess.clear()
        yield client

def test_visits_counter(client):
    # Check that visit counter works for different sessions
    response = client.get('/')
    assert b'You visited this page 1 time' in response.data
    
    response = client.get('/')
    assert b'You visited this page 2 times' in response.data
    
    # Create new session
    with client.session_transaction() as sess:
        sess.clear()
    
    response = client.get('/')
    assert b'You visited this page 1 time' in response.data

def test_login_success(client):
    response = client.post('/login', data={
        'username': 'user',
        'password': 'qwerty',
        'remember': True
    }, follow_redirects=True)
    assert b'Successfully logged in' in response.data
    assert b'Home page' in response.data

def test_login_failure(client):
    response = client.post('/login', data={
        'username': 'user',
        'password': 'wrong_password'
    })
    assert b'Invalid username or password' in response.data
    assert b'Login' in response.data

def test_secret_page_access(client):
    # Try to access without authentication
    response = client.get('/secret', follow_redirects=True)
    assert b'Login' in response.data
    
    # Authenticate
    client.post('/login', data={
        'username': 'user',
        'password': 'qwerty'
    })
    
    # Check access after authentication
    response = client.get('/secret')
    assert b'Secret page' in response.data

def test_remember_me(client):
    with client.session_transaction() as sess:
        sess.clear()
    
    response = client.post('/login', data={
        'username': 'user',
        'password': 'qwerty',
        'remember': True
    })
    
    # Check that user_id is in session
    with client.session_transaction() as sess:
        assert '_user_id' in sess

def test_navbar_links(client):
    # Check navbar for unauthenticated user
    response = client.get('/')
    assert b'Login' in response.data
    assert b'Secret page' not in response.data
    
    # Authenticate
    client.post('/login', data={
        'username': 'user',
        'password': 'qwerty'
    })
    
    # Check navbar for authenticated user
    response = client.get('/')
    assert b'Logout' in response.data
    assert b'Secret page' in response.data

def test_redirect_after_login(client):
    # Try to access secret page
    response = client.get('/secret', follow_redirects=True)
    assert b'Login' in response.data
    
    # Authenticate
    response = client.post('/login', data={
        'username': 'user',
        'password': 'qwerty'
    }, follow_redirects=True)
    
    # Check redirect to secret page
    assert b'Secret page' in response.data

def test_logout(client):
    # Authenticate
    client.post('/login', data={
        'username': 'user',
        'password': 'qwerty'
    })
    
    # Logout
    response = client.get('/logout', follow_redirects=True)
    assert b'Logged out successfully' in response.data
    assert b'Login' in response.data

def test_session_persistence(client):
    # Authenticate with remember me
    client.post('/login', data={
        'username': 'user',
        'password': 'qwerty',
        'remember': True
    })
    
    # Clear session
    with client.session_transaction() as sess:
        sess.clear()
    
    # Check that user is still authenticated
    response = client.get('/secret')
    assert b'Secret page' in response.data

def test_multiple_users_visits(client):
    # First user
    response = client.get('/')
    assert b'You visited this page 1 time' in response.data
    
    # Second user (new session)
    with client.session_transaction() as sess:
        sess.clear()
    
    response = client.get('/')
    assert b'You visited this page 1 time' in response.data 