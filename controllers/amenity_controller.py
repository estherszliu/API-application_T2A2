from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt_identity
from psycopg2 import errorcodes
from init import db
from models.amenity import Amenity, amenity_schema, amenities_schema
from models.user import User

amenity_bp = Blueprint("amenities", __name__, url_prefix="/amenities")

def is_user_admin():
    user_id = get_jwt_identity()
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    return user.is_admin

# Get all the amenities  http://localhost:8090/amenities  --GET
@amenity_bp.route("/")
@jwt_required()
def get_all_amenities():
    stmt = db.select(Amenity).order_by(Amenity.id)
    amenities = db.session.scalars(stmt)
    return amenities_schema.dump(amenities)

# Get a single amenity route  http://localhost:8090/amenities/4  --GET
@amenity_bp.route("/<int:amenity_id>")
@jwt_required()
def get_one_amenity(amenity_id):
    stmt = db.select(Amenity).filter_by(id=amenity_id) 
    amenity = db.session.scalar(stmt)
    if amenity:
        return amenity_schema.dump(amenity)
    else:
        return {"Error": f"Amenity with id {amenity_id} not found"}, 404

 # create an amenity  http://localhost:8090/amenities  --POST
@amenity_bp.route("/", methods=["POST"])
@jwt_required()
def create_amenity():
    is_admin = is_user_admin()
    if not is_admin:
        return {"error": "Not authorised to create a amenity"}, 403
    
    try:
        body_data = request.get_json()
        amenity = Amenity(
            name = body_data.get("name"),
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
@jwt_required()
def delete_amenity(amenity_id):
    is_admin = is_user_admin()
    if not is_admin:
        return {"error": "Not authorised to create a amenity"}, 403
    
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
@jwt_required()
def update_amenity(amenity_id):
    is_admin = is_user_admin()
    if not is_admin:
        return {"error": "Not authorised to create a amenity"}, 403
    
    body_data = request.get_json()
    stmt = db.select(Amenity).filter_by(id=amenity_id)
    amenity = db.session.scalar(stmt)

    if amenity:
        try:
            amenity.name = body_data.get("name") or amenity.type
            amenity.description = body_data.get("description") or amenity.description
            db.session.commit()
            return amenity_schema.dump(amenity)
        
        except IntegrityError as err:
            if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
                return {"error": f"Amenity name already in exist"}, 409
    else:
        return {"error": f"amenity with id {amenity_id} not found"}, 404
     
