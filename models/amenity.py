from init import db, ma

class Amenity(db.Model):
    __tablename__ = "amenities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    cost = db.Column(db.Integer)
    description = db.Column(db.Text)


class AmenitySchema(ma.Schema):

    class Meta:
        fields = ("id", "name", "cost", "decription")


amenity_schema = AmenitySchema()
amenities_schema = AmenitySchema(many=True)