from controllers.validation_helpers import validate_room_exists, validate_room_not_assigned_to_any_amenity, validate_room_has_no_reservations
from models.room_reservation import Room_reservation, room_reservationsSchema
from controllers.room_amenity_controller import room_amenity_bp
from models.room import Room, rooms_schema, room_schema
from models.reservation import Reservation
from decorators import jwt_admin_required
from flask import Blueprint, request
from errors import NotFoundError
from init import db

rooms_bp = Blueprint("rooms", __name__, url_prefix="/rooms")
rooms_bp.register_blueprint(room_amenity_bp)

# Get all the rooms  http://localhost:8090/rooms  --GET
@rooms_bp.route("/")
@jwt_admin_required
def get_all_rooms():

    # QUERY COMMENT
    #   Get an ordered list of all the data for each room in the database, including assigned amenities
    #   Order the list according to room ids
    rooms = db.session.query(Room).order_by(Room.id).all()

    return rooms_schema.dump(rooms)

# Get a single room route  http://localhost:8090/rooms/4  --GET
@rooms_bp.route("/<int:room_id>")
@jwt_admin_required
def get_one_room(room_id):
    
    # QUERY COMMENT
    #   Get all the data for a room with the given room id if it exists
    #   Including assigned amenities
    room = db.session.query(Room).where(Room.id == room_id).first()

    if not room:
        raise NotFoundError(f"Room with id {room_id} not found")
    return room_schema.dump(room)
        

 # create a room  http://localhost:8090/rooms  --POST
@rooms_bp.route("/", methods=["POST"])
@jwt_admin_required
def create_room():
    body_data = room_schema.load(request.get_json())
    room = Room(
        type = body_data.get("type"),
        price = body_data.get("price")
    )

    # QUERY COMMENT
    #   Add the room to the database, it is not assigned to any amenities at start
    db.session.add(room)
    db.session.commit()
    return room_schema.dump(room), 201


# delete room route  http://localhost:8090/rooms/2 --DELETE
@rooms_bp.route("/<int:room_id>", methods=["DELETE"])
@jwt_admin_required
def delete_room(room_id):

    # validate room exists and not in use before delete
    validate_room_exists(room_id)
    validate_room_not_assigned_to_any_amenity(room_id)
    validate_room_has_no_reservations(room_id)
    
    # QUERY COMMENT
    #   Delete the room in the database that has the given room id
    db.session.query(Room).where(Room.id == room_id).delete()
    db.session.commit()

    return {"message": f"Room {room_id} deleted successfully"}


# update room route   
# http://localhost:8090/rooms/2  -- acept both PUT and PATCH, PUT will change the entire resource, PATCH just changes the attribution passed from the front end. 
@rooms_bp.route("/<int:room_id>", methods=["PUT", "PATCH"])
@jwt_admin_required
def update_room(room_id):
    
    # validate data
    validate_room_exists(room_id)

    # get the data from request
    body_data = room_schema.load(request.get_json())
    
    # QUERY COMMENT
    #   Get all the data for the room that has the given room id
    #   This will return None if there is no room with that id
    room = db.session.query(Room).where(Room.id == room_id).first()

    # update the room data    
    room.type = body_data.get("type") or room.type
    room.price = body_data.get("price") or room.price

    # Save the changes back to the database
    db.session.commit()
    return room_schema.dump(room)


# get room_reservation route   http://localhost:8090/rooms/<int:room_id>/reservations
@rooms_bp.route("/<int:room_id>/reservations")
@jwt_admin_required
def get_room_reservation(room_id):

    # Make sure the room exists
    validate_room_exists(room_id)
    
    # QUERY COMMENT: 
    #   Get all the data for every reservation which booked the given room
    room_reservations = db.session.query(Reservation) \
        .join(Room_reservation) \
        .where(Room_reservation.room_id == room_id) \
        .all()

    return room_reservationsSchema.dump(room_reservations)

