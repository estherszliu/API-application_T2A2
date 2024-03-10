from init import db, ma
from marshmallow import fields

class User_reservation(db.Model):
    __tablename__ ="user_reservation"

    id = db.Column(db.Integer, primary_key=True)
    # Foreignkey is provide by psql
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    reservation_id = db.Column(db.Integer, db.ForeignKey("reservations.id"), nullable=False)
    reservation_date = db.Column(db.Date)
     # sqlalchemy create a relationship between tables
    user = db.relationship("User", back_populates="user_reservation")
    reservation = db.relationship("Reservation", back_populates="user_reservation")

    # create schema
class User_reservationSchema(ma.Schema):
    # use schema to serialize the field back to python objects. 
    user = fields.Nested("UserSchema", only=["id", "email"])

    reservation = fields.Nested("ReservationSchema", exclude=["user_reservation"])

    class Meta():
        fields = ("id", "user", "reservation" )

user_reservationSchema = User_reservationSchema()
user_reservationsSchema = User_reservationSchema(many=True)