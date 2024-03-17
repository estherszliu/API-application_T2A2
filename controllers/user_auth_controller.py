from controllers.validation_helpers import validate_email_not_used
from datetime import timedelta
from flask import Blueprint, request
from flask_jwt_extended import create_access_token
from init import bcrypt, db
from models.user import User, user_load_schema, user_schema
from werkzeug.exceptions import BadRequest, Unauthorized



# set auth-blueprint and also set a prefix /auth
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# user register route
@auth_bp.route("/register", methods=["POST"])
def auth_register():
   
    # body data get from json, request needs to import from flask
    body_data = user_load_schema.load(request.get_json())
    
    # check first name and last name given
    first_name = body_data.get("first_name")
    last_name = body_data.get("last_name")
    if not first_name:
        raise BadRequest("first name is required")
    if not last_name:
        raise BadRequest("last name is required")

    # validate the email is not being used
    email=body_data.get("email")
    validate_email_not_used(email)

    # create user without password 
    user = User(
        first_name = body_data.get("first_name"),
        last_name = body_data.get("last_name"),
        email = email.lower()
    )
    
    # hash the password and add it to the user
    password = body_data.get("password")
    user.password = bcrypt.generate_password_hash(password).decode("utf-8")
    
    # QUERY COMMENT
    #   add to the staging area and commit it to the database. 
    db.session.add(user)
    db.session.commit()

    # return back the created user and show the new user info 
    return user_schema.dump(user), 201
    

# user login route
@auth_bp.route("/login", methods=["POST"])
def auth_login():

    body_data = user_load_schema.load(request.get_json(), partial=True)

    # QUERY COMMENT
    #   query the database to find the email address which matches the json request 
    #   this will be same as query command in psql SELECT * FROM user WHERE email = body_data.get("email")
    stmt = db.select(User).filter_by(email=body_data.get("email"))
    user = db.session.scalar(stmt)

    # check if user exists and the user password is a match
    if user and bcrypt.check_password_hash(user.password, body_data.get("password")):
        # create jwt token
        token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=7))
        return {"email": user.email, "token": token, "is_admin": user.is_admin} 
    else:
        raise Unauthorized("invalid email or password")
    