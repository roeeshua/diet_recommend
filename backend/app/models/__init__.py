from .. import db

# 导入所有模型，方便统一导出
from .user import User
from .preference import Preference
from .food import Food
from .user_plan import UserPlan
from .user_meal import UserMeal
from .user_profile import UserProfile

__all__ = ['User', 'Preference', 'Food', 'UserPlan', 'UserMeal', 'UserProfile']