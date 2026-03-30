from flask import Blueprint, request, jsonify
from ..services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """注册接口"""
    data = request.get_json()
    
    # 参数校验
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'code': 400, 'message': '用户名和密码不能为空'}), 400
    
    user, error = AuthService.register(
        username=data.get('username'),
        password=data.get('password'),
        age=data.get('age'),
        gender=data.get('gender'),
        height=data.get('height'),
        weight=data.get('weight')
    )
    
    if error:
        return jsonify({'code': 400, 'message': error}), 400
    
    return jsonify({
        'code': 200,
        'message': '注册成功',
        'data': user.to_dict()
    }), 200

@auth_bp.route('/login', methods=['POST'])
def login():
    """登录接口"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'code': 400, 'message': '用户名和密码不能为空'}), 400
    
    user, token, error = AuthService.login(
        username=data.get('username'),
        password=data.get('password')
    )
    
    if error:
        return jsonify({'code': 401, 'message': error}), 401
    
    return jsonify({
        'code': 200,
        'message': '登录成功',
        'data': {
            'user': user.to_dict(),
            'token': token
        }
    }), 200