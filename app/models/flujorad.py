import json
from peewee import *

from app.database import BaseModel

class JSONField(TextField):
  def db_value(self, value):
    return json.dumps(value, default=str)
  
  def python_value(self, value):
    if value is not None:
      return json.loads(value)
  
class Modelo_FR(BaseModel):
  nombre = CharField(255, unique=True)  

class Norma_FR(BaseModel):
  nombre = CharField(255, unique=True)

class CircuitConfig_FR(BaseModel):
  nombre = CharField(255, null=False)
  potencia = DecimalField(max_digits=10, decimal_places=2, default=0)
  tension = DecimalField(max_digits=10, decimal_places=2, default=0)
  tolerancia = DecimalField(max_digits=10, decimal_places=4, default=0)
  iteraciones = IntegerField(null=False, default=20)
  norma = ForeignKeyField(Norma_FR, field=Norma_FR.nombre, column_name="norma", backref="_configs")
  modelo = ForeignKeyField(Modelo_FR, field=Modelo_FR.nombre, column_name="modelo", backref="_configs")
  active = BooleanField(default=True)

    
  
