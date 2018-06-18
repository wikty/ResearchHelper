# JSON API response status code
status_code = {
    'ok': 0,
    'post_field_required_error': 1
}

# JSON API response wrapper function
def response_json(message='ok', status=0, **data):
    return jsonify({
        'data': data,
        'status': status,
        'message': message
    })