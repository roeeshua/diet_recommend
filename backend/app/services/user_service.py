from ..models.user import User
from .. import db

class UserService:
    
    @staticmethod
    def get_user_info(user_id: int):
        """获取用户信息"""
        user = User.query.get(user_id)
        if not user:
            return None, "用户不存在"
        
        # 返回用户对象，不是分散的字段
        return user, None
    
    @staticmethod
    def update_user_info(user_id: int, data: dict):
        """更新用户信息"""
        user, error = UserService.get_user_info(user_id)
        if error:
            return None, error
        
        # 只更新传入的字段
        if 'age' in data:
            user.age = data['age']
        if 'gender' in data:
            user.gender = data['gender']
        if 'height' in data:
            user.height = data['height']
        if 'weight' in data:
            user.weight = data['weight']
        
        db.session.commit()
        return user, None