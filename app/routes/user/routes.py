

from flask import jsonify, render_template, request, url_for, redirect, flash, session, g, request,session,Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
import re
from app.models import user
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




