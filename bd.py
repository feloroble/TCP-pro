from app.database import db
from app.models.tcp import TCPBusiness

db.connect()
db.create_tables([TCPBusiness])