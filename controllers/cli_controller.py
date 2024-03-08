from flask import Blueprint

from init import db, bcrypt
from models.hotel import Hotel
from models.room import Room
from models.amenity import Amenity
from models.reservation import Reservation
from models.user import User

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

    users = [
        User(
            email="admin@bigohotel.com",
            password=bcrypt.generate_password_hash("123456").decode("utf-8"),
            is_admin=True
        ),
        User(
            first_name="Esther",
            last_name="Dennis",
            email="123456@gmail.com",
            password=bcrypt.generate_password_hash("123456").decode("utf-8")
        )
    ]

    db.session.add_all(users)

    rooms = [
        Room(
            type = "King",
            price = 256,
            status = "avalible",
            hotel = hotel[0]
        ),
        Room(
            type = "Queen",
            price = 228,
            status = "avalible",
            hotel = hotel[0]
        ),
        Room(
            type = "twin",
            price = 256,
            status = "avalible",
            hotel = hotel[0]
        ),
         Room(
            type = "King",
            price = 256,
            status = "avalible",
            hotel = hotel[0]
        ),
        Room(
            type = "Queen",
            price = 228,
            status = "avalible",
            hotel = hotel[0]
        ),
        Room(
            type = "twin",
            price = 256,
            status = "avalible",
            hotel = hotel[0]
        ),
         Room(
            type = "King",
            price = 256,
            status = "avalible",
            hotel = hotel[0]
        ),
        Room(
            type = "Queen",
            price = 228,
            status = "avalible",
            hotel = hotel[0]
        ),
        Room(
            type = "twin",
            price = 256,
            status = "avalible",
            hotel = hotel[0]
        )
    ]
    db.session.add_all(rooms)
    db.session.commit()

    print("Tables seeded")

    
