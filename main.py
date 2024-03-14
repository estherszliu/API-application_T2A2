from errors import BadRequestError, UnauthorisedUserError, NotFoundError, ConflictError
from marshmallow.exceptions import ValidationError
from sqlalchemy.exc import IntegrityError
from init import db, ma, bcrypt, jwt
from psycopg2 import errorcodes
from flask import Flask
import os


def create_app():
    app = Flask(__name__)

    # tell flask do not sort the keys. 
    app.json.sort_keys = False

    # configs
    app.config["SQLALCHEMY_DATABASE_URI"]=os.environ.get("DATABASE_URI")
    app.config["JWT_SECRET_KEY"]=os.environ.get("JWT_SECRET_KEY")

    #connect libraries with flask app
    db.init_app(app)
    ma.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    @app.errorhandler(ValidationError)
    def validation_error(error):
        return {"error": error.messages}, 400
    
    @app.errorhandler(BadRequestError)
    def bad_request_error(error):
        return {"error": str(error)}, 400
    
    @app.errorhandler(UnauthorisedUserError)
    def unauthorised_user_error(error):
        return {"error": str(error)}, 403
    
    @app.errorhandler(NotFoundError)
    def not_found_error(error):
        return {"error": str(error)}, 404

    @app.errorhandler(ConflictError)
    def conflict_error(error):
        return {"error": str(error)}, 409
    
    @app.errorhandler(IntegrityError)
    def integrity_error(error):
        print("start")
        print(str(error.orig.diag))
        
        print("end")
        if error.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"The {error.orig.diag.column_name} is required"}, 400
        if error.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {"error": f"{error.orig}"}, 409
        
        return {"error": f"Unknown integrity error"}, 500

    # register cli_controller blueprint 
    from controllers.cli_controller import db_commands
    app.register_blueprint(db_commands)

    # register auth_controller blueprint 
    from controllers.user_auth_controller import auth_bp
    app.register_blueprint(auth_bp)

    from controllers.room_controller import rooms_bp
    app.register_blueprint(rooms_bp)

    from controllers.amenity_controller import amenity_bp
    app.register_blueprint(amenity_bp)

    from controllers.reservation_controller import reservation_bp
    app.register_blueprint(reservation_bp)

    from controllers.user_controller import user_bp
    app.register_blueprint(user_bp)

    return app