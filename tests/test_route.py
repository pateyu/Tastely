import pytest
import uuid
from app import app
from flask import session

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client

def get_json_or_fail(response):
    if response.content_type != 'application/json':
        print("Expected JSON, got:", response.content_type)
        print("Body:\n", response.data.decode())
        assert False, "Non-JSON response"
    return response.get_json()

def signup(client, username="testuser", email="test@example.com", password="testpass"):
    return client.post('/signup', json={
        "username": username,
        "email": email,
        "password": password
    })

def login(client, username="testuser", password="testpass"):
    return client.post('/login', json={
        "username": username,
        "password": password
    })

def test_signup_success(client):
    unique_username = f"testuser_{uuid.uuid4().hex[:8]}"
    unique_email = f"{unique_username}@test.com"
    
    response = signup(client, username=unique_username, email=unique_email)
    assert response.status_code == 200
    data = get_json_or_fail(response)
    assert data['success']

def test_signup_duplicate_user(client):
    signup(client)
    response = signup(client)
    assert response.status_code == 409
    data = get_json_or_fail(response)
    assert not data['success']

def test_login_success(client):
    signup(client)
    response = login(client)
    assert response.status_code == 200
    data = get_json_or_fail(response)
    assert 'message' in data

def test_login_failure(client):
    response = login(client, username="invalid", password="wrong")
    assert response.status_code == 401
    data = get_json_or_fail(response)
    assert 'message' in data

def test_get_recipes(client):
    response = client.get('/api/recipes')
    assert response.status_code == 200
    data = get_json_or_fail(response)
    assert 'recipes' in data

def test_recommended_requires_login(client):
    response = client.get('/api/recommended')
    assert response.status_code == 401
    data = get_json_or_fail(response)
    assert 'error' in data

def test_authenticated_routes(client):
    signup(client)
    login(client)

    with client.session_transaction() as sess:
        sess['user_id'] = 1

    # settings page
    response = client.get('/settings')
    assert response.status_code == 200

    # dashboard page
    response = client.get('/dashboard')
    assert response.status_code == 200

def test_logout(client):
    signup(client)
    login(client)

    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['is_admin'] = False

    response = client.get('/logout', follow_redirects=False)
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/')
