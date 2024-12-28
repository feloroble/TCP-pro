from functools import wraps
from flask import  session, flash, redirect, url_for, g




def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):  # Si no hay usuario autenticado
            flash('Debes iniciar sesión para acceder a esta página.', 'warning')
            return redirect(url_for('user.login'))  # Redirige a la página de login
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'user') or g.user.rol != 'administrador':
            flash("Acceso denegado. Solo los administradores pueden acceder a esta sección.", "danger")
            return redirect(url_for('main.index'))  # Redirigir al índice o a otra página
        return f(*args, **kwargs)
    return decorated_function