from datetime import datetime
import uuid
from flask import render_template, request, url_for, redirect, flash, session, g, request,session,Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
import re
from app.models.user import User, PasswordResetToken
from app.email_service import generate_reset_token, send_email, verify_reset_token
from .. import login_required, admin_required

user_bp = Blueprint('user', __name__, template_folder='../../templates/user', static_folder='../../static')

@user_bp.route('/registro',methods = ('GET', 'POST'))
def registro():
     if request.method == 'POST':
        # Obtener datos del formulario
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')
        phone = request.form.get('phone')
         
        # Validar datos
        errors = []
        # Regla de contraseña compleja
        password_regex = r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*.?&]{8,}$'
       
        if not first_name or not last_name:
            errors.append("El nombre y los apellidos son obligatorios.")
        
        if not email or '@' not in email:
            errors.append("El correo electrónico no es válido.")
        
        if not username:
            errors.append("El nombre de usuario es obligatorio.")
        elif User.select().where(User.username == username).exists():
            errors.append("El nombre de usuario ya está en uso.")
        
        if not phone or not phone.isdigit():
            errors.append("El teléfono debe ser un número válido.")
        elif User.select().where(User.phone == phone).exists():
            errors.append("ERl telefono ya esta en uso.")

        
        if not re.match(password_regex, password):
           errors.append('La contraseña debe tener al menos 8 caracteres, incluir una mayúscula, un número y un carácter especial.')
        

        if not password:
            errors.append("La contraseña es obligatoria.")
        elif password != confirm_password:
            errors.append("Las contraseñas no coinciden.")

        if User.select().where(User.email == email).exists():
            errors.append("El correo electrónico ya está registrado.") 
       
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('register.html',errors=errors) 
        # Crear usuario
        hashed_password = generate_password_hash(password)
        new_user = User.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
            password=hashed_password,
            phone=phone
        ) 

        # Redirigir al inicio de sesión con mensaje de éxito
        flash("Usuario registrado con éxito. Por favor, inicia sesión.", 'success')
        return redirect(url_for('user.login'))
     return render_template('register.html')

# inicio de seccion del usuario
@user_bp.route('/login',methods = ('GET', 'POST'))
def login():
    if request.method == 'POST':
        username_or_email = request.form.get('userOrEmail')
        password = request.form.get('password')

        # Buscar usuario por nombre de usuario o correo
        user = User.select().where(
            (User.username == username_or_email) | 
            (User.email == username_or_email)
        ).first()
        
         # Buscar usuario por nombre de usuario o correo
        if not user:
            # Usuario o correo no encontrados
            flash('Usuario o contraseña incorrectos..', 'danger')
            return render_template('login.html')

        if not user.check_password(password):
            # Contraseña incorrecta
            flash('Usuario o contraseña incorrectos.', 'danger')
            return render_template('login.html')
            

        session['user_id'] = user.id
        session['username'] = user.username
        flash('Inicio de sesión exitoso.', 'success')
        return redirect(url_for('main.panel_user'))

        

        
    
    return render_template('login.html')
# Restablecer contraseña
@user_bp.route('/reset_password',methods = ('GET', 'POST'))
def reset_password():
     if request.method == 'POST':
        email = request.form.get('email')
        user = User.get_or_none(User.email == email)
        if user:
            # Generar token
            token = generate_reset_token(email)
            # URL de restablecimiento
            reset_url = url_for('user.token_password', token=token, _external=True)
            # Enviar correo
            send_email(
                subject="Restablecimiento de contraseña",
                recipients=[email],
                template="email/reset_password.html",
                title="Restablece tu contraseña",
                reset_url=reset_url
            )
            flash("Se ha enviado un correo con instrucciones para restablecer tu contraseña.", "success")
        else:
            flash("El correo no está registrado.", "danger")
        return redirect(url_for('user.reset_password'))
         
     return render_template('reset_password.html')

@user_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def token_password(token):
    email = verify_reset_token(token)
    if not email:
        flash("El enlace de restablecimiento es inválido o ha expirado.", "danger")
        return redirect(url_for('user.reset_password'))
    
    if request.method == 'POST':
        new_password = request.form.get('password')
        user = User.get_or_none(User.email == email)
        if user:
            # Actualizar contraseña
            user.set_password(new_password)  # Asegúrate de tener un método para encriptar la contraseña
            user.save()
            flash("Tu contraseña ha sido actualizada exitosamente.", "success")
            return redirect(url_for('user.login'))
    
    return render_template('update_password.html', token=token)




@user_bp.route('/logout')
def logout_user():
    session.clear()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('main.index'))

@user_bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id:
        g.user = User.get_or_none(User.id == user_id)
    else:
        g.user = None


@user_bp.route('/send-notification', methods=['GET'])
def send_notification():
    # Configuración del correo
    subject = "Notificación importante"
    recipients = ["roblefelix64@gmail.com"]
    template = "email/notification.html"
    kwargs = {
        "title": "Nueva notificación",
        "message": "Este es un mensaje de ejemplo para tu notificación.",
        "action_url": "https://tu-sitio.com/accion"
    }
    
    # Enviar el correo
    send_email(subject, recipients, template, **kwargs)
    return "Correo enviado con éxito."




@user_bp.route('/admin', methods=['GET', 'POST'])
@login_required
@admin_required

def admin_panel():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        new_role = request.form.get('new_role')

        # Verificar si el usuario existe
        user = User.get_or_none(User.id == user_id)
        if user:
            user.rol = new_role
            user.save()
            flash(f"El rol del usuario {user.username} ha sido actualizado a {new_role}.", "success")
        else:
            flash("El usuario especificado no existe.", "danger")
        return redirect(url_for('user.admin_panel'))

    # Obtener todos los usuarios para mostrarlos en el panel
    users = User.select()
    return render_template('admin/panel.html', users=users)




