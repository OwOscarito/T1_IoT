import socket
import os
import sys
import time
import atexit
import selectors
import struct
from typing import cast

import modelos
import datos
import macaddr
import headers

HOST = os.getenv('SERVER_IP_ADDR', '0.0.0.0')
PORT = int(os.getenv('SERVER_PORT', '1234'))
MAC = macaddr.MacAddress.from_str(os.getenv('SERVER_MAC_ADDR', '00:00:00:00:00:00'))

def handle_tcp(sock: socket.socket):
    conn, addr = sock.accept()
    print(f"Conexión TCP recibida de {addr}.", file=sys.stderr)

    with conn:
        packet = conn.recv(datos.max_packet_size, )
        header = headers.Header.unpack(packet)
        if (len(packet) < header.packet_len):
            packet += conn.recv(header.packet_len - len(packet), socket.MSG_WAITALL)


        print(f"Paquete recibido con tamaño real {len(packet)}, reportado {header.packet_len} y protocolo {header.id_protocol.name}", file=sys.stderr)

        if header.id_protocol == headers.Protocol.HANDSHAKE:
            id_device = cast(int, struct.unpack('<I', packet[headers.header_len:])[0])
            id_protocol, transport_layer = modelos.get_db_config()
            response = headers.Header(
                packet_id = 0,
                mac = MAC,
                transport_layer = transport_layer,
                id_protocol = id_protocol,
                packet_len = headers.header_len
            )
            conn.sendall(response.pack())

        else:
            id_device = modelos.get_id_device(header.mac)
            unpack = datos.unpack_functions[header.id_protocol]
            data = unpack(packet, int(time.time()), id_device, header.mac)
            data.save(force_insert=True)

        modelos.Logs(
            id_device = id_device,
            mac_address = header.mac.as_str,
            transport_layer = headers.TransportLayer.TCP.value,
            id_protocol = header.id_protocol.value,
            arrival_timestamp = int(time.time()),
        ).save(force_insert=True)


def handle_udp(sock: socket.socket):
    packet, addr = sock.recvfrom(datos.max_packet_size)
    print(f"Paquete UDP con tamaño {len(packet)} recibido de {addr}.", file=sys.stderr)

    header = headers.Header.unpack(packet)
    id_device = modelos.get_id_device(header.mac)
    print(f"Paquete reporta tamaño {header.packet_len} y protocolo {header.id_protocol}.", file=sys.stderr)

    modelos.Logs(
        id_device = id_device,
        mac_address = header.mac.as_str,
        transport_layer = headers.TransportLayer.UDP.value,
        id_protocol = header.id_protocol.value,
        arrival_timestamp = int(time.time()),
    ).save(force_insert=True)
    
    if header.id_protocol == headers.Protocol.HANDSHAKE:
        print('Error: Se recibió un paquete de tipo handshake por UDP', file=sys.stderr)
        return

    unpack = datos.unpack_functions[header.id_protocol]
    id_device = modelos.get_id_device(header.mac)

    data = unpack(packet, int(time.time()), id_device, header.mac)
    data.save(force_insert=True)

    id_protocol, transport_layer = modelos.get_db_config()
    response = headers.Header(
        packet_id = 0,
        mac = MAC,
        transport_layer = transport_layer,
        id_protocol = id_protocol,
        packet_len = headers.header_len
    )

    sock.sendto(response.pack(), addr)


sel = selectors.DefaultSelector()

tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcp_sock.bind((HOST, PORT))
tcp_sock.listen()
tcp_sock.setblocking(False)
_ = sel.register(tcp_sock, selectors.EVENT_READ, handle_tcp)

udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
udp_sock.bind((HOST, PORT))
udp_sock.setblocking(False)
_ = sel.register(udp_sock, selectors.EVENT_READ, handle_udp)

_ = atexit.register(tcp_sock.close)
_ = atexit.register(udp_sock.close)

print(f"El servidor está esperando conexiones en el puerto {PORT}", file=sys.stderr)

while True:
    for key, _ in sel.select():
        try:
            callback = key.data
            callback(key.fileobj)
        except Exception as e:
            print(f"Ocurrió un error:\n{e}", file=sys.stderr)

