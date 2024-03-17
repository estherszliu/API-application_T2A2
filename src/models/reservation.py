from datetime import datetime
from init import db, ma
from marshmallow import fields, validates
from marshmallow.exceptions import ValidationError

class Reservation(db.Model):
    __tablename__ = "reservations"

    id = db.Column(db.Integer, primary_key=True)
    check_in_date = db.Column(db.Date, nullable=False)
    check_out_date = db.Column(db.Date, nullable=False)
    
    total_cost = db.Column(db.Integer)
   
    user_reservation = db.relationship("User_reservation", back_populates="reservation", cascade="all, delete")
    room_reservation = db.relationship("Room_reservation", back_populates="reservation", cascade="all, delete")

class ReservationSchema(ma.Schema):

    user_reservation = fields.List(fields.Nested("User_reservationSchema", exclude=["reservation"]))
    room_reservation = fields.List(fields.Nested("Room_reservationSchema", exclude=["reservation"]))

    class Meta:
        fields = ("id", "check_in_date", "check_out_date", "total_cost",  "user_reservation", "room_reservation")

def valid_date(dateString):
    try:
        datetime.strptime(dateString, "%Y-%m-%d")
        return True
    except ValueError:
        return False

class ReservationLoadSchema(ma.Schema):

    check_in_date = fields.String(nullable=False)
    check_out_date = fields.String(nullable=False)
    room_ids = fields.List(fields.Integer(), nullable=False)
    user_id = fields.Integer(nullable=False)
    

    @validates("check_in_date")
    def validate_check_in_date(self, value):
        if not valid_date(value):
            raise ValidationError("Check in date is not valid")

    @validates("check_out_date")
    def validate_check_out_date(self, value):
        if not valid_date(value):
            raise ValidationError("Check out date is not valid")
    
    @validates("room_ids")
    def validate_room_ids(self, value):
        room_ids = value
        if len(room_ids) == 0:
            raise ValidationError("Room ids cannot be an empty list")
        
        for room_id in room_ids:
            if room_id < 1:
                raise ValidationError("Room ids must be positive integers")
            
    @validates("user_id")
    def validate_user_id(self, value):
        user_id = value
        if user_id < 1:
            raise ValidationError("User id must be positive integers")

    class Meta:
        fields = ("check_in_date", "check_out_date", "room_ids", "user_id")

reservation_schema = ReservationSchema()
reservations_schema = ReservationSchema(many=True)
reservation_load_schema = ReservationLoadSchema()