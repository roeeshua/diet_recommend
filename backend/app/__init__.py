from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from .config import Config

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    CORS(app)
    
    # 注册蓝图
    from .routes.auth import auth_bp
    from .routes.user import user_bp
    from .routes.food import food_bp
    from .routes.preference import preference_bp
    from .routes.recommend import recommend_bp
    from .routes.plan import plan_bp
    from .routes.checkin import checkin_bp
    from .routes.ai import ai_bp

    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(food_bp, url_prefix='/api')
    app.register_blueprint(preference_bp, url_prefix='/api')
    app.register_blueprint(recommend_bp, url_prefix='/api')
    app.register_blueprint(plan_bp, url_prefix='/api')
    app.register_blueprint(checkin_bp, url_prefix='/api')
    app.register_blueprint(ai_bp, url_prefix='/api')
    
    @app.route('/health')
    def health():
        return {'status': 'ok'}
    
    return app