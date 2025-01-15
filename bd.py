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

def create_tables():
    with db:
        db.create_tables([CostSheet])

create_tables()