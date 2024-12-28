from flask_mail import Message
from flask import render_template, current_app
from app import mail


def send_email(subject, recipients, template, **kwargs):
    """
    Envía un correo electrónico.
    Args:
        subject (str): Asunto del correo.
        recipients (list): Lista de destinatarios.
        template (str): Nombre del archivo de plantilla HTML.
        kwargs: Variables adicionales para la plantilla.
    """
    msg = Message(subject, sender=current_app.config['MAIL_USERNAME'], recipients=recipients)
    msg.html = render_template(template, **kwargs)
    mail.send(msg)