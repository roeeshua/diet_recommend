from flask import Blueprint, request, jsonify
from ..services.checkin_service import CheckinService
from ..services.statistics_service import StatisticsService
from ..models.user_meal import UserMeal
from .. import db

checkin_bp = Blueprint('checkin', __name__)

@checkin_bp.route('/checkin', methods=['POST'])
def add_meal():
    """添加一餐记录"""
    data = request.get_json()
    user_id = data.get('user_id')
    meal_date = data.get('meal_date')
    meal_type = data.get('meal_type')
    food_data = data.get('food_data')
    
    if not all([user_id, meal_date, meal_type, food_data]):
        return jsonify({'code': 400, 'message': '参数不完整'}), 400
    
    meal, error = CheckinService.add_meal(user_id, meal_date, meal_type, food_data)
    if error:
        return jsonify({'code': 400, 'message': error}), 400
    
    return jsonify({'code': 200, 'message': '添加成功', 'data': meal.to_dict()}), 200

@checkin_bp.route('/checkin/<int:user_id>/<string:date>', methods=['GET'])
def get_meals(user_id, date):
    """获取某天的餐食记录"""
    meals = CheckinService.get_meals_by_date(user_id, date)
    return jsonify({'code': 200, 'data': [m.to_dict() for m in meals]}), 200

@checkin_bp.route('/statistics/<int:user_id>/<string:date>', methods=['GET'])
def get_daily_stats(user_id, date):
    """获取某天的营养统计"""
    stats = StatisticsService.get_daily_stats(user_id, date)
    advice = StatisticsService.get_advice(stats)
    return jsonify({'code': 200, 'data': stats, 'advice': advice}), 200

@checkin_bp.route('/statistics/<int:user_id>/monthly', methods=['GET'])
def get_monthly_trend(user_id):
    """获取月度趋势"""
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    from datetime import datetime
    now = datetime.now()
    year = year or now.year
    month = month or now.month
    
    trend = StatisticsService.get_monthly_trend(user_id, year, month)
    return jsonify({'code': 200, 'data': trend}), 200

@checkin_bp.route('/checkin/<int:meal_id>', methods=['DELETE'])
def delete_meal(meal_id):
    """删除餐食记录"""
    meal = UserMeal.query.get(meal_id)
    if not meal:
        return jsonify({'code': 404, 'message': '记录不存在'}), 404
    
    db.session.delete(meal)
    db.session.commit()
    return jsonify({'code': 200, 'message': '删除成功'}), 200