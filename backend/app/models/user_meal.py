from .. import db
from datetime import date,datetime

class UserMeal(db.Model):
    __tablename__ = 'user_meal'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    meal_date = db.Column(db.Date, nullable=False, default=date.today)
    meal_type = db.Column(db.Enum('breakfast', 'lunch', 'dinner'), nullable=False)
    food_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    calories = db.Column(db.Integer)
    season = db.Column(db.String(20))
    tags = db.Column(db.String(200))
    features = db.Column(db.JSON, default=list)
    protein = db.Column(db.Integer, default=5)
    fiber = db.Column(db.Integer, default=5)
    vitamins = db.Column(db.Integer, default=5)
    sugar = db.Column(db.Integer, default=5)
    saturated_fat = db.Column(db.Integer, default=5)
    sodium = db.Column(db.Integer, default=5)
    is_custom = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'meal_date': self.meal_date.isoformat(),
            'meal_type': self.meal_type,
            'food_name': self.food_name,
            'category': self.category,
            'calories': self.calories,
            'season': self.season,
            'tags': self.tags.split(',') if self.tags else [],
            'features': self.features or [],
            'protein': self.protein,
            'fiber': self.fiber,
            'vitamins': self.vitamins,
            'sugar': self.sugar,
            'saturated_fat': self.saturated_fat,
            'sodium': self.sodium,
            'is_custom': self.is_custom
        }