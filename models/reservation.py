from init import db, ma
from marshmallow import fields

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

reservation_schema = ReservationSchema()
reservations_schema = ReservationSchema(many=True)