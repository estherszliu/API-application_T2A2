from init import db, ma
from marshmallow import fields

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)


    user_reservation = db.relationship("User_reservation", back_populates="user", cascade="all, delete")

class UserSchema(ma.Schema):

    user_reservation = fields.List(fields.Nested("User_reservationSchema",exclude=["user"] ))

    class Meta:
        fields = ("id", "first_name", "last_name", "email","password", "is_admin", "user_reservation")

user_schema = UserSchema(exclude=["password"])
users_schema = UserSchema(many=True, exclude=["password"])