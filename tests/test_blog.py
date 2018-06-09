import pytest
from flask import g, session

from ResearchHelper.db import db
from ResearchHelper.models import Post


def test_index(client, auth):
    response = client.get('/')
    assert b"Sign in" in response.data
    assert b"Sign up" in response.data
    # user cannot update before login
    assert b'href="/1/update"' not in response.data

    auth.login()
    response = client.get('/')
    assert b'test title' in response.data
    assert b'by test' in response.data
    assert b'test body' in response.data
    assert b'href="/1/update"' in response.data


@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
    '/1/delete',
))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers['Location'] == 'http://localhost/auth/login'


def test_author_required(app, client, auth):
    auth.login()
    # current user can't modify other user's post
    assert client.post('/2/update').status_code == 403
    assert client.post('/2/delete').status_code == 403
    # current user doesn't see edit link
    assert b'href="/2/update"' not in client.get('/').data


@pytest.mark.parametrize('path', (
    '/404/update',
    '/404/delete',
))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404


def test_create(client, auth, app):
    auth.login()
    assert client.get('/create').status_code == 200

    with app.app_context(), client:
        client.post('/create', data={'title': 'created', 'body': ''})
        assert len(Post.query.filter_by(user_id=session['user_id']).all()) > 1


def test_update(client, auth, app):
    auth.login()
    assert client.get('/1/update').status_code == 200
    client.post('/1/update', data={'title': 'updated', 'body': ''})

    with app.app_context():
        post = Post.query.get(1)
        assert post and post.title == 'updated'


@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
))
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={'title': '', 'body': ''})
    assert b'Title is required.' in response.data


def test_delete(client, auth, app):
    auth.login()
    response = client.post('/1/delete')
    assert response.headers['Location'] == 'http://localhost/'

    with app.app_context():
        post = Post.query.get(1)
        assert post is None
