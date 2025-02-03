from peewee import *

from app.models.facturas import Cuenta, Comprobante, ComprobanteDetalle, Factura,Cliente,Proveedor, Venta,Compra,DetalleFactura
from app.models.tcp import BusinessRelation
from app.database import DATABASE


db = MySQLDatabase(DATABASE)


db.create_tables([BusinessRelation ])