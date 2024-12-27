from app import db
from app.model.model_user import User

db.connect()
db.create_tables([User])