
from peewee import  CharField, AutoField,ForeignKeyField, DateTimeField, TextField
from datetime import date, datetime
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import IntegerField

from app.database import  BaseModel




class User(BaseModel):
    id = AutoField(primary_key=True)
    first_name = CharField(max_length=50)
    last_name = CharField(max_length=50)
    email = CharField(max_length=100, unique=True)
    username = CharField(max_length=50, unique=True)
    phone = CharField(max_length=15, unique=True)  # Nuevo campo
    password = CharField(max_length=255)
    rol = CharField(max_length=20, default='usuario')
    cargo = CharField(max_length=50)
    license_duration = CharField(null=True)  # Duración en meses para el rol TCP
    license_expiry = DateTimeField(null=True)   # Fecha de expiración del rol TCP
    
    class Meta:
        table_name = 'user'

    def days_remaining(self):
        """Calcula los días restantes de la licencia"""
        if self.license_expiry:
            today = date.today()
            today_datetime = datetime.combine(today, datetime.min.time())
            remaining_days = (self.license_expiry - today_datetime).days
            return remaining_days if remaining_days > 0 else 0
        return 0

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    


class Operation(BaseModel):
     EVENT_TYPES = (
        ('login', 'Inicio de sesión'),
        ('update_profile', 'Actualización de perfil'),
        ('update_type_user', 'Cambio de tipo de usuario en el sistema'),
        ('logout', 'Cierre de sesión'),
        ('rest_password', 'Restablecimiento de contraseña'),
    )

     user = ForeignKeyField(User, backref='operations')
     event_type = CharField(choices=EVENT_TYPES)
     description = TextField()
     created_at = DateTimeField(default=datetime.now)
