from controllers.validation_helpers import validate_admin_or_user, validate_user_admin, validate_user_admin_or_reservation_owner
from flask_jwt_extended import get_jwt_identity, jwt_required
from functools import wraps

def jwt_admin_required(fn):

    @wraps(fn)
    def wrapper(*args, **kwargs):
        validate_user_admin(get_jwt_identity())
        return fn(*args, **kwargs)

    return jwt_required()(wrapper)


def jwt_admin_or_user_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        requested_user_id = kwargs.get('user_id')
        token_user_id = get_jwt_identity()
        validate_admin_or_user(token_user_id, requested_user_id)
        return fn(*args, **kwargs)

    return jwt_required()(wrapper)


def jwt_admin_or_reservation_owner_required(fn):

    @wraps(fn)
    def wrapper(*args, **kwargs):
        reservation_id = kwargs.get('reservation_id')
        validate_user_admin_or_reservation_owner(reservation_id, get_jwt_identity())
        return fn(*args, **kwargs)

    return jwt_required()(wrapper)



