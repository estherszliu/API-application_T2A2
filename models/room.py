from init import db, ma
from marshmallow import fields


class Room(db.Model):
    __tablename__ = "rooms"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String)
    price = db.Column(db.Integer)
    status = db.Column(db.String)

    # Foreignkey is provide by psql
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'), nullable=False)
   
    # sqlalchemy create a relationship between rooms to hotel
    hotel = db.relationship("Hotel", back_populates="rooms")

    room_amenity = db.relationship("Room_amenity", back_populates="room", cascade="all, delete")

class RoomSchema(ma.Schema):
    # create hotel use by marshmallow
    hotel = fields.Nested("HotelSchema", only = ["name", "location"])

    room_amenity = fields.List(fields.Nested("Room_amenitySchema",exclude=["room"] ))

    class Meta:
        fields = ("id", "type", "price", "status", "hotel", "room_amenity")
        order = True

room_schema = RoomSchema()
rooms_schema = RoomSchema(many=True)