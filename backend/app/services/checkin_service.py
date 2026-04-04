from ..models.user_meal import UserMeal
from ..models.food import Food
from .. import db
from datetime import datetime
from .profile_service import ProfileService

class CheckinService:
    
    @staticmethod
    def add_meal(user_id: int, meal_date: str, meal_type: str, food_data: dict):
        """添加一餐记录"""
        # 如果是自定义食物
        if food_data.get('is_custom'):
            features = food_data.get('features', [])
            meal = UserMeal(
                user_id=user_id,
                meal_date=meal_date,
                meal_type=meal_type,
                food_name=food_data['food_name'],
                category=food_data.get('category'),
                calories=food_data.get('calories'),
                season=food_data.get('season'),
                tags=food_data.get('tags'),
                features=features,
                protein=food_data.get('protein', 5),
                fiber=food_data.get('fiber', 5),
                vitamins=food_data.get('vitamins', 5),
                sugar=food_data.get('sugar', 5),
                saturated_fat=food_data.get('saturated_fat', 5),
                sodium=food_data.get('sodium', 5),
                is_custom=True
            )
        else:
            # 从 foods 表获取
            food = Food.query.get(food_data.get('food_id'))
            if not food:
                return None, "食材不存在"
            meal = UserMeal(
                user_id=user_id,
                meal_date=meal_date,
                meal_type=meal_type,
                food_name=food.name,
                category=food.category,
                calories=food.calories,
                season=food.season,
                tags=food.tags,
                features=food.features or [],
                protein=food.protein or 5,
                fiber=food.fiber or 5,
                vitamins=food.vitamins or 5,
                sugar=food.sugar or 5,
                saturated_fat=food.saturated_fat or 5,
                sodium=food.sodium or 5
            )
        
        db.session.add(meal)
        db.session.commit()
        #触发画像更新
        ProfileService.update_profile(user_id)
        return meal, None
    
    @staticmethod
    def get_meals_by_date(user_id: int, target_date: str):
        """获取某天的所有餐食记录"""
        meals = UserMeal.query.filter_by(user_id=user_id, meal_date=target_date).all()
        return meals
    
    @staticmethod
    def get_monthly_stats(user_id: int, year: int, month: int):
        """获取月度统计"""
        start_date = f"{year}-{month:02d}-01"
        # 简单获取当月所有记录
        meals = UserMeal.query.filter(
            UserMeal.user_id == user_id,
            UserMeal.meal_date >= start_date,
            UserMeal.meal_date < f"{year}-{month+1:02d}-01" if month < 12 else f"{year+1}-01-01"
        ).all()
        return meals