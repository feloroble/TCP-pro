from pkgutil import get_data
from flask import render_template, request, url_for, redirect, flash, session, g, request,session,Blueprint

from app.models.tcp import TCPBusiness
from app.models.user import Operation
from .. import login_required, user_tcp_required



tcp_bp = Blueprint('tcp', __name__, template_folder='../../templates/tcp', static_folder='../../static')

# ruta principal de inicio

@tcp_bp.route('/panel-TCP',methods = ('GET', 'POST'))
def panel_tcp():
    if g.user is None:
        return redirect(url_for('user.login'))
    negocio_tcp = TCPBusiness.get_or_none(TCPBusiness.user == g.user)

    return render_template ("panel/panel_tcp.html",negocio_tcp =negocio_tcp)

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
            user=g.user  # Asociación con el usuario autenticado
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