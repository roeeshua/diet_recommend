#!/usr/bin/env python
import pandas as pd
import os
from sqlalchemy import create_engine, text

# 获取当前脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))

# 读取数据（假设 CSV 在项目根目录）
csv_path = os.path.join(script_dir, '../../foods_200.csv')
df = pd.read_csv(csv_path)

# 连接数据库
engine = create_engine('mysql+pymysql://root:111@172.29.208.1:3306/diet_recommend')

# 清空原表
with engine.connect() as conn:
    conn.execute(text("DELETE FROM foods"))
    conn.commit()
    print("✅ 已清空 foods 表")

# 导入新数据
df.to_sql('foods', engine, if_exists='append', index=False)
print(f"✅ 已导入 {len(df)} 条食物数据")

# 验证
with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM foods")).scalar()
    print(f"📊 当前 foods 表共有 {result} 条记录")