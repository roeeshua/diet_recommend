from .. import db
from datetime import date, datetime  # 添加这一行

class Checkin(db.Model):
    __tablename__ = 'checkins'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    checkin_date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.Boolean, default=True)
    actual_calories = db.Column(db.Integer)
    notes = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.checkin_date.isoformat(),
            'status': self.status,
            'actual_calories': self.actual_calories,
            'notes': self.notes
        }