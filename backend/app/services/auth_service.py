from ..models.user import User
from .. import db
from ..utils.password import hash_password, check_password
from ..utils.jwt import generate_token

class AuthService:
    @staticmethod
    def register(username, password, age=None, gender=None, height=None, weight=None):
        """注册"""
        # 检查用户名是否存在
        if User.query.filter_by(username=username).first():
            return None, "用户名已存在"
        
        # 创建新用户
        user = User(
            username=username,
            password=hash_password(password),
            age=age,
            gender=gender,
            height=height,
            weight=weight
        )
        db.session.add(user)
        db.session.commit()
        return user, None
    
    @staticmethod
    def login(username, password):
        """登录"""
        user = User.query.filter_by(username=username).first()
        if not user:
            return None, None, "用户名不存在"
        
        if not check_password(password, user.password):
            return None, None, "密码错误"
        
        token = generate_token(user.id)
        return user, token, None