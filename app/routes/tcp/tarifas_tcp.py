
from datetime import date
from decimal import Decimal
from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.models.tcp import ServiceTariff

from .. import login_required, admin_required

tarifas_bp = Blueprint('tarifas', __name__, template_folder='../../templates/tcp', static_folder='../../static')

@tarifas_bp.route('/nueva', methods=['GET', 'POST'])
@login_required
@admin_required
def new_tariff():
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        if name and price:
            try:
                price = Decimal(price)
                ServiceTariff.create(name=name, price=price, start_date=date.today())
                flash('Nueva tarifa creada con éxito!', 'success')
                return redirect(url_for('admin.list_tariffs'))
            except ValueError:
                flash('El precio debe ser un número válido.', 'error')
        else:
            flash('Por favor, complete todos los campos.', 'error')
    
    return render_template('new_tariff.html')

