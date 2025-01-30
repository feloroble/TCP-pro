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

    # Relación con usuario
    user_id = ForeignKeyField(User, backref="tcp_businesses", on_delete="CASCADE")

    # Campos de control
    created_at = DateTimeField(default=datetime.now, verbose_name="Fecha de creación")
    

    class Meta:
        table_name = 'tcpbusiness'
        
class ServiceTariff(BaseModel):
    business = ForeignKeyField(TCPBusiness, backref='tariffs')
    price = DecimalField(max_digits=10, decimal_places=2)
    start_date = DateField(default=date.today)
    end_date = DateField(null=True)  # Null si no hay fin definido o es indefinido

    class Meta:
        table_name = 'servicetariff'          