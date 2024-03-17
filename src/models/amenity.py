import bleach
from init import db, ma
from marshmallow import fields, validates
from marshmallow.exceptions import ValidationError
from marshmallow.validate import OneOf



VALID_NAME = ("Swimming pool", "Gymnasium", "Hotel breakfast", "Day spa", "Shuttle bus")

class Amenity(db.Model):
    __tablename__ = "amenities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)

    room_amenity = db.relationship("Room_amenity", back_populates="amenity", cascade="all, delete")
class AmenitySchema(ma.Schema):
    
    name = fields.String(validate=OneOf(VALID_NAME))

    @validates("description")
    def validate_description(self, value):
    
        sanitized_description = bleach.clean(value, strip=True)
        if sanitized_description != value:
            raise ValidationError("Description contains invalid characters.")
    
    room_amenity = fields.List(fields.Nested("Room_amenitySchema"))
    class Meta:
        fields = ("id", "name", "description")


amenity_schema = AmenitySchema()
amenities_schema = AmenitySchema(many=True)