from peewee import *
from app.models.flujorad import CircuitConfig_FR, Modelo_FR, Norma_FR
from app.models.inventario import Category, Concept, Product, CostSheet, SubCategory, ConceptType
from app.models.user import  User,Operation
from app.models.tcp import ServiceTariff, TCPBusiness
from app.database import DATABASE


db = MySQLDatabase(DATABASE)


db.create_tables([Category, Concept, Product, CostSheet, SubCategory,ConceptType])