from flask import Blueprint, request, jsonify
from ..services.user_service import UserService

# 创建蓝图，后面要在 app/__init__.py 里注册
user_bp = Blueprint('user', __name__)

@user_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """获取用户信息"""
    user, error = UserService.get_user_info(user_id)
    if error:
        return jsonify({'code': 404, 'message': error}), 404
    return jsonify({'code': 200, 'data': user.to_dict()}), 200


@user_bp.route('/user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """修改用户信息"""
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '请求数据不能为空'}), 400

    user, error = UserService.update_user_info(user_id, data)
    if error:
        return jsonify({'code': 404, 'message': error}), 404

    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': user.to_dict()
    }), 200