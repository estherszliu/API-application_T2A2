from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime,  date

from init import db, bcrypt
from models.user import User, user_schema, users_schema
from models.reservation import Reservation
from models.user_reservation import User_reservation

user_bp = Blueprint("users", __name__, url_prefix="/users")

def is_user_admin():
    user_id = get_jwt_identity()
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    return user.is_admin


# get all the users - only admin can see all the users booking
@user_bp.route("/")
@jwt_required()
def get_all_users():
    is_admin = is_user_admin()
    if not is_admin:
        return {"error": "Not authorised to request all the users"}, 403

    stmt = db.select(User).order_by(User.id)
    print(stmt)
    users = db.session.scalars(stmt)
    return users_schema.dump(users)

# get an user -- only the user owner can see the user page
@user_bp.route("/<int:user_id>")
@jwt_required()
def get_user(user_id):
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    if user: 
        if str(user_id) != get_jwt_identity():
            return {"error": "Not authorised to require this user"}, 403
    
        return user_schema.dump(user)
    else:
        return {"error": f"user with id {user_id} not found"}, 404

# update an user information
@user_bp.route("/<int:user_id>", methods=["PUT", "PATCH"])
@jwt_required()
def update_user(user_id):
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    if not user:
        return {"error": f"user with id {user_id} not found"}, 404 
    
    if str(user_id) != get_jwt_identity():
        return {"error": "Not authorised to update this user"}, 403
      
    body_data = request.get_json()
    user.first_name = body_data.get("first_name") or user.first_name
    user.last_name = body_data.get("last_name") or user.last_name
    user.email = body_data.get("email") or user.email

    if body_data.get("password"):
            user.password = bcrypt.generate_password_hash(body_data.get("password")).decode("utf-8")
    db.session.commit()
    return user_schema.dump(user)


# delete an user
@user_bp.route("/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    if user: 
        if str(user_id) != get_jwt_identity():
            return {"error": "Not authorised to delete this user"}, 403
        # check whether the user has existing booking still on going
        bookings = db.session.query(Reservation).join(User_reservation, Reservation.id==User_reservation.reservation_id).filter(User_reservation.user_id == user_id).all()
        if bookings:
            for booking in bookings:
                check_out_date = booking.check_out_date
                if check_out_date >= date.today():
                    return {"error": f"User currently have booking, it can not be delete. "}, 409
        db.session.delete(user)
        db.session.commit()
        return {"message": f"User {user_id} deleted successfully"}

    else:
        return {"error": f"user with id {user_id} not found"}, 404 