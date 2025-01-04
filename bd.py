from app.database import db
from app.models.inventario import Product,Category 
from peewee_migrate import Migrator

db.connect()
db.create_tables([Product ])