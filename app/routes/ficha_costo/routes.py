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
        return redirect(url_for('product.index'))

    user = User.get_by_id(session.get('user_id'))
    if not user:
        flash('Usuario no encontrado.', 'error')
        return redirect(url_for('user.login'))

    # Comprobar si ya existe una ficha de costo para este producto
    existing_cost_sheet = CostSheet.get_or_none(CostSheet.product == product_id)

    if request.method == 'POST':
        production_level = int(request.form.get('production_level', 0))
        utilization_percentage = float(request.form.get('utilization_percentage', 0.0))
        precio_de_costo = float(request.form.get('precio_de_costo', 0.0))
        nombre_completo = f"{user.first_name} {user.last_name}"  

        if not existing_cost_sheet:
            # Crear una nueva ficha de costo
            existing_cost_sheet = CostSheet.create(
                product=product,
                business=product.business,
                user=user,
                production_level=production_level,
                utilization_percentage=utilization_percentage,
                created_by_role=user.rol,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                nombre_user=nombre_completo,
                precio_de_costo=precio_de_costo
            )
        else:
            # Actualizar ficha de costo existente
            existing_cost_sheet.production_level = production_level
            existing_cost_sheet.utilization_percentage = utilization_percentage
            existing_cost_sheet.updated_at = datetime.now()
            existing_cost_sheet.precio_de_costo = precio_de_costo
            existing_cost_sheet.save()

        # Manejo de conceptos
        concepts_data = request.form.getlist('concept[]')
        base_costs = request.form.getlist('base_cost[]')
        new_costs = request.form.getlist('new_cost[]')
        types = request.form.getlist('concept_type[]')
        concept_ids = request.form.getlist('concept_id[]')  # Para identificar conceptos existentes

        # Actualizar conceptos existentes
        for i, concept_id in enumerate(concept_ids):
            if concept_id:  # Si concept_id está presente, es un concepto existente
                Concept.update(
                    concept=concepts_data[i],
                    base_cost=float(base_costs[i]) if base_costs[i] else 0.0,
                    new_cost=float(new_costs[i]) if new_costs[i] else 0.0,
                    concept_type=types[i]
                ).where(Concept.id == concept_id).execute()
            else:
                # Crear nuevos conceptos
                Concept.create(
                    cost_sheet=existing_cost_sheet,
                    concept=concepts_data[i],
                    base_cost=float(base_costs[i]) if base_costs[i] else 0.0,
                    new_cost=float(new_costs[i]) if new_costs[i] else 0.0,
                    concept_type=types[i]
                )

        # Eliminar conceptos marcados para borrado
        for concept_id in request.form.getlist('delete_concept[]'):
            Concept.delete().where(Concept.id == concept_id).execute()

        flash('Ficha de costo guardada con éxito.', 'success')
        return redirect(url_for('ficha-costo.create_cost_sheet', product_id=product_id))

    # Para renderizar el formulario de creación o edición (GET)
    if existing_cost_sheet:
        concepts = Concept.select().where(Concept.cost_sheet == existing_cost_sheet.id)
        return render_template('costo.html', product=product, 
                               cost_sheet=existing_cost_sheet, concepts=concepts, 
                               concept_types=Concept.FORM_TYPES)
    else:
        return render_template('costo.html', product=product, concept_types=Concept.FORM_TYPES)