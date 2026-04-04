from ..models.user import User
from ..models.preference import Preference
from ..models.food import Food
from ..services.profile_service import ProfileService
from .llm_service import LLMService
import re

class RecommendService:
    
    @staticmethod
    def get_recommendations(user_id: int, limit: int = 5):
        """使用大模型生成个性化推荐（画像 + 偏好，偏好权重更高）"""
        
        user = User.query.get(user_id)
        if not user:
            return []
        
        # 1. 获取静态偏好（用户手动设置，权重更高）
        preferences = Preference.query.filter_by(user_id=user_id).all()
        static_prefs = [p.value for p in preferences]
        static_text = '、'.join(static_prefs) if static_prefs else '无'
        
        # 2. 获取动态画像（基于近30天打卡，作为参考）
        profile_desc = ProfileService.get_profile_description(user_id)
        
        # 3. 获取食材库
        all_foods = Food.query.all()
        food_list = [f"{f.name}({f.category},{f.calories}卡)" for f in all_foods]
        food_knowledge = '、'.join(food_list)
        
        # 4. 构造提示词（偏好优先，画像辅助）
        prompt = f"""你是一个饮食健康专家。请根据用户信息，推荐{limit}种最适合的食材。

【用户手动设置的偏好 - 请优先满足】
{static_text}

【用户近期饮食画像 - 仅供参考，优先级低于手动偏好】
{profile_desc}

可选食材库（从以下选择）：
{food_knowledge}

## 要求
1. 请尽量多样化，不要总是推荐相同的食材组合
2. 可以考虑不同的菜系和烹饪方式
3. 早餐可以尝试不同的主食选择
4. 午餐和晚餐的蛋白质来源可以轮换（鸡胸肉、鱼、豆腐、鸡蛋等）

请只返回{limit}个食材名称，用中文逗号分隔，不要有其他解释。
例如：鸡胸肉,西兰花,糙米饭,鸡蛋,三文鱼"""
        
        # ========== 打印 Prompt ==========
        # print("\n" + "=" * 60)
        # print("🍽️ 【饮食推荐】发送给 AI 的 Prompt:")
        # print("=" * 60)
        # print(prompt)
        # print("=" * 60 + "\n")
        # ========== 打印结束 ==========

        response = LLMService.chat(prompt)
        
        # 解析返回结果
        recommended_names = re.split(r'[，,、]', response)
        recommended_names = [name.strip() for name in recommended_names if name.strip()]
        
        # 匹配数据库
        result = []
        for name in recommended_names[:limit]:
            food = Food.query.filter(Food.name.like(f'%{name}%')).first()
            if food:
                result.append(food.to_dict())
        
        return result