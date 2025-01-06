from app.database import db
from app.models.inventario import Product


db.connect()
db.create_tables([Product ])