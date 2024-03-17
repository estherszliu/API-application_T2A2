from init import db, ma
from marshmallow import fields

class Room_reservation(db.Model):
    __tablename__ = "room_reservation"

    id = db.Column(db.Integer, primary_key=True)
    # Foreignkey is provide by psql
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"), nullable=False)
    reservation_id = db.Column(db.Integer, db.ForeignKey("reservations.id"), nullable=False)
    
    
     # sqlalchemy create a relationship between tables
    room = db.relationship("Room", back_populates="room_reservation")
    reservation = db.relationship("Reservation", back_populates="room_reservation")

# create schema
class Room_reservationSchema(ma.Schema):
    # use schema to serialize the field back to python objects. 
    room = fields.Nested("RoomSchema", only=["id","type"])

    reservation = fields.Nested("ReservationSchema")
    class Meta():
        fields = ("id", "room", "reservation")

room_reservationSchema = Room_reservationSchema()
room_reservationsSchema = Room_reservationSchema(many=True)