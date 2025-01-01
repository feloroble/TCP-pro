
from peewee import  CharField, AutoField,Model,ForeignKeyField, DateTimeField
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import db

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    id = AutoField(primary_key=True)
    first_name = CharField(max_length=50)
    last_name = CharField(max_length=50)
    email = CharField(max_length=100, unique=True)
    username = CharField(max_length=50, unique=True)
    phone = CharField(max_length=15, unique=True)  # Nuevo campo
    password = CharField(max_length=255)
    rol = CharField(max_length=20, default='usuario')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
class PasswordResetToken(BaseModel):
    user = ForeignKeyField(User, backref='reset_tokens', on_delete='CASCADE')
    token = CharField(unique=True)
    created_at = DateTimeField(default=datetime.now)
    expires_at = DateTimeField(default=lambda: datetime.now() + timedelta(hours=1))  # 1 hora de validez


