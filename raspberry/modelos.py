import os
import typing
from peewee import Model, PostgresqlDatabase, TimestampField, IntegerField, CharField, FloatField, CompositeKey

POSTGRES_DB = os.getenv('POSTGRES_DB', 'postgres')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = int(os.getenv('POSTGRES_PORT', '5432'))
POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')

db = PostgresqlDatabase(
    database = POSTGRES_DB,
    host = POSTGRES_HOST,
    port = POSTGRES_PORT,
    user = POSTGRES_USER,
    password = POSTGRES_PASSWORD
)
_ = db.connect()
    
# Definición de un modelo
class BaseModel(Model):
    class Meta:
        database: PostgresqlDatabase = db

# Ahora puedes definir tus modelos específicos heredando de BaseModel
# y db estará conectado al servicio de PostgreSQL cuando realices operaciones de base de datos.

# Ver la documentación de peewee para más información, es super parecido a Django
# https://docs.peewee-orm.com/en/latest/peewee/quickstart.html

@typing.final
class Data(Model):
    type = CharField()
    value = FloatField()
    timestamp = TimestampField()
    device_id = IntegerField()
    mac_address = CharField()

    @typing.final
    class Meta():
        primary_key = CompositeKey('device_id', 'timestamp')
        database: PostgresqlDatabase = db


db.create_tables([Data])

