# backend/constants/features.py

# 口味类（8种）
TASTE_FEATURES = [
    '辣味', '麻辣', '酸味', '甜味',
    '咸鲜', '清淡', '浓郁', '清爽'
]

# 营养类（8种）
NUTRITION_FEATURES = [
    '高蛋白', '低脂', '低碳水', '高纤维',
    '高钙', '低卡', '高维生素', '均衡营养'
]

# 食材类（4种）
INGREDIENT_FEATURES = [
    '海鲜', '红肉', '白肉', '素食'
]

# 健康类（4种）
HEALTH_FEATURES = [
    '抗氧化', '助消化', '补气血', '增强免疫'
]

# 全部特征（24种）
ALL_FEATURES = TASTE_FEATURES + NUTRITION_FEATURES + INGREDIENT_FEATURES + HEALTH_FEATURES

# 特征中文名到数据库字段名的映射（用于画像）
FEATURE_TO_DB = {f: f.replace(' ', '_') for f in ALL_FEATURES}