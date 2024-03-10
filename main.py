import os
from flask import Flask

from init import db, ma, bcrypt, jwt


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

    return app