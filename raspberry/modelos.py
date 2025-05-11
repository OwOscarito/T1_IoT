import os
import time
from typing import final
from peewee import Model, PostgresqlDatabase, IntegerField, \
    CharField, FloatField, CompositeKey, SmallIntegerField
from playhouse.postgres_ext import ArrayField

import macaddr
import headers

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
    

class BaseModel(Model):
    @final
    class Meta:
        database = db

@final
class Data(BaseModel):
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

    arrival_timestamp = IntegerField()
    id_device = IntegerField()
    mac_address = CharField(max_length=17)


@final
class Logs(BaseModel):
    id_device = IntegerField()
    mac_address = CharField(max_length=17)
    transport_layer = SmallIntegerField()
    id_protocol = IntegerField()
    arrival_timestamp = IntegerField()



@final
class Configuration(BaseModel):
    id_protocol = SmallIntegerField()
    transport_layer = SmallIntegerField()
    
@final
class Loss(BaseModel):
    id_device = IntegerField()
    packet_id = IntegerField()
    timestamp = IntegerField(null=True)
    arrival_timestamp = IntegerField()
    delay = IntegerField(null=True)
    packet_loss = IntegerField()

db.create_tables([Data, Logs, Configuration, Loss])

def get_id_device(mac: macaddr.MacAddress) -> int:
    log: Logs | None = Logs.get_or_none(Logs.mac_address == mac.as_str)
    if log == None:
        raise Exception(f"No se encontró el ID para el dispositivo con MAC {mac.as_str}")

    return log.id_device

def get_db_config() -> tuple[headers.Protocol, headers.TransportLayer]:
    db_config: Configuration | None = Configuration.get_or_none()
    if db_config == None:
        raise Exception("No hay configuración en la base de datos")
    return headers.Protocol(db_config.id_protocol), headers.TransportLayer(db_config.transport_layer)
    
def set_db_config(id_protocol: headers.Protocol, transport_layer: headers.TransportLayer):
    db_config: Configuration | None = Configuration.get_or_none()
    if db_config == None:
        db_config = Configuration(
            id_protocol=id_protocol.value, 
            transport_layer=transport_layer.value
            )
        db_config.save(force_insert=True)
    else:
        db_config.id_protocol = id_protocol.value
        db_config.transport_layer = transport_layer.value
        db_config.save()

def update_loss(id_device: int, packet_id: int, timestamp: int | None):
    arrival_timestamp = int(time.time())

    delay = arrival_timestamp - timestamp if timestamp is not None else None

    max_id_loss: Loss | None = (
        Loss.select()
        .where(Loss.id_device == id_device)
        .order_by(Loss.packet_id.desc())
        .first()
    )

    latest_loss: Loss | None = (
        Loss.select()
        .where(Loss.id_device == id_device)
        .order_by(Loss.arrival_timestamp.desc())
        .first()
    )

    if max_id_loss and latest_loss:
        if max_id_loss.packet_id < packet_id:
            packet_loss = latest_loss.packet_loss + (max_id_loss.packet_id - packet_id - 1)
        elif max_id_loss.packet_id == packet_id:
            packet_loss = latest_loss.packet_loss
        else:
            packet_loss = latest_loss.packet_loss - 1
    else:
        packet_loss = 0

    return Loss.create(
        id_device=id_device,
        packet_id=packet_id,
        timestamp=timestamp,
        arrival_timestamp=arrival_timestamp,
        delay=delay,
        packet_loss=packet_loss,
    )

try:
    _ = get_db_config()
except Exception:
    set_db_config(headers.Protocol.PROTOCOL0, headers.TransportLayer.TCP)
