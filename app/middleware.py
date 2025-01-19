from datetime import datetime
from mailbox import Message
from flask import request, session

from app.models.user import User
from app.extensions import mail
def track_url_middleware(app):
    @app.before_request
    def track_url():
        if 'user_id' in session:  # Solo rastrear si el usuario ha iniciado sesión
            if 'url_history' not in session:
                session['url_history'] = []
            
            excluded_paths = ['/static', '/tcp/static' , '/tcp/inventario/static','/user/operations' , '/login', '/logout' , '//tcp/inventario/cost_sheet','/user/static'  ]   
            if not any(request.path.startswith(path) for path in excluded_paths):
                session['url_history'].append(request.path)
                session['url_history'] = session['url_history'][-5:]  # Mantén máximo 5 URLs
                print("Historial actualizado:", session['url_history'])  # Depuración



