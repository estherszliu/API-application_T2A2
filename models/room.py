from init import db, ma
from marshmallow import fields, validates
from marshmallow.validate import Length, And, Regexp, OneOf
from marshmallow.exceptions import ValidationError

VALID_TYPE = ("King", "Queen", "Double")
VALID_STATUS = ("Avalible", "Occupy")
class Room(db.Model):
    __tablename__ = "rooms"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String)
    price = db.Column(db.Integer)
    status = db.Column(db.String, default="avalible")

    # Foreignkey is provide by psql
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'), nullable=False)
   
    # sqlalchemy create a relationship between rooms to hotel
    hotel = db.relationship("Hotel", back_populates="rooms")

    room_amenity = db.relationship("Room_amenity", back_populates="room", cascade="all, delete")

    room_reservation = db.relationship("Room_reservation", back_populates="room", cascade="all, delete")

class RoomSchema(ma.Schema):

    type = fields.String(validate=OneOf(VALID_TYPE))

    status = fields.String(validate=OneOf(VALID_STATUS))

    # @validates("status")
    # def validate_status(self, value):
    #     if value == VALID_STATUS[1]:
    #         stmt = db.select(db.func.count()).select_from(Room).filter_by(status=VALID_STATUS[1])
    #         count = db.session.scalar(stmt)

    #         if count > 0:
    #             raise ValidationError("You already have an occupy room")

    # create hotel use by marshmallow
    hotel = fields.Nested("HotelSchema", only = ["name", "location"])

    room_amenity = fields.List(fields.Nested("Room_amenitySchema",exclude=["room"] ))

    room_reservation = fields.List(fields.Nested("Room_reservationSchema",exclude=["room"] ))

    class Meta:
        fields = ("id", "type", "price", "status", "hotel", "room_amenity")
        order = True

room_schema = RoomSchema()
rooms_schema = RoomSchema(many=True)