from flask import Blueprint, request, jsonify
from ..services.user_service import UserService

# 创建蓝图，后面要在 app/__init__.py 里注册
user_bp = Blueprint('user', __name__)

@user_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """获取用户信息"""
    # 1. 调用 Service 层获取用户对象
    user, error = UserService.get_user_info(user_id)
    
    # 2. 如果有错误（用户不存在），返回 404
    if error:
        return jsonify({'code': 404, 'message': error}), 404
    
    # 3. 成功则返回用户信息
    return jsonify({
        'code': 200,
        'data': user.to_dict()
    }), 200


@user_bp.route('/user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """修改用户信息"""
    # 1. 从请求体获取要修改的数据
    data = request.get_json()
    
    # 2. 简单的参数校验：请求体不能为空
    if not data:
        return jsonify({'code': 400, 'message': '请求数据不能为空'}), 400
    
    # 3. 调用 Service 层更新用户
    user, error = UserService.update_user_info(user_id, data)
    
    # 4. 如果有错误（用户不存在），返回 404
    if error:
        return jsonify({'code': 404, 'message': error}), 404
    
    # 5. 成功则返回更新后的用户信息
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': user.to_dict()
    }), 200