from app.database import db
from app.models.user import PasswordResetToken

db.connect()
db.create_tables([PasswordResetToken])