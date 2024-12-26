from flask import render_template,session, redirect, url_for, flash
from app.main import main_bp
from functools import wraps


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):  # Si no hay usuario autenticado
            flash('Debes iniciar sesión para acceder a esta página.', 'warning')
            return redirect(url_for('user.login'))  # Redirige a la página de login
        return f(*args, **kwargs)
    return decorated_function


# ruta principal de inicio
@main_bp.route('/')
def index():
    return render_template('index.html')

# proyecto flujorad web

@main_bp.route('/flujorad')
def flujorad():
    return render_template('proyectos/flujorad.html')

@main_bp.route('/perfil')
@login_required
def panel_user():
    return render_template('perfil/panel.html')


