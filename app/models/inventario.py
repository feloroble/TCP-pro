from datetime import datetime
from app.database import  BaseModel
from peewee import CharField, TextField,ForeignKeyField,IntegerField,DecimalField,DateTimeField

class Category(BaseModel):
    name = CharField(unique=True)
    description = TextField(null=True)

class Product(BaseModel):
    name = CharField()
    category = ForeignKeyField(Category, backref='products', on_delete='CASCADE')
    type = CharField(choices=[('digital', 'Digital'), ('physical', 'Físico')])
    sub_type = CharField(choices=[
        ('food', 'Alimentos'),
        ('goods', 'Víveres'),
        ('liquids', 'Líquidos'),
        ('other', 'Otros'),
        ('software', 'Programas'),
        ('services', 'Servicios'),
    ], null=True)
    stock = IntegerField(default=0)
    price = DecimalField(max_digits=10, decimal_places=2, default=0.00)
    price_compra = DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)