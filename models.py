from exts import db
from datetime import datetime


class ArticleModel(db.Model):
    __tablename__ = "article"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(10), nullable=False)
    abstract = db.Column(db.String(11), nullable=False)
    filepath = db.Column(db.String(20), nullable=False)
    join_time = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.Integer, nullable=True, default=1)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # 在ORM层面绑定两者之间的关系，第一个参数是绑定的表的类名，
    # 第二个参数back_populates是通过User反向访问时的字段名称
    user = db.relationship('UserModel', backref="articles")

    def keys(self):
        return ['id', 'title', 'abstract', 'join_time', 'status']

    def __getitem__(self, item):
        return getattr(self, item)


class UserModel(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(10), nullable=False, unique=True)
    phone = db.Column(db.String(11), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    join_time = db.Column(db.DateTime, default=datetime.now)
    icon = db.Column(db.String(200), nullable=True)
