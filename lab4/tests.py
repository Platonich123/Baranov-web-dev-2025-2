import pytest
from app import app, db, User, Role
from werkzeug.security import generate_password_hash
from datetime import datetime, UTC

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            role = Role(name='admin', description='Administrator')
            db.session.add(role)
            user = User(
                login='testuser',
                first_name='Test',
                last_name='User',
                role_id=1,
                created_at=datetime.now(UTC)
            )
            user.set_password('Test123!')
            db.session.add(user)
            db.session.commit()
        yield client
        with app.app_context():
            db.session.remove()
            db.drop_all()

def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'User' in response.data
    assert b'Test' in response.data

def test_login_success(client):
    response = client.post('/login', data={
        'login': 'testuser',
        'password': 'Test123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'User' in response.data
    assert b'Test' in response.data

def test_login_failure(client):
    response = client.post('/login', data={
        'login': 'testuser',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid login or password' in response.data

def test_create_user(client):
    client.post('/login', data={
        'login': 'testuser',
        'password': 'Test123!'
    })
    
    response = client.post('/user/new', data={
        'login': 'newuser',
        'password': 'NewPass123!',
        'first_name': 'New',
        'last_name': 'User',
        'role_id': '1'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'User successfully created' in response.data

def test_edit_user(client):
    client.post('/login', data={
        'login': 'testuser',
        'password': 'Test123!'
    })
    
    response = client.post('/user/1/edit', data={
        'first_name': 'Updated',
        'last_name': 'User',
        'role_id': '1'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'User successfully updated' in response.data

def test_delete_user(client):
    client.post('/login', data={
        'login': 'testuser',
        'password': 'Test123!'
    })
    
    response = client.post('/user/1/delete', follow_redirects=True)
    assert response.status_code == 200
    assert b'User successfully deleted' in response.data

def test_change_password(client):
    client.post('/login', data={
        'login': 'testuser',
        'password': 'Test123!'
    })
    
    response = client.post('/change-password', data={
        'old_password': 'Test123!',
        'new_password': 'NewPass123!',
        'confirm_password': 'NewPass123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Password successfully changed' in response.data

def test_password_validation(client):
    client.post('/login', data={
        'login': 'testuser',
        'password': 'Test123!'
    })
    
    response = client.post('/user/new', data={
        'login': 'newuser',
        'password': 'weak',
        'first_name': 'New',
        'last_name': 'User',
        'role_id': '1'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Password must be between 8 and 128 characters' in response.data

def test_login_validation(client):
    client.post('/login', data={
        'login': 'testuser',
        'password': 'Test123!'
    })

    response = client.post('/user/new', data={
        'login': 'a',
        'password': 'NewPass123!',
        'first_name': 'New',
        'last_name': 'User',
        'role_id': '1'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Login must contain only Latin letters and numbers, minimum 5 characters' in response.data 