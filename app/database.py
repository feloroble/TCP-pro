from peewee import  MySQLDatabase, Model

from app.config import DATABASE

db = MySQLDatabase(
    DATABASE['name'],
    user=DATABASE['user'],
    password=DATABASE['password'],
    host=DATABASE['host'],
    port=DATABASE['port']
)

# Clase base para los modelos
class BaseModel(Model):
    class Meta:
        database = db
        
        

# Función para inicializar la base de datos
def init_db():
    from app.models.user import User , PasswordResetToken # Importar modelos
    

    # Crear las tablas si no existen
    