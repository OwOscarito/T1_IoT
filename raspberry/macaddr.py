from typing import final
import struct
import socket
import psutil

@final
class MacAddress:
    def __init__(self, as_bytes: bytes, as_str: str) -> None:
        if len(as_bytes) != 6:
            raise ValueError(f"Número incorrecto de bytes en dirección MAC ({len(as_bytes)})")
        elif len(as_str) != 17:
            raise ValueError(f"Dirección MAC con largo incorrecto ({as_str})")

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

