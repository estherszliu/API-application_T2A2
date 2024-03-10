from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from init import db
from models.room import Room, rooms_schema, room_schema
from models.hotel import Hotel
from models.room_amenity import Room_amenity, room_amenity_schema, room_amenities_schema
from models.amenity import Amenity

rooms_bp = Blueprint("rooms", __name__, url_prefix="/rooms")

# Get all the rooms  http://localhost:8090/rooms  --GET
@rooms_bp.route("/")
@jwt_required()
def get_all_rooms():
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
@jwt_required()
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
@jwt_required()
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
    




# Check the room_amenities route-- get the room with all the amenities
@rooms_bp.route("/<int:room_id>/amenities")
def get_room_amenities(room_id):
    stmt = db.select(Room_amenity).filter_by(room_id=room_id)
    amenities = db.session.scalar(stmt)
    if amenities:
        return room_amenity_schema.dump(amenities)
    else:
        return {"Error": f"Amenities with room id {room_id} not found"}, 404
    

# Create the room amenities 
@rooms_bp.route("/<int:room_id>/amenities", methods=["POST"])
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
@rooms_bp.route("/<int:room_id>/amenities/<int:room_amenity_id>", methods=["DELETE"])
def delete_room_amenity(room_id, room_amenity_id):
    stmt = db.select(Room_amenity).filter_by(id=room_amenity_id)
    amenity = db.session.scalar(stmt)
    if amenity and amenity.room_id == room_id:
        db.session.delete(amenity)
        db.session.commit()
        return {"message": f"Amenity with id {room_amenity_id} has been deleted"}
    else:
        return {"Error": f"Amenity with id {room_amenity_id} not found"}, 404
    

