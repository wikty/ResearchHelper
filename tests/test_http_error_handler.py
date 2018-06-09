from werkzeug.exceptions import abort

def test_404(client):
    response = client.get('/fdjldfifd')
    assert b'Not Found' in response.data

def test_500(app, client):
    @app.route('/test500')
    def test_500_view():
        abort(500)
    response = client.get('/test500')
    assert b'Server Internal Error' in response.data