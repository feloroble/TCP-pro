from app.database import BaseModel
from peewee import CharField

class Example(BaseModel):
    name = CharField(unique=True)