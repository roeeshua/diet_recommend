#!/usr/bin/env python
"""初始化数据库：创建所有表并插入初始数据"""

import sys
import os

# 把 backend 目录加入 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Preference, Food, Plan, Checkin

app = create_app()

def init_db():
    with app.app_context():
        # 删除所有表
        db.drop_all()
        print("✅ 已删除所有表")
        
        # 创建所有表
        db.create_all()
        print("✅ 已创建所有表")
        
        # 插入初始食材数据
        foods = [
            {'name': '苹果', 'category': '水果', 'calories': 52, 'season': '四季', 'tags': '健康,低卡'},
            {'name': '香蕉', 'category': '水果', 'calories': 89, 'season': '四季', 'tags': '高钾,能量'},
            {'name': '鸡胸肉', 'category': '蛋白质', 'calories': 165, 'season': '四季', 'tags': '高蛋白,低脂'},
            {'name': '鸡蛋', 'category': '蛋白质', 'calories': 155, 'season': '四季', 'tags': '优质蛋白'},
            {'name': '西兰花', 'category': '蔬菜', 'calories': 34, 'season': '四季', 'tags': '高纤维,维生素'},
            {'name': '西红柿', 'category': '蔬菜', 'calories': 18, 'season': '夏季', 'tags': '维生素C'},
            {'name': '三文鱼', 'category': '蛋白质', 'calories': 208, 'season': '四季', 'tags': 'Omega-3'},
            {'name': '糙米饭', 'category': '主食', 'calories': 111, 'season': '四季', 'tags': '粗粮,低GI'},
            {'name': '燕麦', 'category': '主食', 'calories': 389, 'season': '四季', 'tags': '膳食纤维'},
            {'name': '牛奶', 'category': '蛋白质', 'calories': 42, 'season': '四季', 'tags': '钙质'},
        ]
        
        for f in foods:
            food = Food(**f)
            db.session.add(food)
        
        db.session.commit()
        print(f"✅ 已插入 {len(foods)} 条食材数据")
        
        # 验证
        food_count = Food.query.count()
        print(f"📊 当前食材表共有 {food_count} 条记录")
        print("🎉 数据库初始化完成！")

if __name__ == '__main__':
    init_db()