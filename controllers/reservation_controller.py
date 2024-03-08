from datetime import datetime, timedelta, date

from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes
from init import db
from models.reservation import Reservation, reservation_schema, reservations_schema 


reservation_bp = Blueprint("reservations", __name__, url_prefix="/reservations")


def validate_check_in_date(check_in_date):
    if check_in_date < date.today():
        raise ValueError
    
def validate_dates(check_in_date, check_out_date):
    if check_in_date >= check_out_date:
        raise ValueError

# http://localhost:8090/reservations/ --GET
@reservation_bp.route("/")
def get_all_reservations():
    stmt = db.select(Reservation).order_by(Reservation.id)
    reservations = db.session.scalars(stmt)
    return reservations_schema.dump(reservations)


# http://localhost:8090/reservations/<reservation_id> --GET a single reservation by id
@reservation_bp.route("/<int:reservation_id>")
def get_reservation(reservation_id):
    stmt = db.select(Reservation).filter_by(id=Reservation.id)
    reservation = db.session.scalar(stmt)
    if reservation:
        return reservation_schema.dump(reservation)
    else:
        return {"Error": f"Reservation with id {reservation_id} not found"}, 404
    

# Create a reservation http://localhost:8090/reservations/ --POST
@reservation_bp.route("/", methods = ["POST"])
def create_reservation():
   
    body_data = request.get_json()
    try:
        check_in_date = datetime.strptime(body_data.get("check_in_date"), "%y-%m-%d").date()
        check_out_date = datetime.strptime(body_data.get("check_out_date"), "%y-%m-%d").date()
        validate_check_in_date(check_in_date)
        validate_dates(check_in_date, check_out_date)
        reservation = Reservation(
            check_in_date = check_in_date,
            check_out_date = check_out_date,
            total_night = (check_out_date - check_in_date).days
        )
        db.session.add(reservation)
        db.session.commit()
        return reservation_schema.dump(reservation), 201

    except ValueError:
        return {"Error": f"invalid check_in_date or check_out_date please user format yy-mm-dd and make sure check in date is above today"}, 409

    except TypeError:
        return {"Error": f"check_in_date and check_out_date must be provided"}, 400
    
    

# Delete a reservation http://localhost:8090/reservations/<reservation_id> --POST
@reservation_bp.route("/<int:reservation_id>", methods = ["DELETE"])
def delete_reservation(reservation_id):
    stmt = db.select(Reservation).where(Reservation.id==reservation_id)
    reservation = db.session.scalar(stmt)
    if reservation:
        db.session.delete(reservation)
        db.session.commit()
        return {"Message": f"reservation with id {reservation_id} deleted successfully"}
    else:
        return {"Error": f"reservation with id {reservation_id} not found"}, 404

# Update a reservation http://localhost:8090/reservations/<reservation_id> --PUT OR PATCH
@reservation_bp.route("/<int:reservation_id>", methods = ["PUT", "PATCH"])
def update_reservation(reservation_id):
    body_data = request.get_json()
    stmt = db.select(Reservation).filter_by(id=reservation_id)
    reservation = db.session.scalar(stmt)
    if reservation: 
        try:   
            if "check_in_date" in body_data and "check_out_date" in body_data:
                check_in_date = datetime.strptime(body_data.get("check_in_date"), "%y-%m-%d").date()
                check_out_date = datetime.strptime(body_data.get("check_out_date"), "%y-%m-%d").date()
                validate_check_in_date(check_in_date)
                validate_dates(check_in_date, check_out_date)
                reservation.check_in_date = check_in_date
                reservation.check_out_date = check_out_date

            elif "check_in_date" in body_data:
                check_in_date = datetime.strptime(body_data.get("check_in_date"), "%y-%m-%d").date()
                validate_check_in_date(check_in_date)
                check_out_date = reservation.check_out_date
                validate_dates(check_in_date, check_out_date)
                reservation.check_in_date = check_in_date
                
            elif "check_out_date" in body_data:
                check_out_date = datetime.strptime(body_data.get("check_out_date"), "%y-%m-%d").date()
                check_in_date = reservation.check_in_date
                validate_dates(check_in_date, check_out_date)
                reservation.check_out_date = check_out_date
            
            reservation.total_night = (reservation.check_out_date - reservation.check_in_date).days
            db.session.commit()
            return reservation_schema.dump(reservation)

        except ValueError:
            return {"Error": f"invalid check_in_date or check_out_date"}, 409
    else:
            return{"Error":f"reservation with id {reservation_id} not found"}, 404


    