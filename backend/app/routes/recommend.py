# backend/app/routes/recommend.py
from flask import Blueprint, jsonify
from ..services.recommend_service import RecommendService

recommend_bp = Blueprint('recommend', __name__)

@recommend_bp.route('/recommend/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    """获取推荐食材"""
    foods = RecommendService.get_recommendations(user_id, limit=5)
    return jsonify({'code': 200, 'data': foods}), 200