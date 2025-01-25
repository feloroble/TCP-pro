from datetime import datetime
from app.database import  BaseModel
from peewee import  CharField, ForeignKeyField, IntegerField, FloatField, TextField, DateTimeField


from app.models.tcp import TCPBusiness
from app.models.user import User


class Category(BaseModel):
    name = CharField(max_length=255, unique=True, index=True)  # Nombre único de la categoría
    description = TextField(null=True)  # Descripción opcional
    created_at = DateTimeField(default=datetime.now)  # Fecha de creación


class SubCategory(BaseModel):
    name = CharField(max_length=255)  # Nombre de la subcategoría
    description = TextField(null=True)  # Descripción opcional
    category = ForeignKeyField(Category, backref='subcategories', on_delete='CASCADE')  # Relación con Categoría
    created_at = DateTimeField(default=datetime.now)  # Fecha de creación

class Product(BaseModel):
    PRODUCT_TYPES = (
        ('physical', 'Físico'),
        ('digital', 'Digital'),
    )

    

    name = CharField(max_length=255)
    description = TextField(null=True)
    category = ForeignKeyField(Category, backref='products', on_delete='CASCADE')
    tipo = CharField(choices=PRODUCT_TYPES)
    stock = IntegerField(default=0)
    price = FloatField()
    costo = FloatField()
    business = ForeignKeyField(TCPBusiness, backref='products', on_delete='CASCADE')
    created_at = DateTimeField(default=datetime.now)
    um = CharField(null=False)   
    created_by = ForeignKeyField(User, backref='products')
    code = CharField(unique=True)

    @classmethod
    def generate_product_code(cls, business_id, user_id):
        """
        Genera un código único para un producto con el formato:
        INV-(consecutivo dentro del negocio)-(id del negocio)-(id del usuario)
        """
        # Obtener el número consecutivo de productos dentro del negocio
        product_count = cls.select().where(cls.business_id == business_id).count() + 1
        return f"INV-{product_count}-{business_id}-{user_id}"

class CostSheet(BaseModel):
    product = ForeignKeyField(Product, backref='cost_sheet', unique=True, on_delete='CASCADE')
    business = ForeignKeyField(TCPBusiness, backref='cost_sheets', on_delete='CASCADE')
    user = ForeignKeyField(User, backref='edited_cost_sheets', on_delete='SET NULL', null=True)
    
    unit_of_measure = CharField()
    production_level = IntegerField()
    utilization_percentage = FloatField()
    created_by_role = CharField()  # Cargo del usuario
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    nombre_user = CharField(max_length=50)
    precio_de_costo = FloatField()
   
    




class Concept(BaseModel):
    FORM_TYPES = (
        ('direct', 'Gastos Directos'),
        ('indirect', 'Gastos Indirectos'),
    )
    cost_sheet = ForeignKeyField(CostSheet, backref='concepts')
    concept = CharField()
    row = IntegerField()
    base_cost = FloatField()
    new_cost = FloatField()
    concept_type = CharField(choices=FORM_TYPES)
    created_at = DateTimeField(default=datetime.now)
