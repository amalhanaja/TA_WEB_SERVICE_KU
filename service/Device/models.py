from .app import db
from sqlalchemy.dialects.postgresql.

class Device(db):
    uuid = db.Column(db.String(36), primary_key=True)
    model = db.Column(db.String(32), nullable=False)
    brand = db.Column(db.String(16), nullable=False)
    os_version = db.Column(db.String(16), nullable=False)
    fcm_token = db.Column(db.String, nullable=False)