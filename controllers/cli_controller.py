from flask import Blueprint
from datetime import datetime, timedelta, date

from init import db, bcrypt
from models.hotel import Hotel
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
    hotel = Hotel(
            name = "Big O hotel",
            location = "Brisbane",
            email = "bigohotel@bitohotel.com",
            contact = "12345678"
        )
    db.session.add(hotel)

    users = [
        User(
            email="admin@bigohotel.com",
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
            price = 256,
            status = "avalible",
            hotel = hotel
        ),
        Room(
            type = "Queen",
            price = 228,
            status = "avalible",
            hotel = hotel
        ),
        Room(
            type = "twin",
            price = 256,
            status = "avalible",
            hotel = hotel
        ),
         Room(
            type = "King",
            price = 256,
            status = "avalible",
            hotel = hotel
        ),
        Room(
            type = "Queen",
            price = 228,
            status = "avalible",
            hotel = hotel
        ),
        Room(
            type = "twin",
            price = 256,
            status = "avalible",
            hotel = hotel
        ),
         Room(
            type = "King",
            price = 256,
            status = "avalible",
            hotel = hotel
        ),
        Room(
            type = "Queen",
            price = 228,
            status = "avalible",
            hotel = hotel
        ),
        Room(
            type = "twin",
            price = 256,
            status = "avalible",
            hotel = hotel
        )
    ]
    db.session.add_all(rooms)

    amenity = [
        Amenity(
            name = "Swimming pool",
            cost = 0,
            description = "Swimming pool is open from 8am to 9pm everydays for all the room guests"
        ),
        Amenity(
            name = "Gymnasium",
            cost = 0,
            description = "Gymnasium is open 24 hours for all the room guests, access by the room card"
        ),
        Amenity(
            name = "Hotel breakfast",
            cost = 60,
            description = "Breakfast buffet from morning 6am to 10am everyday"
        )
    ]
    db.session.add_all(amenity)

    reservation = [
        Reservation(
            check_in_date = datetime(24, 5, 9).date(),
            check_out_date = datetime(24, 5, 10).date(),
            total_night = 1
        ),
        Reservation(
            check_in_date = datetime(24, 6, 9).date(),
            check_out_date = datetime(24, 6, 15).date(),
            total_night = 6
        ),
        Reservation(
            check_in_date = datetime(24, 7, 10).date(),
            check_out_date = datetime(24, 7, 15).date(),
            total_night = 5
        ),
        Reservation(
            check_in_date = datetime(24, 5, 9).date(),
            check_out_date = datetime(24, 5, 19).date(),
            total_night = 10
        )
    ]
    db.session.add_all(reservation)

    room_amenity = [
        Room_amenity(
            room = rooms[0],
            amenity = amenity[0]
        ),
        Room_amenity(
            room = rooms[0],
            amenity = amenity[2]
        ),
        Room_amenity(
            room = rooms[1],
            amenity = amenity[0]
        ),
        Room_amenity(
            room = rooms[1],
            amenity = amenity[1]
        ),
        Room_amenity(
            room = rooms[1],
            amenity = amenity[2]
        ),
        Room_amenity(
            room = rooms[2],
            amenity = amenity[0]
        ),
        Room_amenity(
            room = rooms[2],
            amenity = amenity[2]
        ),
        Room_amenity(
            room = rooms[3],
            amenity = amenity[0]
        ),
        Room_amenity(
            room = rooms[3],
            amenity = amenity[2]
        ),
        Room_amenity(
            room = rooms[4],
            amenity = amenity[0]
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
        ),
        User_reservation(
            user = users[3],
            reservation = reservation[2],
            reservation_date = date.today()
        ),
        User_reservation(
            user = users[4],
            reservation = reservation[3],
            reservation_date = date.today()
        )
    ]
    db.session.add_all(user_reservation)

    room_reservation = [
        Room_reservation(
            room = rooms[0],
            reservation = reservation[0],
            total_cost = (rooms[0].price) * (reservation[0].total_night)
        ),
        Room_reservation(
            room = rooms[1],
            reservation = reservation[1],
            total_cost = (rooms[1].price) * (reservation[1].total_night)
        ),
        Room_reservation(
            room = rooms[2],
            reservation = reservation[2],
            total_cost = (rooms[2].price) * (reservation[2].total_night)
        ),
        Room_reservation(
            room = rooms[3],
            reservation = reservation[3],
            total_cost = (rooms[3].price) * (reservation[3].total_night)
        )

    ]
    db.session.add_all(room_reservation)
    db.session.commit()

    print("Tables seeded")

    
