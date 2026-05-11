import re
import json
from ..models.user import User
from ..models.preference import Preference
from ..models.food import Food
from ..services.profile_service import ProfileService
from ..services.retrieval_service import RetrievalService
from .llm_service import LLMService


class RecommendService:

    @staticmethod
    def get_recommendations(user_id: int, limit: int = 5):
        """使用 RAG + 大模型生成个性化推荐"""
        user = User.query.get(user_id)
        if not user:
            return []

        # 1. 获取静态偏好
        preferences = Preference.query.filter_by(user_id=user_id).all()
        static_prefs = [p.value for p in preferences]
        static_text = '、'.join(static_prefs) if static_prefs else '无'

        # 2. 获取动态画像
        profile_desc = ProfileService.get_profile_description(user_id)

        # 3. RAG 检索阶段
        query = f"用户饮食偏好：{static_text}。用户饮食特征：{profile_desc}"
        retrieved_foods = RetrievalService.search_by_category(query)
        food_list = [f"{f['name']}({f['category']},{f['calories']}卡)" for f in retrieved_foods]
        food_knowledge = '、'.join(food_list)

        # 4. RAG 生成阶段
        prompt = f"""你是一个饮食健康专家。请根据用户信息，推荐{limit}种最适合的食材。

【用户手动设置的偏好 - 请优先满足】
{static_text}

【用户近期饮食画像 - 仅供参考，优先级低于手动偏好】
{profile_desc}

【检索到的相关食材库 - 请优先从以下精选食材中选择】
{food_knowledge}

## 要求
1. 请尽量多样化
2. 严格从上面「检索到的相关食材库」中选择
3. **必须返回且只返回{limit}个食材名称**，每个名称占一行，用中文逗号分隔也行

请只返回{limit}个食材名称："""

        response = LLMService.chat(prompt)
        names = RecommendService._parse_names(response)

        # 匹配数据库
        result = []
        for name in names[:limit]:
            food = Food.query.filter(Food.name.like(f'%{name}%')).first()
            if food:
                result.append(food.to_dict())

        # 如果不足 limit 个，从检索结果中补全
        if len(result) < limit:
            existing_names = {r['name'] for r in result}
            for food_dict in retrieved_foods:
                if len(result) >= limit:
                    break
                if food_dict['name'] not in existing_names:
                    result.append(food_dict)
                    existing_names.add(food_dict['name'])

        return result[:limit]

    @staticmethod
    def _parse_names(text: str) -> list:
        """鲁棒地解析 LLM 返回的食材名称列表"""
        if not text:
            return []

        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return [str(n).strip() for n in parsed if str(n).strip()]
        except json.JSONDecodeError:
            pass

        # 2. 尝试按逗号/顿号/换行拆分
        for sep in [',', '，', '、', '\n', ';', '；']:
            if sep in text:
                parts = [p.strip() for p in text.split(sep) if p.strip()]
                # 过滤掉非食材词
                parts = [p for p in parts
                         if not p.startswith('[') and not p.startswith('"')
                         and not p.startswith('「') and not p.startswith('《')
                         and len(p) >= 2]
                if len(parts) >= 2:
                    return parts

        # 3. 尝试按数字编号拆分
        parts = re.split(r'[\d]+[.、．\s]+', text)
        parts = [p.strip() for p in parts if p.strip() and len(p.strip()) >= 2]
        if parts:
            return parts

        # 4. 最后兜底：整段作为一个名称尝试
        return [text.strip()]
