from init import db
from models.room import Room
from models.amenity import Amenity
from models.room_amenity import Room_amenity
from models.room_reservation import Room_reservation
from errors import NotFoundError, ConflictError

def validate_room_exists(room_id):
    # QUERY COMMENT
    #   Get the number of rooms in the database that have the given room id
    #   This will return 0 if no rooms exist for give id
    numRooms = db.session.query(Room).where(Room.id == room_id).count()
    
    if numRooms == 0:
        raise NotFoundError(f"room with id {room_id} not found")
    
def validate_room_not_assigned_to_any_amenity(room_id):
    # QUERY COMMENT
    #   Get the number of amenities this room id is assigned to
    #   This will return 0 if not assigned to any amenities
    #   SELECT COUNT(*) FROM Room_amenity WHERE room_id = room_id
    numAssignments = db.session.query(Room_amenity) \
        .filter(Room_amenity.room_id==room_id) \
        .count()
    if numAssignments > 0:
        raise ConflictError(f"the room with id {room_id} is assigned to an amenity, can not be delete.")
    
def validate_room_has_no_reservations(room_id):
    # QUERY COMMENT
    #   Get the number of reservations this room id has
    #   This will return 0 if not it has no reservations
    #   SELECT COUNT(*) FROM Room_reservations WHERE room_id = room_id
    numReservations = db.session.query(Room_reservation).where(Room_reservation.room_id == room_id).count()
    if numReservations > 0:
        raise ConflictError(f"room with id {room_id} has a reservation, can not be deleted")

def validate_amenity_exists(amenity_id):
    # QUERY COMMENT
    #   Get the number of amenities which has the given amenity id
    #   This will return 0 if there is no amenity with that id
    #   SELECT COUNT(*) FROM amenities WHERE id = amenity_id
    numAmenity = db.session.query(Amenity).filter(Amenity.id==amenity_id).count()
    
    if numAmenity == 0:
        raise NotFoundError(f"amenity with id {amenity_id} not found")
    

def validate_amenity_not_assigned_to_any_rooms(amenity_id):
    # QUERY COMMENT
    #   Get the number of rooms this amenity id is assigned to
    #   This will return 0 if not assigned to any rooms
    #   SELECT COUNT(*) FROM Room_amenity WHERE amenity_id = amenity_id
    numAssignments = db.session.query(Room_amenity) \
        .filter(Room_amenity.amenity_id==amenity_id) \
        .count()
    if numAssignments > 0:
        raise ConflictError(f"the amenity with id {amenity_id} is in use, can not be delete.")

def is_amenity_assigned_to_given_room(amenity_id, room_id):
    # QUERY COMMENT
    #   Get the number of room_amenity which has the given amenity id
    #   This will return 0 if there is no room_amenity with that id
    #   SELECT COUNT(*) FROM room_amenity WHERE room_amenity.room_id = amenity_id, room_amenity.amenity_id = amenity_id
    numRoom_amenity = db.session.query(Room_amenity)\
        .filter(Room_amenity.room_id==room_id, Room_amenity.amenity_id==amenity_id)\
        .count()
    if numRoom_amenity > 0:
        return True
    return False

def validate_amenity_not_already_assigned_to_room(amenity_id, room_id):
    if is_amenity_assigned_to_given_room(amenity_id, room_id):
        raise ConflictError(f"amenity id {amenity_id} already assigned to room id {room_id}")
    
def validate_amenity_is_assigned_to_room(amenity_id, room_id):
    if not is_amenity_assigned_to_given_room(amenity_id, room_id):
        raise NotFoundError(f"amenity id {amenity_id} not assigned to room id {room_id}")