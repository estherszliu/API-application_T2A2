from controllers.validation_helpers import validate_email_not_used, validate_user_has_no_reservations, validate_user_exists
from decorators import jwt_admin_or_user_required, jwt_admin_required
from flask import Blueprint, request
from init import bcrypt, db
from models.user import User, user_load_schema, user_schema, users_schema

user_bp = Blueprint("users", __name__, url_prefix="/users")

# get all the users - only admin can see all the users booking
@user_bp.route("/")
@jwt_admin_required
def get_all_users():
   
    # QUERY COMMENT
    #   Get an ordered list of all the data for each user in the database
    #   Order the list according to user ids  SELECT * FROM users;
    users = db.session.query(User).order_by(User.id).all()
    return users_schema.dump(users)

# get an user -- only admin or the user owner can see the user page
@user_bp.route("/<int:user_id>")
@jwt_admin_or_user_required
def get_user(user_id):

    # QUERY COMMENT
    #   Get all the data for a user with the given user id
    #   Including assigned amenities
    user = db.session.query(User).filter(User.id == user_id).first()
    return user_schema.dump(user)

# update an user -- only admin or the user owner can update the user
@user_bp.route("/<int:user_id>", methods=["PUT", "PATCH"])
@jwt_admin_or_user_required
def update_user(user_id):
    validate_user_exists(user_id)
    body_data = user_load_schema.load(request.get_json(), partial=True)

    # QUERY COMMENT
    #   Get all the data for the room that has the given room id
    #   This will return None if there is no room with that id
    user = db.session.query(User).where(User.id == user_id).first()

    # can't change email if new email is already used
    if body_data.get("email"):
        validate_email_not_used(body_data.get("email"))
        user.email = body_data.get("email").lower()

    user.first_name = body_data.get("first_name") or user.first_name
    user.last_name = body_data.get("last_name") or user.last_name

    if body_data.get("password"):
        user.password = bcrypt.generate_password_hash(body_data.get("password")).decode("utf-8")

    db.session.commit()
    return user_schema.dump(user)


# get an user -- only admin or the user owner can see the user page
# also need to check whether user has any reservations before deleting it
@user_bp.route("/<int:user_id>", methods=["DELETE"])
@jwt_admin_or_user_required
def delete_user(user_id):
    validate_user_exists(user_id)
    validate_user_has_no_reservations(user_id)

    # QUERY COMMENT
    #   Delete the user in the database that has the given user id
    db.session.query(User).where(User.id == user_id).delete()
    db.session.commit()
    return {"message": f"User {user_id} deleted successfully"}