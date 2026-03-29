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
    app.register_blueprint(auth_bp, url_prefix='/api')

    from .routes.user import user_bp
    app.register_blueprint(user_bp, url_prefix='/api')

    from .routes.preference import preference_bp
    app.register_blueprint(preference_bp, url_prefix='/api')

    from .routes.food import food_bp
    app.register_blueprint(food_bp, url_prefix='/api')
    
    @app.route('/health')
    def health():
        return {'status': 'ok'}
    
    return app