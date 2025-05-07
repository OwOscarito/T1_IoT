import struct
from enum import Enum
from typing import final
import socket
import psutil
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

@final
class MacAddress:
    def __init__(self, as_bytes: bytes, as_str: str) -> None:
        if len(as_bytes) != 6:
            raise ValueError("Incorrect byte number on mac address.")
        elif len(as_str) != 17:
            raise ValueError("Incorrect length on mac address string.")
            
        self.as_bytes = as_bytes
        self.as_str = as_str.upper()

    @classmethod
    def from_bytes(cls, mac: bytes) -> 'MacAddress':
        mac_str = ':'.join(f"{int(byte):02X}" for byte in mac)
        return cls(mac, mac_str)

    @classmethod
    def from_str(cls, mac: str) -> 'MacAddress':
        mac_bytes = struct.pack('<6B', *[int(hexpair, base=16) for hexpair in mac.split(':')])
        return cls(mac_bytes, mac)
        

def get_iface_by_addr(address: str, port: int) -> str | None:
    addrinfo = socket.getaddrinfo(address, port)
    address_family: socket.AddressFamily = addrinfo[0][0]

    for iface_name, iface_addrs in psutil.net_if_addrs().items():
        for addr in iface_addrs:
            if addr.family == address_family and addr.address == address:
                return iface_name

    return None

def get_mac_by_iface_name(iface_name: str) -> MacAddress | None:
    iface_addrs = psutil.net_if_addrs()[iface_name]
    for addr in iface_addrs:
        if addr.family == psutil.AF_LINK:
            return MacAddress.from_str(addr.address)

    return None

header_struct = struct.Struct('<H6xBBH')
header_len = header_struct.size

@final
class Header:
    def __init__(self, packet_id: int, mac: MacAddress, transport_layer: TransportLayer, 
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
        mac = MacAddress.from_bytes(packet[2:2+6])

        transport_layer = TransportLayer(fields[1])

        id_protocol = Protocol(fields[2])

        packet_len: int = fields[3]

        return cls(packet_id, mac, transport_layer, id_protocol, packet_len)

    def pack(self) -> bytes:
        return struct.pack('<H', self.packet_id) + self.mac.as_bytes + \
            struct.pack('<BBH', self.transport_layer.value, self.id_protocol.value, self.packet_len)

proto_0_struct = struct.Struct('<B')
def unpack_protocol_0(packet: bytes, timestamp: int, id_device: int, mac: MacAddress) -> modelos.Data:
    fields = proto_0_struct.unpack(packet[header_len:proto_0_struct.size])
    data = modelos.Data(
        arrival_timestamp = timestamp,
        id_device = id_device,
        mac_address = mac
    )

    data.batt_level = fields[0]
    return data


proto_1_struct = struct.Struct('<BI')
def unpack_protocol_1(packet: bytes, timestamp: int, id_device: int, mac: MacAddress) -> modelos.Data:
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
def unpack_protocol_2(packet: bytes, timestamp: int, id_device: int, mac: MacAddress) -> modelos.Data:
    fields = proto_2_struct.unpack(packet[header_len:proto_2_struct.size])

    data = modelos.Data(
        arrival_timestamp = timestamp,
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
def unpack_protocol_3(packet: bytes, timestamp: int, id_device: int, mac: MacAddress) -> modelos.Data:
    data = unpack_protocol_2(packet, timestamp, id_device, mac)
    fields = proto_3_struct.unpack(packet[header_len+proto_2_struct.size:proto_3_struct.size])

    data.rms = fields[-7]
    data.amp_x = fields[-6]
    data.frec_x = fields[-5]
    data.amp_y = fields[-4]
    data.frec_y = fields[-3]
    data.amp_z = fields[-2]
    data.frec_z = fields[-1]

    return data


def unpack_protocol_4(packet: bytes, timestamp: int, id_device: int, mac: MacAddress) -> modelos.Data:
    data = unpack_protocol_2(packet, timestamp, id_device, mac)
    gyro_data = packet[header_len+proto_2_struct.size:]

    data.acc_x = struct.unpack('<2000f', gyro_data[:8000])
    data.acc_y = struct.unpack('<2000f', gyro_data[8000:16000])
    data.acc_z = struct.unpack('<2000f', gyro_data[16000:24000])
    data.rgyr_x = struct.unpack('<2000f', gyro_data[24000:32000])
    data.rgyr_y = struct.unpack('<2000f', gyro_data[32000:40000])
    data.rgyr_z = struct.unpack('<2000f', gyro_data[40000:48000])

    return data

