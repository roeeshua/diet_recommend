from datetime import date, timedelta
from ..models.user_meal import UserMeal
from ..models.user_profile import UserProfile
from .. import db
import json

class ProfileService:
    """用户画像服务 - 基于24个饮食特征"""
    
    # 特征关键词映射（打卡食物的 features 字段到画像字段）
    FEATURE_KEYWORDS = {
        # 口味
        '辣味': 'taste_spicy',
        '麻辣': 'taste_numbing',
        '酸味': 'taste_sour',
        '甜味': 'taste_sweet',
        '咸鲜': 'taste_savory',
        '清淡': 'taste_light',
        '浓郁': 'taste_rich',
        '清爽': 'taste_refreshing',
        # 营养
        '高蛋白': 'nutrition_high_protein',
        '低脂': 'nutrition_low_fat',
        '低碳水': 'nutrition_low_carb',
        '高纤维': 'nutrition_high_fiber',
        '高钙': 'nutrition_high_calcium',
        '低卡': 'nutrition_low_calorie',
        '高维生素': 'nutrition_high_vitamin',
        '均衡营养': 'nutrition_balanced',
        # 食材
        '海鲜': 'preference_seafood',
        '红肉': 'preference_red_meat',
        '白肉': 'preference_white_meat',
        '素食': 'preference_vegan',
        # 功效
        '抗氧化': 'effect_antioxidant',
        '助消化': 'effect_digestion',
        '补气血': 'effect_blood_tonic',
        '增强免疫': 'effect_immunity'
    }
    
    @staticmethod
    def update_profile(user_id: int):
        """根据用户近30天打卡记录重新计算画像（完全基于数据，不依赖历史）"""
        
        thirty_days_ago = date.today() - timedelta(days=30)
        meals = UserMeal.query.filter(
            UserMeal.user_id == user_id,
            UserMeal.meal_date >= thirty_days_ago
        ).all()
        
        # 获取或创建画像
        profile = UserProfile.query.get(user_id)
        if not profile:
            profile = UserProfile(user_id=user_id)
            db.session.add(profile)
        
        # 如果没有打卡记录，所有指标归零
        if not meals:
            for field in ProfileService.FEATURE_KEYWORDS.values():
                setattr(profile, field, 0.0)
            db.session.commit()
            print(f"✅ 用户 {user_id} 画像已重置（近30天无打卡记录）")
            return profile
        
        total = len(meals)
        
        # 初始化计数器
        counters = {field: 0 for field in ProfileService.FEATURE_KEYWORDS.values()}
        
        for meal in meals:
            features = []
            if meal.features:
                try:
                    features = json.loads(meal.features) if isinstance(meal.features, str) else meal.features
                except:
                    features = []
            
            for feature in features:
                if feature in ProfileService.FEATURE_KEYWORDS:
                    field = ProfileService.FEATURE_KEYWORDS[feature]
                    counters[field] += 1
        
        # 直接根据比例计算新值
        for field, count in counters.items():
            new_value = count / total if total > 0 else 0
            setattr(profile, field, new_value)
        
        db.session.commit()
        print(f"✅ 用户 {user_id} 画像已重新计算（基于近30天共 {total} 条打卡记录）")
        
        return profile
    
    @staticmethod
    def get_profile(user_id: int):
        """获取用户画像"""
        profile = UserProfile.query.get(user_id)
        if not profile:
            profile = UserProfile(user_id=user_id)
            db.session.add(profile)
            db.session.commit()
        return profile
    
    @staticmethod
    def get_profile_description(user_id: int) -> str:
        """获取画像的文字描述（用于大模型 prompt）"""
        profile = ProfileService.get_profile(user_id)
        top_features = profile.get_top_features(top_n=5, threshold=0.15)
        
        if not top_features:
            return "暂无明显饮食偏好"
        
        # 分类整理描述
        descriptions = []
        for feature in top_features:
            descriptions.append(feature)
        
        return f"用户偏好：{', '.join(descriptions)}"
    
    @staticmethod
    def get_full_profile_dict(user_id: int):
        """获取完整画像字典（24个指标）"""
        profile = ProfileService.get_profile(user_id)
        return profile.to_dict()