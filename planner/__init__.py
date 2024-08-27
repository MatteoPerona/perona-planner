from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .config import DevelopmentConfig, ProductionConfig
# from .auth import auth as auth_blueprint
# from .main import main as main_blueprint
# from .profile import profile as profile_blueprint

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    # app.config['SECRET_KEY'] = 'secret-key-goes-here'
    # app.config.from_pyfile('../config.py') 
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///planner.db'
    app.config.from_object(DevelopmentConfig)
    # app.config.from_object(ProductionConfig)
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    from . import models

    with app.app_context():
        db.create_all()

    # app.register_blueprint(auth_blueprint)
    # app.register_blueprint(main_blueprint)
    # app.register_blueprint(profile_blueprint)

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .profile import profile_bp as profile_blueprint
    app.register_blueprint(profile_blueprint)

    return app