from datetime import datetime
import enum
from peewee import *
from app.models.inventario import Product
from app.models.user import User
from app.models.tcp import TCPBusiness
from app.database import BaseModel

class TipoCuenta:
    """ Definición de Tipos de Cuenta """
    ACTIVO = 'activo'
    PASIVO = 'pasivo'
    PATRIMONIO = 'patrimonio'
    INGRESOS = 'ingresos'
    GASTOS = 'gastos'

class Cuenta(BaseModel):
    """ Plan de cuentas contable asociado a un negocio """
    negocio = ForeignKeyField(TCPBusiness, backref="cuentas")  # Cada negocio tiene su propio plan de cuentas
    codigo = CharField(max_length=20)  # Código único dentro del negocio
    nombre = CharField(max_length=100)
    tipo = CharField(max_length=20, choices=[(t, t) for t in TipoCuenta.__dict__.values() if isinstance(t, str)])
    descripcion = TextField(null=True)
    cuenta_padre = ForeignKeyField('self', null=True, backref='subcuentas')  # Estructura jerárquica
    
    class Meta:
        indexes = ((('negocio', 'codigo'), True),)  # Evita duplicados de código dentro de un negocio
        
class TipoComprobante:
    """ Tipos de Comprobante """
    INGRESO = 'ingreso'
    EGRESO = 'egreso'
    AJUSTE = 'ajuste'
    OTRO = 'otro'

class Comprobante(BaseModel):
    """ Representa un asiento contable en el libro diario """
    negocio = ForeignKeyField(TCPBusiness, backref="comprobantes")
    fecha = DateTimeField(default=datetime.now)
    tipo = CharField(max_length=20, choices=[(t, t) for t in TipoComprobante.__dict__.values() if isinstance(t, str)])
    descripcion = TextField()

class ComprobanteDetalle(BaseModel):
    """ Detalle de cada asiento en el comprobante """
    comprobante = ForeignKeyField(Comprobante, backref="detalles")
    cuenta = ForeignKeyField(Cuenta, backref="movimientos")  # Cuenta contable afectada
    debe = DecimalField(default=0, max_digits=12, decimal_places=2)
    haber = DecimalField(default=0, max_digits=12, decimal_places=2)
    
class Factura(BaseModel):
    """ Modelo base para facturación (compra/venta) """
    negocio = ForeignKeyField(TCPBusiness, backref="facturas")
    fecha = DateTimeField(default=datetime.now)
    total = DecimalField(default=0, max_digits=12, decimal_places=2)

class Cliente(BaseModel):
    """ Modelo de cliente (para ventas) """
    negocio = ForeignKeyField(TCPBusiness, backref="clientes")
    nombre = CharField(max_length=100)
    email = CharField(null=True, max_length=100)

class Proveedor(BaseModel):
    """ Modelo de proveedor (para compras) """
    negocio = ForeignKeyField(TCPBusiness, backref="proveedores")
    nombre = CharField(max_length=100)
    contacto = CharField(null=True, max_length=100)

class Venta(Factura):
    """ Factura de Venta asociada a un cliente """
    cliente = ForeignKeyField(Cliente, backref="ventas")

class Compra(Factura):
    """ Factura de Compra asociada a un proveedor """
    proveedor = ForeignKeyField(Proveedor, backref="compras")



class DetalleFactura(BaseModel):
    """ Detalle de productos en una factura """
    factura = ForeignKeyField(Factura, backref="detalles")
    producto = ForeignKeyField(Product, backref="facturas")
    cantidad = IntegerField(default=1)
    precio_unitario = DecimalField(max_digits=10, decimal_places=2)
    subtotal = DecimalField(max_digits=12, decimal_places=2)