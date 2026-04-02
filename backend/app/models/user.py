from .. import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_first_login = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.Boolean, nullable=True)   # True=男, False=女
    height = db.Column(db.Float, nullable=True)
    weight = db.Column(db.Float, nullable=True)
    
    # 关联
    preferences = db.relationship('Preference', backref='user', lazy=True, cascade='all, delete-orphan')
    # plans = db.relationship('Plan', backref='user', lazy=True)
    checkins = db.relationship('Checkin', backref='user', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'is_first_login': self.is_first_login,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'age': self.age,
            'gender': self.gender,
            'height': self.height,
            'weight': self.weight
        }