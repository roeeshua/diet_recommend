# backend/app/services/recommend_service.py
import re
from ..models.user import User
from ..models.preference import Preference
from ..models.food import Food
from .llm_service import LLMService

class RecommendService:
    """推荐服务（使用大模型）"""
    
    @staticmethod
    def get_recommendations(user_id: int, limit: int = 5):
        """使用大模型生成个性化推荐"""
        
        # 1. 获取用户信息和偏好
        user = User.query.get(user_id)
        if not user:
            return []
        
        preferences = Preference.query.filter_by(user_id=user_id).all()
        pref_values = [p.value for p in preferences]
        pref_text = ', '.join(pref_values) if pref_values else '无特殊偏好'
        
        # 2. 获取所有食材名称（作为知识库）
        all_foods = Food.query.all()
        food_names = [f.name for f in all_foods]
        
        # 3. 构造提示词
        prompt = f"""你是一个饮食健康专家。请根据用户偏好，推荐{limit}种最适合的食材。

用户偏好：{pref_text}

可选食材（只能从以下选择）：
{', '.join(food_names)}

请只返回{limit}个食材名称，用中文逗号分隔，不要有其他解释。
例如：鸡胸肉,西兰花,糙米饭,鸡蛋,三文鱼"""

        # 4. 调用大模型
        response = LLMService.chat(prompt)
        
        # 5. 解析返回结果
        recommended_names = re.split(r'[，,、]', response)
        recommended_names = [name.strip() for name in recommended_names if name.strip()]
        
        # 6. 匹配数据库中的食材
        result = []
        for name in recommended_names[:limit]:
            # 精确匹配
            food = Food.query.filter(Food.name == name).first()
            if not food:
                # 模糊匹配
                food = Food.query.filter(Food.name.like(f'%{name}%')).first()
            if food:
                result.append(food.to_dict())
        
        # 如果大模型返回的结果不够，用规则补全
        if len(result) < limit:
            for food in all_foods:
                if food.to_dict() not in result:
                    result.append(food.to_dict())
                    if len(result) >= limit:
                        break
        
        return result