from flask import Blueprint, request, jsonify
import requests
import os
import json
import re
from ..models.user_meal import UserMeal
from ..models.user import User

ai_bp = Blueprint('ai', __name__)

# DeepSeek API 配置
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', 'sk-72352f4f200443a39d204feed685215e')
DEEPSEEK_API_URL = 'https://api.deepseek.com/v1/chat/completions'

# ==================== 1. AI 自动补全食物营养 ====================
@ai_bp.route('/ai/fill_food', methods=['POST'])
def fill_food():
    """AI 自动补全食物营养信息"""
    data = request.get_json()
    food_name = data.get('food_name', '')
    
    if not food_name:
        return jsonify({'code': 400, 'message': '食物名称不能为空'}), 400
    
    # 构造 prompt
    prompt = f"""请为食物"{food_name}"填写以下信息（十分制，1-10分）：
- 类别（主食/蛋白质/蔬菜/水果）
- 预估卡路里（整数）
- 季节（春季/夏季/秋季/冬季/四季）
- 标签（多个用逗号分隔）
- 饮食特征（从以下列表中选择1-3个最匹配的：辣味、麻辣、酸味、甜味、咸鲜、清淡、浓郁、清爽、高蛋白、低脂、低碳水、高纤维、高钙、低卡、高维生素、均衡营养、海鲜、红肉、白肉、素食、抗氧化、助消化、补气血、增强免疫）
- 蛋白质（1-10分）
- 膳食纤维（1-10分）
- 微量元素（1-10分）
- 添加糖（1-10分）
- 饱和脂肪（1-10分）
- 钠（1-10分）

只返回JSON，格式如下：
{{"category":"蔬菜","calories":35,"season":"四季","tags":"低卡,维生素","features":["高纤维","高维生素"],"protein":6,"fiber":8,"vitamins":7,"sugar":2,"saturated_fat":1,"sodium":2}}"""

    headers = {
        'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'model': 'deepseek-chat',
        'messages': [
            {'role': 'system', 'content': '你是一个营养学专家。只返回JSON，不要有其他解释。'},
            {'role': 'user', 'content': prompt}
        ],
        'temperature': 0.7,
        'max_tokens': 500
    }
    
    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        # 调试：打印 AI 原始返回
        print(f"🤖 AI 原始返回: {content}")
        
        # 提取 JSON
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            food_data = json.loads(json_match.group())
            # 调试：打印解析后的数据
            print(f"📦 解析后的数据: {food_data}")
            
            # 获取 features，确保是列表
            features = food_data.get('features', [])
            if isinstance(features, str):
                features = [features]
            
            return jsonify({
                'code': 200,
                'data': {
                    'category': food_data.get('category', ''),
                    'calories': food_data.get('calories', 0),
                    'season': food_data.get('season', ''),
                    'tags': food_data.get('tags', ''),
                    'features': features,  # 新增：返回饮食特征
                    'protein': food_data.get('protein', 5),
                    'fiber': food_data.get('fiber', 5),
                    'vitamins': food_data.get('vitamins', 5),
                    'sugar': food_data.get('sugar', 5),
                    'saturated_fat': food_data.get('saturated_fat', 5),
                    'sodium': food_data.get('sodium', 5)
                }
            }), 200
        else:
            print(f"❌ 未找到 JSON: {content}")
            return jsonify({'code': 500, 'message': 'AI 返回格式异常'}), 500
            
    except requests.exceptions.RequestException as e:
        print(f"DeepSeek API 请求失败: {e}")
        return jsonify({'code': 500, 'message': f'API 请求失败: {str(e)}'}), 500
    except Exception as e:
        print(f"处理失败: {e}")
        return jsonify({'code': 500, 'message': f'处理失败: {str(e)}'}), 500
    
    # ==================== 2. 获取用户上下文 ====================
def get_user_context(user_id, include_profile=True, include_user_profile=True, include_preference=True, include_history=False, start_date=None, end_date=None):
    """构建用户上下文"""
    context_parts = []
    
    # 评分规则说明
    score_rules = """
【营养指标评分规则】
- 每个指标采用十分制（1-10分）
- 一天所有餐食的评分会累加
- 正常范围：30-70分（累计后）
- 低于30分：表示该营养素摄入不足，需要补充
- 高于70分：表示该营养素摄入超标，需要控制
"""
    
    # 1. 用户基本信息
    if include_profile:
        user = User.query.get(user_id)
        if user:
            context_parts.append(f"""【用户基本信息】
- 年龄：{user.age if user.age else '未知'}岁
- 性别：{'男' if user.gender else '女' if user.gender is not None else '未知'}
- 身高：{user.height if user.height else '未知'}cm
- 体重：{user.weight if user.weight else '未知'}kg""")
    
    # 2. 用户饮食画像（基于30天打卡的动态画像）
    if include_user_profile:
        from ..services.profile_service import ProfileService
        profile_desc = ProfileService.get_profile_description(user_id)
        context_parts.append(f"【用户饮食画像（基于近30天打卡）】\n- {profile_desc}")

    # 3. 用户饮食偏好
    if include_preference:
        from ..models.preference import Preference
        preferences = Preference.query.filter_by(user_id=user_id).all()
        if preferences:
            pref_values = [p.value for p in preferences]
            context_parts.append(f"【饮食偏好】\n- 偏好：{', '.join(pref_values)}")
        else:
            context_parts.append("【饮食偏好】\n- 暂无设置偏好")
    
    # 4. 历史饮食记录
    if include_history and start_date and end_date:
        meals = UserMeal.query.filter(
            UserMeal.user_id == user_id,
            UserMeal.meal_date >= start_date,
            UserMeal.meal_date <= end_date
        ).all()
        
        if meals:
            context_parts.append(score_rules)
            context_parts.append("【历史饮食记录】")
            
            daily_stats = {}
            for meal in meals:
                date_str = meal.meal_date.isoformat()
                if date_str not in daily_stats:
                    daily_stats[date_str] = {
                        'calories': 0, 'protein': 0, 'fiber': 0, 'vitamins': 0,
                        'sugar': 0, 'saturated_fat': 0, 'sodium': 0, 'foods': []
                    }
                daily_stats[date_str]['calories'] += (meal.calories or 0)
                daily_stats[date_str]['protein'] += (meal.protein or 5)
                daily_stats[date_str]['fiber'] += (meal.fiber or 5)
                daily_stats[date_str]['vitamins'] += (meal.vitamins or 5)
                daily_stats[date_str]['sugar'] += (meal.sugar or 5)
                daily_stats[date_str]['saturated_fat'] += (meal.saturated_fat or 5)
                daily_stats[date_str]['sodium'] += (meal.sodium or 5)
                daily_stats[date_str]['foods'].append(meal)
            
            for date_str, stats in daily_stats.items():
                def get_status(score):
                    if score < 30:
                        return "⚠️ 不足（需要补充）"
                    elif score > 70:
                        return "⚠️ 超标（需要控制）"
                    else:
                        return "✅ 正常"
                
                # 构建完整食物清单（显示名称和卡路里）
                food_list = []
                for meal in stats['foods']:
                    food_list.append(f"{meal.food_name}({meal.calories}卡)")
                foods_text = '；'.join(food_list)
                
                context_parts.append(f"""
日期：{date_str}
- 总热量：{stats['calories']}卡
- 蛋白质评分：{stats['protein']}（{get_status(stats['protein'])}）
- 膳食纤维评分：{stats['fiber']}（{get_status(stats['fiber'])}）
- 微量元素评分：{stats['vitamins']}（{get_status(stats['vitamins'])}）
- 添加糖评分：{stats['sugar']}（{get_status(stats['sugar'])}）
- 饱和脂肪评分：{stats['saturated_fat']}（{get_status(stats['saturated_fat'])}）
- 钠评分：{stats['sodium']}（{get_status(stats['sodium'])}）
- 食物清单：{foods_text}
""")
        else:
            context_parts.append("【历史饮食记录】暂无记录")
    
    return '\n'.join(context_parts)

# ==================== 3. AI 对话接口 ====================
@ai_bp.route('/ai/chat', methods=['POST'])
def chat():
    """AI 对话接口"""
    data = request.get_json()
    user_id = data.get('user_id')
    message = data.get('message', '')
    include_profile = data.get('include_profile', True)
    include_user_profile = data.get('include_user_profile', True)
    include_preference = data.get('include_preference', True)
    include_history = data.get('include_history', False)
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    if not user_id or not message:
        return jsonify({'code': 400, 'message': '参数不完整'}), 400
    
    user_context = get_user_context(user_id, include_profile, include_user_profile, include_preference, include_history, start_date, end_date)
    
    system_prompt = """你是一个专业的饮食健康助手。请根据提供的用户信息和历史饮食记录，回答用户的问题。
回答要专业、友好、有针对性。如果用户有异常指标，要给出具体的改善建议。
使用中文回答，保持简洁清晰。"""
    
    user_message = f"""{user_context}

用户问题：{message}

请根据以上信息回答用户的问题。"""
    
    try:
        from ..services.llm_service import LLMService
        reply = LLMService.chat(user_message, system_prompt=system_prompt)
        
        if reply is None:
            return jsonify({'code': 500, 'message': 'AI 服务暂时不可用'}), 500
            
        return jsonify({
            'code': 200,
            'data': {'response': reply}
        }), 200
        
    except Exception as e:
        print(f"AI 对话失败: {e}")
        return jsonify({'code': 500, 'message': f'AI 服务暂时不可用: {str(e)}'}), 500
    
@ai_bp.route('/ai/switch_model', methods=['POST'])
def switch_model():
    """切换大模型引擎"""
    data = request.get_json()
    engine = data.get('engine', 'ollama')
    
    if engine not in ['ollama', 'deepseek']:
        return jsonify({'code': 400, 'message': 'engine 必须是 ollama 或 deepseek'}), 400
    
    # 修改 .env 文件中的 LLM_ENGINE
    env_path = os.path.join(os.path.dirname(__file__), '../../.env')
    try:
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        with open(env_path, 'w') as f:
            for line in lines:
                if line.startswith('LLM_ENGINE='):
                    f.write(f'LLM_ENGINE={engine}\n')
                else:
                    f.write(line)
        
        # 同时更新运行时配置
        from ..services.llm_service import LLMService
        LLMService.ENGINE = engine
        
        return jsonify({'code': 200, 'message': f'已切换至 {engine}', 'data': {'engine': engine}}), 200
    except Exception as e:
        return jsonify({'code': 500, 'message': f'切换失败: {str(e)}'}), 500


@ai_bp.route('/ai/get_model', methods=['GET'])
def get_current_model():
    """获取当前使用的大模型"""
    from ..services.llm_service import LLMService
    return jsonify({'code': 200, 'data': {'engine': LLMService.ENGINE}}), 200