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
    user = ForeignKeyField(User, backref='products', on_delete='CASCADE')  # Referencia como cadena
    created_at = DateTimeField(default=datetime.now)
    
       



class CostSheet(BaseModel):
    product = ForeignKeyField(Product, backref='cost_sheet', unique=True, on_delete='CASCADE')
    business = ForeignKeyField(TCPBusiness, backref='cost_sheets', on_delete='CASCADE')
    user = ForeignKeyField(User, backref='edited_cost_sheets', on_delete='SET NULL', null=True)
    sequence_number = IntegerField() 
    code = CharField(unique=True)
    unit_of_measure = CharField()
    production_level = IntegerField()
    utilization_percentage = FloatField()
    created_by_role = CharField()  # Cargo del usuario
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    nombre_user = CharField(max_length=50)
    precio_de_costo = FloatField()
   
    @staticmethod
    def generate_sequence_number(business_id):
        """
        Calcula el siguiente número de la secuencia para el negocio dado.
        """
        # Obtener el último número de secuencia para el negocio seleccionado
        last_sheet = CostSheet.select().where(CostSheet.business_id == business_id).order_by(CostSheet.sequence_number.desc()).first()
        return (last_sheet.sequence_number + 1) if last_sheet else 1




class Concept(BaseModel):
    cost_sheet = ForeignKeyField(CostSheet, backref='concepts')
    concept = CharField()
    row = IntegerField()
    base_cost = FloatField()
    new_cost = FloatField()
    created_at = DateTimeField(default=datetime.now)
