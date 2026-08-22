import jwt
from datetime import datetime, timezone
from functools import wraps
from flask import request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password: str) -> str:
    """Hashes a plain text password using pbkdf2:sha256 via werkzeug.security."""
    return generate_password_hash(password)

def verify_password(stored_hash: str, password: str) -> bool:
    """Verifies a plain text password against a stored password hash."""
    return check_password_hash(stored_hash, password)

def generate_jwt_token(user_id: int, employee_id: str, email: str, role: str) -> str:
    """
    Generates a signed JWT access token containing user identity and role payload.
    """
    payload = {
        'user_id': user_id,
        'employee_id': employee_id,
        'email': email,
        'role': role,
        'exp': datetime.now(timezone.utc) + current_app.config['JWT_ACCESS_TOKEN_EXPIRES'],
        'iat': datetime.now(timezone.utc)
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')

def decode_jwt_token(token: str) -> tuple[dict | None, str]:
    """
    Decodes and validates a JWT access token.
    
    Returns:
        (payload_dict, error_message)
    """
    try:
        payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return payload, ""
    except jwt.ExpiredSignatureError:
        return None, "Authentication token has expired. Please sign in again."
    except jwt.InvalidTokenError:
        return None, "Invalid authentication token."

def token_required(f):
    """
    Decorator that enforces JWT authentication on protected routes.
    Attaches `g.current_user` dictionary containing token payload to Flask's global context.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', None)
        if not auth_header:
            return jsonify({'error': 'Authentication token is required.'}), 401
            
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({'error': 'Authorization header format must be Bearer <token>'}), 401
            
        token = parts[1]
        payload, error = decode_jwt_token(token)
        if error:
            return jsonify({'error': error}), 401
            
        request.current_user = payload
        return f(*args, **kwargs)
    return decorated

def role_required(allowed_roles: list[str]):
    """
    Decorator that enforces Role-Based Access Control (RBAC).
    Checks whether the authenticated user's role exists in `allowed_roles`.
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(request, 'current_user') or not request.current_user:
                return jsonify({'error': 'Authentication required.'}), 401
                
            user_role = request.current_user.get('role', 'employee')
            if user_role not in allowed_roles:
                return jsonify({
                    'error': 'Forbidden: You do not have permission to perform this action.'
                }), 403
                
            return f(*args, **kwargs)
        return decorated
    return decorator
