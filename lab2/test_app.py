import pytest
from app import app
import re

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_url_params(client):
    response = client.get('/url_params?param1=value1&param2=value2')
    assert b'param1' in response.data
    assert b'value1' in response.data
    assert b'param2' in response.data
    assert b'value2' in response.data

def test_headers(client):
    headers = {'User-Agent': 'Test', 'Accept': 'text/html'}
    response = client.get('/headers', headers=headers)
    assert b'User-Agent' in response.data
    assert b'Test' in response.data

def test_cookies_set(client):
    response = client.get('/cookies')
    assert 'user_id=12345' in response.headers.get('Set-Cookie', '')

def test_cookies_delete(client):
    # Сначала устанавливаем cookie через первый запрос
    client.get('/cookies')
    # Затем делаем второй запрос, который должен удалить cookie
    response = client.get('/cookies')
    assert 'Expires=Thu, 01 Jan 1970 00:00:00 GMT' in response.headers.get('Set-Cookie', '')

def test_form_params_get(client):
    response = client.get('/form_params')
    assert b'name' in response.data
    assert b'email' in response.data

def test_form_params_post(client):
    response = client.post('/form_params', data={
        'name': 'Test User',
        'email': 'test@example.com'
    })
    assert b'Test User' in response.data
    assert b'test@example.com' in response.data

def test_phone_valid_format_1(client):
    response = client.post('/phone', data={'phone': '+7 (123) 456-75-90'})
    assert b'8-123-456-75-90' in response.data
    assert b'is-invalid' not in response.data

def test_phone_valid_format_2(client):
    response = client.post('/phone', data={'phone': '8(123)4567590'})
    assert b'8-123-456-75-90' in response.data
    assert b'is-invalid' not in response.data

def test_phone_valid_format_3(client):
    response = client.post('/phone', data={'phone': '123.456.75.90'})
    assert b'8-123-456-75-90' in response.data
    assert b'is-invalid' not in response.data

def test_phone_invalid_digits_count(client):
    response = client.post('/phone', data={'phone': '123456789'})
    assert b'is-invalid' in response.data
    assert 'Недопустимый ввод. Неверное количество цифр.' in response.data.decode('utf-8')

def test_phone_invalid_symbols(client):
    response = client.post('/phone', data={'phone': '123@456-75-90'})
    assert b'is-invalid' in response.data
    assert 'Недопустимый ввод. В номере телефона встречаются недопустимые символы.' in response.data.decode('utf-8')

def test_phone_empty_input(client):
    response = client.post('/phone', data={'phone': ''})
    assert b'is-invalid' in response.data
    assert 'Недопустимый ввод. Неверное количество цифр.' in response.data.decode('utf-8')

def test_phone_invalid_start(client):
    response = client.post('/phone', data={'phone': '91234567890'})
    assert b'is-invalid' in response.data
    assert 'Недопустимый ввод. Неверное количество цифр.' in response.data.decode('utf-8')

def test_phone_with_spaces(client):
    response = client.post('/phone', data={'phone': '123 456 75 90'})
    assert b'8-123-456-75-90' in response.data
    assert b'is-invalid' not in response.data

def test_phone_with_mixed_separators(client):
    response = client.post('/phone', data={'phone': '123-456.75(90)'})
    assert b'8-123-456-75-90' in response.data
    assert b'is-invalid' not in response.data 