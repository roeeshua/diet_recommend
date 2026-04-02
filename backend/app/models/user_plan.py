from .. import db
from datetime import datetime

class UserPlan(db.Model):
    __tablename__ = 'user_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_name = db.Column(db.String(100), nullable=False)
    foods = db.Column(db.JSON, nullable=False)  # 存储三餐食物列表
    total_calories = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'plan_name': self.plan_name,
            'foods': self.foods,
            'total_calories': self.total_calories,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }