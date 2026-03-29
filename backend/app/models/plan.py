from .. import db
from datetime import date, datetime  # 添加这一行

class Plan(db.Model):
    __tablename__ = 'plans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_date = db.Column(db.Date, nullable=False, default=date.today)  # 这里用了 date
    breakfast = db.Column(db.String(200))
    lunch = db.Column(db.String(200))
    dinner = db.Column(db.String(200))
    total_calories = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 这里用了 datetime
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.plan_date.isoformat(),
            'breakfast': self.breakfast.split(',') if self.breakfast else [],
            'lunch': self.lunch.split(',') if self.lunch else [],
            'dinner': self.dinner.split(',') if self.dinner else [],
            'total_calories': self.total_calories
        }