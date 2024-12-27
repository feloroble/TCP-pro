from flask import Flask
from peewee import MySQLDatabase
from .config import  SECRET_KEY
from app.routes.user.routes import user_bp
from app.routes.main.routes import main_bp





def create_app():
    app = Flask(__name__)
    app.secret_key = SECRET_KEY

     

    # Registrar Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(user_bp, url_prefix='/user')
    
    return app
    
    

