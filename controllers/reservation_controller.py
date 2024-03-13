from datetime import datetime, timedelta, date
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes
from init import db
from models.reservation import Reservation, reservation_schema, reservations_schema 
from models.room_reservation import Room_reservation, room_reservationSchema
from models.room import Room, room_schema, rooms_schema
from models.user import User, users_schema
from models.user_reservation import User_reservation, user_reservationSchema, user_reservationsSchema


class ValidationError(Exception):
    pass

class ConflictError(Exception):
    pass

class NotFoundError(Exception):
    pass

reservation_bp = Blueprint("reservations", __name__, url_prefix="/reservations")
    
def validate_dates(check_in_date, check_out_date):
    if check_in_date < date.today():
        raise ValidationError("Check in date must not be in the past")

    if check_in_date >= check_out_date:
        raise ValidationError("Check out date must be greater than check in date")
    
def validate_rooms(room_ids):
    stmt = db.select(Room).where(Room.id.in_(room_ids))
    existing_rooms = list(db.session.scalars(stmt))

    if len(existing_rooms) != len(room_ids):
        raise ValidationError("Invalid room ids")
    
def validate_user(user_id):
    stmt = db.select(User).where(User.id == user_id)
    existing_user = db.session.scalar(stmt)

    if not existing_user:
        raise ValidationError("Invalid user id")
    
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
                raise ConflictError("Reservation overlaps with existing booking")
            
def get_room_reservation_cost(room_id, check_in_date, check_out_date):
    stmt = db.select(Room).where(Room.id == room_id)
    room = db.session.scalar(stmt)

    total_nights = (check_out_date - check_in_date).days
    return room.price * total_nights

def get_total_reservation_cost(room_ids, check_in_date, check_out_date):
    total_cost = 0
    for room_id in room_ids:
        total_cost += get_room_reservation_cost(room_id, check_in_date, check_out_date)
    return total_cost
    

def validate_reservation_id(reservation_id):
    reservation = db.session.query(Reservation) \
        .filter(Reservation.id == reservation_id) \
        .first()
    if not reservation:
        raise NotFoundError("Reservation id {} does not exist", reservation_id)

def is_admin():
    user_id = get_jwt_identity()
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    return user.is_admin

def is_reservation_owner(reservation_id):
    user_reservation = db.session.query(User_reservation) \
        .join(Reservation, Reservation.id==User_reservation.reservation_id) \
        .filter(Reservation.id == reservation_id) \
        .first()
    
    user_id = user_reservation.user_id

    if (str(user_id) != get_jwt_identity()):
        return False

    return True


def is_admin_or_reservation_owner(reservation_id):
    return is_admin() or is_reservation_owner(reservation_id)

def get_user_id_from_reservation(reservation):
    user_reservation = db.session.query(User_reservation)\
        .join(Reservation, Reservation.id == User_reservation.reservation_id)\
        .filter(User_reservation.reservation_id == reservation.id).one()
    return user_reservation.user_id

def get_room_ids_from_reservation(reservation):
    room_reservations = db.session.query(Room_reservation)\
        .join(Reservation, Reservation.id == Room_reservation.reservation_id)\
        .filter(Room_reservation.reservation_id == reservation.id).all()
    room_ids = []
    for room_reservation in room_reservations:
        room_ids.append(room_reservation.room_id)
    
    return room_ids

def get_check_in_date_from_reservation(reservation):
    return reservation.check_in_date

def get_check_out_date_from_reservation(reservation):
    return reservation.check_out_date

# http://localhost:8090/reservations/ --GET
@reservation_bp.route("/")
@jwt_required()
def get_all_reservations():
    if is_admin():
        stmt = db.select(Reservation).order_by(Reservation.id)
        reservations = db.session.scalars(stmt)
        return reservations_schema.dump(reservations)
    else:
        return {"error": f"Not authorised to get all the reservations"}, 403


# http://localhost:8090/reservations/<reservation_id> --GET a single reservation by id
@reservation_bp.route("/<int:reservation_id>")
@jwt_required()
def get_reservation(reservation_id):
    stmt = db.select(Reservation).filter_by(id=Reservation.id)
    reservation = db.session.scalar(stmt)
    if reservation:
        if is_admin_or_reservation_owner(reservation_id): 
            return reservation_schema.dump(reservation)
        else: 
            return {"error": f"Not authorised to get the reservations"}, 403
    else:
        return {"Error": f"Reservation with id {reservation_id} not found"}, 404
    

# Create a reservation http://localhost:8090/reservations/ --POST
@reservation_bp.route("/", methods = ["POST"])
@jwt_required()
def create_reservation():
    body_data = request.get_json()
    try:

        # extract and validate the data
        user_id = body_data.get("user_id")
        validate_user(user_id)
    
        check_in_date = datetime.strptime(body_data.get("check_in_date"), "%y-%m-%d").date()
        check_out_date = datetime.strptime(body_data.get("check_out_date"), "%y-%m-%d").date()
        validate_dates(check_in_date, check_out_date)

        room_ids = body_data.get("room_ids")
        validate_rooms(room_ids)

        validate_rooms_available(room_ids, check_in_date, check_out_date)

        # create the reservation in the reservation table (get the id)
        reservation = Reservation(
            check_in_date = check_in_date,
            check_out_date = check_out_date,
            total_cost = get_total_reservation_cost(room_ids, check_in_date, check_out_date)
        )  
        db.session.add(reservation)
        db.session.flush()

        # add the reservation to the guest_reservation table
        user_reservation = User_reservation(
            user_id = user_id,
            reservation = reservation,
            reservation_date = date.today()
        )
        db.session.add(user_reservation)

        # for each room add, reservation to the room_reservation table
        for room_id in room_ids:
            room_reservation = Room_reservation(
                room_id = room_id,
                reservation_id = reservation.id,
            )
            db.session.add(room_reservation)

        # only commit when all data is added
        db.session.commit()
        return reservation_schema.dump(reservation), 201

    except ValidationError as error:
        return {"Error": str(error)}, 400
    except NotFoundError as error:
        return {"Error": str(error)}, 404
    except ConflictError as error:
        return {"Error": str(error)}, 409
    

# Delete a reservation http://localhost:8090/reservations/<reservation_id> --POST
@reservation_bp.route("/<int:reservation_id>", methods = ["DELETE"])
@jwt_required()
def delete_reservation(reservation_id):

    try:
        validate_reservation_id(reservation_id)

        # delete the user_reservation
        stmt = db.select(User_reservation).where(Reservation.id == reservation_id)
        user_reservation = db.session.scalar(stmt)
        if user_reservation:
            db.session.delete(user_reservation)

        # delete the room reservations
        stmt = db.select(Room_reservation).where(Reservation.id == reservation_id)
        room_reservations = db.session.scalars(stmt)
        for room_reservation in room_reservations:
            db.session.delete(room_reservation)
        
        # delete the reservation
        stmt = db.select(Reservation).where(Reservation.id==reservation_id)
        reservation = db.session.scalar(stmt)
        if reservation:
            db.session.delete(reservation)

        db.session.commit()
        return {"Message": f"reservation with id {reservation_id} deleted successfully"}
    
    except ValidationError as error:
        return {"Error": str(error)}, 400
    except NotFoundError as error:
        return {"Error": str(error)}, 404


# Update a reservation http://localhost:8090/reservations/<reservation_id> --PUT OR PATCH
@reservation_bp.route("/<int:reservation_id>", methods = ["PUT", "PATCH"])
@jwt_required()
def update_reservation(reservation_id):
    try:
        validate_reservation_id(reservation_id)
        body_data = request.get_json()

        # get the reservation
        reservation = db.session.query(Reservation) \
            .filter_by(id=reservation_id) \
            .first()

        # get the check in dates
        check_in_date = get_check_in_date_from_reservation(reservation)
        if body_data.get("check_in_date"):
            check_in_date = datetime.strptime(body_data.get("check_in_date"), "%y-%m-%d").date()
        check_out_date = get_check_out_date_from_reservation(reservation)
        if body_data.get("check_out_date"):
            check_out_date = datetime.strptime(body_data.get("check_out_date"), "%y-%m-%d").date()
        validate_dates(check_in_date, check_out_date)

        # get the new and old room ids
        new_room_ids = body_data.get("room_ids")
        old_room_ids = get_room_ids_from_reservation(reservation)
        room_ids = old_room_ids
        if new_room_ids:
            validate_rooms(new_room_ids)
            validate_rooms_available(new_room_ids, check_in_date, check_out_date, reservation.id)

            room_ids_to_add = set(new_room_ids) - set(old_room_ids)
            room_ids_to_delete = set(old_room_ids) - set(new_room_ids)

            # add extra rooms
            for room_id in room_ids_to_add:
                room_reservation = Room_reservation(
                    room_id = room_id,
                    reservation_id = reservation.id,
                )
                db.session.add(room_reservation)

            # delete removed rooms
            for room_id in room_ids_to_delete:
                room_reservation = db.session.query(Room_reservation) \
                    .filter_by(reservation_id=reservation.id, room_id=room_id) \
                    .first()
                if room_reservation:
                    db.session.delete(room_reservation)
            
            room_ids = new_room_ids

        # update the reservation
        reservation.check_in_date = check_in_date
        reservation.check_out_date = check_out_date
        reservation.total_cost = get_total_reservation_cost(room_ids, check_in_date, check_out_date)

        # only commit when all data is added
        db.session.commit()
        return reservation_schema.dump(reservation), 201

    except ValidationError as error:
        return {"Error": str(error)}, 400
    except NotFoundError as error:
        return {"Error": str(error)}, 404
    except ConflictError as error:
        return {"Error": str(error)}, 409


    # 


    