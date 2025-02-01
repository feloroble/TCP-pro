from datetime import datetime
from itertools import product
from flask import  render_template, request, url_for, redirect, flash, session, g, request,session,Blueprint
from app.models.inventario import  Concept, CostSheet, Product, TCPBusiness
from app.models.user import User
from .. import login_required, user_tcp_required
from flask_wtf.csrf import generate_csrf
from peewee import *

ver_ficha_dp = Blueprint('ver-ficha', __name__, template_folder='../../templates/ficha-costo', static_folder='../../static')
ficha_bp = Blueprint('ficha-costo', __name__, template_folder='../../templates/ficha-costo', static_folder='../../static')



@ficha_bp.route('/<int:product_id>', methods=['GET', 'POST'])
@login_required
def create_cost_sheet(product_id):
    # Obtener el producto y usuario
    product = Product.get_or_none(Product.id == product_id)
    user = User.get_or_none(User.id == session.get('user_id'))

    # Verificar si ya existe una ficha de costo para este producto
    existing_cost_sheet = CostSheet.get_or_none(CostSheet.product == product_id)

    if request.method == 'POST':
        action = request.form.get('action')  # Acción enviada desde el formulario

        # Guardar datos generales de la ficha de costo
        if action in ['save', 'delete']:
            production_level = int(request.form.get('production_level', 0))
            utilization_percentage = float(request.form.get('utilization_percentage', 0.0))
            precio_de_costo = float(request.form.get('precio_de_costo', 0.0))

            if not existing_cost_sheet:
                existing_cost_sheet = CostSheet.create(
                    product=product,
                    business=product.business,
                    user=user,
                    production_level=production_level,
                    utilization_percentage=utilization_percentage,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    precio_de_costo=precio_de_costo
                )
            else:
                existing_cost_sheet.production_level = production_level
                existing_cost_sheet.utilization_percentage = utilization_percentage
                existing_cost_sheet.updated_at = datetime.now()
                existing_cost_sheet.precio_de_costo = precio_de_costo
                existing_cost_sheet.save()

        # Eliminar conceptos seleccionados
        if action == 'delete':
            delete_concepts = request.form.getlist('delete_concept[]')
            for concept_id in delete_concepts:
                try:
                    concept = Concept.get_by_id(concept_id)
                    concept.delete_instance()
                    flash(f'Concepto con ID {concept_id} eliminado.', 'success')
                except DoesNotExist:
                    flash(f'El concepto con ID {concept_id} no existe.', 'warning')

        # Agregar o editar un concepto
        elif action == 'add_concept':
            concept_id = request.form.get('concept_id')  # ID del concepto (vacío si es nuevo)
            concept_name = request.form.get('concept')
            base_cost = float(request.form.get('base_cost'))
            new_cost = float(request.form.get('new_cost'))
            concept_type = request.form.get('concept_type')

            try:
                if concept_id:  # Editar concepto existente
                    concept = Concept.get_by_id(concept_id)
                    concept.concept = concept_name
                    concept.base_cost = base_cost
                    concept.new_cost = new_cost
                    concept.concept_type = concept_type
                    concept.save()
                    flash('Concepto actualizado exitosamente.', 'success')
                else:  # Crear nuevo concepto
                    Concept.create(
                        cost_sheet=existing_cost_sheet,
                        concept=concept_name,
                        base_cost=base_cost,
                        new_cost=new_cost,
                        concept_type=concept_type
                    )
                    flash('Concepto agregado exitosamente.', 'success')
            except Exception as e:
                flash(f'Error al procesar el concepto: {str(e)}', 'error')

        return redirect(url_for('ficha-costo.create_cost_sheet', product_id=product_id))

    # Renderizar formulario (GET)
    if existing_cost_sheet:
        concepts = Concept.select().where(Concept.cost_sheet == existing_cost_sheet.id)
        return render_template('costo.html', product=product, 
                               cost_sheet=existing_cost_sheet, concepts=concepts, 
                               concept_types=Concept.FORM_TYPES)
    else:
        return render_template('costo.html', product=product, concept_types=Concept.FORM_TYPES)
    
@ver_ficha_dp.route('/<int:product_id>', methods=['GET'])
@login_required
def view_cost_sheet(product_id):
    # Buscamos la ficha de costo asociada al producto
    cost_sheet = CostSheet.get_or_none(CostSheet.product == product_id)
    
    if not cost_sheet:
        flash('La ficha de costo no existe para este producto.', 'error')
        return redirect(url_for('product.index'))  # O redirige a donde sea apropiado

    # Obtener todos los conceptos de esta ficha de costo ordenados por fila
    concepts = Concept.select().where(Concept.cost_sheet == cost_sheet.id).order_by(Concept.row)

    # Preparar datos para las sumas
    sum_1_4 = Concept.calculate_sum(cost_sheet.id, 1, 4)
    sum_6_10 = Concept.calculate_sum(cost_sheet.id, 6, 10)
    sum_1_10 = Concept.calculate_sum(cost_sheet.id, 1, 10)

    # Aquí podrías incluir más lógica para calcular otros valores si es necesario

    return render_template('ver_ficha.html', 
                           cost_sheet=cost_sheet, 
                           concepts=concepts, 
                           sum_1_4=sum_1_4, 
                           sum_6_10=sum_6_10, 
                           sum_1_10=sum_1_10)    