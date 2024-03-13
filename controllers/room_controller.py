from datetime import datetime, date
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes
from init import db
from models.room import Room, rooms_schema, room_schema
from models.room_amenity import Room_amenity, room_amenities_schema, room_amenity_schema
from models.user import User
from models.amenity import Amenity, amenities_schema, amenity_schema
from models.room_reservation import Room_reservation, room_reservationsSchema, room_reservationSchema
from models.reservation import Reservation
from controllers.room_amenity_controller import room_amenity_bp

rooms_bp = Blueprint("rooms", __name__, url_prefix="/rooms")
rooms_bp.register_blueprint(room_amenity_bp)



def is_user_admin():
    user_id = get_jwt_identity()
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    return user.is_admin

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
    body_data = request.get_json()
    # create new room and add to session and commit
    room = Room(
        type = body_data.get("type"),
        price = body_data.get("price")
    )
    db.session.add(room)

    amenity_ids = body_data.get("room_amenity")
    
    for id in amenity_ids:
        amenity_stmt = db.select(Amenity).filter_by(id=id)
        amenity = db.session.scalar(amenity_stmt)
        if amenity:
            room_amenity = Room_amenity(
                room = room, 
                amenity = amenity
           )
            db.session.add(room_amenity)
        else:
            return {"error": f"amenity id {id} not fount"}, 409
    db.session.add(room_amenity)

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
        stmt = db.select(Room_reservation).filter_by(room_id=room_id)
        occupy = db.session.scalar(stmt)
        if occupy:
            return {"error": f"room with id {room_id} has a booking, can not be deleted"}
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
    body_data = request.get_json()
    stmt = db.select(Room).filter_by(id=room_id)
    room = db.session.scalar(stmt)
    if room:
        room.type = body_data.get("type") or room.type
        room.price = body_data.get("price") or room.price
        amenity_id= body_data.get("amenity_id")
        if amenity_id:
            amenity_stmt = db.select(Amenity).filter_by(id=amenity_id)
            amenity = db.session.scalar(amenity_stmt)
            if not amenity:
                return {"error": f"amenity with id {amenity_id} not found"}, 409
        
            # validate the amenity whether is the same, if is the same then don't need to do anything, if not, added it. 
            exist_stmt = db.select(Room_amenity).filter_by(room_id=room_id,amenity_id=amenity_id)
            exist = db.session.scalar(exist_stmt) 
            if not exist:
                room_amenity = Room_amenity(
                    room = room,
                    amenity = amenity
                )
                db.session.add(room_amenity)  
        db.session.commit()
        return room_schema.dump(room)
    
    else:
        return {"error": f"Room with id {room_id} not found"}, 404
    




# valiadate the owner
# if str (xxx.user_id) != get_jwt_identity():
#     return {"error"}


# get room_reservation route   http://localhost:8090/rooms/<int:room_id>/reservations
@rooms_bp.route("/<int:room_id>/reservations")
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

