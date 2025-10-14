from functools import wraps

import jwt
from flask import request, jsonify

from config import api


def authorization_wrapper(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = request.headers['Authorization']

        if not token:
            return jsonify({"error": "Missing token", "details": "A valid token is missing"}), 400

        player = jwt.decode(token, api.config['SECRET_KEY'], algorithms=['HS256'])

        return f(player, *args, **kwargs)

    return decorator
