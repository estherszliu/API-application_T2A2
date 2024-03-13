from functools import wraps
from flask_jwt_extended import get_jwt_identity, jwt_required
from controllers.helpers import validate_user_admin

def jwt_admin_required(fn):

    @wraps(fn)
    def wrapper(*args, **kwargs):
        validate_user_admin(get_jwt_identity())
        return fn(*args, **kwargs)

    return jwt_required()(wrapper)