import datetime
import uuid
from functools import wraps

import jwt
from flask import Flask, jsonify, request, abort, g
from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as context
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)


class Driver(db.Model):
    __tablename__ = "driver"
    driver_uuid = db.Column(db.String(36), primary_key=True)
    username = db.Column(db.String(32), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), unique=True, nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    phone_number = db.Column(db.BigInteger, nullable=False)
    country_code = db.Column(db.SmallInteger, nullable=False)
    fcm_token = db.Column(db.String, nullable=False, unique=True)
    status = db.Column(db.String(16), nullable=False, default="IDLE")
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())
    last_modified = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())

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
                "sub": self.driver_uuid.__str__()
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


def requires_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        header = request.headers.get("Authorization")
        if not header:
            abort(400)
        parts = header.split()
        if parts[0].lower != "bearer":
            abort(400)
        elif len(parts) == 1:
            abort(400)
        elif len(parts) > 2:
            abort(400)
        token = parts[1]
        payload = Driver.verify_token(token)
        if not payload:
            abort(401)
        driver = Driver.query.filter_by(driver_uuid=payload["sub"]).first()
        if not driver:
            abort(401)
        g.driver = driver

    return decorated


@app.route("/driver/register", methods=["POST"])
def register_driver():
    username = request.json.get("username")
    password = request.json.get("password")
    first_name = request.json.get("firstName")
    last_name = request.json.get("lastName")
    phone_number = request.json.get("phoneNumber")
    country_code = request.json.get("countryCode")
    fcm_token = request.json.get("fcmToken")

    if not username or not password or not first_name or not last_name or not phone_number or not country_code \
            or not fcm_token:
        abort(400)
    if Driver.query.filter((Driver.username == username) | (
                Driver.fcm_token == fcm_token) | (Driver.phone_number == phone_number)).first():
        abort(400)
    try:
        driver = Driver(driver_uuid=uuid.uuid4().__str__(),
                        username=username,
                        first_name=first_name,
                        last_name=last_name,
                        phone_number=phone_number,
                        country_code=country_code,
                        fcm_token=fcm_token)
        driver.hash_password(password)
        db.session.add(driver)
        db.session.commit()
        return jsonify(), 201
    except IntegrityError as e:
        print(e)
        abort(401)


@app.route("/driver", methods=["GET"])
@requires_token
def get_driver():
    driver = g.driver
    return jsonify(driver.__dict__)


@app.route("/driver/login", methods=["POST"])
def login_driver():
    username = request.json.get("username")
    password = request.json.get("password")
    fcm_token = request.json.get("fcmToken")
    if not username or not password or not fcm_token:
        abort(400)
    driver = Driver.query.filter_by(username=username).first()
    if not driver or not driver.verify_password(password):
        abort(404)
    if fcm_token != driver.fcm_token:
        abort(401)
    token_expiration_time = datetime.timedelta(days=365)
    token = driver.generate_token(expires_in=token_expiration_time)
    return jsonify(
        accessToken=token.decode("utf-8"),
        expiresIn=token_expiration_time.total_seconds(),
        tokenType="Bearer")


if __name__ == "__main__":
    app.run(debug=True, port=5001, host="0.0.0.0")
