from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_session import Session
import os
import logging
from logging.handlers import RotatingFileHandler

db = SQLAlchemy()
login_manager = LoginManager()
socketio = SocketIO()
server_session = Session()

def create_app(config_name='default'):
    app = Flask(__name__)
    
    from app.config import config
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message = '请先登录'
    
    server_session.init_app(app)
    
    socketio.init_app(app, async_mode=app.config['SOCKETIO_ASYNC_MODE'],
                      cors_allowed_origins=app.config['SOCKETIO_CORS_ALLOWED_ORIGINS'])
    
    if not app.debug and not app.testing:
        if not os.path.exists(app.config['LOG_FILE']):
            os.makedirs(os.path.dirname(app.config['LOG_FILE']), exist_ok=True)
        
        file_handler = RotatingFileHandler(app.config['LOG_FILE'],
                                           maxBytes=10240000,
                                           backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('AI舆情分析系统启动')
    
    from app.routes import main_routes, ai_routes
    app.register_blueprint(main_routes.bp)
    app.register_blueprint(ai_routes.bp)
    
    with app.app_context():
        db.create_all()
    
    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))
