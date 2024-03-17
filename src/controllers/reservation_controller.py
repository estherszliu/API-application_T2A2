from datetime import date, datetime
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from controllers.validation_helpers import validate_dates, validate_reservation_exists, validate_rooms_available, validate_rooms_exist, validate_user_exists, validate_user_authorised_to_create_reservation
from decorators import jwt_admin_or_reservation_owner_required, jwt_admin_required
from init import db
from models.reservation import Reservation, reservation_load_schema, reservation_schema, reservations_schema
from models.room import Room
from models.room_reservation import Room_reservation
from models.user_reservation import User_reservation

reservation_bp = Blueprint("reservations", __name__, url_prefix="/reservations")
            
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
@jwt_admin_required
def get_all_reservations():

    # QUERY COMMENT
    #   Get an ordered list of all the data for each reservation in the database
    #   Order the list according to reservation ids SELECT * FROM reservations ORDER_BY id;
    reservations = db.session.query(Reservation).order_by(Reservation.id).all()
    return reservations_schema.dump(reservations)


# http://localhost:8090/reservations/<reservation_id> --GET a single reservation by id
@reservation_bp.route("/<int:reservation_id>")
@jwt_admin_or_reservation_owner_required
def get_reservation(reservation_id):

    # validate the data
    validate_reservation_exists(reservation_id)

    # QUERY COMMENT
    #   Get all the data for a reservation with the given reservation id
    #   SELECT * FROM reservaions WHERE id=reservation_id;
    reservation = db.session.query(Reservation).filter(Reservation.id == reservation_id).first()
    return reservation_schema.dump(reservation)
   
    
# Create a reservation http://localhost:8090/reservations/ --POST
@reservation_bp.route("/", methods = ["POST"])
@jwt_required()
def create_reservation():
    body_data = reservation_load_schema.load(request.get_json())

    # extract and validate the data
    user_id = body_data.get("user_id")
    validate_user_exists(user_id)

    token_user_id = get_jwt_identity()
    validate_user_authorised_to_create_reservation(token_user_id, user_id)
    

    check_in_date = datetime.strptime(body_data.get("check_in_date"), "%Y-%m-%d").date()
    check_out_date = datetime.strptime(body_data.get("check_out_date"), "%Y-%m-%d").date()
    validate_dates(check_in_date, check_out_date)

    room_ids = body_data.get("room_ids")
    
    validate_rooms_exist(room_ids)
    validate_rooms_available(room_ids, check_in_date, check_out_date)

    # QUERY COMMENT
    #   create the reservation in the reservation table (get the id)
    reservation = Reservation(
        check_in_date = check_in_date,
        check_out_date = check_out_date,
        total_cost = get_total_reservation_cost(room_ids, check_in_date, check_out_date)
    )  
    db.session.add(reservation)
    db.session.flush() # have to flush it to get reservation id

    # QUERY COMMENT
    #   add the user and reservation to the user_reservation table
    user_reservation = User_reservation(
        user_id = user_id,
        reservation = reservation,
        reservation_date = date.today()
    )
    db.session.add(user_reservation)

    # QUERY COMMENT
    #   for each room add the room and reservation to the room_reservation table
    for room_id in room_ids:
        room_reservation = Room_reservation(
            room_id = room_id,
            reservation_id = reservation.id,
        )
        db.session.add(room_reservation)

    # only commit when all data is added
    db.session.commit()
    return reservation_schema.dump(reservation), 201
    

# Delete a reservation http://localhost:8090/reservations/<reservation_id> --POST
@reservation_bp.route("/<int:reservation_id>", methods = ["DELETE"])
@jwt_admin_or_reservation_owner_required
def delete_reservation(reservation_id):
    validate_reservation_exists(reservation_id)

    # QUERY COMMENT
    #   get the user_reservation entry for the given reservation id
    #   returns None if no entry for reservation id exists
    stmt = db.select(User_reservation).where(Reservation.id == reservation_id)
    user_reservation = db.session.scalar(stmt)
    if user_reservation:

        # QUERY COMMENT
        #   delete the user_reservation entry
        db.session.delete(user_reservation)

    # QUERY COMMENT
    #   get the list of room_reservation entries for the given reservation id
    #   returns an empty list if no entries for reservation id exists
    stmt = db.select(Room_reservation).where(Reservation.id == reservation_id)
    room_reservations = db.session.scalars(stmt)
    for room_reservation in room_reservations:

        # QUERY COMMENT
        #   delete the room_reservation entry
        db.session.delete(room_reservation)
    
    # QUERY COMMENT
    #   get the reservation for the given reservation id
    stmt = db.select(Reservation).where(Reservation.id==reservation_id)
    reservation = db.session.scalar(stmt)
    if reservation:

        # QUERY COMMENT
        #   delete the reservation entry
        db.session.delete(reservation)

    db.session.commit()
    return {"Message": f"reservation with id {reservation_id} deleted successfully"}


# Update a reservation http://localhost:8090/reservations/<reservation_id> --PUT OR PATCH
@reservation_bp.route("/<int:reservation_id>", methods = ["PUT", "PATCH"])
@jwt_admin_or_reservation_owner_required
def update_reservation(reservation_id):
    validate_reservation_exists(reservation_id)
    body_data = reservation_load_schema.load(request.get_json(), partial=True)

    # QUERY COMMENT
    #   get the reservation with the given reservation id
    reservation = db.session.query(Reservation) \
        .filter_by(id=reservation_id) \
        .first()

    # get the check in and check out dates
    check_in_date = get_check_in_date_from_reservation(reservation)
    if body_data.get("check_in_date"):
        check_in_date = datetime.strptime(body_data.get("check_in_date"), "%Y-%m-%d").date()
    check_out_date = get_check_out_date_from_reservation(reservation)
    if body_data.get("check_out_date"):
        check_out_date = datetime.strptime(body_data.get("check_out_date"), "%Y-%m-%d").date()
    validate_dates(check_in_date, check_out_date)

    # get the new and old room ids - update if they changed
    new_room_ids = body_data.get("room_ids")
    old_room_ids = get_room_ids_from_reservation(reservation)
    room_ids = old_room_ids
    if new_room_ids:
        validate_rooms_exist(new_room_ids)
        validate_rooms_available(new_room_ids, check_in_date, check_out_date, reservation.id)

        room_ids_to_add = set(new_room_ids) - set(old_room_ids)
        room_ids_to_delete = set(old_room_ids) - set(new_room_ids)

        # add extra rooms
        for room_id in room_ids_to_add:
            room_reservation = Room_reservation(
                room_id = room_id,
                reservation_id = reservation.id,
            )

            # QUERY COMMENT
            #   Add the given room_reservation
            db.session.add(room_reservation)

        # delete removed rooms
        for room_id in room_ids_to_delete:
            room_reservation = db.session.query(Room_reservation) \
                .filter_by(reservation_id=reservation.id, room_id=room_id) \
                .first()
            if room_reservation:

                # QUERY COMMENT
                #   Delete the given room_reservation
                db.session.delete(room_reservation)
        
        room_ids = new_room_ids

    # update the reservation
    reservation.check_in_date = check_in_date
    reservation.check_out_date = check_out_date
    reservation.total_cost = get_total_reservation_cost(room_ids, check_in_date, check_out_date)

    # only commit when all data is added
    db.session.commit()
    return reservation_schema.dump(reservation), 201