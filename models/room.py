from init import db, ma
from marshmallow import fields, validates
from marshmallow.exceptions import ValidationError
from marshmallow.validate import OneOf


VALID_TYPE = ("King", "Queen", "Double", "Single")

class Room(db.Model):
    __tablename__ = "rooms"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String)
    price = db.Column(db.Integer)

    room_amenity = db.relationship("Room_amenity", back_populates="room", cascade="all, delete")

    room_reservation = db.relationship("Room_reservation", back_populates="room", cascade="all, delete")

class RoomSchema(ma.Schema):

    type = fields.String(validate=OneOf(VALID_TYPE))

    @validates("price")
    def validate_price(self, value):
        if value == str(value) or value <= 0:
            raise ValidationError(f"The price should a postive integer.")

    # room_amenity = fields.List(fields.Nested("Room_amenitySchema",exclude=["room"] ))
    room_amenity = fields.List(fields.Nested("Room_amenitySchema"))
    room_reservation = fields.List(fields.Nested("Room_reservationSchema",exclude=["room"] ))

    class Meta:
        fields = ("id", "type", "price", "room_amenity")
        order = True

room_schema = RoomSchema()
rooms_schema = RoomSchema(many=True)