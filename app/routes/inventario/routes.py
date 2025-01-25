from flask import  render_template, request, url_for, redirect, flash, session, g, request,session,Blueprint
from app.models.inventario import Category, Concept, CostSheet, Product, TCPBusiness
from peewee import fn, JOIN
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
    
    # Verificar que el negocio exista
    
    business = TCPBusiness.get_by_id(selected_business_id)
    if not business:
        flash("El negocio seleccionado no existe.", "danger")
        return redirect(url_for('tcp.panel_tcp'))
    
    # Obtener productos del negocio seleccionado
    products = (Product
                .select(Product, Category.name.alias('category_name'))
                .join(Category, JOIN.LEFT_OUTER)
                .where(Product.business_id == selected_business_id))

    # Obtener categorías con conteo de productos
    categories = (Category
                  .select(Category, fn.COUNT(Product.id).alias('product_count'))
                  .join(Product, JOIN.LEFT_OUTER, on=(Category.id == Product.category_id))
                  .group_by(Category.id))
    
    def obtener_conceptos_por_negocio(business_id):
        try:
        # Obtiene todos los productos del negocio seleccionado
            productos = Product.select().where(Product.business_id == business_id)

        # Obtiene todas las fichas de costo asociadas a los productos del negocio
            fichas_costo = CostSheet.select().where(CostSheet.product.in_(productos))

        # Obtiene todos los conceptos asociados a esas fichas de costo
            conceptos = (
               Concept.select(Concept, CostSheet, Product)
              .join(CostSheet, on=(Concept.cost_sheet == CostSheet.id))
              .join(Product, on=(CostSheet.product == Product.id))
              .where(CostSheet.product.in_(productos))
              .order_by(Product.id, Concept.id)
           )

        # Retorna la lista de conceptos
            return conceptos

        except Exception as e:
            print(f"Error al obtener los conceptos: {e}")
            return []

    conceptos = obtener_conceptos_por_negocio(selected_business_id)

    for produ in products:
        productooo =  produ.id
    print(productooo)


    for concepto in conceptos:
       print(f"Producto: {concepto.cost_sheet.product.name}")
       print(f"Descripción: {concepto.concept}")
       print(f"Cantidad: {concepto.row}")
       print(f"Costo Unitario: {concepto.base_cost}")
       print(f"Costo Total: {concepto.new_cost}")
       print("-" * 40)
   
    cargo = session.get('cargo')
    nombre_complet = session.get('nombre_completo')
   
   
   
    # Obtener filtros de la solicitud
    product_name = request.args.get('product_name', '').strip()
    category_id = request.args.get('category_id', type=int)
    product_type = request.args.get('product_type', '').strip()
     # Obtener productos del negocio
    query  = Product.select().where(Product.business_id == selected_business_id).prefetch(CostSheet)
    
    # Aplicar filtro por nombre
    if product_name:
        query = query.where(Product.name.contains(product_name))

    # Aplicar filtro por categoría
    if category_id:
        query = query.where(Product.category == category_id)

    # Aplicar filtro por tipo de producto
    if product_type:
        query = query.where(Product.tipo == product_type)
    # Obtener resultados finales
    products = query
    
    if not products:
        flash("No hay productos asociados a este negocio.", "info")
    
    
    
    print(f"Negocio ID seleccionado: {selected_business_id}")
    print(f"Productos encontrados: {[p.id for p in products]}")
    print(f"Nombre del negocio: {business.project_name}")

    print(f"Producto nombre: {product_name}")
    print(f"Producto categoria ID : {category_id}")
    print(f"Producto typo: {product_type}")

    

    return render_template(
        'manager_inventory.html',
        coseptos=conceptos,
        nombre_completo=nombre_complet,
        cargo=cargo, 
        categories=categories,
        products=products, 
        prod = productooo,
        business_name=business.project_name,
        business_id=selected_business_id,
        selected_filters={
            'product_name': product_name,
            'category_id': category_id,
            'product_type': product_type
        }
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
def add_category():
    name = request.form.get('name')
    description = request.form.get('desc')

    if not name:
        flash('El nombre de la categoría es obligatorio.', 'danger')
        return redirect(url_for('inventario.index'))

    try:
        Category.create(name=name, description=description)
        flash('Categoría agregada con éxito.', 'success')
    except Exception as e:
        flash(f'Error al agregar la categoría: {e}', 'danger')
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
    

  



