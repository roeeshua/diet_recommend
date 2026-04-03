from flask import Blueprint, request, jsonify
from datetime import datetime, date
from ..services.plan_service import PlanService

plan_bp = Blueprint('plan', __name__)

@plan_bp.route('/plan/generate', methods=['POST'])
def generate_plan():
    """AI 生成饮食计划"""
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'code': 400, 'message': 'user_id 不能为空'}), 400
    
    plan = PlanService.generate_plan_by_ai(user_id)
    if not plan:
        return jsonify({'code': 500, 'message': '生成计划失败'}), 500
    
    return jsonify({'code': 200, 'data': plan}), 200

@plan_bp.route('/plan/save', methods=['POST'])
def save_plan():
    """保存计划"""
    data = request.get_json()
    user_id = data.get('user_id')
    plan_name = data.get('plan_name')
    foods = data.get('foods')
    total_calories = data.get('total_calories', 0)
    
    if not all([user_id, plan_name, foods]):
        return jsonify({'code': 400, 'message': '参数不完整'}), 400
    
    plan, error = PlanService.save_plan(user_id, plan_name, foods, total_calories)
    if error:
        return jsonify({'code': 400, 'message': error}), 400
    
    return jsonify({'code': 200, 'message': '保存成功', 'data': plan.to_dict()}), 200

@plan_bp.route('/plan/list/<int:user_id>', methods=['GET'])
def get_plans(user_id):
    """获取用户所有计划"""
    plans = PlanService.get_user_plans(user_id)
    return jsonify({'code': 200, 'data': plans}), 200

@plan_bp.route('/plan/<int:plan_id>', methods=['DELETE'])
def delete_plan(plan_id):
    """删除计划"""
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'code': 400, 'message': 'user_id 不能为空'}), 400
    
    success = PlanService.delete_plan(plan_id, user_id)
    if not success:
        return jsonify({'code': 404, 'message': '计划不存在'}), 404
    
    return jsonify({'code': 200, 'message': '删除成功'}), 200

@plan_bp.route('/plan/checkin/<int:plan_id>', methods=['POST'])
def checkin_plan(plan_id):
    """一键打卡"""
    data = request.get_json()
    user_id = data.get('user_id')
    target_date = data.get('date')
    
    if not user_id:
        return jsonify({'code': 400, 'message': 'user_id 不能为空'}), 400
    
    target_date_obj = datetime.strptime(target_date, '%Y-%m-%d').date() if target_date else date.today()
    
    success, message = PlanService.checkin_plan(plan_id, user_id, target_date_obj)
    if not success:
        return jsonify({'code': 404, 'message': message}), 404
    
    return jsonify({'code': 200, 'message': message}), 200