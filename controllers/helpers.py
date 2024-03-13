from models.user import User
from init import db
from errors import UnauthorisedUserError

def is_user_admin(user_id):
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    return user.is_admin

def validate_user_admin(user_id):
    if not is_user_admin(user_id):
        raise UnauthorisedUserError("Not authorised to perform requested operation")