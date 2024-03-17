from datetime import date
from init import db
from models.amenity import Amenity
from models.reservation import Reservation
from models.room import Room
from models.room_amenity import Room_amenity
from models.room_reservation import Room_reservation
from models.user import User
from models.user_reservation import User_reservation
from werkzeug.exceptions import Forbidden, NotFound, Conflict


def validate_room_exists(room_id):
    # QUERY COMMENT
    #   Get the number of rooms in the database that have the given room id
    #   This will return 0 if no rooms exist for give id
    numRooms = db.session.query(Room).where(Room.id == room_id).count()
    
    if numRooms == 0:
        raise NotFound(f"room with id {room_id} not found")


def validate_room_not_assigned_to_any_amenity(room_id):
    # QUERY COMMENT
    #   Get the number of amenities this room id is assigned to
    #   This will return 0 if not assigned to any amenities
    #   SELECT COUNT(*) FROM Room_amenity WHERE room_id = room_id
    numAssignments = db.session.query(Room_amenity) \
        .filter(Room_amenity.room_id==room_id) \
        .count()
    if numAssignments > 0:
        raise Conflict(f"the room with id {room_id} is assigned to an amenity, can not be delete.")


def validate_room_has_no_reservations(room_id):
    # QUERY COMMENT
    #   Get the number of reservations this room id has
    #   This will return 0 if not it has no reservations
    #   SELECT COUNT(*) FROM Room_reservations WHERE room_id = room_id
    numReservations = db.session.query(Room_reservation).where(Room_reservation.room_id == room_id).count()
    if numReservations > 0:
        raise Conflict(f"room with id {room_id} has a reservation, can not be deleted")


def validate_amenity_exists(amenity_id):
    # QUERY COMMENT
    #   Get the number of amenities which has the given amenity id
    #   This will return 0 if there is no amenity with that id
    #   SELECT COUNT(*) FROM amenities WHERE id = amenity_id
    numAmenity = db.session.query(Amenity).filter(Amenity.id==amenity_id).count()
    
    if numAmenity == 0:
        raise NotFound(f"amenity with id {amenity_id} not found")
    

def validate_amenity_not_assigned_to_any_rooms(amenity_id):
    # QUERY COMMENT
    #   Get the number of rooms this amenity id is assigned to
    #   This will return 0 if not assigned to any rooms
    #   SELECT COUNT(*) FROM Room_amenity WHERE amenity_id = amenity_id
    numAssignments = db.session.query(Room_amenity) \
        .filter(Room_amenity.amenity_id==amenity_id) \
        .count()
    if numAssignments > 0:
        raise Conflict(f"the amenity with id {amenity_id} is in use, can not be delete.")


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
        raise Conflict(f"amenity id {amenity_id} already assigned to room id {room_id}")

   
def validate_amenity_is_assigned_to_room(amenity_id, room_id):
    if not is_amenity_assigned_to_given_room(amenity_id, room_id):
        raise NotFound(f"amenity id {amenity_id} not assigned to room id {room_id}")


def validate_email_not_used(email):
    # QUERY COMMENT
    #   Get the number of user which has the given email
    #   This will return 0 if there is no user with that email
    #   SELECT COUNT(*) FROM users WHERE email = email
    user = db.session.query(User).where(User.email==email).count()
    if user != 0:
        raise Conflict("user with that email already exist")
    

def validate_user_has_no_reservations(user_id):
    # QUERY COMMENT
    #   Get the number of reservations that belong to the given user id
    numReservations = db.session.query(Reservation)\
        .join(User_reservation, Reservation.id==User_reservation.reservation_id)\
        .filter(User_reservation.user_id == user_id)\
        .count()
    
    # check to see if any reservations are still coming
    if numReservations > 0:
        raise Conflict(f"user currently has a reservation, can not be deleted")
    

def validate_dates(check_in_date, check_out_date):
    if check_in_date < date.today():
        raise Conflict("check in date must not be in the past")

    if check_in_date >= check_out_date:
        raise Conflict("check out date must be greater than check in date")


def validate_rooms_exist(room_ids):
    stmt = db.select(Room).where(Room.id.in_(room_ids))
    existing_rooms = list(db.session.scalars(stmt))

    if len(existing_rooms) != len(room_ids):
        raise Conflict("not all room ids exist")


def user_exists(user_id):
    # QUERY COMMENT
    #   Get the number of user which has the given user id
    #   This will return 0 if there is no user with that id
    #   SELECT COUNT(*) FROM users WHERE id = user_id
    user = db.session.query(User).where(User.id==user_id).count()
    if user == 0:
        return False
    return True


def validate_user_exists(user_id):
    if not user_exists(user_id):
        raise NotFound(f"user with id {user_id} not found")


def reservation_exists(reservation_id):
    # QUERY COMMENT
    #   Get the number of reservation which has the given reservation id
    #   This will return 0 if there is no reservation with that id
    #   SELECT COUNT(*) FROM reservations WHERE id = reservaion_id
    reservation = db.session.query(Reservation) \
        .filter(Reservation.id == reservation_id) \
        .count()
    if reservation == 0:
        return False
    return True


def validate_reservation_exists(reservation_id):
    if not reservation_exists(reservation_id):
        raise NotFound(f"reservation id {reservation_id} does not exist")


def validate_rooms_available(room_ids, check_in_date, check_out_date, reservation_id=None):

    for room_id in room_ids:
        stmt = None
        if not reservation_id:
            stmt = (
                db.select(Reservation)
                .join(Room_reservation, Reservation.id == Room_reservation.reservation_id)
                .where(Room_reservation.room_id == room_id)
            )
        
        # if changing a booking, wont check the old reservation
        else:
            stmt = (
                db.select(Reservation)
                .join(Room_reservation, Reservation.id == Room_reservation.reservation_id)
                .where(Room_reservation.room_id == room_id, Reservation. id != reservation_id)
            )
        reservations = db.session.scalars(stmt)
        for reservation in reservations:
            reservation_check_in_date = reservation.check_in_date
            reservation_check_out_date = reservation.check_out_date

            if (check_in_date < reservation_check_out_date and check_out_date > reservation_check_in_date):
                raise Conflict("reservation overlaps with existing booking")
            

def is_user_admin(user_id):    
    # QUERY COMMENT
    #   Get the user with the given user id from the users table
    #   SELECT * FROM users WHERE id = user_id
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    return user and user.is_admin


def validate_user_admin(user_id):
    if not is_user_admin(user_id):
        raise Forbidden("not authorised to perform requested operation")
    

def validate_admin_or_user(token_user_id, requested_user_id):
    if is_user_admin(token_user_id):
        return
    
    if int(token_user_id) != requested_user_id:
        raise Forbidden("not authorised to perform requested operation")
    

def is_reservation_owner(reservation_id, user_id):
    # QUERY COMMENT
    #   Get the user_reservation entry from the user_reservation table which has the given reservatin id.
    #   Returns None if no reservation is found
    user_reservation = db.session.query(User_reservation) \
        .join(Reservation, Reservation.id==User_reservation.reservation_id) \
        .filter(Reservation.id == reservation_id) \
        .first()
    
    # If no reservation found, their is no owner
    if not user_reservation:
        return False
    
    # Check if the user_id match
    reservation_user_id = user_reservation.user_id
    if (str(reservation_user_id) != user_id):
        return False
    return True


def validate_user_admin_or_reservation_owner(reservation_id, user_id):
    # admin can access all reservations
    if is_user_admin(user_id):
        return

    if not is_reservation_owner(reservation_id, user_id):
        raise Forbidden("not authorised to perform requested operation")
    
def validate_user_authorised_to_create_reservation(token_user_id, requested_user_id):
    # admin always authorised
    if is_user_admin(token_user_id):
        return
    
    if int(token_user_id) != requested_user_id:
        raise Forbidden("not authorised to perform requested operation")