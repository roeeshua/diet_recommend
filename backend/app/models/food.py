from .. import db

class Food(db.Model):
    __tablename__ = 'foods'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))  # 主食/蛋白质/蔬菜/水果
    calories = db.Column(db.Float)       # 每100g热量
    season = db.Column(db.String(20))    # 春季/夏季/秋季/冬季/四季
    tags = db.Column(db.String(200))     # 标签，如"辣","低卡"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'calories': self.calories,
            'season': self.season,
            'tags': self.tags.split(',') if self.tags else []
        }