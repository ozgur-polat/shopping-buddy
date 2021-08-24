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
    journeys = db.relationship('Journey', backref='user', lazy=True)
 
    def set_password(self,password):
        self.password_hash = generate_password_hash(password)
     
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)
 
 
@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Neighbourhood(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    journeys = db.relationship('Journey', backref='neighbourhood', lazy=True)

class Store(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    address = db.Column(db.String(120))
    journeys = db.relationship('Journey', backref='store', lazy=True)

class Journey(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    n_id = db.Column(db.Integer, db.ForeignKey('neighbourhood.id'), nullable=False)
    s_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    cost = db.Column(db.Integer)
    passenger_limit = db.Column(db.Integer)
    note = db.Column(db.String(100))
    passenger_list = db.Column(db.String(100))
    is_cancelled = db.Column(db.Integer)
