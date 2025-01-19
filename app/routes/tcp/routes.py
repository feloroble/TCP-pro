from datetime import datetime
from flask import jsonify, render_template, request, url_for, redirect, flash, session, g, request,session,Blueprint
from app.email_service import send_email
from app.models.tcp import TCPBusiness
from app.models.user import Operation, User

from .. import login_required, user_tcp_required



tcp_bp = Blueprint('tcp', __name__, template_folder='../../templates/tcp', static_folder='../../static')

# ruta principal de inicio

@tcp_bp.route('/panel-TCP',methods = ('GET', 'POST'))
@login_required
@user_tcp_required
def panel_tcp():
    negocio_id = session.get('negocio_id')

    if request.method == 'POST':
        # Selección de negocio
        negocio_id = request.form.get('negocio_id')
        if negocio_id:
            
            nombre_negoco = TCPBusiness.select().where(TCPBusiness.id == negocio_id)

            for nomb_tcp in nombre_negoco:
                nombre = nomb_tcp.project_name 
                
            flash(f"Negocio {nombre } seleccionado correctamente.", "success")
        else:
            flash('No tienes permiso para acceder a este negocio.', 'danger')

        return redirect(url_for('tcp.panel_tcp'))
    
    user = g.user # Obtén el usuario actual
    if user.rol == "usuario TCP" and user.license_expiry:
        days_left = (user.license_expiry - datetime.now()).days
        if 0 < days_left <= 7:
            
            
            
            flash(f"Tu licencia expira en {days_left} días. ¡Renueva pronto!", "warning")

    # Diccionario de eventos
    EVENT_TYPES_DICT = {
        'login': 'Inicio de sesión',
        'update_profile': 'Actualización de perfil',
        'update_type_user': 'Cambio de tipo de usuario en el sistema',
        'logout': 'Cierre de sesión',
        'rest_password': 'Restablecimiento de contraseña',
    }
    
   # Carga el negocio actualmente seleccionado
    negocio_tcp = None
    if negocio_id:
        negocio_tcp = TCPBusiness.get_or_none(TCPBusiness.id == negocio_id, TCPBusiness.user == g.user.id)

    # Manejo de filtro de actividades
    event_filter = request.args.get('event_filter', 'all')  # 'all' es el valor por defecto
    query = Operation.select().where(Operation.user == g.user.id)

    if event_filter != 'all':
        query = query.where(Operation.event_type == event_filter)

    operations = query.order_by(Operation.created_at.desc())

    # Mapea los eventos
    operations_with_names = [
        {
            "event_name": EVENT_TYPES_DICT.get(op.event_type, "Evento desconocido"),
            "description": op.description,
            "created_at": op.created_at,
        }
        for op in operations
    ]
    


    return render_template ("panel/panel_tcp.html",negocio_tcp =negocio_tcp, negocios=g.negocios,operations=operations_with_names, filter_selected=event_filter)



@tcp_bp.before_request
def load_user_negocios():
    # Carga los negocios del usuario actual
    if g.user:
        g.negocios = TCPBusiness.select().where(TCPBusiness.user_id == g.user.id)




@tcp_bp.route('/create', methods=['GET', 'POST'])
@user_tcp_required
@login_required
def create_tcp_business():
    if request.method == 'POST':
        # Obtener datos del formulario
        project_name = request.form.get('project_name')
        description = request.form.get('description')
        main_activity = request.form.get('main_activity')
        is_registered_in_conservation_zone = bool(request.form.get('is_registered_in_conservation_zone'))
        has_bank_account = bool(request.form.get('has_bank_account'))
        payment_method = request.form.get('payment_method')
        bank_type = request.form.get('bank_type')
        fiscal_bank_branch = request.form.get('fiscal_bank_branch')
        has_transportation = bool(request.form.get('has_transportation'))
        does_ecommerce = bool(request.form.get('does_ecommerce'))
        location = request.form.get('location')
        residential_commercial_area = bool(request.form.get('residential_commercial_area'))
        music_service = bool(request.form.get('music_service'))
        operation_hours = request.form.get('operation_hours')
        nic = request.form.get('nic')
        business_address = request.form.get('business_address')

        # Crear una nueva entrada de TCPBusiness asociada al usuario autenticado
        tcp_business = TCPBusiness(
            project_name=project_name,
            description=description,
            main_activity=main_activity,
            is_registered_in_conservation_zone=is_registered_in_conservation_zone,
            has_bank_account=has_bank_account,
            payment_method=payment_method,
            bank_type=bank_type,
            fiscal_bank_branch=fiscal_bank_branch,
            has_transportation=has_transportation,
            does_ecommerce=does_ecommerce,
            location=location,
            residential_commercial_area=residential_commercial_area,
            music_service=music_service,
            operation_hours=operation_hours,
            nic=nic,
            business_address=business_address,
            user_id=g.user  # Asociación con el usuario autenticado
        )

        # Guardar en la base de datos
        try:
            tcp_business.save()
            flash("Negocio TCP creado exitosamente", "success")
            return redirect(url_for('tcp.view_tcp_business'))
        except Exception as e:
            flash(f"Hubo un error al crear el negocio: {str(e)}", "danger")
            return redirect(url_for('tcp.create_tcp_business'))

    return render_template('tcp/create_tcp_business.html')

@tcp_bp.before_request
def set_selected_business():
    selected_business_id = session.get('selected_business_id')
    if selected_business_id:
        try:
            g.selected_business = TCPBusiness.get(TCPBusiness.id == selected_business_id)
        except TCPBusiness.DoesNotExist:
            g.selected_business = None
    else:
        g.selected_business = None


## vista de selcion de negocio para selecionar
@tcp_bp.route('/select', methods=['POST'])
def select_business():
    business_id = request.form.get('business_id')
    try:
        # Validar que el negocio pertenece al usuario autenticado
        business = TCPBusiness.get(TCPBusiness.id == business_id, TCPBusiness.user_id == g.user)
        session['selected_business_id'] = business.id
        session['selected_business_name'] = business.name
        return jsonify({"success": True, "message": f"Negocio '{business.name}' seleccionado"})
    except TCPBusiness.DoesNotExist:
        return jsonify({"success": False, "message": "Negocio no encontrado o no autorizado"}), 404

