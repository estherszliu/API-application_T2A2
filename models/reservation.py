from init import db, ma


class Reservation(db.Model):
    __tablename__ = "reservations"

    id = db.Column(db.Integer, primary_key=True)
    check_in_date = db.Column(db.Date, nullable=False)
    check_out_date = db.Column(db.Date, nullable=False)
    total_night = db.Column(db.Integer)
   
    

class ReservationSchema(ma.Schema):

    class Meta:
        fields = ("id", "check_in_date", "check_out_date","total_night")

reservation_schema = ReservationSchema()
reservations_schema = ReservationSchema(many=True)