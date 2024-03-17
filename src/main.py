import os
from flask import Flask
from init import bcrypt, db, jwt, ma
from marshmallow.exceptions import ValidationError
from psycopg2 import errorcodes
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest, Forbidden, Unauthorized, NotFound, Conflict


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

    # set up global error handling
    @app.errorhandler(ValidationError)
    def validation_error(error):
        return {"error": error.messages}, 400

    @app.errorhandler(BadRequest)
    def bad_request(error):
        return {"error": error.description}, 400
    
    @app.errorhandler(Unauthorized)
    def unauthorized(error):
        return {"error": error.description}, 401
    
    @app.errorhandler(Forbidden)
    def forbidden(error):
        return {"error": error.description}, 403
    
    @app.errorhandler(NotFound)
    def not_found(error):
        return {"error": error.description}, 404

    @app.errorhandler(Conflict)
    def conflict(error):
        return {"error": error.description}, 409
    
    @app.errorhandler(IntegrityError)
    def integrity_error(error):
        if error.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"The {error.orig.diag.column_name} is required"}, 400
        if error.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {"error": f"{error.orig.diag.message_detail}"}, 409
        
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