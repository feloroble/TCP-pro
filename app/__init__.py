from flask import Flask, render_template
from peewee import MySQLDatabase
from app.main import main_bp
from .config import DATABASE, SECRET_KEY

db = MySQLDatabase(
    DATABASE['name'],
    user=DATABASE['user'],
    password=DATABASE['password'],
    host=DATABASE['host'],
    port=DATABASE['port']
)



def create_app():
    app = Flask(__name__)
    app.secret_key = SECRET_KEY

    # Inicializar base de datos
     # Manejador de error 404
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
    

    # Registrar Blueprints
    app.register_blueprint(main_bp)

    from app.user import user_bp
    app.register_blueprint(user_bp, url_prefix='/user')

    return app
    
    

