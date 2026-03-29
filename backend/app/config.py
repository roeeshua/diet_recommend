import os
from dotenv import load_dotenv

load_dotenv()  # 保留这行，万一后面 .env 生效了也能覆盖

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-123456')
    MYSQL_HOST = '172.29.208.1'
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '111')    # 👈 也把密码默认值写上
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'diet_recommend')
    
    # 打印验证
    print(f"🔧 连接数据库: {MYSQL_HOST}:{MYSQL_PORT} 用户:{MYSQL_USER}")
    
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False