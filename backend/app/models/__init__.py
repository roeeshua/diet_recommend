from .. import db

# 导入所有模型，方便统一导出
from .user import User
from .preference import Preference
from .food import Food
from .plan import Plan
from .checkin import Checkin
from .user_meal import UserMeal

__all__ = ['User', 'Preference', 'Food', 'Plan', 'Checkin', 'UserMeal']