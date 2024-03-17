from init import db, ma
from marshmallow import fields

class Room_amenity(db.Model):
    __tablename__ ="room_amenity"

    id = db.Column(db.Integer, primary_key=True)
    # Foreignkey is provide by psql
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"), nullable=False)
    amenity_id = db.Column(db.Integer, db.ForeignKey("amenities.id"), nullable=False)

     # sqlalchemy create a relationship between tables
    room = db.relationship("Room", back_populates="room_amenity", cascade="all, delete")
    amenity = db.relationship("Amenity", back_populates="room_amenity", cascade="all, delete")


# create schema
class Room_amenitySchema(ma.Schema):
        
    # user schema to serialize the field back to python objects. 
    room = fields.Nested("RoomSchema", only=["id","type"])
    amenity = fields.Nested("AmenitySchema")
    
    class Meta():
        fields = ("id", "room", "amenity")


room_amenity_schema = Room_amenitySchema()
room_amenities_schema = Room_amenitySchema(many=True)