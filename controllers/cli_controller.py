from flask import Blueprint
from datetime import datetime, timedelta, date

from init import db, bcrypt
from models.room import Room
from models.amenity import Amenity
from models.reservation import Reservation
from models.user import User
from models.room_amenity import Room_amenity
from models.user_reservation import User_reservation
from models.room_reservation import Room_reservation

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

    users = [
        User(
            first_name ="Patrick",
            last_name = "Cummins",
            email="patrick@gmail.com",
            password=bcrypt.generate_password_hash("123456").decode("utf-8"),
            is_admin=True
        ),
        User(
            first_name="Esther",
            last_name="Dennis",
            email="esther@gmail.com",
            password=bcrypt.generate_password_hash("123456").decode("utf-8")
        ),
        User(
            first_name="Emma",
            last_name="Jason",
            email="emma@gmail.com",
            password=bcrypt.generate_password_hash("123456").decode("utf-8")
        ),
        User(
            first_name="Jasmine",
            last_name="Marshall",
            email="jasmine@gmail.com",
            password=bcrypt.generate_password_hash("123456").decode("utf-8")
        ),
        User(
            first_name="Willow",
            last_name="Rose",
            email="willow@gmail.com",
            password=bcrypt.generate_password_hash("123456").decode("utf-8")
        )
    ]

    db.session.add_all(users)

    rooms = [
        Room(
            type = "King",
            price = 256
        ),
        Room(
            type = "Queen",
            price = 228
        ),
        Room(
            type = "Double",
            price = 218
        )
    ]
    db.session.add_all(rooms)

    amenity = [
        Amenity(
            name = "Swimming pool",
            description = "Swimming pool is open from 8am to 9pm everydays for all the room guests"
        ),
        Amenity(
            name = "Gymnasium",
            description = "Gymnasium is open 24 hours for all the room guests, access by the room card"
        ),
        Amenity(
            name = "Hotel breakfast",
            description = "Breakfast buffet from morning 6am to 10am everyday"
        )
    ]
    db.session.add_all(amenity)

    reservation = [
        Reservation(
            check_in_date = datetime(2024, 5, 9).date(),
            check_out_date = datetime(2024, 5, 10).date(),
            total_cost = 256
        ),
        Reservation(
            check_in_date = datetime(2024, 6, 9).date(),
            check_out_date = datetime(2024, 6, 15).date(),
            total_cost = 1368
        )
    ]
    db.session.add_all(reservation)

    room_amenity = [
        Room_amenity(
            room = rooms[0],
            amenity = amenity[0]
        ),
        Room_amenity(
            room = rooms[1],
            amenity = amenity[1]
        )

    ]
    db.session.add_all(room_amenity)

    user_reservation = [
        User_reservation(
            user = users[1],
            reservation = reservation[0],
            reservation_date = date.today()
        ),
        User_reservation(
            user = users[2],
            reservation = reservation[1],
            reservation_date = date.today()
        )
    ]
    db.session.add_all(user_reservation)

    room_reservation = [
        Room_reservation(
            room = rooms[0],
            reservation = reservation[0]
        ),
        Room_reservation(
            room = rooms[1],
            reservation = reservation[1]
        )

    ]
    db.session.add_all(room_reservation)
    db.session.commit()

    print("Tables seeded")

    
