from .. import db

# 导入所有模型，方便统一导出
from .user import User
from .preference import Preference
from .food import Food
from .user_plan import UserPlan
from .checkin import Checkin
from .user_meal import UserMeal

__all__ = ['User', 'Preference', 'Food', 'UserPlan', 'Checkin', 'UserMeal']