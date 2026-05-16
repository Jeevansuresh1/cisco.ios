import functools
import hashlib
import hmac
import json
import time
import base64

from flask import request, jsonify, g

SECRET_KEY = "your-secret-key-change-in-production"
TOKEN_EXPIRY = 3600


def generate_token(user_id, username):
    header = base64.urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).decode().rstrip("=")
    payload_data = {
        "user_id": user_id,
        "username": username,
        "iat": int(time.time()),
        "exp": int(time.time()) + TOKEN_EXPIRY,
    }
    payload = base64.urlsafe_b64encode(json.dumps(payload_data).encode()).decode().rstrip("=")
    signature = hmac.new(
        SECRET_KEY.encode(), f"{header}.{payload}".encode(), hashlib.sha256
    ).hexdigest()
    return f"{header}.{payload}.{signature}"


def decode_token(token):
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None, "Invalid token format"

        header, payload, signature = parts

        expected_sig = hmac.new(
            SECRET_KEY.encode(), f"{header}.{payload}".encode(), hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(signature, expected_sig):
            return None, "Invalid signature"

        padding = 4 - len(payload) % 4
        payload_data = json.loads(base64.urlsafe_b64decode(payload + "=" * padding))

        if payload_data.get("exp", 0) < time.time():
            return None, "Token expired"

        return payload_data, None
    except Exception as e:
        return None, str(e)


def require_auth(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error": "Missing Authorization header"}), 401

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({"error": "Invalid Authorization header format. Use: Bearer <token>"}), 401

        token_data, error = decode_token(parts[1])
        if error:
            return jsonify({"error": f"Authentication failed: {error}"}), 401

        g.current_user = token_data
        return f(*args, **kwargs)

    return decorated


def optional_auth(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                token_data, _ = decode_token(parts[1])
                g.current_user = token_data
            else:
                g.current_user = None
        else:
            g.current_user = None
        return f(*args, **kwargs)

    return decorated
