
from flask import Flask, g, session

from app.middleware import track_url_middleware
from app.models.tcp import TCPBusiness
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

    @app.before_request
    def set_selected_business():
       selected_business_id = session.get('selected_business_id')
       if selected_business_id:
        try:
            g.selected_business = TCPBusiness.get(TCPBusiness.id == selected_business_id)
        except TCPBusiness.DoesNotExist:
            g.selected_business = None
       else:
         g.selected_business = None
    
    # Agregar middleware
    track_url_middleware(app)
    
    
    
    @app.context_processor
    def inject_business_context():
      return {
        'selected_business_name': getattr(g.selected_business, 'name', None),
        'selected_business_id': getattr(g.selected_business, 'id', None),
      }
    

     

    # Registrar Blueprints
    from app.routes.user.routes import user_bp
    from app.routes.main.routes import main_bp
    from app.routes.tcp.routes import tcp_bp
    from app.routes.inventario.routes import inventario_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(tcp_bp, url_prefix='/tcp')
    app.register_blueprint(inventario_bp, url_prefix='/tcp/inventario')
    
    return app
    
   

