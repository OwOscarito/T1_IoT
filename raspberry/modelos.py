import os
import typing
from peewee import Model, PostgresqlDatabase, TimestampField, IntegerField, CharField, FloatField, CompositeKey, SmallIntegerField
from playhouse.postgres_ext import ArrayField


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
    batt_level = SmallIntegerField(null=True)
    # este timestamp representa el valor que se envia desde el esp,
    # es distinto del arrival_timestamp, que representa cuando llega el paquete al server
    timestamp = IntegerField(null=True) 

    temp = SmallIntegerField(null=True)
    press = IntegerField(null=True)
    hum = SmallIntegerField(null=True)
    co = FloatField(null=True)

    rms = FloatField(null=True)
    amp_x = FloatField(null=True)
    frec_x = FloatField(null=True)
    amp_y = FloatField(null=True)
    frec_y = FloatField(null=True)
    amp_z = FloatField(null=True)
    frec_z = FloatField(null=True)

    acc_x = ArrayField(field_class=FloatField, null=True)
    acc_y = ArrayField(field_class=FloatField, null=True)
    acc_z = ArrayField(field_class=FloatField, null=True)
    rgyr_x = ArrayField(field_class=FloatField, null=True)
    rgyr_y = ArrayField(field_class=FloatField, null=True)
    rgyr_z = ArrayField(field_class=FloatField, null=True)

    arrival_timestamp = TimestampField(null=False)
    id_device = IntegerField(null=False)
    mac_address = CharField(null=False, max_length=17)

    @typing.final
    class Meta:
        primary_key = CompositeKey('id_device', 'arrival_timestamp')
        database = db

@typing.final
class Logs(BaseModel):
    id_device = IntegerField()
    transport_layer = SmallIntegerField()
    arrival_timestamp = TimestampField()


@typing.final
class Configuration(BaseModel):
    id_protocol = SmallIntegerField()
    
@typing.final
class Loss(BaseModel):
    pass

db.create_tables([Data, Logs, Configuration, Loss])

