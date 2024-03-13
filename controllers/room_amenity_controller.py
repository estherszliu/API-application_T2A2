from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from init import db
from models.user import User
from models.room_amenity import Room_amenity, room_amenities_schema, room_amenity_schema
from models.room import Room
from models.amenity import Amenity
from marshmallow.exceptions import ValidationError

room_amenity_bp = Blueprint("room_amenity", __name__, url_prefix="/<int:room_id>/amenity")

class BadRequestError(Exception):
    pass

class ConflictError(Exception):
    pass

class NotFoundError(Exception):
    pass

# validate admin user
def is_user_admin():
    user_id = get_jwt_identity()
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    return user.is_admin

# validate the amenity id whether exist
def validate_amenity_exists(amenity_id):
    exist_amenity = db.session.query(Amenity).filter(Amenity.id==amenity_id).first()
    if not exist_amenity:
        raise NotFoundError(f"Amenity id {amenity_id} does not exist" )

    
# validate amenity id should not be exist in the room
def validate_amenity_id_not_assigned_room(amenity_id, room_id):
    validate_amenity_exists(amenity_id)
    
    check_room_amenity = db.session.query(Room_amenity)\
        .filter(Room_amenity.room_id==room_id, Room_amenity.amenity_id==amenity_id)\
        .first()
    if check_room_amenity:
        raise ConflictError(f"Amenity id {amenity_id} already exist in the room")
    

# get room amenity route
@room_amenity_bp.route("/")
@jwt_required()
def get_room_amenity(room_id):
    is_admin = is_user_admin()
    if not is_admin:
        return {"error": "Not authorised to enquire the room amenity"}, 403
    
    stmt = db.select(Room_amenity).filter_by(room_id=room_id)
    amenities = db.session.scalars(stmt)
    return room_amenities_schema.dump(amenities)

# assign an amenity to the room
@room_amenity_bp.route("/", methods=["POST"])
@jwt_required()
def assign_amenity(room_id):
    is_admin = is_user_admin()
    if not is_admin:
        return {"error": "Not authorised to enquire the room amenity"}, 403

    try:
        body_data = request.get_json()
        amenity_id = body_data.get("amenity_id")
        stmt = db.select(Room).filter_by(id=room_id)
        room = db.session.scalar(stmt)
        validate_amenity_id_not_assigned_room(amenity_id, room_id)

        room_amenity = Room_amenity(
            room = room,
            amenity_id = amenity_id
        )
        db.session.add(room_amenity)
        db.session.commit()
        return room_amenity_schema.dump(room_amenity)

    except NotFoundError as error:
        return {"Error": str(error)}, 404
    except ConflictError as error:
        return {"Error": str(error)}, 409
    
# delete a room amenity
@room_amenity_bp.route("/", methods=["DELETE"])
@jwt_required()
def delete_room_amenity(room_id):
    is_admin = is_user_admin()
    if not is_admin:
        return {"error": "Not authorised to enquire the room amenity"}, 403
    
    try:
        body_data = request.get_json()
        amenity_id = body_data.get("amenity_id")

        # check if the amenity id is valid
        validate_amenity_exists(amenity_id )
        room_amenity = db.select(Room_amenity).filter_by(room_id=room_id, amenity_id=amenity_id)
        room_amenity = db.session.scalar(room_amenity)
       
        if not room_amenity:
            return {"error": f"Amenity id {amenity_id} does not exist for the room"}, 404
        
        db.session.delete(room_amenity)
        db.session.commit()
        return {f"Amenity id {amenity_id} deleted seccussfully."}
        
    except NotFoundError as error:
        return {"Error": str(error)}, 404
    except ConflictError as error:
        return {"Error": str(error)}, 409