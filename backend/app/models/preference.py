from .. import db
from datetime import datetime

class Preference(db.Model):
    __tablename__ = 'preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)   # 如: taste, allergy, diet_type
    value = db.Column(db.String(100), nullable=False)     # 如: 辣, 海鲜, 素食
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category': self.category,
            'value': self.value,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }