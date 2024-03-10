from init import db, ma

from marshmallow import fields

class Amenity(db.Model):
    __tablename__ = "amenities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    cost = db.Column(db.Integer)
    description = db.Column(db.Text)

    room_amenity = db.relationship("Room_amenity", back_populates="amenity")
class AmenitySchema(ma.Schema):
    
    # room_amenity = fields.List(fields.Nested("Room_amenitySchema"), exclude=["amenity"])
    room_amenity = fields.List(fields.Nested("Room_amenitySchema"))
    class Meta:
        fields = ("id", "name", "cost", "description")


amenity_schema = AmenitySchema()
amenities_schema = AmenitySchema(many=True)