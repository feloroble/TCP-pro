from datetime import datetime
from flask import current_app, render_template,url_for
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from app.extensions import mail
from app.models.user import User  # Asegúrate de inicializar `mail` en tu `__init__.py` principal.


def send_email(subject, recipients, template, **kwargs):
    """
    Envía un correo electrónico usando Flask-Mail.
    
    Args:
        subject (str): Asunto del correo.
        recipients (list): Lista de destinatarios.
        template (str): Ruta de la plantilla HTML (relativa a la carpeta `templates`).
        kwargs: Variables que se pasarán al contexto de la plantilla.
    """
    try:
        logo_url = url_for('static', filename='images/logo/icol_logo.png', _external=True)
        current_year = datetime.now().year
        msg = Message(
            subject=subject,
            recipients=recipients,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        msg.html = render_template(template, logo_url=logo_url, current_year=current_year, **kwargs)
        mail.send(msg)
    except Exception as e:
        current_app.logger.error(f"Error enviando correo: {e}")


def generate_reset_token(email):
    """
    Genera un token para el restablecimiento de contraseña.
    Args:
        email (str): Dirección de correo del usuario.
    Returns:
        str: Token seguro.
    """
    serializer = URLSafeTimedSerializer(current_app.secret_key)
    return serializer.dumps(email, salt='password-reset-salt')

def verify_reset_token(token, expiration=3600):
    """
    Verifica la validez del token.
    Args:
        token (str): Token generado.
        expiration (int): Tiempo de expiración en segundos (default: 1 hora).
    Returns:
        str: Email si el token es válido, None en caso contrario.
    """
    serializer = URLSafeTimedSerializer(current_app.secret_key)
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=expiration)
        return email
    except Exception:
        return None

