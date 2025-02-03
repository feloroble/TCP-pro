from datetime import date
from pkgutil import get_data
from flask import render_template, request, url_for, redirect, flash, session, g, request,session,Blueprint

from app.models.facturas import Cliente, DetalleFactura, Factura, Proveedor
from app.models.inventario import Product
from app.models.tcp import TCPBusiness


from .. import login_required

facturas_venta_bp = Blueprint('ventas', __name__, template_folder='../../templates/facturas', static_folder='../../static')
facturas_copra_bp = Blueprint('compras', __name__, template_folder='../../templates/facturas', static_folder='../../static')
facturas_bp = Blueprint('facturas', __name__, template_folder='../../templates/facturas', static_folder='../../static')

# ruta principal de inicio

@facturas_bp.route('/facturas',methods = ('GET', 'POST'))
def ver_facturas_tcp():

    return render_template ("panel/panel_tcp.html")

#facutas de compras

@facturas_copra_bp.route("/crear-compra", methods=["GET", "POST"])
def crear_factura_compra():
    proveedores = Proveedor.select()
    productos = Product.select()

    if request.method == "POST":
        negocio_id = request.form.get("negocio_id")
        proveedor_id = request.form.get("proveedor_id")
        productos_seleccionados = request.form.getlist("productos[]")
        cantidades = request.form.getlist("cantidades[]")
        precios_compra = request.form.getlist("precios_compra[]")

        if not negocio_id or not proveedor_id or not productos_seleccionados:
            flash("Todos los campos son obligatorios", "danger")
            return redirect(url_for("compras.crear_factura_compra"))

        negocio = TCPBusiness.get_by_id(negocio_id)
        proveedor = Proveedor.get_by_id(proveedor_id)

        factura = Factura.create(negocio=negocio, proveedor=proveedor, fecha=date.today(), total=0)

        total_factura = 0
        for i, producto_id in enumerate(productos_seleccionados):
            producto = TCPBusiness.get_by_id(producto_id)
            cantidad = int(cantidades[i])
            precio_compra = float(precios_compra[i])

            subtotal = precio_compra * cantidad
            total_factura += subtotal

            DetalleFactura.create(factura=factura, producto=producto, cantidad=cantidad, precio_unitario=precio_compra, subtotal=subtotal)

        factura.total = total_factura
        factura.save()

        flash("Factura de compra creada con éxito", "success")
        return redirect(url_for("compra.crear_factura_compra"))

    return render_template("compras/crear_compra.html", proveedores=proveedores, productos=productos)

# facturas de ventas

@facturas_venta_bp.route("/", methods=["GET", "POST"])
def crear_factura_venta():
    clientes = Cliente.select()
    productos = Product.select()

    if request.method == "POST":
        negocio_id = request.form.get("negocio_id")
        cliente_id = request.form.get("cliente_id")
        productos_seleccionados = request.form.getlist("productos[]")
        cantidades = request.form.getlist("cantidades[]")

        if not negocio_id or not cliente_id or not productos_seleccionados:
            flash("Todos los campos son obligatorios", "danger")
            return redirect(url_for("ventas.crear_factura_venta"))

        negocio = TCPBusiness.get_by_id(negocio_id)
        cliente = Cliente.get_by_id(cliente_id)

        factura = Factura.create(negocio=negocio, cliente=cliente, fecha=date.today(), total=0)

        total_factura = 0
        for i, producto_id in enumerate(productos_seleccionados):
            producto = Product.get_by_id(producto_id)
            cantidad = int(cantidades[i])

            if producto.stock < cantidad:
                flash(f"Stock insuficiente para {producto.nombre}", "warning")
                return redirect(url_for("ventas.crear_factura_venta"))

            subtotal = producto.precio * cantidad
            total_factura += subtotal

            DetalleFactura.create(factura=factura, producto=producto, cantidad=cantidad, precio_unitario=producto.precio, subtotal=subtotal)

            # Reducir stock
            producto.stock -= cantidad
            producto.save()

        # Actualizar total de la factura
        factura.total = total_factura
        factura.save()

        flash("Factura de venta creada con éxito", "success")
        return redirect(url_for("ventas.crear_factura_venta"))

    return render_template("ventas/crear_venta.html", clientes=clientes, productos=productos)