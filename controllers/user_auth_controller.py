from datetime import timedelta
from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token
from psycopg2 import errorcodes

from init import db, bcrypt
from models.user import User, user_schema


# set auth-blueprint and also set a prefix /auth
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# user register route
@auth_bp.route("/register", methods=["POST"])
def auth_register():
    try:
        # body data get from json, request need to import from flask
        body_data = request.get_json()

         # create user without password, then check if password exist then hash the password to it. 
        user = User(
            first_name=body_data.get("first_name"),
            last_name=body_data.get("last_name"),
            email=body_data.get("email")
            )
        
        # store the password from request first, then check whether the password is exist.
        password = body_data.get("password")
        
       # hash the password from the json request
        if password:
            user.password = bcrypt.generate_password_hash(password).decode("utf-8")
        
       
        # add to the staging area and commit it to the database. 
        db.session.add(user)
        db.session.commit()
        # return back the create user to show the new user info 
        return user_schema.dump(user), 201

    # Error for user has duplicate email address. 
    except IntegrityError as err:
        # if the error pgcode is the not_null_violation return that particular error column name to the user. 
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"The {err.orig.diag.column_name} is required"}, 409
         # if the error pgcode is the unique_violation means the email is being used.
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {"error": "Email address already in use"}, 409
    

# user login route
@auth_bp.route("/login", methods=["POST"])
def auth_login():
    body_data = request.get_json()
    # query the database find the email address which match to the json request 
    # this will be same as query command in psql SELECT email FROM user WHERE email == body_data.get("email")
    stmt = db.select(User).filter_by(email=body_data.get("email"))
    user = db.session.scalar(stmt)

    # if user exist and if the user password is match
    if user and bcrypt.check_password_hash(user.password, body_data.get("password")):
        # Create jwt 
        token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=7))
        # return the token with the user info
        return {"email": user.email, "token": token, "is_admin": user.is_admin}
    # else 
    else:
        # return error
        return {"error": "Invalid email or password"}, 401
    






