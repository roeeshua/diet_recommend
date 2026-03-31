import requests
import pandas as pd
import time
import re

# 你的 USDA API Key
API_KEY = "mLa7undvqXh9fOx5ljXrZMaBes6BCLRWWc9TEpz6"
BASE_URL = "https://api.nal.usda.gov/fdc/v1/"

def search_food(keyword, page_size=10):
    """搜索食物，返回 FDC ID 列表"""
    url = f"{BASE_URL}foods/search"
    params = {
        'api_key': API_KEY,
        'query': keyword,
        'pageSize': page_size,
        'dataType': ['Foundation', 'SR Legacy', 'Branded']
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        foods = []
        for item in data.get('foods', []):
            foods.append({
                'fdcId': item['fdcId'],
                'description': item['description'],
                'foodCategory': item.get('foodCategory', '未知')
            })
        return foods
    except Exception as e:
        print(f"搜索失败: {e}")
        return []

def get_food_nutrients(fdc_id):
    """获取食物的营养数据"""
    url = f"{BASE_URL}food/{fdc_id}"
    params = {'api_key': API_KEY}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # 提取营养数据
        nutrients = {
            'calories': 0, 'protein': 0, 'fiber': 0,
            'sugar': 0, 'saturated_fat': 0, 'sodium': 0
        }
        
        for nutrient in data.get('foodNutrients', []):
            name = nutrient.get('nutrientName', '')
            value = nutrient.get('value', 0)
            if 'Energy' in name and 'kcal' in name:
                nutrients['calories'] = value
            elif 'Protein' in name:
                nutrients['protein'] = value
            elif 'Fiber' in name:
                nutrients['fiber'] = value
            elif 'Sugars' in name:
                nutrients['sugar'] = value
            elif 'Saturated fat' in name:
                nutrients['saturated_fat'] = value
            elif 'Sodium' in name:
                nutrients['sodium'] = value
        
        # 估算微量元素（用维生素C+钙的均值）
        total_minerals = 0
        count = 0
        for nutrient in data.get('foodNutrients', []):
            name = nutrient.get('nutrientName', '')
            value = nutrient.get('value', 0)
            if 'Vitamin C' in name:
                total_minerals += min(100, value / 10)  # 维生素C 10分制
                count += 1
            elif 'Calcium' in name:
                total_minerals += min(100, value / 100)  # 钙 10分制
                count += 1
        nutrients['vitamins'] = round(total_minerals / count) if count > 0 else 5
        
        return nutrients
    except Exception as e:
        print(f"获取营养失败: {e}")
        return None

# 评分转换函数（十分制，3-7分为正常）
def score_converter(value, low_threshold, ideal_low, ideal_high, high_threshold):
    """通用评分转换"""
    if value < low_threshold:
        return max(1, int(value / low_threshold * 3))
    elif low_threshold <= value <= high_threshold:
        # 映射到 3-7 分
        return int(3 + (value - low_threshold) / (high_threshold - low_threshold) * 4)
    else:
        return min(10, 7 + int((value - high_threshold) / (high_threshold) * 3))

def calculate_scores(nutrients):
    """计算六个指标的十分制评分"""
    scores = {}
    
    # 蛋白质 (g) 正常范围 10-40g
    scores['protein'] = score_converter(nutrients['protein'], 10, 10, 40, 40)
    
    # 膳食纤维 (g) 正常范围 5-20g
    scores['fiber'] = score_converter(nutrients['fiber'], 5, 5, 20, 20)
    
    # 微量元素（虚拟指标）正常范围 3-7分
    scores['vitamins'] = max(1, min(10, nutrients.get('vitamins', 5)))
    
    # 添加糖 (g) 正常范围 0-25g（越低越好）
    if nutrients['sugar'] < 10:
        scores['sugar'] = 7 - int(nutrients['sugar'] / 3)
    elif nutrients['sugar'] < 25:
        scores['sugar'] = 5
    else:
        scores['sugar'] = max(1, 7 - int((nutrients['sugar'] - 25) / 5))
    scores['sugar'] = max(1, min(10, scores['sugar']))
    
    # 饱和脂肪 (g) 正常范围 5-25g
    scores['saturated_fat'] = score_converter(nutrients['saturated_fat'], 5, 5, 25, 25)
    
    # 钠 (mg) 正常范围 400-2000mg
    scores['sodium'] = score_converter(nutrients['sodium'], 400, 400, 2000, 2000)
    
    return scores

# 要爬取的食物列表（常见菜品）
foods_to_crawl = [
    "chicken breast", "salmon", "beef steak", "pork chop",
    "brown rice", "quinoa", "oatmeal", "whole wheat bread",
    "broccoli", "spinach", "tomato", "carrot", "cucumber",
    "apple", "banana", "orange", "blueberry", "strawberry",
    "egg", "milk", "greek yogurt", "tofu", "lentil",
    "olive oil", "almond", "walnut"
]

# 主函数
def main():
    all_foods = []
    
    for keyword in foods_to_crawl:
        print(f"搜索: {keyword}")
        foods = search_food(keyword, page_size=3)
        for food in foods[:2]:  # 每种取前2个
            print(f"  获取: {food['description']}")
            nutrients = get_food_nutrients(food['fdcId'])
            if nutrients:
                scores = calculate_scores(nutrients)
                all_foods.append({
                    'name': food['description'],
                    'category': food['foodCategory'],
                    'calories': nutrients['calories'],
                    'protein': scores['protein'],
                    'fiber': scores['fiber'],
                    'vitamins': scores['vitamins'],
                    'sugar': scores['sugar'],
                    'saturated_fat': scores['saturated_fat'],
                    'sodium': scores['sodium'],
                    'season': '四季',  # 可后续手动调整
                    'tags': ''  # 可后续手动添加
                })
            time.sleep(0.5)  # 避免请求过快
    
    # 保存到 CSV
    df = pd.DataFrame(all_foods)
    df.to_csv('foods_data.csv', index=False, encoding='utf-8')
    print(f"✅ 共爬取 {len(all_foods)} 条食物数据，已保存到 foods_data.csv")

if __name__ == '__main__':
    main()