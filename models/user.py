import bleach
import re
from init import db, ma
from marshmallow import fields, validates
from marshmallow.exceptions import ValidationError


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


class UserLoadSchema(ma.Schema):
    first_name = fields.String(required=True, nullable=False)
    last_name = fields.String(required=True, nullable=False)
    email = fields.String(nullable=False)
    password = fields.String(nullable=False)
    
    @validates("first_name")
    def validate_first_name(self, value):
        if not value.isalpha():
            raise ValidationError("invalid characters in first name")

        if len(value) < 2:
            raise ValidationError("first name must be at least 2 characters long")

    @validates("last_name")
    def validate_last_name(self, value):
        if not value.isalpha():
            raise ValidationError("invalid characters in last name")

        if len(value) < 2:
            raise ValidationError("last name must be at least 2 characters long")

    @validates("email")
    def validate_email(self, value):
        sanitized_value = bleach.clean(value, strip=True)
        if sanitized_value != value:
            raise ValidationError("invalid characters in email")

        # Regular expression pattern for email validation
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        regex = re.compile(pattern)
        
        # Match the email against the pattern
        if not regex.match(value):
            raise  ValidationError(f"email address {value} is an invalid email")

    @validates("password")
    def validate_password(self, value):
        sanitized_value = bleach.clean(value, strip=True)
        if sanitized_value != value:
            raise ValidationError("invalid characters in password")

        if len(value) < 6:
            raise ValidationError("password must be at least 6 characters long")
        
    class Meta:
        fields = ("first_name", "last_name", "email", "password")

  
user_schema = UserSchema(exclude=["password"])
users_schema = UserSchema(many=True, exclude=["password"])
user_load_schema = UserLoadSchema()