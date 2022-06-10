from exts import db
from datetime import datetime


class UserModel(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(10), nullable=False, unique=True)
    phone = db.Column(db.String(11), nullable=False, unique=True)
    password = db.Column(db.String(20), nullable=False)
    join_time = db.Column(db.DateTime, default=datetime.now)
    icon = db.Column(db.String(200), nullable=True)