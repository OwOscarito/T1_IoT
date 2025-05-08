from enum import Enum
import struct
from typing import final

import macaddr

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

# los 6 bits de la MAC se ignoran en el patrón (caracter x) porque se obtienen por separado
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
