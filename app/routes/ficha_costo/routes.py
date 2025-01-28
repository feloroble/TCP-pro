from datetime import datetime
from itertools import product
from flask import  render_template, request, url_for, redirect, flash, session, g, request,session,Blueprint
from app.models.inventario import  Concept, CostSheet, Product, TCPBusiness
from app.models.user import User
from .. import login_required, user_tcp_required
from flask_wtf.csrf import generate_csrf
from peewee import DoesNotExist


ficha_bp = Blueprint('ficha-costo', __name__, template_folder='../../templates/ficha-costo', static_folder='../../static')


@ficha_bp.route('/<int:product_id>', methods=['GET', 'POST'])
@login_required
def create_cost_sheet(product_id):
    product = Product.get_or_none(Product.id == product_id)
    if not product:
        flash('El producto no existe.', 'error')
        return redirect(url_for('product.index'))  # Suponiendo que 'product.index' existe

    if request.method == 'POST':
        # Creación de la ficha de costo
        production_level = int(request.form.get('production_level', 0))
        utilization_percentage = float(request.form.get('utilization_percentage', 0.0))
        precio_de_costo = float(request.form.get('precio_de_costo', 0.0))
        user = User.get_by_id(session.get('user_id'))  # Obtener usuario de la sesión
        print(f"usuario: {user}")
        nombre_compelto = f"{user.first_name} {user.last_name}"  
        
        if not user:
            flash('Usuario no encontrado.', 'error')
            return redirect(url_for('cost_sheet.create_cost_sheet', product_id=product_id))

        cost_sheet = CostSheet.create(
            product=product,
            business=product.business,
            user=user,
            production_level=production_level,
            utilization_percentage=utilization_percentage,
            created_by_role=user.rol,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            nombre_user=nombre_compelto,
            precio_de_costo=precio_de_costo
        )

        # Crear conceptos de la ficha de costo
        concepts_data = request.form.getlist('concept[]')
        base_costs = request.form.getlist('base_cost[]')
        new_costs = request.form.getlist('new_cost[]')
        types = request.form.getlist('concept_type[]')

        for i, concept in enumerate(concepts_data):
            Concept.create(
                cost_sheet=cost_sheet,
                concept=concept,
                row=i+1,  # Asumiendo que la fila empieza en 1
                base_cost=float(base_costs[i]) if base_costs[i] else 0.0,
                new_cost=float(new_costs[i]) if new_costs[i] else 0.0,
                concept_type=types[i]
            )

        flash('Ficha de costo creada con éxito.', 'success')
        return redirect(url_for('ficha-costo.view_cost_sheet', cost_sheet_id=cost_sheet.id))

    # Para renderizar el formulario de creación (GET)
    return render_template('costo.html', product=product)

@ficha_bp.route('/cost-sheet/<int:product_id>')
@login_required
def view_cost_sheet(product_id):
    cost_sheet = CostSheet.get(CostSheet.product == product_id)
    if not cost_sheet:
        flash('La ficha de costo no existe.', 'error')
        return redirect(url_for('inventario.index'))  # O asumiendo que existe alguna ruta de productos

    concepts = Concept.select().where(Concept.cost_sheet == product_id).order_by(Concept.row)
    return render_template('ver_ficha.html', cost_sheet=cost_sheet, concepts=concepts)