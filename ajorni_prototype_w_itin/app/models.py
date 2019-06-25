from datetime  import datetime
from app import db
from sqlalchemy.dialects.sqlite import BLOB
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from hashlib import md5

followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id')))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    itineraries = db.relationship('Itinerary', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship('User',
                               secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'),
                               lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_itineraries(self):
        followed =  Itinerary.query.join(followers, (followers.c.followed_id == Itinerary.user_id)).filter(
            followers.c.follower_id == self.id)
        own = Itinerary.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Itinerary.timestamp.desc())

class Itinerary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    city = db.Column(db.String(32))
    picture = db.Column(db.String(32))
    __searchable__ = ['name']

    def __repr__(self):
        return f'<Itinerary {self.name}>'

    def get_activities(self):
        return Activity.query.filter_by(itinerary_id=self.id).order_by(Activity.order_id.asc())


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    itinerary_id = db.Column(db.Integer, db.ForeignKey('itinerary.id'))
    description = db.Column(db.String(140))
    order_id = db.Column(db.Integer)
    # __searchable__ = ['name', 'description']

    def __repr__(self):
        return f'<Activity {self.name}>'

    def get_user(self):
        return Itinerary.query.filter_by(id=self.itinerary_id).first().user_id


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

