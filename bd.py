from app import db
from app.user.models import User

db.connect()
db.create_tables([User])