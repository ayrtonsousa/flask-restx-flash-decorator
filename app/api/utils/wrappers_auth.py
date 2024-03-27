from functools import wraps

from flask_jwt_extended import get_jwt, verify_jwt_in_request


def admin_required():
    """ access by role """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            is_admin = claims.get('is_admin', False)
            if is_admin:
                return fn(*args, **kwargs)
            else:
                return {'message': 'user must be admin!'}, 403

        return decorator

    return wrapper

def role_or_admin_required(role):
    """ access by role """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            roles = claims.get('roles', [])
            is_admin = claims.get('is_admin', False)
            if role in roles or is_admin:
                return fn(*args, **kwargs)
            else:
                return {'message': 'user without permission or not admin!'}, 403

        return decorator

    return wrapper