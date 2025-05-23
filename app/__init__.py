
from flask import Flask, g, session

from app.middleware import track_url_middleware
from app.models.tcp import TCPBusiness
from app.tasks.scheduler import initialize_scheduler
from .config import  SECRET_KEY, MAIL, UPLOAD_FOLDER

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
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


    # Inicializar extensiones
    mail.init_app(app)

    # Agregar middleware
    track_url_middleware(app)
    
    initialize_scheduler(app)
    
     # Registrar Blueprints
    from app.routes.user.routes import user_bp
    from app.routes.user.detalle_usuario import detalle_bp
    from app.routes.main.routes import main_bp
    from app.routes.tcp.routes_tcp import tcp_bp, relation_bp,agreg_cl_prb_bp, edit_cl_prb_bp
    from app.routes.facturas.routes import facturas_bp,facturas_copra_bp,facturas_venta_bp
    from app.routes.tcp.tarifas_tcp import tarifas_bp
    from app.routes.inventario.routes import inventario_bp
    from app.routes.ficha_costo.routes import ficha_bp, ver_ficha_dp
    from app.routes.producto.routes import producto_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(detalle_bp, url_prefix='/user/detalles')
    app.register_blueprint(tcp_bp, url_prefix='/tcp')
    app.register_blueprint(relation_bp, url_prefix='/tcp-manager/ver')
    app.register_blueprint(agreg_cl_prb_bp, url_prefix='/tcp-manager/crear')
    app.register_blueprint(edit_cl_prb_bp, url_prefix='/tcp-manager/editar')
    app.register_blueprint(facturas_venta_bp, url_prefix='/tcp/factura-venta')
    app.register_blueprint(facturas_copra_bp, url_prefix='/tcp/factura-compra')
    app.register_blueprint(tarifas_bp, url_prefix='/tcp/tarifas')
    app.register_blueprint(inventario_bp, url_prefix='/tcp/inventario')
    app.register_blueprint(ficha_bp, url_prefix='/ficha-costo')
    app.register_blueprint(ver_ficha_dp, url_prefix='/ficha-costo/ver')
    app.register_blueprint(producto_bp, url_prefix='/edit-product')
    
    return app
    
   

