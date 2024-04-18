from app import app, db
# from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    questionaire_filled = db.Column(db.Boolean, default=False)

class UserResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    q_1 = db.Column(db.String(10))
    q_2 = db.Column(db.String(10))
    q_3 = db.Column(db.String(10))
    q_4 = db.Column(db.String(100))
    q_5_breathing = db.Column(db.String(100))
    q_5_chest = db.Column(db.String(100))
    q_5_speech = db.Column(db.String(100))
    q_5_pale = db.Column(db.String(100))
    q_5_none = db.Column(db.String(100))
    date_created = db.Column(db.DateTime, nullable=True)

    # Define the relationship to the User model
    user = db.relationship('User', backref='responses')

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(255), nullable=False)
    result = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    gptResponse = db.Column(db.String(5000), nullable=True)

    # Define the foreign key relationship
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('images', lazy=True))