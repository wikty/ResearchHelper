import os
import tempfile

import pytest
from ResearchHelper import create_app
from ResearchHelper.db import db
from ResearchHelper.models import (
    User, InvitationCode, Post, Category, Tag, Series
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
        'SQLALCHEMY_ECHO': False
    })

    # create the database and load test data
    data.init(app, db)
    data.insert(app, db)

    yield app

    # close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


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
