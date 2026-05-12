import re
import json
from datetime import date
from ..models.user import User
from ..models.food import Food
from ..models.user_plan import UserPlan
from ..models.user_meal import UserMeal
from .. import db
from .llm_service import LLMService
from .profile_service import ProfileService
from .retrieval_service import RetrievalService


class PlanService:
    """饮食计划服务"""

    # 每个餐类最少需要的食材数
    MIN_MEAL_ITEMS = {
        'breakfast': 1,
        'lunch': 2,
        'dinner': 2,
    }

    @staticmethod
    def generate_plan_by_ai(user_id: int):
        """RAG + AI 生成饮食计划"""
        user = User.query.get(user_id)
        if not user:
            return None

        from ..models.preference import Preference
        preferences = Preference.query.filter_by(user_id=user_id).all()
        pref_text = ', '.join([p.value for p in preferences]) if preferences else '无特殊偏好'
        profile_desc = ProfileService.get_profile_description(user_id)
        gender_text = '男' if user.gender else '女' if user.gender is not None else '未知'

        # RAG 检索
        query = (
            f"用户是个{user.age or '未知'}岁的{gender_text}，"
            f"身高{user.height or '未知'}cm，体重{user.weight or '未知'}kg。"
            f"饮食偏好：{pref_text}。"
            f"饮食特征：{profile_desc}"
        )
        retrieved_foods = RetrievalService.search_by_category(query)
        # 包含营养评分的食材信息，让 AI 能够计算营养均衡
        food_list = [
            f"{f['name']}({f['category']},{f['calories']}卡,"
            f"蛋白质{f['protein']}分/纤维{f['fiber']}分/维生素{f['vitamins']}分"
            f"/糖{f['sugar']}分/脂肪{f['saturated_fat']}分/钠{f['sodium']}分)"
            for f in retrieved_foods
        ]
        food_knowledge = '、'.join(food_list)

        target_calories = int(user.weight * 30) if user.weight else None
        _cal_example = target_calories or 1800
        cal_note = (
            f"\n【⚠️ 最重要：控制总热量】"
            f"\n一日三餐的总热量必须控制在 ** {target_calories - 300}~{target_calories + 300} 大卡**"
            f"\n这是根据用户体重 {int(user.weight)}kg × 30 计算得出的目标值，请优先满足此项。"
        ) if target_calories else ""

        prompt = f"""你是一个饮食健康专家。请为用户生成一日三餐饮食计划。

用户信息：
- 年龄：{user.age or '未知'}岁
- 性别：{gender_text}
- 身高：{user.height or '未知'}cm
- 体重：{user.weight or '未知'}kg{cal_note}

【用户手动设置的偏好 - 请优先满足】
{pref_text}

【用户近期饮食画像 - 仅供参考】
{profile_desc}

【检索到的相关食材库 - 请优先从以下精选食材中选择】
{food_knowledge}

## 营养均衡要求
每种食材都有六项营养评分（十分制），一日三餐的每项累计总分应在合理范围：
- 蛋白质、膳食纤维、微量元素：**30-70 分**
- 添加糖、饱和脂肪、钠：**10-50 分**（越低越好）

## 其他要求
1. 早餐至少包含1种食材，午餐至少包含2种，晚餐至少包含2种
2. 严格从上面「检索到的相关食材库」中选择
3. 允许同一种食材在多餐中出现（例如早餐和午餐都可以有鸡蛋）。**善用此规则来调整总热量**——热量不够时就多加食材或重复使用高热量食材，热量超了就减少食材或用低热量食材替换。

请严格按照以下JSON格式返回，只返回JSON，不要包含其他内容：
{{"breakfast": ["食材名称1", "食材名称2"], "lunch": ["食材名称1", "食材名称2", "食材名称3"], "dinner": ["食材名称1", "食材名称2"], "total_calories": {_cal_example}}}"""

# 热量校准：不在合理范围内就重试（最多3次）

        cal_low = target_calories - 300
        cal_high = target_calories + 300
        best_plan = None
        best_diff = float('inf')
        cal_range = {'low': cal_low, 'high': cal_high, 'target': target_calories}



        for attempt in range(3):

            response = LLMService.chat(prompt)

            plan_data = PlanService._parse_plan_json(response)



            if not plan_data:

                continue



            breakfast = PlanService._match_foods(plan_data.get('breakfast', []))

            lunch = PlanService._match_foods(plan_data.get('lunch', []))

            dinner = PlanService._match_foods(plan_data.get('dinner', []))



            breakfast = PlanService._fill_meal(breakfast, retrieved_foods, '早餐', PlanService.MIN_MEAL_ITEMS['breakfast'])

            lunch = PlanService._fill_meal(lunch, retrieved_foods, '午餐', PlanService.MIN_MEAL_ITEMS['lunch'])

            dinner = PlanService._fill_meal(dinner, retrieved_foods, '晚餐', PlanService.MIN_MEAL_ITEMS['dinner'])



            total = sum(f.get('calories', 0) for f in breakfast + lunch + dinner)

            diff = abs(total - target_calories)



            if diff < best_diff:

                best_plan = {'breakfast': breakfast, 'lunch': lunch, 'dinner': dinner, 'total_calories': total}

                best_diff = diff



            if cal_low <= total <= cal_high:
                return best_plan
        if best_plan is not None:
            best_plan['_cal_range'] = cal_range
        return best_plan or {'breakfast': [], 'lunch': [], 'dinner': [], 'total_calories': 0}

    @staticmethod
    def _parse_plan_json(text: str) -> dict:
        """鲁棒地解析 LLM 返回的计划 JSON"""
        if not text:
            return None

        # 1. 提取 ```json ... ``` 代码块
        code_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
        if code_match:
            text = code_match.group(1)

        # 2. 提取 {...} JSON 对象
        json_match = re.search(r'\{[\s\S]*\}', text)
        if not json_match:
            return None

        try:
            data = json.loads(json_match.group())
            # 验证必要的键
            if not isinstance(data, dict):
                return None
            return data
        except json.JSONDecodeError:
            pass

        # 3. 尝试修复常见 JSON 错误（尾部逗号、单引号等）
        raw = json_match.group()
        # 单引号转双引号
        raw = re.sub(r"(?<!\\)'", '"', raw)
        # 移除尾部逗号
        raw = re.sub(r',\s*}', '}', raw)
        raw = re.sub(r',\s*]', ']', raw)
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass

        return None

    @staticmethod
    def _match_foods(names: list) -> list:
        """将名称列表匹配为数据库中的食材"""
        result = []
        for name in names:
            if isinstance(name, str) and name.strip():
                food = Food.query.filter(Food.name.like(f'%{name.strip()}%')).first()
                if food:
                    result.append(food.to_dict())
        return result

    @staticmethod
    def _fill_meal(current: list, candidates: list, meal_name: str, min_items: int) -> list:
        """如果餐类食材不足，从候选中补全"""
        if len(current) >= min_items:
            return current

        existing_names = {f['name'] for f in current}
        # 根据餐类选择合适的食材类型
        category_priority = {
            '早餐': ['主食', '蛋白质', '水果'],
            '午餐': ['蛋白质', '蔬菜', '主食'],
            '晚餐': ['蛋白质', '蔬菜', '主食'],
        }
        preferred = category_priority.get(meal_name, ['蛋白质', '蔬菜', '主食'])

        # 按偏好类别排序候选
        sorted_candidates = sorted(
            candidates,
            key=lambda f: (
                preferred.index(f['category']) if f['category'] in preferred else 99,
                -f.get('protein', 0) if meal_name != '早餐' else -f.get('calories', 0)
            )
        )

        for food in sorted_candidates:
            if len(current) >= min_items:
                break
            if food['name'] not in existing_names:
                current.append(food)
                existing_names.add(food['name'])

        return current

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
        return [plan.to_dict() for plan in plans]

    @staticmethod
    def update_plan(plan_id: int, user_id: int, plan_name: str = None, foods: dict = None, total_calories: int = None):
        """修改计划"""
        plan = UserPlan.query.filter_by(id=plan_id, user_id=user_id).first()
        if not plan:
            return None, "计划不存在"
        if plan_name is not None:
            plan.plan_name = plan_name
        if foods is not None:
            plan.foods = foods
        if total_calories is not None:
            plan.total_calories = total_calories
        db.session.commit()
        return plan, None

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
        """一键打卡"""
        if target_date is None:
            target_date = date.today()

        plan = UserPlan.query.filter_by(id=plan_id, user_id=user_id).first()
        if not plan:
            return False, "计划不存在"

        foods = plan.foods
        count = 0

        for meal_type in ['breakfast', 'lunch', 'dinner']:
            for food in foods.get(meal_type, []):
                existing = UserMeal.query.filter_by(
                    user_id=user_id,
                    meal_date=target_date,
                    meal_type=meal_type,
                    food_name=food.get('name')
                ).first()
                if not existing:
                    raw_tags = food.get('tags')
                    processed_tags = ','.join(raw_tags) if isinstance(raw_tags, list) else raw_tags
                    raw_features = food.get('features', [])
                    processed_features = raw_features if isinstance(raw_features, list) else []

                    meal = UserMeal(
                        user_id=user_id,
                        meal_date=target_date,
                        meal_type=meal_type,
                        food_name=food.get('name'),
                        category=food.get('category'),
                        calories=food.get('calories'),
                        season=food.get('season'),
                        tags=processed_tags,
                        features=processed_features,
                        protein=food.get('protein', 5),
                        fiber=food.get('fiber', 5),
                        vitamins=food.get('vitamins', 5),
                        sugar=food.get('sugar', 5),
                        saturated_fat=food.get('saturated_fat', 5),
                        sodium=food.get('sodium', 5),
                    )
                    db.session.add(meal)
                    count += 1

        db.session.commit()
        ProfileService.update_profile(user_id)
        return True, f"已添加 {count} 种食物到 {target_date} 的打卡记录"
