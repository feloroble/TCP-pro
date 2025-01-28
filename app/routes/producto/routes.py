import os
from flask import  app, current_app, jsonify, render_template, request, url_for, redirect, flash, session, g, request,session,Blueprint
from app.config import ALLOWED_EXTENSIONS
from app.models.inventario import Category, Concept, CostSheet, Product, SubCategory, TCPBusiness
from peewee import fn, JOIN
from .. import login_required, user_tcp_required
from werkzeug.utils import secure_filename



producto_bp = Blueprint('producto', __name__, template_folder='../../templates/inventario', static_folder='../../static')


@producto_bp.route('/<int:product_id>', methods=['GET', 'POST'])
@login_required
@user_tcp_required
def edit_product(product_id):
    """Editar un producto."""
    product = Product.get_or_none(Product.id == product_id)
    if not product:
        flash("Producto no encontrado.", "danger")
        return redirect(url_for('inventario.index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        category_id = request.form.get('category_id')
        stock = request.form.get('stock', 0)
        um = request.form.get('um')
        tipo = request.form.get('type')
        image_url = request.form.get('image_url')  # Campo para URL remota
        image_file = request.files.get('image_file')  # Campo para archivo local
        
        # Validar nombre y categoría
        if not name or not category_id:
            flash("El nombre y la categoría son obligatorios.", "danger")
            return redirect(url_for('inventario.edit_product', product_id=product.id))

        category = Category.get_or_none(Category.id == category_id)
        if not category:
            flash("Categoría no válida.", "danger")
            return redirect(url_for('inventario.edit_product', product_id=product.id))
        
        # Manejo de imagen
        image_file = request.files.get('image_file')
        
        if image_file and allowed_file(image_file.filename):
            # Si hay imagen previa, eliminarla
            if product.image_path:
                old_image_path = os.path.join(current_app.root_path, 'static/uploads/products', product.image_path)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
            filename = secure_filename(image_file.filename)
            upload_folder = os.path.join(current_app.root_path, 'static/uploads/products')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder, exist_ok=True)
            filepath = os.path.join(upload_folder, filename)
            image_file.save(filepath)
            product.image_path = filename 
        
        # Actualizar producto
        product.name = name
        product.category = category
        product.stock = stock
        product.um = um
        product.tipo = tipo
        product.save()
        
        flash("Producto actualizado con éxito.", "success")
        return redirect(url_for('inventario.index'))
    
    # Categorías para el formulario
    categories = Category.select().where(Category.business == product.business)
    
    return render_template('edit_product.html', product=product, categories=categories)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
