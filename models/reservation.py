from init import db, ma


class Reservation(db.Model):
    __tablename__ = "reservations"

    id = db.Column(db.Integer, primary_key=True)
    check_in_date = db.Column(db.date, nullable=False)
    check_out_date = db.Column(db.date, nullable=False)
    total_cost = db.Column(db.Integer, nullable=False)

class ReservationSchema(ma.Schema):

    class Meta:
        fields = ("id", "check_in_date", "check_out_date", "total_cost")

reservation_schema = ReservationSchema()
reservation_schema = ReservationSchema(many=True)