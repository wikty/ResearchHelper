import pytest
from flask import g, session
from ResearchHelper.db import db
from ResearchHelper.models import User, InvitationCode


def test_register(client, app):
    # test that viewing the page renders without template errors
    assert client.get('/auth/register').status_code == 200

    username = 'a'
    password = 'a'
    invitation_code = 'testxx'
    # test that successful registration redirects to the login page
    with app.app_context():
        invitation = InvitationCode(code=invitation_code)
        db.session.add(invitation)
        db.session.commit()
    response = client.post(
        '/auth/register', 
        data={'username': username, 
              'password': password, 
              'confirm': password,
              'email': 'a@example.com',
              'invitation': invitation_code,
              'refer': 'refer'
        }
    )
    
    print(response.data)

    assert 'http://localhost/auth/login' == response.headers['Location']

    # test that the user was inserted into the database
    # and test that invitation code is allocated
    with app.app_context():
        assert User.query.filter_by(
            username=username
        ).first() is not None
        assert InvitationCode.query.filter_by(
            code=invitation_code, 
            assigned=True
        ).first() is not None


# run the same test function with different arguments
@pytest.mark.parametrize(
    ('username', 'email', 'password', 'confirm', 'invitation', 'message'), 
    (
        ('a', 'a@e.com', 'a', 'a', '', b'Invitation Code is required.'),
        ('a', 'a@e.com', 'a', 'a', '**--++', b'Invitation Code is invalid.'),
        ('a', 'a@e.com', 'a', 'a', 'used12', b'Invitation Code has already been used.'),
        ('', 'a@e.com', 'a', 'a', 'invitation', b'Username is required.'),
        ('a', '', 'a', 'a', 'invitation', b'Email is required.'),
        ('a', 'a@e.com', '', 'a', 'invitation', b'Password is required.'),
        ('a', 'a@e.com', 'a', '', 'invitation', b'Re-Password is required.'),
        ('a', 'a@e.com', 'a', 'b', 'invitation', b'Passwords must match.'),
        ('test', 'test@e.com', 'test', 'test', 'unused', b'already registered'),
    )
)
def test_register_validate_input(client, 
    username, email, password, confirm, invitation, message):
    response = client.post(
        '/auth/register',
        data={'username': username,
              'email': email, 
              'password': password,
              'confirm': confirm,
              'invitation': invitation,
              'refer': ''}
    )
    assert message in response.data


def test_login(client, auth):
    # test that viewing the page renders without template errors
    assert client.get('/auth/login').status_code == 200

    # test that successful login redirects to the index page
    response = auth.login()
    assert response.headers['Location'] == 'http://localhost/'

    # login request set the user_id in the session
    # check that the user is loaded from the session
    # Note: Using client in a with block allows accessing context variables 
    # such as session after the response is returned.
    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user.username == 'test'


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', 'test', b'Username is required.'),
    ('a', 'test', b'Incorrect username.'),
    ('test', '', b'Password is required.'),
    ('test', 'a', b'Incorrect password.'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session
