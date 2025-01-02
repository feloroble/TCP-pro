from peewee import Model, CharField, DecimalField, DateField, ForeignKeyField
from app.models.user import User
from app.database import BaseModel


class SalesInvoice(Model):
    user = ForeignKeyField(User, backref='sales_invoices')
    product_name = CharField()
    quantity = DecimalField()
    price = DecimalField()
    total = DecimalField()
    date = DateField()
