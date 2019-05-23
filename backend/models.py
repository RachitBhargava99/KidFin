from backend import db
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin
from flask import current_app
from datetime import datetime


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(127), nullable=False)
    email = db.Column(db.String(63), unique=False, nullable=False)
    password = db.Column(db.String(63), unique=False, nullable=False)
    isParent = db.Column(db.Boolean, nullable=False, default=True)
    accountId = db.Column(db.Integer, nullable=False, default=-1)
    parent_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    isSnap = db.Column(db.Boolean, nullable=False, default=False)
    snapPic = db.Column(db.String(255), nullable=True)
    isActive = db.Column(db.Boolean, nullable=False, default=True)

    def get_auth_token(self, expires_seconds=86400):
        s = Serializer(current_app.config['SECRET_KEY'], expires_seconds)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def get_reset_token(self, expires_seconds=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_seconds)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User ID {self.id}"


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(127), nullable=False)


class Restriction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, nullable=True)
    transaction = db.Column(db.Integer, nullable=True)
    primary_location = db.Column(db.String(127), nullable=True)
    distance = db.Column(db.Integer, nullable=True)
    cat_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    isActive = db.Column(db.Boolean, nullable=False, default=True)


class Merchant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    merchant_id = db.Column(db.Integer, nullable=False)
    restriction = db.Column(db.Integer, db.ForeignKey('restriction.id'), nullable=True)


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False, default=0)
    merchant_id = db.Column(db.Integer, db.ForeignKey('merchant.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now())
