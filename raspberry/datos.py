import struct
from enum import Enum
from typing import final, Callable

import macaddr
import modelos
import headers

proto_0_struct = struct.Struct('<B')
def unpack_protocol_0(packet: bytes, arrival_timestamp: int, id_device: int, mac: macaddr.MacAddress) -> modelos.Data:
    data_slice = packet[headers.header_len:]
    fields = proto_0_struct.unpack(data_slice[:proto_0_struct.size])

    data = modelos.Data(
        arrival_timestamp = arrival_timestamp,
        id_device = id_device,
        mac_address = mac.as_str
    )

    data.batt_level = fields[0]
    return data


proto_1_struct = struct.Struct('<BI')
def unpack_protocol_1(packet: bytes, timestamp: int, id_device: int, mac: macaddr.MacAddress) -> modelos.Data:
    data_slice = packet[headers.header_len:]
    fields = proto_1_struct.unpack(data_slice[:proto_1_struct.size])

    data = modelos.Data(
        arrival_timestamp = timestamp,
        id_device = id_device,
        mac_address = mac.as_str
    )
    data.batt_level = fields[0]
    data.timestamp = fields[1]

    return data


proto_2_struct = struct.Struct('<BIBIBf')
def unpack_protocol_2(packet: bytes, arrival_timestamp: int, id_device: int, mac: macaddr.MacAddress) -> modelos.Data:
    data_slice = packet[headers.header_len:]
    fields = proto_2_struct.unpack(data_slice[:proto_2_struct.size])

    data = modelos.Data(
        arrival_timestamp = arrival_timestamp,
        id_device = id_device,
        mac_address = mac.as_str
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
    data_slice = packet[headers.header_len:]
    fields = proto_3_struct.unpack(data_slice[:proto_3_struct.size])

    data.rms = fields[-7]
    data.amp_x = fields[-6]
    data.frec_x = fields[-5]
    data.amp_y = fields[-4]
    data.frec_y = fields[-3]
    data.amp_z = fields[-2]
    data.frec_z = fields[-1]

    return data


proto_4_struct = struct.Struct(proto_2_struct.format + '12000f')
max_packet_size = headers.header_len + proto_4_struct.size

def unpack_protocol_4(packet: bytes, arrival_timestamp: int, id_device: int, \
                      mac: macaddr.MacAddress) -> modelos.Data:
    data = unpack_protocol_2(packet, arrival_timestamp, id_device, mac)
    gyro_data = packet[headers.header_len+proto_2_struct.size:]

    data.acc_x = struct.unpack('<2000f', gyro_data[:8000])
    data.acc_y = struct.unpack('<2000f', gyro_data[8000:16000])
    data.acc_z = struct.unpack('<2000f', gyro_data[16000:24000])
    data.rgyr_x = struct.unpack('<2000f', gyro_data[24000:32000])
    data.rgyr_y = struct.unpack('<2000f', gyro_data[32000:40000])
    data.rgyr_z = struct.unpack('<2000f', gyro_data[40000:48000])

    return data


unpack_functions: dict[headers.Protocol, Callable[[bytes, int, int, macaddr.MacAddress], modelos.Data]] = {
    headers.Protocol.PROTOCOL0: unpack_protocol_0, 
    headers.Protocol.PROTOCOL1: unpack_protocol_1, 
    headers.Protocol.PROTOCOL2: unpack_protocol_2, 
    headers.Protocol.PROTOCOL3: unpack_protocol_3, 
    headers.Protocol.PROTOCOL4: unpack_protocol_4, 
}
