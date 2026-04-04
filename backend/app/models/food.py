from .. import db

class Food(db.Model):
    __tablename__ = 'foods'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    calories = db.Column(db.Float)
    season = db.Column(db.String(20))
    tags = db.Column(db.String(200))
    features = db.Column(db.JSON, default=list)
    
    # 新增营养指标字段（十分制）
    protein = db.Column(db.Integer, default=5)      # 蛋白质
    fiber = db.Column(db.Integer, default=5)        # 膳食纤维
    vitamins = db.Column(db.Integer, default=5)     # 微量元素
    sugar = db.Column(db.Integer, default=5)        # 添加糖
    saturated_fat = db.Column(db.Integer, default=5) # 饱和脂肪
    sodium = db.Column(db.Integer, default=5)       # 钠
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
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
            'sodium': self.sodium
        }