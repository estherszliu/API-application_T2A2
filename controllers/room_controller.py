from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from init import db
from models.room import Room, rooms_schema, room_schema
from models.hotel import Hotel
from models.user import User
from controllers.room_amenity_controller import room_amenity_bp

from models.room_reservation import Room_reservation, room_reservationsSchema, room_reservationSchema

rooms_bp = Blueprint("rooms", __name__, url_prefix="/rooms")
rooms_bp.register_blueprint(room_amenity_bp)

# Get all the rooms  http://localhost:8090/rooms  --GET
@rooms_bp.route("/")
@jwt_required()
def get_all_rooms():
    is_admin = is_user_admin()
    if not is_admin:
        return {"error": "Not authorised to require all the rooms"}, 403
    stmt = db.select(Room).order_by(Room.id)
    rooms = db.session.scalars(stmt)
    return rooms_schema.dump(rooms)

# Get a single room route  http://localhost:8090/rooms/4  --GET
@rooms_bp.route("/<int:room_id>")
@jwt_required()
def get_one_room(room_id):
    stmt = db.select(Room).filter_by(id=room_id) # SELECT * FROM room WHERE id=room_id
    room = db.session.scalar(stmt)
    if room:
        return room_schema.dump(room)
    else:
        return {"Error": f"Room with id {room_id} not found"}, 404

 # create a room  http://localhost:8090/rooms  --POST
@rooms_bp.route("/", methods=["POST"])
@jwt_required()
def create_room():
    is_admin = is_user_admin()
    if not is_admin:
        return {"error": "Not authorised to create a room"}, 403
    body_data = room_schema.load(request.get_json())
    # query the hotel model and later for set the hotel_id to this hotel id. 
    hotel = db.select(Hotel)
    hotel = db.session.scalar(hotel)
    # create new room and add to session and commit
    room = Room(
        type = body_data.get("type"),
        price = body_data.get("price"),
        status = body_data.get("status"),
        hotel_id = hotel.id
    )
    db.session.add(room)
    db.session.commit()
    return room_schema.dump(room), 201


# delete room route  http://localhost:8090/rooms/2 --DELETE
@rooms_bp.route("/<int:room_id>", methods=["DELETE"])
@jwt_required()
def delete_room(room_id):
    # get the room from db
    is_admin = is_user_admin()
    if not is_admin:
        return {"error": "Not authorised to delete a room"}, 403
    stmt = db.select(Room).where(Room.id == room_id)
    room = db.session.scalar(stmt)
    if room:
        db.session.delete(room)
        db.session.commit()
        return {"message": f"Room {room_id} deleted successfully"}
    else:
        return {"error": f"Room with id {room_id} not found"}, 404


# update room route   
# http://localhost:8090/rooms/2  -- acept both PUT and PATCH, PUT will change the entire resouces, PATCH just change the attribution passed from the front end. 
@rooms_bp.route("/<int:room_id>", methods=["PUT", "PATCH"])
@jwt_required()
def update_room(room_id):
    is_admin = is_user_admin()
    if not is_admin:
        return {"error": "Not authorised to change the room information"}, 403
    # get the data from request
    body_data = room_schema.load(request.get_json(), partial=True)
    stmt = db.select(Room).filter_by(id=room_id)
    room = db.session.scalar(stmt)
    if room:
        room.type = body_data.get("type") or room.type
        room.price = body_data.get("price") or room.price
        room.status = body_data.get("status") or room.status
        db.session.commit()
        return room_schema.dump(room)
    
    else:
        return {"error": f"Room with id {room_id} not found"}, 404
    



def is_user_admin():
    user_id = get_jwt_identity()
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    return user.is_admin

# valiadate the owner
# if str (xxx.user_id) != get_jwt_identity():
#     return {"error"}


# get room_reservation route   http://localhost:8090/rooms/<int:room_id>/reservations
@rooms_bp.route("/reservations")
@jwt_required()
def get_room_reservation(room_id):
    is_admin = is_user_admin()
    if not is_admin:
        return {"error": "Not authorised to view all the reservations of the room"}, 403
    
    stmt = db.select(Room_reservation).filter_by(room_id=room_id)
    room_reservations = db.session.scalars(stmt)
    if room_reservations:
        return room_reservationsSchema.dump(room_reservations)
    else:
        return {"error": f"Reservation with room id {room_id} not found"}, 404

# get one room_reservation route   http://localhost:8090/rooms/reservations/<int:reservation_id>
@rooms_bp.route("/reservations/<int:reservation_id>")
@jwt_required()
def get_one_room_reservation(room_id, reservation_id):
    is_admin = is_user_admin()
    if not is_admin:
        return {"error": "Not authorised to view all the room reservations"}, 403
    
    body_data = request.get_json()
    stmt = db.select(Room).filter_by(id=room_id)
    room = db.session.scalar(stmt)
    if room:
        reservation
