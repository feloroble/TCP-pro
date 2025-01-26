from flask import render_template, request, url_for, redirect, flash, session, g, request,session,Blueprint


from app.models.user import Operation
from .. import login_required



main_bp = Blueprint('main', __name__, template_folder='../../templates/main', static_folder='../../static')

# ruta principal de inicio
@main_bp.route('/')
def index():
    return render_template('main/index.html')

# proyecto flujorad web
@main_bp.route('/flujorad')
def flujorad():
    return render_template('proyectos/flujorad.html')

@main_bp.route('/perfil')
@login_required
def panel_user():
    return render_template('perfil/panel.html')

@main_bp.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    if not g.user:
        flash('Debes iniciar sesión para editar tu perfil', 'danger')
        return redirect(url_for('user.login'))

    user = g.user
    if request.method == 'POST':
        user.first_name = request.form['firstName']
        user.last_name = request.form['lastName']
        user.email = request.form['email']
        user.phone = request.form['phone']
        user.username = request.form['username']
        user.document_id = request.form['document_id']
        
        try:
            user.save()  # Guardar cambios en la base de datos
            flash('Perfil actualizado con éxito', 'success')
            session['user_id'] = user.id
            Operation.create(user=user, event_type='update_profile', description='Perfil actualizado.')
            return redirect(url_for('main.panel_user'))
        except Exception as e:
            flash('Error al actualizar el perfil: {}'.format(e), 'danger')

    return render_template('perfil/edit_profile.html', user=user)