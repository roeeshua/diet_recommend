from flask import Blueprint, request, jsonify
from ..services.preference_service import PreferenceService

preference_bp = Blueprint('preference', __name__)

@preference_bp.route('/user/<int:user_id>/preferences', methods=['GET'])
def get_preferences(user_id):
    """获取用户所有偏好"""
    preferences, error = PreferenceService.get_user_preferences(user_id)
    if error:
        return jsonify({'code': 404, 'message': error}), 404
    
    return jsonify({
        'code': 200,
        'data': [p.to_dict() for p in preferences]
    }), 200

@preference_bp.route('/user/<int:user_id>/preferences', methods=['POST'])
def set_preference(user_id):
    """设置单个偏好"""
    data = request.get_json()
    category = data.get('category')
    value = data.get('value')
    
    if not category or not value:
        return jsonify({'code': 400, 'message': 'category 和 value 不能为空'}), 400
    
    pref, error = PreferenceService.set_preference(user_id, category, value)
    if error:
        return jsonify({'code': 404, 'message': error}), 404
    
    return jsonify({
        'code': 200,
        'message': '设置成功',
        'data': pref.to_dict()
    }), 200

@preference_bp.route('/user/<int:user_id>/preferences/<int:pref_id>', methods=['DELETE'])
def delete_preference(user_id, pref_id):
    """删除某个偏好"""
    success, error = PreferenceService.delete_preference(user_id, pref_id)
    if not success:
        return jsonify({'code': 404, 'message': error}), 404
    
    return jsonify({'code': 200, 'message': '删除成功'}), 200

@preference_bp.route('/user/<int:user_id>/preferences/batch', methods=['PUT'])
def batch_update_preferences(user_id):
    """批量更新用户偏好"""
    data = request.get_json()
    tags = data.get('tags', [])
    
    if not isinstance(tags, list):
        return jsonify({'code': 400, 'message': 'tags 必须是数组'}), 400
    
    success, error = PreferenceService.update_preferences(user_id, tags)
    if error:
        return jsonify({'code': 404, 'message': error}), 404
    
    return jsonify({'code': 200, 'message': '更新成功'}), 200