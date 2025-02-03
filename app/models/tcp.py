from datetime import date, datetime
from peewee import *
from app.database import BaseModel
from app.models.user import User

class TCPBusiness(BaseModel):
    # Campos principales del negocio
    project_name = CharField(max_length=255, verbose_name="Nombre del proyecto TCP")
    description = TextField(verbose_name="Descripción del proyecto")
    main_activity = CharField(max_length=255, verbose_name="Actividad principal")

    # Campos de información adicional
    is_registered_in_conservation_zone = BooleanField(verbose_name="Registrado en las Zonas Priorizadas para la Conservación")
    has_bank_account = BooleanField(verbose_name="Posee cuenta bancaria")
    payment_method = CharField(choices=["Tarjeta", "Efectivo"], max_length=10, verbose_name="Método de pago")
    bank_type = CharField(
        choices=["Metropolitano", "BANDEC", "BPA"], 
        max_length=20, 
        null=True, 
        verbose_name="Tipo de banco"
    )
    fiscal_bank_branch = CharField(max_length=255, null=True, verbose_name="Sucursal bancaria de su domicilio fiscal")
    has_transportation = BooleanField(verbose_name="Posee un medio de transporte")
    does_ecommerce = BooleanField(verbose_name="Realiza comercio electrónico")

    # Detalles adicionales
    location = CharField(max_length=255, verbose_name="Lugar donde ejerce")
    residential_commercial_area = BooleanField(verbose_name="Área comercial en vivienda")
    music_service = BooleanField(verbose_name="Servicio de música")
    operation_hours = CharField(max_length=255, verbose_name="Horario de funcionamiento de la instalación")
    nic = CharField(max_length=50, verbose_name="NIC")
    business_address = TextField(verbose_name="Dirección del negocio")
    
    contact_phone = CharField(max_length=15, null=True, verbose_name="Teléfono de contacto")
    contact_email = CharField(max_length=100, null=True, verbose_name="Correo de contacto")

    # Relación con usuario
    user_id = ForeignKeyField(User, backref="tcp_businesses", on_delete="CASCADE")

    # Campos de control
    created_at = DateTimeField(default=datetime.now, verbose_name="Fecha de creación")
    

    class Meta:
        table_name = 'tcpbusiness'
        
class BusinessRelation(BaseModel):
    business = ForeignKeyField(TCPBusiness, backref="relations", on_delete="CASCADE")  # Negocio actual
    related_business = ForeignKeyField(TCPBusiness, null=True, backref="related_as", on_delete="SET NULL")  # Cliente/proveedor si ya existe en la BD
    name = CharField(max_length=255, null=True)  # Para clientes/proveedores nuevos no registrados en TCPBusiness
    phone = CharField(max_length=15, null=True)
    email = CharField(max_length=100, null=True)
    address = TextField(null=True)
    type = CharField(choices=["Cliente", "Proveedor"], max_length=10)  # Define si es cliente o proveedor
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        table_name = "business_relation"
        
class ServiceTariff(BaseModel):
    business = ForeignKeyField(TCPBusiness, backref='tariffs')
    price = DecimalField(max_digits=10, decimal_places=2)
    start_date = DateField(default=date.today)
    end_date = DateField(null=True)  # Null si no hay fin definido o es indefinido

    class Meta:
        table_name = 'servicetariff'          