from .checkin_service import CheckinService
from datetime import datetime

class StatisticsService:
    
    @staticmethod
    def get_daily_stats(user_id: int, target_date: str):
        """获取某天的营养统计"""
        meals = CheckinService.get_meals_by_date(user_id, target_date)
        
        stats = {
            'date': target_date,
            'total_calories': 0,
            'protein': 0,
            'fiber': 0,
            'vitamins': 0,
            'sugar': 0,
            'saturated_fat': 0,
            'sodium': 0,
            'meal_count': 0,
            'breakfast': [],
            'lunch': [],
            'dinner': []
        }
        
        for meal in meals:
            stats['total_calories'] += (meal.calories or 0)
            stats['protein'] += (meal.protein or 5)
            stats['fiber'] += (meal.fiber or 5)
            stats['vitamins'] += (meal.vitamins or 5)
            stats['sugar'] += (meal.sugar or 5)
            stats['saturated_fat'] += (meal.saturated_fat or 5)
            stats['sodium'] += (meal.sodium or 5)
            stats['meal_count'] += 1
            
            if meal.meal_type == 'breakfast':
                stats['breakfast'].append(meal.to_dict())
            elif meal.meal_type == 'lunch':
                stats['lunch'].append(meal.to_dict())
            else:
                stats['dinner'].append(meal.to_dict())
        
        # 计算平均值（如果有餐食）
        if stats['meal_count'] > 0:
            stats['protein'] = round(stats['protein'] / stats['meal_count'], 1)
            stats['fiber'] = round(stats['fiber'] / stats['meal_count'], 1)
            stats['vitamins'] = round(stats['vitamins'] / stats['meal_count'], 1)
            stats['sugar'] = round(stats['sugar'] / stats['meal_count'], 1)
            stats['saturated_fat'] = round(stats['saturated_fat'] / stats['meal_count'], 1)
            stats['sodium'] = round(stats['sodium'] / stats['meal_count'], 1)
        
        return stats
    
    @staticmethod
    def get_monthly_trend(user_id: int, year: int, month: int):
        """获取月度趋势（用于折线图）"""
        meals = CheckinService.get_monthly_stats(user_id, year, month)
        
        # 按日期分组
        daily_data = {}
        for meal in meals:
            date_str = meal.meal_date.isoformat()
            if date_str not in daily_data:
                daily_data[date_str] = {
                    'date': date_str,
                    'total_calories': 0,
                    'protein': 0,
                    'fiber': 0,
                    'vitamins': 0,
                    'sugar': 0,
                    'saturated_fat': 0,
                    'sodium': 0,
                    'meal_count': 0
                }
            daily_data[date_str]['total_calories'] += (meal.calories or 0)
            daily_data[date_str]['protein'] += (meal.protein or 5)
            daily_data[date_str]['fiber'] += (meal.fiber or 5)
            daily_data[date_str]['vitamins'] += (meal.vitamins or 5)
            daily_data[date_str]['sugar'] += (meal.sugar or 5)
            daily_data[date_str]['saturated_fat'] += (meal.saturated_fat or 5)
            daily_data[date_str]['sodium'] += (meal.sodium or 5)
            daily_data[date_str]['meal_count'] += 1
        
        # 计算平均值
        result = []
        for date_str, data in sorted(daily_data.items()):
            result.append({
                'date': date_str,
                'total_calories': data['total_calories'],
                'protein': data['protein'],
                'fiber': data['fiber'],
                'vitamins': data['vitamins'],
                'sugar': data['sugar'],
                'saturated_fat': data['saturated_fat'],
                'sodium': data['sodium']
            })
        
        return result
    
    @staticmethod
    def get_advice(stats: dict):
        """根据统计数据生成建议"""
        advice = {}
        
        # 热量建议（假设正常范围 1600-2200 卡）
        calories = stats.get('total_calories', 0)
        if calories < 1600:
            advice['calories'] = '热量摄入偏低，建议增加主食或蛋白质'
        elif calories > 2200:
            advice['calories'] = '热量摄入偏高，建议减少高热量食物'
        else:
            advice['calories'] = '热量摄入正常，继续保持'
        
        # 营养指标（正常范围 30-70 分）
        for nutrient, value in [('protein', '蛋白质'), ('fiber', '膳食纤维'), ('vitamins', '微量元素'),
                                  ('sugar', '添加糖'), ('saturated_fat', '饱和脂肪'), ('sodium', '钠')]:
            score = stats.get(nutrient, 0)
            if score < 30:
                advice[nutrient] = f'{value}摄入不足，建议多补充'
            elif score > 70:
                advice[nutrient] = f'{value}摄入偏高，建议适当控制'
            else:
                advice[nutrient] = f'{value}摄入正常，继续保持'
        
        return advice