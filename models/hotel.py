from init import db, ma
from marshmallow import fields

class Hotel(db.Model):
    __tablename__ = "hotel"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False)
    contact = db.Column(db.String, nullable=False)
    # sqlalchemy create a relationship between rooms to hotel
    rooms = db.relationship("Room", back_populates="hotel", cascade="all, delete")

class HotelSchema(ma.Schema):
    rooms = fields.List(fields.Nested("RoomSchema", exclude=["hotel"]))

    class Meta:
        fields = ("id", "name", "location", "email", "contact", "rooms")





