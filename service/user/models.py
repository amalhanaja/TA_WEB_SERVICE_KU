from app import db


class User(db.Model):
    uuid = db.Column(db.String(36), primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    phone_number = db.Column(db.BigInteger, nullable=False)
    country_code = db.Column(db.SmallInteger, nullable=False)
    fcm_token = db.Column(db.String, nullable=False)
