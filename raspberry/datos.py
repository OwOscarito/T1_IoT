import struct
from enum import Enum
from typing import final

import macaddr
import modelos

class TransportLayer(Enum):
    TCP = 0
    UDP = 1

class Protocol(Enum):
    PROTOCOL0 = 0
    PROTOCOL1 = 1
    PROTOCOL2 = 2
    PROTOCOL3 = 3
    PROTOCOL4 = 4
    HANDSHAKE = 5

header_struct = struct.Struct('<H6xBBH')
header_len = header_struct.size

@final
class Header:
    def __init__(self, packet_id: int, mac: macaddr.MacAddress, transport_layer: TransportLayer, 
                 id_protocol: Protocol, packet_len: int) -> None:
        self.packet_id = packet_id
        self.mac = mac
        self.transport_layer = transport_layer
        self.id_protocol = id_protocol
        self.packet_len = packet_len
        
    @classmethod
    def unpack(cls, packet: bytes) -> 'Header':
        fields = header_struct.unpack(packet[:header_len])
        packet_id: int = fields[0]
        mac = macaddr.MacAddress.from_bytes(packet[2:2+6])

        transport_layer = TransportLayer(fields[1])

        id_protocol = Protocol(fields[2])

        packet_len: int = fields[3]

        return cls(packet_id, mac, transport_layer, id_protocol, packet_len)

    def pack(self) -> bytes:
        return struct.pack('<H', self.packet_id) + self.mac.as_bytes + \
            struct.pack('<BBH', self.transport_layer.value, self.id_protocol.value, self.packet_len)

proto_0_struct = struct.Struct('<B')
def unpack_protocol_0(packet: bytes, arrival_timestamp: int, id_device: int, mac: macaddr.MacAddress) -> modelos.Data:
    fields = proto_0_struct.unpack(packet[header_len:proto_0_struct.size])
    data = modelos.Data(
        arrival_timestamp = arrival_timestamp,
        id_device = id_device,
        mac_address = mac
    )

    data.batt_level = fields[0]
    return data


proto_1_struct = struct.Struct('<BI')
def unpack_protocol_1(packet: bytes, timestamp: int, id_device: int, mac: macaddr.MacAddress) -> modelos.Data:
    fields = proto_1_struct.unpack(packet[header_len:proto_1_struct.size])

    data = modelos.Data(
        arrival_timestamp = timestamp,
        id_device = id_device,
        mac_address = mac
    )
    data.batt_level = fields[0]
    data.timestamp = fields[1]

    return data


proto_2_struct = struct.Struct('<BIBIBf')
def unpack_protocol_2(packet: bytes, arrival_timestamp: int, id_device: int, mac: macaddr.MacAddress) -> modelos.Data:
    fields = proto_2_struct.unpack(packet[header_len:proto_2_struct.size])

    data = modelos.Data(
        arrival_timestamp = arrival_timestamp,
        id_device = id_device,
        mac_address = mac
    )
    data.batt_level = fields[0]
    data.timestamp = fields[1]
    data.temp = fields[2]
    data.press = fields[3]
    data.hum = fields[4]
    data.co = fields[5]

    return data

proto_3_struct = struct.Struct(proto_2_struct.format + '7f')
def unpack_protocol_3(packet: bytes, arrival_timestamp: int, id_device: int, mac: macaddr.MacAddress) -> modelos.Data:
    data = unpack_protocol_2(packet, arrival_timestamp, id_device, mac)
    fields = proto_3_struct.unpack(packet[header_len+proto_2_struct.size:proto_3_struct.size])

    data.rms = fields[-7]
    data.amp_x = fields[-6]
    data.frec_x = fields[-5]
    data.amp_y = fields[-4]
    data.frec_y = fields[-3]
    data.amp_z = fields[-2]
    data.frec_z = fields[-1]

    return data


def unpack_protocol_4(packet: bytes, arrival_timestamp: int, id_device: int, mac: macaddr.MacAddress) -> modelos.Data:
    data = unpack_protocol_2(packet, arrival_timestamp, id_device, mac)
    gyro_data = packet[header_len+proto_2_struct.size:]

    data.acc_x = struct.unpack('<2000f', gyro_data[:8000])
    data.acc_y = struct.unpack('<2000f', gyro_data[8000:16000])
    data.acc_z = struct.unpack('<2000f', gyro_data[16000:24000])
    data.rgyr_x = struct.unpack('<2000f', gyro_data[24000:32000])
    data.rgyr_y = struct.unpack('<2000f', gyro_data[32000:40000])
    data.rgyr_z = struct.unpack('<2000f', gyro_data[40000:48000])

    return data

