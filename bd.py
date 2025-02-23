from peewee import *

from app.models.user import User, Operation
from app.models.tcp import  TCPBusiness , BusinessRelation
from app.models.inventario import Category,SubCategory,Product,CostSheet,ConceptType,Concept
from app.config import DATABASE



db = MySQLDatabase(DATABASE)


db.create_tables([Concept])