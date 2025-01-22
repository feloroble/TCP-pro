from peewee import *
from app.models.flujorad import CircuitConfig_FR, Modelo_FR, Norma_FR
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


db.create_tables([Modelo_FR, Norma_FR, CircuitConfig_FR])