from flask import Blueprint, request, jsonify
from ..services.food_service import FoodService

food_bp = Blueprint('food', __name__)

@food_bp.route('/foods', methods=['GET'])
def get_foods():
    """获取所有食材"""
    foods = FoodService.get_all_foods()
    return jsonify({
        'code': 200,
        'data': [f.to_dict() for f in foods]
    }), 200

@food_bp.route('/foods/<int:food_id>', methods=['GET'])
def get_food(food_id):
    """获取单个食材"""
    food = FoodService.get_food_by_id(food_id)
    if not food:
        return jsonify({'code': 404, 'message': '食材不存在'}), 404
    return jsonify({'code': 200, 'data': food.to_dict()}), 200

@food_bp.route('/foods', methods=['POST'])
def create_food():
    """新增食材"""
    data = request.get_json()
    
    if not data.get('name'):
        return jsonify({'code': 400, 'message': '食材名称不能为空'}), 400
    
    food = FoodService.create_food(
        name=data['name'],
        category=data.get('category'),
        calories=data.get('calories'),
        season=data.get('season'),
        tags=data.get('tags')
    )
    
    return jsonify({
        'code': 200,
        'message': '添加成功',
        'data': food.to_dict()
    }), 200

@food_bp.route('/foods/<int:food_id>', methods=['PUT'])
def update_food(food_id):
    """更新食材"""
    data = request.get_json()
    food = FoodService.update_food(food_id, **data)
    
    if not food:
        return jsonify({'code': 404, 'message': '食材不存在'}), 404
    
    return jsonify({
        'code': 200,
        'message': '更新成功',
        'data': food.to_dict()
    }), 200

@food_bp.route('/foods/<int:food_id>', methods=['DELETE'])
def delete_food(food_id):
    """删除食材"""
    success = FoodService.delete_food(food_id)
    if not success:
        return jsonify({'code': 404, 'message': '食材不存在'}), 404
    return jsonify({'code': 200, 'message': '删除成功'}), 200