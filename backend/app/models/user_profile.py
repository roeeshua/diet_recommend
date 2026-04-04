from .. import db
from datetime import datetime

class UserProfile(db.Model):
    __tablename__ = 'user_profile'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    
    # 口味特征（8个）
    taste_spicy = db.Column(db.Float, default=0.0)
    taste_numbing = db.Column(db.Float, default=0.0)
    taste_sour = db.Column(db.Float, default=0.0)
    taste_sweet = db.Column(db.Float, default=0.0)
    taste_savory = db.Column(db.Float, default=0.0)
    taste_light = db.Column(db.Float, default=0.0)
    taste_rich = db.Column(db.Float, default=0.0)
    taste_refreshing = db.Column(db.Float, default=0.0)
    
    # 营养诉求（8个）
    nutrition_high_protein = db.Column(db.Float, default=0.0)
    nutrition_low_fat = db.Column(db.Float, default=0.0)
    nutrition_low_carb = db.Column(db.Float, default=0.0)
    nutrition_high_fiber = db.Column(db.Float, default=0.0)
    nutrition_high_calcium = db.Column(db.Float, default=0.0)
    nutrition_low_calorie = db.Column(db.Float, default=0.0)
    nutrition_high_vitamin = db.Column(db.Float, default=0.0)
    nutrition_balanced = db.Column(db.Float, default=0.0)
    
    # 食材偏好（4个）
    preference_seafood = db.Column(db.Float, default=0.0)
    preference_red_meat = db.Column(db.Float, default=0.0)
    preference_white_meat = db.Column(db.Float, default=0.0)
    preference_vegan = db.Column(db.Float, default=0.0)
    
    # 健康功效（4个）
    effect_antioxidant = db.Column(db.Float, default=0.0)
    effect_digestion = db.Column(db.Float, default=0.0)
    effect_blood_tonic = db.Column(db.Float, default=0.0)
    effect_immunity = db.Column(db.Float, default=0.0)
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 24个指标的名称映射（用于遍历）
    FEATURE_NAMES = {
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
    
    def to_dict(self):
        result = {'user_id': self.user_id, 'updated_at': self.updated_at.isoformat() if self.updated_at else None}
        for cn_name, db_field in self.FEATURE_NAMES.items():
            result[cn_name] = round(getattr(self, db_field, 0), 2)
        return result
    
    def get_top_features(self, top_n=5, threshold=0.3):
        """获取偏好度最高的几个特征（用于描述）"""
        features = []
        for cn_name, db_field in self.FEATURE_NAMES.items():
            value = getattr(self, db_field, 0)
            if value >= threshold:
                features.append((value, cn_name))
        features.sort(reverse=True)
        return [name for _, name in features[:top_n]]