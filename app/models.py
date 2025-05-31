from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)



class Palette(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    hex_list = db.Column(db.PickleType, nullable=False)  # Ex: ['#123456', '#ABCDEF']
    description = db.Column(db.Text)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    creator = db.relationship('User', backref='palettes')

class Favorite(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    palette_id = db.Column(db.Integer, db.ForeignKey('palette.id'), primary_key=True)


