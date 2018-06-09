import os
import tempfile
from contextlib import contextmanager

import pytest
from flask import appcontext_pushed, g

from ResearchHelper import create_app
from ResearchHelper.db import db
from ResearchHelper.models import (
    User, InvitationCode, Post, PostCategory, PostTag, PostSeries
)

import data

# - Test Fixture
# Current file setups functions called fixtures that each test will use them.
# - Test Case
# Tests are in Python modules that start with test_, and each test function 
# in those modules also starts with test_. test function will load fixture by
# matching the argument name with fixture's name.


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    # create the app with common test configuration(override the development)
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///{}'.format(db_path),
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SQLALCHEMY_ECHO': False,
        'WTF_CSRF_ENABLED': False, # disable all WTF's CSRF protection
        # 'TRAP_BAD_REQUEST_ERRORS': True, # avoid 400(Bad Request) when form miss a key
    })

    # create the database and load test data
    data.init(app, db)
    data.insert(app, db)

    yield app

    # close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def app_context(app):
    """Use as a with block to push the context, which will make `current_app` point at
    this application.
    In the view function or cli command function, a application context is automatically
    pushed. But in the test enviroment you should create it for yourself and use it in
    a with block.
    Note: due to db depends on app context, all db operations should inside a context.  
    """
    def new_context():
        return app.app_context()
    return new_context


@pytest.fixture
def client(app):
    """A test client agent for the app.
    Client has get(), post() and so on to make a http request.
    Besides, using client in a with block allows accessing context variables
    such as session after the response is returned. In other words, even the
    request has been done, the context variables(`request`, `session`) will 
    still be keep in the with block. 
    """
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


@contextmanager
def user_set(app, user):
    def handler(sender, **kwargs):
        g.user = user
    with appcontext_pushed.connected_to(handler, app):
        yield


@pytest.fixture
def hook_user(app):
    """Override the `g.user` in with context block."""
    def inner(user):
        return user_set(app, user)
    return inner


class AuthActions(object):
    '''For most of the views, a user needs to be logged in. The easiest way to
     do this in tests is to make a POST request to the login view with the 
     client. Rather than writing that out every time, you can write a class with
     methods to do that, and use a fixture to pass it the client for each test.
    '''
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)
