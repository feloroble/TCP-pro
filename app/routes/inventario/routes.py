from flask import  app, render_template, request, url_for, redirect, flash, session, g, request,session,Blueprint
from app.models.inventario import Category, Concept, CostSheet, Product, TCPBusiness
from peewee import fn, JOIN
from .. import login_required, user_tcp_required



inventario_bp = Blueprint('inventario', __name__, template_folder='../../templates/inventario', static_folder='../../static')

# ruta principal de inicio

@inventario_bp.route('/', methods=('GET', 'POST'))
@login_required
@user_tcp_required
def index():
    """Vista principal del inventario."""
    selected_business_id = session.get('negocio_id')

    if not selected_business_id:
        flash("Debes seleccionar un negocio primero.", "warning")
        return redirect(url_for('tcp.panel_tcp'))

    # Verificar que el negocio exista
    try:
        business = TCPBusiness.get_by_id(selected_business_id)
    except TCPBusiness.DoesNotExist:
        flash("El negocio seleccionado no existe.", "danger")
        return redirect(url_for('tcp.panel_tcp'))

    # Obtener productos del negocio seleccionado con categorías
    products = (
        Product.select(Product, Category.name.alias('category_name'))
        .join(Category, JOIN.LEFT_OUTER)
        .where(Product.business_id == selected_business_id)
    )

    # Obtener categorías con conteo de productos
    categories = (
        Category.select(Category, fn.COUNT(Product.id).alias('product_count'))
        .join(Product, JOIN.LEFT_OUTER, on=(Category.id == Product.category_id))
        .where(Category.business_id == selected_business_id)
        .group_by(Category.id)
    )

    # Obtener conceptos asociados a las fichas de costo del negocio
    def obtener_conceptos_por_negocio(business_id):
        try:
            productos = Product.select().where(Product.business_id == business_id)
            conceptos = (
                Concept.select(Concept, CostSheet, Product)
                .join(CostSheet, on=(Concept.cost_sheet == CostSheet.id))
                .join(Product, on=(CostSheet.product == Product.id))
                .where(CostSheet.product.in_(productos))
                .order_by(Product.id, Concept.id)
            )
            return conceptos
        except Exception as e:
            app.logger.error(f"Error al obtener los conceptos: {e}")
            return []

    conceptos = obtener_conceptos_por_negocio(selected_business_id)

    # Filtros
    product_name = request.args.get('product_name', '').strip()
    category_id = request.args.get('category_id', type=int)
    product_type = request.args.get('product_type', '').strip()

    query = Product.select().where(Product.business_id == selected_business_id).prefetch(CostSheet)

    if product_name:
        query = query.where(Product.name.contains(product_name))

    if category_id:
        query = query.where(Product.category == category_id)

    if product_type:
        query = query.where(Product.tipo == product_type)

    products = query
    print(products)

    if len(products) == 0:
        flash("No hay productos asociados a este negocio.", "info")

    # Preparar datos para la plantilla
    return render_template(
        'manager_inventory.html',
        conceptos=conceptos,
        nombre_completo=session.get('nombre_completo'),
        cargo=session.get('cargo'),
        categories=categories,
        products=products,
        business_name=business.project_name,
        business_id=selected_business_id,
        selected_filters={
            'product_name': product_name,
            'category_id': category_id,
            'product_type': product_type,
        },
    )


@inventario_bp.route('/add_product', methods=['POST'])
@login_required
@user_tcp_required
def add_product():
    """Agregar un producto al inventario."""
    name = request.form.get('name')
    category_id = request.form.get('category_id')
    stock = request.form.get('stock', 0)
    price = request.form.get('price', 0)
    um = request.form.get('um')
    typo = request.form.get('type')
    business_id = request.form.get('business_id')
    user_id = g.user.id 

    if not all([name, category_id, business_id]):
        flash("Todos los campos son obligatorios.", "danger")
        return redirect(url_for('inventario.index', business_id=business_id))
    
    category = Category.get_or_none(Category.id == category_id)
    if not category:
        flash("Categoría no válida para el negocio seleccionado.", "danger")
        return redirect(url_for('inventario.index', business_id=business_id))
    
    existing_product = Product.get_or_none(
        Product.name == name,
        Product.business == business_id
    )

    if existing_product:
        flash("Ya existe un producto con este nombre en este negocio.", "danger")
        return redirect(url_for('inventario.index'))
    
     # Generar el código único para el producto
    product_code = Product.generate_product_code(business_id, user_id)
    
    Product.create(
            name=name,
            category=category,
            business=business_id,
            user=g.user.id,
            stock=stock,
            price=price,
            tipo=typo,
            um=um,
            created_by=user_id,
            code=product_code
            )
            
    flash("Producto agregado exitosamente.", "success")
    return redirect(url_for('inventario.index', business_id=business_id))
    
@inventario_bp.route('/categories/add', methods=['POST'])
@login_required
@user_tcp_required
def add_category():
    """Agregar una nueva categoría al negocio actual."""
    # Obtener datos del formulario
    name = request.form.get('name')
    description = request.form.get('desc')

    # Obtener el negocio actual
    selected_business_id = session.get('negocio_id')

    if not selected_business_id:
        flash('Debes seleccionar un negocio primero.', 'warning')
        return redirect(url_for('tcp.panel_tcp'))

    if not name:
        flash('El nombre de la categoría es obligatorio.', 'danger')
        return redirect(url_for('inventario.index'))

    try:
        # Verificar que el negocio exista
        business = TCPBusiness.get_by_id(selected_business_id)
        if not business:
            flash('El negocio seleccionado no existe.', 'danger')
            return redirect(url_for('tcp.panel_tcp'))

        # Validar unicidad del nombre de la categoría dentro del negocio
        existing_category = Category.get_or_none(
            (Category.name == name) & (Category.business == business.id)
        )
        if existing_category:
            flash('Ya existe una categoría con este nombre en el negocio.', 'warning')
            return redirect(url_for('inventario.index'))

        # Crear la nueva categoría asociada al negocio
        Category.create(name=name, description=description, business=business)
        flash('Categoría agregada con éxito.', 'success')
    except Exception as e:
        flash(f'Error al agregar la categoría: {str(e)}', 'danger')

    return redirect(url_for('inventario.index'))
   
@inventario_bp.route('/edit_product', methods=['POST'])
@login_required
@user_tcp_required
def edit_product():
    product_id = request.form.get('product_id')
    product = Product.get_by_id(product_id)
    product.name = request.form.get('name')
    product.price = request.form.get('price')
    product.stock = request.form.get('stock')
    product.save()
    return redirect(url_for('inventario.index', business_id=product.business.id))

@inventario_bp.route('/delete_product/<int:product_id>' , methods=['POST'])
@login_required
@user_tcp_required
def delete_product(product_id):
    if request.method == 'GET':
        flash("Usa un formulario con método POST para eliminar productos.", "danger")
        return redirect(url_for('inventario.index'))

    try:
        product = Product.get(Product.id == product_id)
        product.delete_instance()
        flash("Producto eliminado con éxito.", "success")
    except Exception as e:
        flash(f"Error al intentar eliminar el producto: {str(e)}", "danger")
    return redirect(url_for('inventario.index'))
    

  



