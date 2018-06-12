import pytest
from ResearchHelper import cli
from ResearchHelper.db import db


# monkeypatch is Pytest's built-in fixture
def test_create_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False
        bind = -1

    def fake_create_db(bind):
        Recorder.called = True
        Recorder.bind = bind

    monkeypatch.setattr(cli, 'create_db', fake_create_db)
    
    result = runner.invoke(args=['db', 'create'])
    assert 'Created' in result.output
    assert Recorder.called
    assert Recorder.bind is None

    Recorder.called = False
    result = runner.invoke(args=['db', 'create', '--bind', 'all'])
    assert 'Created' in result.output
    assert Recorder.called
    assert Recorder.bind == 'all'

def test_drop_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False
        bind = -1

    def fake_drop_db(bind):
        Recorder.called = True
        Recorder.bind = bind

    monkeypatch.setattr(cli, 'drop_db', fake_drop_db)
    
    result = runner.invoke(args=['db', 'drop'])
    assert 'Droped' in result.output
    assert Recorder.called
    assert Recorder.bind is None

    Recorder.called = False
    result = runner.invoke(args=['db', 'drop', '--bind', 'all'])
    assert 'Droped' in result.output
    assert Recorder.called
    assert Recorder.bind == 'all'

def test_renew_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False
        bind = -1

    def fake_renew_db(bind):
        Recorder.called = True
        Recorder.bind = bind

    monkeypatch.setattr(cli, 'renew_db', fake_renew_db)
    
    result = runner.invoke(args=['db', 'renew'])
    assert 'Renewed' in result.output
    assert Recorder.called
    assert Recorder.bind is None

    Recorder.called = False
    result = runner.invoke(args=['db', 'renew', '--bind', 'all'])
    assert 'Renewed' in result.output
    assert Recorder.called
    assert Recorder.bind == 'all'

def test_generate_invitation_command(runner, monkeypatch):
    class Recorder(object):
        called = False
        count = None

    def fake_generate_invitation(count, length):
        Recorder.called = True
        Recorder.count = count
        Recorder.length = length

    monkeypatch.setattr(cli, 'generate_invitation', 
        fake_generate_invitation
    )
    
    result = runner.invoke(args=['invitation', 'generate'])
    assert 'generated' in result.output
    assert Recorder.called
    assert Recorder.count == 100
    assert Recorder.length == 32

    Recorder.called = False
    result = runner.invoke(args=[
        'invitation', 'generate', '--count', 10, '--length', 16])
    assert 'generated' in result.output
    assert Recorder.called
    assert Recorder.count == 10
    assert Recorder.length == 16


def test_get_invitation_command(runner, monkeypatch):
    class Recorder(object):
        called = False
        count = None

    def fake_get_invitation(count):
        Recorder.called = True
        Recorder.count = count

    monkeypatch.setattr(cli, 'get_invitation', 
        fake_get_invitation
    )
    
    result = runner.invoke(args=['invitation', 'get'])
    assert Recorder.called
    assert Recorder.count == 1

    Recorder.called = False
    result = runner.invoke(args=['invitation', 'get', '--count', 10])
    assert Recorder.called
    assert Recorder.count == 10