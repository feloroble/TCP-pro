from flask import Blueprint, render_template, request, url_for, redirect, flash, session, g, request,session
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from app.user import user_bp



#registro de usuarios
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

        if not user.set_password(password):
            # Contraseña incorrecta
            flash('Usuario o contraseña incorrectos.', 'danger')
            return render_template('login.html')
            

        session['user_id'] = user.id
        session['username'] = user.username
        flash('Inicio de sesión exitoso.', 'success')
        return redirect(url_for('user.user'))

        

        
    
    return render_template('login.html')
# Restablecer contraseña
@user_bp.route('/reset_password',methods = ('GET', 'POST'))
def reset_password():

    return render_template('reset_password.html')
# panel de usuario
@user_bp.route('/user')
def user():
    # Lógica para listar clientes
    return render_template('panel.html')

@user_bp.route('/logout')
def logout_user():
    session.clear()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('main.index'))