import datetime

import jwt

from app import db, app
from passlib.apps import custom_app_context as context


class Driver(db.Model):
    __tablename__ = "driver"
    driver_uuid = db.Column(db.String(36), primary_key=True)
    username = db.Column(db.String(32), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), unique=True, nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    phone_number = db.Column(db.BigInteger, nullable=False, unique=True)
    country_code = db.Column(db.SmallInteger, nullable=False)
    fcm_token = db.Column(db.String, nullable=False, unique=True)
    status = db.Column(db.String(16), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    last_modified = db.Column(db.DateTime, nullable=False)

    def hash_password(self, password):
        self.password_hash = context.encrypt(password)

    def verify_password(self, password):
        return context.verify(password, self.password_hash)

    """
    expires_in: Must Be datetime type
    """

    def generate_token(self, expires_in):
        try:
            payload = {
                "exp": datetime.datetime.utcnow() + expires_in,
                "iat": datetime.datetime.utcnow(),
                "sub": self.driver_uuid
            }
            return jwt.encode(
                payload,
                app.config["SECRET_KEY"],
                "HS256"
            )
        except Exception as e:
            print(e)

    @staticmethod
    def verify_token(token):
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
