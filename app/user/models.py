
from peewee import Model, CharField, AutoField
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

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

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

