from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from init import db
from models.room import Room
from models.amenity import Amenity
from models.room_amenity import Room_amenity, room_amenity_schema


room_amenity_bp = Blueprint("room_amenity", __name__, url_prefix="/<int:room_id>/amenities")
#########################################################################
# Check the room_amenities route-- get the room with all the amenities
@room_amenity_bp.route("/")
@jwt_required()
def get_room_amenities(room_id):
    stmt = db.select(Room_amenity).filter_by(room_id=room_id)
    amenities = db.session.scalar(stmt)
    if amenities:
        return room_amenity_schema.dump(amenities)
    else:
        return {"Error": f"Amenities with room id {room_id} not found"}, 404
    

# Create the room amenities 
@room_amenity_bp.route("/", methods=["POST"])
@jwt_required()
def create_room_amenity(room_id):
    body_data = request.get_json()
    stmt = db.select(Room).filter_by(id=room_id)
    room = db.session.scalar(stmt)
    if room:
        amenity_id = body_data.get("amenity_id")
        amenity_stmt = db.select(Amenity).filter_by(id=amenity_id)
        amenity = db.session.scalar(amenity_stmt)

        validate_room = db.select(Room_amenity).filter_by(room_id=room_id)
        validate_room = db.session.scalars(validate_room)
        print(validate_room)

        if not amenity:
            return {"Error": f"amenity id not found"}, 404
        # validate the amenity_id wherether is in this room_amenity already

        validate_room = db.select(Room_amenity).filter_by(room_id=room_id,amenity_id=amenity_id)
        validate_room = db.session.scalars(validate_room)
        if validate_room:
            return {"Error": f"amenity id is already exists"}, 409
        
        room_amenity = Room_amenity(
            amenity_id = amenity_id,
            room_id = room_id
        )
        db.session.add(room_amenity)
        db.session.commit()
        return room_amenity_schema.dump(room_amenity), 201   
            
    else:
        return {"Error": f"Amenities with room id {room_id} not found"}, 404


# Delete the room amenities
@room_amenity_bp.route("/<int:room_amenity_id>", methods=["DELETE"])
@jwt_required()
def delete_room_amenity(room_id, room_amenity_id):
    stmt = db.select(Room_amenity).filter_by(id=room_amenity_id)
    amenity = db.session.scalar(stmt)
    if amenity and amenity.room_id == room_id:
        db.session.delete(amenity)
        db.session.commit()
        return {"message": f"Amenity with id {room_amenity_id} has been deleted"}
    else:
        return {"Error": f"Amenity with id {room_amenity_id} not found"}, 404
    
