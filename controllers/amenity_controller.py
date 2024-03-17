from controllers.validation_helpers import validate_amenity_exists, validate_amenity_not_assigned_to_any_rooms
from decorators import jwt_admin_required
from flask import Blueprint, request
from init import db
from models.amenity import Amenity, amenity_schema, amenities_schema

amenity_bp = Blueprint("amenities", __name__, url_prefix="/amenities")
    
# Get all the amenities  http://localhost:8090/amenities  --GET
@amenity_bp.route("/")
@jwt_admin_required
def get_all_amenities():

    # QUERY COMMENT
    #   Get an ordered list of all the data for each amenity in the database.
    #   Order the list according to amenity ids
    #   SELECT * FROM amenities ORDER BY id;
    stmt = db.select(Amenity).order_by(Amenity.id)
    amenities = db.session.scalars(stmt)
    return amenities_schema.dump(amenities)

# Get a single amenity route  http://localhost:8090/amenities/4  --GET
@amenity_bp.route("/<int:amenity_id>")
@jwt_admin_required
def get_one_amenity(amenity_id):
    validate_amenity_exists(amenity_id)

    # QUERY COMMENT
    #   Get the amenity which has the given amenity id
    #   This will return None if there is no amenity with that id
    #   SELECT * FROM amenities WHERE id = amenity_id
    amenity = db.session.query(Amenity) \
        .filter_by(id=amenity_id) \
        .first() 

    return amenity_schema.dump(amenity)

 # create an amenity  http://localhost:8090/amenities  --POST
@amenity_bp.route("/", methods=["POST"])
@jwt_admin_required
def create_amenity():

    # load the data
    body_data = amenity_schema.load(request.get_json())
    
    # create a new amenity
    amenity = Amenity(
        name = body_data.get("name"),
        description = body_data.get("description")
    )
    # QUERY COMMENT
    #   Add the new amenity to the amenity table
    db.session.add(amenity)

    db.session.commit()
    return amenity_schema.dump(amenity), 201
    

# delete amenity route  http://localhost:8090/amenities/1 --DELETE
@amenity_bp.route("/<int:amenity_id>", methods=["DELETE"])
@jwt_admin_required
def delete_amenity(amenity_id):

    # validate the data
    validate_amenity_exists(amenity_id)
    validate_amenity_not_assigned_to_any_rooms(amenity_id)

    # QUERY COMMENT
    #   Delete the amenity to the database that has the given amenity_id
    db.session.query(Amenity).where(Amenity.id == amenity_id).delete()
    db.session.commit()
    return {"message": f"Amenity {amenity_id} deleted successfully"}

    
# update amenity route   
# http://localhost:8090/amenities/2  -- acept both PUT and PATCH
@amenity_bp.route("/<int:amenity_id>", methods=["PUT", "PATCH"])
@jwt_admin_required
def update_amenity(amenity_id):
    
    # validate data
    validate_amenity_exists(amenity_id)

    # get the data from request
    body_data = amenity_schema.load(request.get_json())

    # QUERY COMMENT
    #   Get the amenity which has the given amenity id
    #   SELECT * FROM amenities WHERE id = amenity_id
    amenity = db.session.query(Amenity) \
        .filter_by(id=amenity_id) \
        .first()
    
    # update amenity data
    amenity.name = body_data.get("name") or amenity.name
    amenity.description = body_data.get("description") or amenity.description
    
    # save data back to database
    db.session.commit()
    return amenity_schema.dump(amenity)

   
     
