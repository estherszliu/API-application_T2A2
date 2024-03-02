from flask import Blueprint
from init import db
from models.hotel import Hotel
from models.room import Room
from models.amenity import Amenity


db_commands = Blueprint("db", __name__)


@db_commands.cli.command('create')
def create_tables():
    db.create_all()
    print("Tables created")

@db_commands.cli.command("drop")
def drop_tables():
    db.drop_all()
    print("Tables dropped")


@db_commands.cli.command("seed")
def seed_tables(): 
    hotel = [
        Hotel(
            name = "Big O hotel",
            location = "Brisbane",
            email = "bigohotel@bitohotel.com",
            contact = "12345678"
        )
    ]
    db.session.add_all(hotel)
    db.session.commit()

    print("Tables seeded")

    
