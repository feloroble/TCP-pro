from flask import Flask
from .config import  SECRET_KEY,MAIL
from app.routes.user.routes import user_bp
from app.routes.main.routes import main_bp
from flask_mail import Mail




def create_app():
    app = Flask(__name__)
    app.secret_key = SECRET_KEY
    app.config['MAIL_SERVER'] = MAIL['mail_server']
    app.config['MAIL_PORT'] = MAIL['mail_port']
    app.config['MAIL_USE_TLS'] = MAIL['mail_use_TLS']
    app.config['MAIL_USERNAME'] = MAIL['mail_usename']  # Reemplázalo con tu correo
    app.config['MAIL_PASSWORD'] = MAIL['mail_password'] # Usa un token de aplicación si es necesario

    mail = Mail(app)


     

    # Registrar Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(user_bp, url_prefix='/user')
    
    return app
    
    

