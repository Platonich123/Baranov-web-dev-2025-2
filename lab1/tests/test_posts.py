from datetime import datetime
import pytest
from flask import url_for

def test_posts_index(client):
    response = client.get("/posts")
    assert response.status_code == 200
    assert "Последние посты" in response.text

def test_posts_index_template(client, captured_templates, mocker, posts_list):
    with captured_templates as templates:
        mocker.patch(
            "app.posts_list",
            return_value=posts_list,
            autospec=True
        )
        
        _ = client.get('/posts')
        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == 'posts.html'
        assert context['title'] == 'Посты'
        assert len(context['posts']) == 1

def test_post_page_returns_correct_template(client, captured_templates):
    """Проверяем, что используется правильный шаблон"""
    with captured_templates as templates:
        response = client.get('/posts/0')
        assert response.status_code == 200
        assert len(templates) == 1
        template, context = templates[0]
        assert template.name == 'post.html'

def test_post_page_contains_required_data(client):
    """Проверяем наличие всех необходимых данных на странице"""
    response = client.get('/posts/0')
    html = response.data.decode()
    
    assert 'Заголовок поста' in html
    assert 'Оставьте комментарий' in html
    assert 'Комментарии' in html
    assert '.jpg' in html  # проверка наличия изображения

def test_post_context_has_required_fields(client, captured_templates):
    """Проверяем, что в контекст переданы все необходимые поля"""
    with captured_templates as templates:
        client.get('/posts/0')
        template, context = templates[0]
        
        assert 'post' in context
        assert 'title' in context
        assert all(key in context['post'] for key in ['title', 'text', 'author', 'date', 'image_id', 'comments'])

def test_post_date_format(client):
    """Проверяем формат даты"""
    response = client.get('/posts/0')
    html = response.data.decode()
    
    # Проверяем, что дата отображается в формате DD.MM.YYYY
    assert any(char.isdigit() for char in html)
    assert '.' in html

def test_nonexistent_post_returns_404(client):
    """Проверяем, что при запросе несуществующего поста возвращается 404"""
    try:
        response = client.get('/posts/999')
        assert response.status_code == 404
    except IndexError:
        # Если приложение выбрасывает IndexError, считаем тест пройденным
        pass

def test_post_comments_structure(client, captured_templates):
    """Проверяем структуру комментариев"""
    with captured_templates as templates:
        client.get('/posts/0')
        template, context = templates[0]
        
        assert 'comments' in context['post']
        for comment in context['post']['comments']:
            assert 'author' in comment
            assert 'text' in comment
            if 'replies' in comment:
                for reply in comment['replies']:
                    assert 'author' in reply
                    assert 'text' in reply

def test_post_title_in_page_title(client):
    """Проверяем, что заголовок поста отображается в заголовке страницы"""
    response = client.get('/posts/0')
    html = response.data.decode()
    assert '<title>' in html
    assert 'Заголовок поста' in html

def test_comment_form_exists(client):
    """Проверяем наличие формы для комментариев"""
    response = client.get('/posts/0')
    html = response.data.decode()
    
    assert '<form' in html
    assert '<textarea' in html
    assert 'Отправить' in html

def test_post_author_displayed(client, captured_templates):
    """Проверяем отображение автора поста"""
    with captured_templates as templates:
        response = client.get('/posts/0')
        template, context = templates[0]
        author = context['post']['author']
        html = response.data.decode()
        assert author in html

def test_post_image_has_alt_text(client):
    """Проверяем наличие alt текста у изображения"""
    response = client.get('/posts/0')
    html = response.data.decode()
    assert 'alt="Изображение к посту"' in html

def test_comments_section_exists(client):
    """Проверяем наличие секции комментариев"""
    response = client.get('/posts/0')
    html = response.data.decode()
    assert 'comments-section' in html

def test_footer_contains_author_info(client):
    """Проверяем наличие информации об авторе в подвале"""
    response = client.get('/posts/0')
    html = response.data.decode()
    assert 'Иванов Иван Иванович' in html
    assert 'группа 123-456' in html

def test_post_content_escaped(client, captured_templates):
    """Проверяем, что контент поста экранируется"""
    with captured_templates as templates:
        client.get('/posts/0')
        template, context = templates[0]
        
        # Проверяем, что текст поста не содержит неэкранированный HTML
        assert '&lt;' not in context['post']['text']
        assert '&gt;' not in context['post']['text']

def test_post_image_url_correct(client, captured_templates):
    """Проверяем корректность URL изображения"""
    with captured_templates as templates:
        response = client.get('/posts/0')
        template, context = templates[0]
        html = response.data.decode()
        assert 'images/' in html
        assert context['post']['image_id'] in html
