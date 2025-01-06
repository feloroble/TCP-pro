from datetime import datetime
from app.database import  BaseModel
from peewee import  CharField, ForeignKeyField, IntegerField, FloatField, TextField, DateTimeField

from app.models.user import User
from app.models.tcp import TCPBusiness


class Category(BaseModel):
    name = CharField(unique=True)
    description = TextField(null=True)

class Product(BaseModel):
    PRODUCT_TYPES = (
        ('physical', 'Físico'),
        ('digital', 'Digital'),
    )

    name = CharField(max_length=255, unique=True)
    description = TextField(null=True)
    category = ForeignKeyField(Category, backref='products', on_delete='CASCADE')
    type = CharField(choices=PRODUCT_TYPES)
    stock = IntegerField(default=0)
    price = FloatField()
    business = ForeignKeyField(TCPBusiness, backref='products', on_delete='CASCADE')
    user = ForeignKeyField(User, backref='products', on_delete='CASCADE')
    created_at = DateTimeField(default=datetime.now)
