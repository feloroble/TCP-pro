
from flask import Flask, g, session

from app.middleware import track_url_middleware
from app.models.tcp import TCPBusiness
from app.tasks.scheduler import initialize_scheduler
from .config import  SECRET_KEY, MAIL

from app.extensions import mail


# Crear un serializer para los tokens de confirmación



def create_app():
    app = Flask(__name__)
    app.secret_key = SECRET_KEY
    # Configuración para Flask-Mail
    app.config['MAIL_SERVER'] = MAIL['mail_server']
    app.config['MAIL_PORT'] = MAIL['mail_port']
    app.config['MAIL_USE_TLS'] = MAIL['mail_use_TLS']
    app.config['MAIL_USERNAME'] = MAIL['mail_usename']
    app.config['MAIL_PASSWORD'] = MAIL['mail_password']
    app.config['MAIL_DEFAULT_SENDER'] = MAIL['mail_default_sender']


    # Inicializar extensiones
    mail.init_app(app)

    # Agregar middleware
    track_url_middleware(app)
    
    initialize_scheduler(app)
    
     # Registrar Blueprints
    from app.routes.user.routes import user_bp
    from app.routes.main.routes import main_bp
    from app.routes.tcp.routes import tcp_bp
    from app.routes.inventario.routes import inventario_bp
    from app.routes.ficha_costo.routes import ficha_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(tcp_bp, url_prefix='/tcp')
    app.register_blueprint(inventario_bp, url_prefix='/tcp/inventario')
    app.register_blueprint(ficha_bp, url_prefix='/ficha-costo')
    
    return app
    
   

