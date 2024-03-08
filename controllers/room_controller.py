from flask import Blueprint, request

from init import db
from models.room import Room, rooms_schema, room_schema
from models.hotel import Hotel

rooms_bp = Blueprint("rooms", __name__, url_prefix="/rooms")

# Get all the rooms  http://localhost:8090/rooms  --GET
@rooms_bp.route("/")
def get_all_rooms():
    stmt = db.select(Room).order_by(Room.id)
    rooms = db.session.scalars(stmt)
    return rooms_schema.dump(rooms)

# Get a single room route  http://localhost:8090/rooms/4  --GET
@rooms_bp.route("/<int:room_id>")
def get_one_room(room_id):
    stmt = db.select(Room).filter_by(id=room_id) # SELECT * FROM room WHERE id=room_id
    room = db.session.scalar(stmt)
    if room:
        return room_schema.dump(room)
    else:
        return {"Error": f"Room with id {room_id} not found"}, 404

 # create a room  http://localhost:8090/rooms  --POST
@rooms_bp.route("/", methods=["POST"])
def create_room():
    body_data = request.get_json()
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
def delete_room(room_id):
    # get the room from db
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
def update_room(room_id):
    # get the data from request
    body_data = request.get_json()
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
