from ..models.preference import Preference
from ..models.user import User
from .. import db

class PreferenceService:
    
    @staticmethod
    def get_user_preferences(user_id: int):
        """获取用户的所有偏好"""
        user = User.query.get(user_id)
        if not user:
            return None, "用户不存在"
        
        preferences = Preference.query.filter_by(user_id=user_id).all()
        return preferences, None
    
    @staticmethod
    def set_preference(user_id: int, category: str, value: str):
        """设置单个偏好（如果已存在则更新）"""
        user = User.query.get(user_id)
        if not user:
            return None, "用户不存在"
        
        # 查找是否已有相同 category 的偏好
        pref = Preference.query.filter_by(user_id=user_id, category=category).first()
        if pref:
            pref.value = value
        else:
            pref = Preference(user_id=user_id, category=category, value=value)
            db.session.add(pref)
        
        db.session.commit()
        return pref, None
    
    @staticmethod
    def delete_preference(user_id: int, preference_id: int):
        """删除某个偏好"""
        pref = Preference.query.get(preference_id)
        if not pref or pref.user_id != user_id:
            return False, "偏好不存在或无权操作"
        
        db.session.delete(pref)
        db.session.commit()
        return True, None
    
    @staticmethod
    def update_preferences(user_id: int, tags: list):
        """批量更新用户偏好（先删后增）"""
        user = User.query.get(user_id)
        if not user:
            return None, "用户不存在"
        
        # 删除该用户所有偏好
        Preference.query.filter_by(user_id=user_id).delete()
        
        # 批量添加新偏好
        for tag in tags:
            pref = Preference(user_id=user_id, category='taste', value=tag)
            db.session.add(pref)
        
        db.session.commit()
        return True, None