from datetime import datetime
from flask import  render_template, request, url_for, redirect, flash, session, g, request,session,Blueprint
from app.models.inventario import  Concept, CostSheet, Product, TCPBusiness
from .. import login_required, user_tcp_required
from flask_wtf.csrf import generate_csrf
from peewee import DoesNotExist


ficha_bp = Blueprint('ficha-costo', __name__, template_folder='../../templates/ficha-costo', static_folder='../../static')


@ficha_bp.route('/<int:product_id>', methods=['GET', 'POST'])
@login_required
def manage_cost_sheet(product_id):
    # Obtener el producto
    product = Product.get_or_none(Product.id == product_id)
    if not product:
        flash("Producto no encontrado.", "danger")
        return redirect(url_for('inventario.index'))

    # Obtener la ficha de costo asociada
    cost_sheet = CostSheet.get_or_none(CostSheet.product == product)
    if not cost_sheet:
        # Si no existe, crear una nueva ficha de costo
        try:
            business = TCPBusiness.get(TCPBusiness.id == session.get('negocio_id'))
        except DoesNotExist:
            flash("Negocio no encontrado para el usuario.", "danger")
            return redirect(url_for('inventario.index'))

        cost_sheet = CostSheet.create(
            product=product,
            business=business,
            sequence_number=CostSheet.generate_sequence_number(business.id),
            code=f"COST-{business.id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            unit_of_measure=product.um,
            production_level=0,
            utilization_percentage=0.0,
            created_by_role="Administrador",
            nombre_user=session.get('user_name', 'Desconocido'),
            precio_de_costo=0.0
        )

    if request.method == 'POST':
        form_type = request.form.get('form_type')

        # Manejo de formulario de opciones generales
        if form_type == 'general_options':
            cost_sheet.production_level = int(request.form.get('production_level', cost_sheet.production_level))
            cost_sheet.utilization_percentage = float(request.form.get('utilization_percentage', cost_sheet.utilization_percentage))
            cost_sheet.save()
            flash("Opciones generales actualizadas correctamente.", "success")

        # Manejo de formulario de gastos directos
        elif form_type == 'direct_costs':
            handle_concepts(request, cost_sheet, is_direct=True)
            flash("Gastos directos actualizados correctamente.", "success")

        # Manejo de formulario de gastos indirectos
        elif form_type == 'indirect_costs':
            handle_concepts(request, cost_sheet, is_direct=False)
            flash("Gastos indirectos actualizados correctamente.", "success")

        return redirect(url_for('ficha-costo.manage_cost_sheet', product_id=product.id))

    # Cargar conceptos directos e indirectos
    direct_concepts = Concept.select().where(Concept.cost_sheet == cost_sheet, Concept.concept_type == 'direct')
    indirect_concepts = Concept.select().where(Concept.cost_sheet == cost_sheet, Concept.concept_type == 'indirect')

    return render_template(
        'costo.html',
        product=product,
        cost_sheet=cost_sheet,
        direct_concepts=direct_concepts,
        indirect_concepts=indirect_concepts
    )


@ficha_bp.route('/delete_concept/<int:concept_id>', methods=['POST'])
def delete_concept(concept_id):
    # Eliminar concepto por ID
    concept = Concept.get_or_none(Concept.id == concept_id)
    if concept:
        concept.delete_instance()
        flash("Concepto eliminado correctamente.", "success")
    else:
        flash("Concepto no encontrado.", "danger")

    return redirect(request.referrer or url_for('inventario.index'))


def handle_concepts(request, cost_sheet, concept_type):
    """Procesar conceptos directos o indirectos según el formulario recibido."""
    concepts = request.form.getlist('concept[]')
    rows = request.form.getlist('row[]')
    base_costs = request.form.getlist('base_cost[]')
    new_costs = request.form.getlist('new_cost[]')
    concept_ids = request.form.getlist('concept_id[]')

    for idx, concept_name in enumerate(concepts):
        if concept_name.strip():  # Solo procesar conceptos no vacíos
            try:
                # Obtener datos de cada fila con validación del índice
                row = int(rows[idx]) if idx < len(rows) else None
                base_cost = float(base_costs[idx]) if idx < len(base_costs) else 0.0
                new_cost = float(new_costs[idx]) if idx < len(new_costs) else 0.0
                concept_id = concept_ids[idx] if idx < len(concept_ids) else None

                if concept_id:  # Actualizar si existe
                    concept = Concept.get_or_none(Concept.id == concept_id)
                    if concept:
                        concept.concept = concept_name
                        concept.row = row
                        concept.base_cost = base_cost
                        concept.new_cost = new_cost
                        concept.concept_type = concept_type  # Asegurar tipo
                        concept.save()
                else:  # Crear nuevo
                    Concept.create(
                        cost_sheet=cost_sheet,
                        concept=concept_name,
                        row=row,
                        base_cost=base_cost,
                        new_cost=new_cost,
                        concept_type=concept_type
                    )
            except IndexError:
                flash("Error al procesar los datos del formulario. Por favor, intenta nuevamente.", "danger")
                continue