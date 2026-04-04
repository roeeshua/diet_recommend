from flask import Blueprint, jsonify
from ..services.profile_service import ProfileService

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile/<int:user_id>', methods=['GET'])
def get_profile(user_id):
    """获取用户画像"""
    profile = ProfileService.get_profile(user_id)
    return jsonify({'code': 200, 'data': profile.to_dict()}), 200

@profile_bp.route('/profile/<int:user_id>/description', methods=['GET'])
def get_profile_description(user_id):
    """获取用户画像文字描述（用于大模型）"""
    description = ProfileService.get_profile_description(user_id)
    return jsonify({'code': 200, 'data': {'description': description}}), 200