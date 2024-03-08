from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes
from init import db
from models.amenity import Amenity, amenity_schema, amenities_schema

amenity_bp = Blueprint("amenities", __name__, url_prefix="/amenities")

# Get all the amenities  http://localhost:8090/amenities  --GET
@amenity_bp.route("/")
def get_all_amenities():
    stmt = db.select(Amenity).order_by(Amenity.id)
    amenities = db.session.scalars(stmt)
    return amenities_schema.dump(amenities)

# Get a single amenity route  http://localhost:8090/amenities/4  --GET
@amenity_bp.route("/<int:amenity_id>")
def get_one_amenity(amenity_id):
    stmt = db.select(Amenity).filter_by(id=amenity_id) 
    amenity = db.session.scalar(stmt)
    if amenity:
        return amenity_schema.dump(amenity)
    else:
        return {"Error": f"Amenity with id {amenity_id} not found"}, 404

 # create an amenity  http://localhost:8090/amenities  --POST
@amenity_bp.route("/", methods=["POST"])
def create_amenity():
    try:
        body_data = request.get_json()
        amenity = Amenity(
            name = body_data.get("name"),
            cost = body_data.get("cost"),
            description = body_data.get("description")
        )
        db.session.add(amenity)
        db.session.commit()
        return amenity_schema.dump(amenity), 201
    
    
    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"The {err.orig.diag.column_name} is required"}, 409
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {"error": "Amenity name already in exist"}, 409



# delete amenity route  http://localhost:8090/amenities/1 --DELETE
@amenity_bp.route("/<int:amenity_id>", methods=["DELETE"])
def delete_amenity(amenity_id):
    stmt = db.select(Amenity).where(Amenity.id == amenity_id)
    amenity = db.session.scalar(stmt)
    if amenity:
        db.session.delete(amenity)
        db.session.commit()
        return {"message": f"Amenity {amenity_id} deleted successfully"}
    else:
        return {"error": f"Amenity with id {amenity_id} not found"}, 404


# update Amenity route   
# http://localhost:8090/amenities/2  -- acept both PUT and PATCH
@amenity_bp.route("/<int:amenity_id>", methods=["PUT", "PATCH"])
def update_amenity(amenity_id):
    body_data = request.get_json()
    stmt = db.select(Amenity).filter_by(id=amenity_id)
    amenity = db.session.scalar(stmt)
    if amenity:
         try:
            amenity.name = body_data.get("name") or amenity.type
            amenity.cost = body_data.get("cost") or amenity.cost
            amenity.description = body_data.get("description") or amenity.description
            db.session.commit()
            return amenity_schema.dump(amenity)
         except IntegrityError as err:
            if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
                return {"error": "Amenity name already in exist"}, 409
     
