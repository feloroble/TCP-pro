from datetime import datetime
from app.database import  BaseModel
from peewee import  CharField, ForeignKeyField, IntegerField, FloatField, TextField, DateTimeField


from app.models.tcp import TCPBusiness
from app.models.user import User


class Category(BaseModel):
    name = CharField(max_length=255)  # Nombre de la categoría
    description = TextField(null=True)  # Descripción opcional
    business = ForeignKeyField(TCPBusiness, backref='categories', on_delete='CASCADE')  # Relación con el negocio
    created_at = DateTimeField(default=datetime.now)  # Fecha de creación

    class Meta:
        table_name = 'category'
        indexes = (
            (('name', 'tcpbusiness'), True),  # Asegura que el nombre de la categoría sea único dentro de un negocio
        )


class SubCategory(BaseModel):
    name = CharField(max_length=255)  # Nombre de la subcategoría
    description = TextField(null=True)  # Descripción opcional
    category = ForeignKeyField(Category, backref='subcategories', on_delete='CASCADE')  # Relación con la categoría
    business = ForeignKeyField(TCPBusiness, backref='subcategories', on_delete='CASCADE')  # Relación con el negocio
    created_at = DateTimeField(default=datetime.now)  # Fecha de creación

    class Meta:
        table_name = 'subcategory'
        indexes = (
            (('name', 'category', 'tcpbusiness'), True),  # Asegura que el nombre de la subcategoría sea único dentro de una categoría y un negocio
        )




class Product(BaseModel):
    PRODUCT_TYPES = (
        ('physical', 'Físico'),
        ('digital', 'Digital'),
        ('service', 'Servicio'),
    )

    name = CharField(max_length=255)
    description = TextField(null=True)
    category = ForeignKeyField(Category, backref='products', on_delete='CASCADE')
    tipo = CharField(choices=PRODUCT_TYPES)
    stock = IntegerField(default=0)
    price = FloatField()
    costo = FloatField()
    business = ForeignKeyField(TCPBusiness, backref='products', on_delete='CASCADE')  # Relación con negocio
    created_at = DateTimeField(default=datetime.now)
    um = CharField(null=False)  # Unidad de medida definida en el producto
    created_by = ForeignKeyField(User, backref='products', on_delete='SET NULL', null=True)  # Usuario creador
    code = CharField(unique=True)  # Código único del producto
    image_path = CharField(null=True) 

    @classmethod
    def generate_product_code(cls, business_id, user_id):
        """
        Genera un código único para un producto con el formato:
        INV-(consecutivo dentro del negocio)-(id del negocio)-(id del usuario)
        """
        product_count = cls.select().where(cls.business_id == business_id).count() + 1
        return f"INV-{product_count}-{business_id}-{user_id}-TT"

    def save(self, *args, **kwargs):
        """Sobreescribe el método save para generar automáticamente el código."""
        if not self.code:
            self.code = self.generate_product_code(self.business_id, self.created_by_id)
        super().save(*args, **kwargs)

    class Meta:
        indexes = (
            (('name', 'business'), True),  # Nombre único por negocio
        )


class CostSheet(BaseModel):
    product = ForeignKeyField(Product, backref='cost_sheet', unique=True, on_delete='CASCADE')  # Relación con producto
    business = ForeignKeyField(TCPBusiness, backref='cost_sheets', on_delete='CASCADE')  # Relación con negocio
    user = ForeignKeyField(User, backref='edited_cost_sheets', on_delete='SET NULL', null=True)  # Usuario que editó
    production_level = IntegerField()  # Nivel de producción
    utilization_percentage = FloatField()  # Porcentaje de utilización
    created_by_role = CharField()  # Cargo del usuario que crea
    created_at = DateTimeField(default=datetime.now)  # Fecha de creación
    updated_at = DateTimeField(default=datetime.now)  # Fecha de última edición
    nombre_user = CharField(max_length=50)  # Nombre del usuario
    precio_de_costo = FloatField()  # Precio de costo

    class Meta:
        indexes = (
            (('product', 'business'), True),  # Ficha única por producto y negocio
        )


class Concept(BaseModel):
    FORM_TYPES = (
        ('direct', 'Gastos Directos'),
        ('indirect', 'Gastos Indirectos'),
    )
    cost_sheet = ForeignKeyField(CostSheet, backref='concepts', on_delete='CASCADE')  # Relación con ficha de costo
    concept = CharField()  # Nombre del concepto
    row = IntegerField()  # Número de fila
    base_cost = FloatField()  # Costo base
    new_cost = FloatField()  # Costo nuevo
    concept_type = CharField(choices=FORM_TYPES)  # Tipo de concepto
    created_at = DateTimeField(default=datetime.now)  # Fecha de creación