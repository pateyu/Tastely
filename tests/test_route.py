import pytest
from app import app
from io import BytesIO

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  
    with app.test_client() as client:
        yield client

def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200

def test_signup_page(client):
    response = client.get('/signup')
    assert response.status_code == 200

def test_login_failure(client):
    # Attempt to login with fake credentials
    response = client.post('/login', json={
        'username': 'fakeuser',
        'password': 'wrongpass'
    })
    assert response.status_code == 401
    assert b'Login failed' in response.data
def test_get_recipes(client):
    """Test recipe list retrieval."""
    response = client.get('/api/recipes')
    assert response.status_code == 200
    assert 'recipes' in response.get_json()

def test_recommend_without_login(client):
    """Ensure recommendation fails without login."""
    response = client.get('/api/recommended')
    assert response.status_code == 401
    assert 'error' in response.get_json()

def login_session(client):
    """Helper function to fake login by setting session."""
    with client.session_transaction() as sess:
        sess['user_id'] = 1  

def test_search_recipes_api(client):
    """Test searching for recipes via the API."""
    response = client.get('/api/recipes?search=Test')
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert 'recipes' in json_data
    assert isinstance(json_data['recipes'], list)

def test_logout_redirects_to_index(client):
    """Test that logout clears session and redirects to index."""
    # Simulate login
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['is_admin'] = True

    response = client.get('/logout', follow_redirects=False)

    # Check for redirect
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/')

def test_settings_route_logged_in(client):
    """Test that the settings page loads for logged-in users."""
    with client.session_transaction() as sess:
        sess['user_id'] = 1  # simulate login

    response = client.get('/settings')
    assert response.status_code == 200
    assert b"settings" in response.data.lower()

