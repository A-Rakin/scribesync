from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
import os

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app(config_class=Config):
    # Get the absolute path to the templates directory
    base_dir = os.path.abspath(os.path.dirname(__file__))
    templates_path = os.path.join(base_dir, '..', 'templates')
    static_path = os.path.join(base_dir, '..', 'static')

    print(f"Base directory: {base_dir}")
    print(f"Templates path: {templates_path}")
    print(f"Templates exists: {os.path.exists(templates_path)}")

    app = Flask(__name__,
                template_folder=templates_path,
                static_folder=static_path)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Import and register blueprints
    from app.routes import main, auth, api
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(api, url_prefix='/api')

    return app