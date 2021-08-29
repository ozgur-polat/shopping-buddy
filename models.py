from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager
 
login = LoginManager()
db = SQLAlchemy()
 
class User(UserMixin, db.Model):
 
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True)
    name = db.Column(db.String(100))
    surname = db.Column(db.String(100))
    password_hash = db.Column(db.String())
    city = db.Column(db.String(100))
    postcode = db.Column(db.String(100))
    lat = db.Column(db.Float())
    lon = db.Column(db.Float())
    journey = db.relationship('JourneyRequest', backref='user', lazy=True)
 
    def set_password(self,password):
        self.password_hash = generate_password_hash(password)
     
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)
 
 
@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Store(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    city = db.Column(db.String(100))
    postcode = db.Column(db.String(100))
    lat = db.Column(db.Float())
    lon = db.Column(db.Float())
    journey = db.relationship('JourneyRequest', backref='store', lazy=True)
    journey = db.relationship('Journey', backref='store', lazy=True)


class JourneyRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    requester_lat = db.Column(db.Float())
    requester_lon = db.Column(db.Float())
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    store_name = db.Column(db.String(100))
    store_lat = db.Column(db.Float())
    store_lon = db.Column(db.Float())
    date = db.Column(db.DateTime)


class Journey(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    s_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    passenger_list = db.Column(db.String(100))
    date = db.Column(db.DateTime)