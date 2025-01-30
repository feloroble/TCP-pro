from decimal import Decimal
from flask import Blueprint, flash, redirect, render_template, request, url_for
from datetime import date

from app.models.user import User
from app.models.tcp import ServiceTariff, TCPBusiness
# Asegúrate de importar tu nuevo modelo
from .. import login_required, admin_required

detalle_bp = Blueprint('detalles', __name__, template_folder='../../templates/user', static_folder='../../static')

@detalle_bp.route('/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def user_details(user_id):
    user = User.get_or_none(User.id == user_id)
    if not user:
        flash("El usuario especificado no existe.", "danger")
        return redirect(url_for('user.admin_panel'))

    businesses = user.tcp_businesses  # Assuming 'businesses' is the backref name for the relationship
    
    if request.method == 'POST':
        for business in businesses:
            new_price = request.form.get(f'price_{business.id}')
            if new_price:
                try:
                    new_price = Decimal(new_price)
                    # Buscar la última tarifa activa para este negocio
                    current_tariff = ServiceTariff.select().where(
                        (ServiceTariff.business == business) & 
                        (ServiceTariff.end_date.is_null() | (ServiceTariff.end_date >= date.today()))
                    ).order_by(ServiceTariff.start_date.desc()).first()
                    
                    if current_tariff:
                        # Actualizar la tarifa existente
                        current_tariff.price = new_price
                        current_tariff.save()
                        flash(f'Tarifa actualizada para {business.project_name}.', 'success')
                    else:
                        # Si no hay tarifa activa, crear una nueva (esto puede ser opcional dependiendo de tu lógica de negocio)
                        ServiceTariff.create(business=business, price=new_price, start_date=date.today())
                        flash(f'Nueva tarifa creada para {business.project_name}.', 'success')
                except ValueError:
                    flash(f'El precio para {business.project_name} debe ser un número válido.', 'error')
        return redirect(url_for('detalles.user_details', user_id=user_id))

    # Cálculo del total a pagar
    total_amount_to_pay = sum(tariff.price for business in businesses for tariff in business.tariffs if tariff.end_date is None or tariff.end_date >= date.today())
    
    # Datos para la plantilla
    user_details = {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
        "email": user.email,
        "phone": user.phone,
        "rol": user.rol,
        "license_duration": user.license_duration,
        "license_expiry": user.license_expiry,
        "days_remaining": user.days_remaining() if hasattr(user, 'days_remaining') else None,
        "business_count": len(businesses),
        "amount_to_pay": total_amount_to_pay,
        "amount_message": f"${total_amount_to_pay:.2f}" if businesses else "No hay negocios asociados a este usuario."
    }

    return render_template('admin/user_details.html', user=user_details, businesses=businesses)