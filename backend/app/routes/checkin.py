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
    
    user_id = meal.user_id  # 直接从记录中获取
    # 可选：验证这条记录属于该用户
    if meal.user_id != user_id:
        return jsonify({'code': 403, 'message': '无权删除此记录'}), 403
    
    db.session.delete(meal)
    db.session.commit()
    
    # 触发画像更新
    from ..services.profile_service import ProfileService
    ProfileService.update_profile(user_id)
    
    return jsonify({'code': 200, 'message': '删除成功'}), 200

@checkin_bp.route('/checkin/<int:user_id>/<string:date>', methods=['DELETE'])
def delete_day_meals(user_id, date):
    """删除指定用户指定日期的所有餐食记录"""
    
    # 查询该用户该日期的所有记录
    meals = UserMeal.query.filter_by(user_id=user_id, meal_date=date).all()
    
    if not meals:
        return jsonify({'code': 404, 'message': '该日期无打卡记录'}), 404
    
    # 删除所有记录
    for meal in meals:
        db.session.delete(meal)
    
    db.session.commit()
    
    # 触发画像更新
    from ..services.profile_service import ProfileService
    ProfileService.update_profile(user_id)
    
    return jsonify({
        'code': 200, 
        'message': f'已删除 {len(meals)} 条打卡记录',
        'data': {'deleted_count': len(meals)}
    }), 200