
from peewee import fn,JOIN
from datetime import datetime, timedelta
from flask import current_app, jsonify, render_template, request, url_for, redirect, flash, session, g, request,session,Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
import re

from app.config import confirm_token, generate_confirmation_token
from app.models import user
from app.models.tcp import TCPBusiness
from app.models.user import Operation, User
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
        try:
            hashed_password = generate_password_hash(password)
            new_user = User.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=hashed_password,
                phone=phone,
                verified=False
                ) 
            token = generate_confirmation_token(new_user.email)
            confirm_url = url_for('user.confirm_email', token=token, _external=True)
        
            # Enviar correo de verificación
            subject = "Verificación de correo electrónico"
            recipients = [new_user.email]
            template = 'email/verify_email.html'
            context = {'username': new_user.username, 'confirm_url': confirm_url}
            send_email(subject, recipients, template, **context)

            flash('Te hemos enviado un correo para verificar tu cuenta.', 'success')
            return redirect(url_for('user.login'))
        except Exception as e:
            current_app.logger.error(f"Error registrando usuario: {e}")
            flash('Ocurrió un error al registrar al usuario.', 'danger')

        
     return render_template('register.html')

@user_bp.route('/resend-verification-email', methods=['POST'])
def resend_verification_email():
    email = request.form.get('resend_email')
    user = User.get_or_none(User.email == email)
    
    if not user:
        flash('El correo ingresado no está registrado.', 'danger')
        return redirect(url_for('user.login'))
    
    if user.verified:
        flash('Tu cuenta ya está verificada.', 'info')
        return redirect(url_for('user.login'))
    
    # Generar y enviar el enlace de verificación
    token = generate_confirmation_token(user.email)
    verification_url = url_for('user.confirm_email', token=token, _external=True)
    subject = "Verifica tu cuenta"
    recipients = [user.email]
    template = 'email/verify_email.html'
    context = {'username': user.username, 'confirm_url': verification_url}
    send_email(subject, recipients, template, **context)
    flash('Te hemos enviado un enlace de verificación a tu correo.', 'info')
    return redirect(url_for('user.login'))
    
@user_bp.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = confirm_token(token)
        if not email:
            flash('El enlace de verificación es inválido o ha expirado.', 'danger')
            return redirect(url_for('login'))

        user = User.get(User.email == email)
        
        if user.verified:
            flash('Tu cuenta ya está verificada. Por favor, inicia sesión.', 'info')
        else:
            user.verified = True
            user.save()
            user_reloaded = User.get(User.id == user.id)
            print(f"Verified value after save: {user_reloaded.verified}")

            # Enviar correo de bienvenida
            subject = "¡Bienvenido a nuestra aplicación!"
            recipients = [user.email]
            template = 'email/welcome.html'
            context = {'username': user.username}
            send_email(subject, recipients, template, **context)

            flash('Tu cuenta ha sido verificada exitosamente.', 'success')
        return redirect(url_for('user.login'))
    except Exception as e:
        current_app.logger.error(f"Error verificando correo: {e}")
        flash('Ocurrió un error al verificar tu correo.', 'danger')
        return redirect(url_for('user.login'))
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
    #    print(user.verified)

        if not User.verified:
                flash('Tu cuenta no ha sido verificada. Por favor, revisa tu correo.', 'warning')
                return redirect(url_for('user.login'))
         # Buscar usuario por nombre de usuario o correo
        if not user:
            # Usuario o correo no encontrados
            flash('Usuario o contraseña incorrectos..', 'danger')
            return render_template('login.html')

        if not user.check_password(password):
            # Contraseña incorrecta
            flash('Usuario o contraseña incorrectos.', 'danger')
            return render_template('login.html')
       
        negocios_ids = [negocio.id for negocio in  TCPBusiness.select( TCPBusiness.id).where( TCPBusiness.user_id == user)]
        print(negocios_ids)     

        session['user_id'] = user.id
        session['username'] = user.username
        session['nombre_completo'] = f"{user.first_name} {user.last_name}"
        session['cargo'] = user.cargo
        session['negocio_id'] = negocios_ids 
        session['url_history'] = []
        flash('Inicio de sesión exitoso.', 'success')
        
        Operation.create(user=user, event_type='login', description='Inicio de sesión exitoso.')
        return redirect(url_for('main.panel_user'))
    return render_template('login.html')

# Restablecer contraseña
@user_bp.route('/reset_password',methods = ('GET', 'POST'))
def reset_password():
     if request.method == 'POST':
        email = request.form.get('email')
        user = User.get_or_none(User.email == email)
        usuario = g.user.first_name +" "+ g.user.last_name
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
                reset_url=reset_url,
                usuario=usuario
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
            session['user_id'] = user.id
            Operation.create(user=user, event_type='rest_password', description='Su contraseña fue restablecida de forma satisfactoria.')
            
            send_email(
                subject="Su contraseña fue actualisada con exito",
                recipients=[email],
                template="email/password_update.html",
                title="Su contraseña fue actualisada con exito",
                
            )
            
            
            
            
            return redirect(url_for('user.login'))
    
    return render_template('update_password.html', token=token)


@user_bp.route('/logout')
def logout_user():
    
    if 'user_id' in session:
        # Registrar el evento de cierre de sesión
        Operation.create(
            user=session['user_id'],  # Suponiendo que user_id es el ID del usuario autenticado
            event_type='logout',
            description='Cierre de sesión exitoso.'
        )

        session.clear()

        flash('Has cerrado sesión exitosamente.', 'success')
        return redirect(url_for('main.index'))
    else:
        flash('No estabas autenticado.', 'warning')
        return redirect(url_for('main.index'))


@user_bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id:
        g.user = User.get_or_none(User.id == user_id)
    else:
        g.user = None

def check_user_license_warning():
    if not hasattr(g, 'user') and g.user.rol == 'usuario TCP':
        days_remaining = (user.license_expiry - datetime.now()).days
        if days_remaining <= 7:  # Advertir con 7 días de antelación
            flash(f"Tu licencia TCP expira en {days_remaining} días.", "warning")



@user_bp.route('/send-notification', methods=['GET'])
def send_notification():
    usuario = g.user.first_name +" "+ g.user.last_name
    # Configuración del correo
    subject = "Notificación importante"
    recipients = ["roblefelix64@gmail.com"]
    template = "email/notification.html"
    kwargs = {
        "title": usuario,
        
    }
    
    # Enviar el correo
    send_email(subject, recipients, template, **kwargs)
    return "Correo enviado con éxito."

@user_bp.route('/operations/latest', methods=['GET'])
def get_latest_operations():
    if not g.user:
        return jsonify({"error": "Usuario no autenticado"}), 401

    # Obtenemos el filtro de la consulta
    filter_param = request.args.get("filter", "all")

    # Filtrar operaciones según el tipo de evento
    query = Operation.select().where(Operation.user == g.user)
    if filter_param != "all":
        query = query.where(Operation.event_type == filter_param)
    
    # Ordenar y limitar a las últimas 10
    operations = query.order_by(Operation.created_at.desc()).limit(10)
    result = [
        {
            "event_name": dict(Operation.EVENT_TYPES).get(op.event_type, "Evento desconocido"),
            "description": op.description,
            "created_at": op.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        for op in operations
    ]
    return jsonify(result)

# panel de administrador funciones

@user_bp.route('/admin', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_panel():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        new_role = request.form.get('new_role')
        license_duration = request.form.get('license_duration', type=int)
        # Verificar si el usuario existe
        user = User.get_or_none(User.id == user_id)
        if not user:
            flash("El usuario especificado no existe.", "danger")
            return redirect(url_for('user.admin_panel'))
        # Actualiza el rol del usuario
        user.rol = new_role
           
        if new_role == "usuario TCP":
            if license_duration and license_duration > 0:
                user.license_duration = int(license_duration)
                user.license_expiry = datetime.now() + timedelta(days=30 * license_duration)
            else:
                flash("Debe especificar una duración válida para la licencia.", "error")
                return redirect(url_for('user.admin_panel'))
        else:
            # Si no es "usuario TCP", elimina la duración de licencia y la fecha de expiración
            user.license_duration = None
            user.license_expiry = None

        user.save()
        flash(f"Rol de usuario actualizado a {new_role}", "success")

    # Obtener todos los usuarios para mostrarlos en el panel
    users = (
         User.select(
            User,
            fn.COUNT(TCPBusiness.id).alias('business_count')  # Contar negocios
        )
        .join(TCPBusiness, JOIN.LEFT_OUTER, on=(TCPBusiness.user_id == User.id))  # Unir con negocios
        .group_by(User)  # Agrupar por usuario    
    )

        # Obtener parámetros de filtro
    role_filter = request.args.get('role')  # Filtro por rol
    name_filter = request.args.get('name')  # Filtro por nombre
    email_filter = request.args.get('email')  # Filtro por email

    # Base de la consulta
    query = (
        User.select(
            User,
            fn.COUNT(TCPBusiness.id).alias('business_count')  # Contar negocios
        )
        .join(TCPBusiness, JOIN.LEFT_OUTER, on=(TCPBusiness.user_id == User.id))
        .group_by(User.id)
    )

    # Aplicar filtros
    if role_filter:
        query = query.where(User.rol == role_filter)
    if name_filter:
        query = query.where(
            (User.first_name.contains(name_filter)) | 
            (User.last_name.contains(name_filter))
        )
    if email_filter:
        query = query.where(User.email.contains(email_filter))

    # Ejecutar la consulta
    users = query
    users_with_license_info = [
        {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "rol": user.rol,
            "license_duration": user.license_duration,
            "license_expiry": user.license_expiry,
            "days_remaining": user.days_remaining(),  # Calcula los días restantes
            "business_count": user.business_count
        }
        for user in users
    ]
    return render_template('admin/panel.html', users=users_with_license_info)



