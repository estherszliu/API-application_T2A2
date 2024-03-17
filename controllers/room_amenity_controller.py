from controllers.validation_helpers import validate_amenity_exists, validate_amenity_is_assigned_to_room, validate_amenity_not_already_assigned_to_room, validate_room_exists
from decorators import jwt_admin_required
from flask import Blueprint
from init import db
from models.room_amenity import Room_amenity, room_amenities_schema, room_amenity_schema

room_amenity_bp = Blueprint("room_amenity", __name__, url_prefix="/<int:room_id>/amenity")

# get room amenity route
@room_amenity_bp.route("/")
@jwt_admin_required
def get_room_amenity(room_id):

    stmt = db.select(Room_amenity).filter_by(room_id = room_id)
    amenities = db.session.scalars(stmt)
    return room_amenities_schema.dump(amenities)


# assign an amenity to the room
@room_amenity_bp.route("/<int:amenity_id>", methods=["POST"])
@jwt_admin_required
def assign_room_amenity(room_id, amenity_id):

    # validate the data
    validate_room_exists(room_id)
    validate_amenity_exists(amenity_id)
    validate_amenity_not_already_assigned_to_room(amenity_id, room_id)

    # QUERY COMMENT
    #   create new amenity_room pair and add database
    room_amenity = Room_amenity(
        room_id = room_id,
        amenity_id = amenity_id
    )
    db.session.add(room_amenity)

    # commit changes 
    db.session.commit()
    return room_amenity_schema.dump(room_amenity)
    

# delete a room amenity
@room_amenity_bp.route("/<int:amenity_id>", methods=["DELETE"])
@jwt_admin_required
def unassign_room_amenity(room_id, amenity_id):
    
    # validate the data
    validate_room_exists(room_id)
    validate_amenity_exists(amenity_id)
    validate_amenity_is_assigned_to_room(amenity_id, room_id)
        
    # QUERY COMMENT
    #   Delete the room_amenity pair with give ids from database
    db.session.query(Room_amenity) \
        .where(Room_amenity.room_id == room_id, Room_amenity.amenity_id == amenity_id) \
        .delete()
    
    db.session.commit()
    
    return {"message": f"room id {room_id} unassigned from amenity id {amenity_id}."}, 200