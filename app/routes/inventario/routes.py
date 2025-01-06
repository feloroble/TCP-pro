from pkgutil import get_data
from flask import jsonify, render_template, request, url_for, redirect, flash, session, g, request,session,Blueprint

from app.models.inventario import Category, Product, TCPBusiness


from .. import login_required, user_tcp_required



inventario_bp = Blueprint('inventario', __name__, template_folder='../../templates/inventario', static_folder='../../static')

# ruta principal de inicio

@inventario_bp.route('/',methods = ('GET', 'POST'))
@login_required
@user_tcp_required
def index():
    """Vista principal del inventario."""
    selected_business_id = session.get('negocio_id')

    if not selected_business_id:
        flash("Debes seleccionar un negocio primero.", "warning")
        return redirect(url_for('tcp.panel_tcp'))
    
    products = Product.select().where(Product.business == selected_business_id)
    business_name = TCPBusiness.get_or_none(TCPBusiness.id == selected_business_id).project_name


    categories = Category.select()
    products = Product.select().limit(10)  # Mostrar los últimos 10 productos
    return render_template('manager_inventory.html', categories=categories, products=products, business_name=business_name,business_id=selected_business_id)
   
@inventario_bp.route('/add_product', methods=['POST'])
def add_product():
    """Agregar un producto al inventario."""
    name = request.form.get('name')
    category_id = request.form.get('category_id')
    stock = request.form.get('stock', 0)
    price = request.form.get('price', 0)
    business_id = request.form.get('negocio_id')

    if not all([name, category_id, business_id]):
        flash("Todos los campos son obligatorios.", "danger")
        return redirect(url_for('inventario.index', business_id=business_id))

    category = Category.get_or_none(Category.id == category_id)
    if not category:
        flash("Categoría no válida para el negocio seleccionado.", "danger")
        return redirect(url_for('inventario.index', business_id=business_id))

    Product.create(
        name=name,
        category=category,
        business=business_id,
        user=g.user.id,
        stock=stock,
        price=price
    )
    flash("Producto agregado exitosamente.", "success")
    return redirect(url_for('inventario.index', business_id=business_id))


@inventario_bp.route('/filter_products', methods=['GET'])
def filter_products():
    category_id = request.args.get('category_id')
    type = request.args.get('type')

    query = Product.select()
    if category_id:
        query = query.where(Product.category == category_id)
    if type:
        query = query.where(Product.type == type)

    products = query.limit(10)  # Limitando a los últimos 10 resultados.
    return jsonify([
        {
            'id': product.id,
            'name': product.name,
            'category': product.category.name,
            'type': product.type,
            'sub_type': product.sub_type,
            'stock': product.stock,
            'price': float(product.price),
        }
        for product in products
    ])


@inventario_bp.route('/categories/add', methods=['POST'])
def add_category():
    name = request.form.get('name')
    description = request.form.get('description')

    if not name:
        flash('El nombre de la categoría es obligatorio.', 'danger')
        return redirect(url_for('inventario.index'))

    try:
        Category.create(name=name, description=description)
        flash('Categoría agregada con éxito.', 'success')
    except Exception as e:
        flash(f'Error al agregar la categoría: {e}', 'danger')
    return redirect(url_for('inventario.index'))