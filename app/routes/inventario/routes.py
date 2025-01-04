from pkgutil import get_data
from flask import jsonify, render_template, request, url_for, redirect, flash, session, g, request,session,Blueprint

from app.models.inventario import Category, Product


from .. import login_required



inventario_bp = Blueprint('inventario', __name__, template_folder='../../templates/inventario', static_folder='../../static')

# ruta principal de inicio

@inventario_bp.route('/',methods = ('GET', 'POST'))
def index():
    categories = Category.select()
    products = Product.select().limit(10)  # Mostrar los últimos 10 productos
    return render_template('manager_inventory.html', categories=categories, products=products)
   
@inventario_bp.route('/add_product', methods=['POST'])
def add_product():
    name = request.form.get('name')
    category_id = request.form.get('category')
    type = request.form.get('type')
    sub_type = request.form.get('sub_type')
    stock = request.form.get('stock', 0, type=int)
    price = request.form.get('price', 0.00, type=float)

    if not name or not category_id or not type:
        flash('Todos los campos obligatorios deben ser completados.', 'danger')
        return redirect(url_for('inventario.index'))

    try:
        category = Category.get_by_id(category_id)
        Product.create(
            name=name,
            category=category,
            type=type,
            sub_type=sub_type,
            stock=stock,
            price=price
        )
        flash('Producto agregado con éxito.', 'success')
    except Exception as e:
        flash(f'Error al agregar el producto: {e}', 'danger')
    return redirect(url_for('inventario.index'))

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