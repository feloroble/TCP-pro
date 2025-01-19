from peewee import *
from app.models.inventario import Category, Concept, Product, CostSheet, SubCategory
from app.models.user import User
from app.models.tcp import TCPBusiness
from app.database import DATABASE


db = MySQLDatabase(
    'tcp_db',
    user='root',
    password='frroble91',
    host='localhost',
    port=3306
)

for user in User.select():
    if user.rol == "usuario TCP" and not user.license_expiry:
        user.license_duration = 0
        user.license_expiry = None
        user.save()