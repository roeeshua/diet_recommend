# backend/app/services/plan_service.py
import re
import json
from datetime import date
from ..models.user import User
from ..models.food import Food
from ..models.user_plan import UserPlan
from ..models.user_meal import UserMeal
from .. import db
from .llm_service import LLMService

class PlanService:
    """饮食计划服务"""
    
    @staticmethod
    def generate_plan_by_ai(user_id: int):
        """AI 生成饮食计划"""
        user = User.query.get(user_id)
        if not user:
            return None
        
        from ..models.preference import Preference
        preferences = Preference.query.filter_by(user_id=user_id).all()
        pref_text = ', '.join([p.value for p in preferences]) if preferences else '无特殊偏好'
        
        all_foods = Food.query.all()
        food_list = [f"{f.name}({f.category},{f.calories}卡)" for f in all_foods]
        food_knowledge = '、'.join(food_list)
        
        prompt = f"""你是一个饮食健康专家。请为用户生成一日三餐饮食计划。

用户信息：
- 年龄：{user.age if user.age else '未知'}岁
- 性别：{'男' if user.gender else '女' if user.gender is not None else '未知'}
- 身高：{user.height if user.height else '未知'}cm
- 体重：{user.weight if user.weight else '未知'}kg

饮食偏好：{pref_text}

可选食材（只能从以下选择）：
{food_knowledge}

请按以下JSON格式返回计划，只返回JSON：
{{"breakfast": ["食材名称1", "食材名称2"], "lunch": ["食材名称1", "食材名称2", "食材名称3"], "dinner": ["食材名称1", "食材名称2"], "total_calories": 数值}}"""

        response = LLMService.chat(prompt)
        
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                plan_data = json.loads(json_match.group())
            else:
                plan_data = json.loads(response)
        except json.JSONDecodeError:
            return None
        
        def match_food(name):
            food = Food.query.filter(Food.name.like(f'%{name}%')).first()
            return food.to_dict() if food else None
        
        breakfast = [match_food(name) for name in plan_data.get('breakfast', []) if match_food(name)]
        lunch = [match_food(name) for name in plan_data.get('lunch', []) if match_food(name)]
        dinner = [match_food(name) for name in plan_data.get('dinner', []) if match_food(name)]
        
        total = sum(f.get('calories', 0) for f in breakfast + lunch + dinner)
        
        return {
            'breakfast': breakfast,
            'lunch': lunch,
            'dinner': dinner,
            'total_calories': total
        }
    
    @staticmethod
    def save_plan(user_id: int, plan_name: str, foods: dict, total_calories: int):
        """保存用户计划"""
        count = UserPlan.query.filter_by(user_id=user_id).count()
        if count >= 10:
            return None, "计划数量已达上限（最多10个），请先删除一些"
        
        user_plan = UserPlan(
            user_id=user_id,
            plan_name=plan_name,
            foods=foods,
            total_calories=total_calories
        )
        db.session.add(user_plan)
        db.session.commit()
        return user_plan, None
    
    @staticmethod
    def get_user_plans(user_id: int):
        """获取用户所有计划"""
        plans = UserPlan.query.filter_by(user_id=user_id).order_by(UserPlan.created_at.desc()).all()
        result = []
        for plan in plans:
            plan_dict = plan.to_dict()
            # foods 已经是完整的三餐食物对象
            result.append(plan_dict)
        return result
    
    @staticmethod
    def delete_plan(plan_id: int, user_id: int):
        """删除计划"""
        plan = UserPlan.query.filter_by(id=plan_id, user_id=user_id).first()
        if not plan:
            return False
        db.session.delete(plan)
        db.session.commit()
        return True
    
    @staticmethod
    def checkin_plan(plan_id: int, user_id: int, target_date: date = None):
        """一键打卡：将计划中的所有食物添加到打卡记录"""
        if target_date is None:
            target_date = date.today()
        
        plan = UserPlan.query.filter_by(id=plan_id, user_id=user_id).first()
        if not plan:
            return False, "计划不存在"
        
        foods = plan.foods
        count = 0
        
        # 将三餐食物添加到打卡记录
        for meal_type in ['breakfast', 'lunch', 'dinner']:
            for food in foods.get(meal_type, []):
                existing = UserMeal.query.filter_by(
                    user_id=user_id,
                    meal_date=target_date,
                    meal_type=meal_type,
                    food_name=food.get('name')
                ).first()
                if not existing:
                    # 在创建 UserMeal 之前，处理 tags 字段
                    raw_tags = food.get('tags')
                    # 如果 raw_tags 是一个列表，就把它用逗号连接成字符串；否则保持原样
                    processed_tags = ','.join(raw_tags) if isinstance(raw_tags, list) else raw_tags
                    meal = UserMeal(
                        user_id=user_id,
                        meal_date=target_date,
                        meal_type=meal_type,
                        food_name=food.get('name'),
                        category=food.get('category'),
                        calories=food.get('calories'),
                        season=food.get('season'),
                        tags=processed_tags, # 现在 processed_tags 是一个字符串，比如 "膳食纤维,早餐"
                        protein=food.get('protein', 5),
                        fiber=food.get('fiber', 5),
                        vitamins=food.get('vitamins', 5),
                        sugar=food.get('sugar', 5),
                        saturated_fat=food.get('saturated_fat', 5),
                        sodium=food.get('sodium', 5)
                    )
                    db.session.add(meal)
                    count += 1
        
        db.session.commit()
        return True, f"已添加 {count} 种食物到 {target_date} 的打卡记录"