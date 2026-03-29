from ..models.food import Food
from .. import db

class FoodService:
    
    @staticmethod
    def get_all_foods():
        """获取所有食材"""
        return Food.query.all()
    
    @staticmethod
    def get_food_by_id(food_id: int):
        """根据 ID 获取单个食材"""
        return Food.query.get(food_id)
    
    @staticmethod
    def create_food(name: str, category: str = None, calories: float = None, 
                    season: str = None, tags: str = None):
        """新增食材"""
        food = Food(
            name=name,
            category=category,
            calories=calories,
            season=season,
            tags=tags
        )
        db.session.add(food)
        db.session.commit()
        return food
    
    @staticmethod
    def update_food(food_id: int, **kwargs):
        """更新食材信息"""
        food = Food.query.get(food_id)
        if not food:
            return None
        
        for key, value in kwargs.items():
            if hasattr(food, key):
                setattr(food, key, value)
        
        db.session.commit()
        return food
    
    @staticmethod
    def delete_food(food_id: int):
        """删除食材"""
        food = Food.query.get(food_id)
        if not food:
            return False
        db.session.delete(food)
        db.session.commit()
        return True