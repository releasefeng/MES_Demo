from flask import Flask
from config import Config
from app.extensions import db, login_manager
from flask_migrate import Migrate
import os

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    migrate = Migrate(app, db)

    # 注册蓝图
    from app.routes import auth, main, production, process, report
    from app.api import bp as api_bp
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(production.bp)
    app.register_blueprint(process.bp)
    app.register_blueprint(report.bp)
    app.register_blueprint(api_bp)

    # 创建数据库表
    with app.app_context():
        if not os.path.exists(app.instance_path):
            os.makedirs(app.instance_path)
        db.create_all()

        # 如果没有用户，创建一个管理员用户
        from app.models.user import User
        if not User.query.first():
            admin = User(username='admin', role='admin')
            admin.set_password('admin')
            db.session.add(admin)
            db.session.commit()

    return app 