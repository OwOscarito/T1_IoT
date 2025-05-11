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

HOST = os.getenv('SERVER_HOST', '0.0.0.0')
PORT = int(os.getenv('SERVER_PORT', '7777'))
MAC = macaddr.MacAddress.from_str(os.getenv('SERVER_MAC', '00:00:00:00:00:00'))

def receive_exactly(conn: socket.socket, total_bytes: int) -> bytes:
    data = bytearray()
    while len(data) < total_bytes:
        chunk = conn.recv(total_bytes - len(data))
        if not chunk:
            raise ConnectionError("La conexión fue cerrada antes de tiempo")
        data.extend(chunk)
    return bytes(data)


def handle_tcp(sock: socket.socket):
    conn, addr = sock.accept()
    print(f"Conexión TCP recibida de {addr}.", file=sys.stderr)
    conn.settimeout(10.0)

    with conn:
        header_bytes = receive_exactly(conn, headers.header_len)
        header = headers.Header.unpack(header_bytes)
        print(f"Paquete recibido con protocolo {header.id_protocol.name} y tamaño {header.packet_len}", file=sys.stderr)

        print("Esperando paquete completo... ", file=sys.stderr, end='', flush=True)
        data_bytes = receive_exactly(conn, header.packet_len - headers.header_len)
        packet = header_bytes + data_bytes
        print("Listo.", file=sys.stderr)

        conn.shutdown(socket.SHUT_RD)

        # Siempre se envia un header de vuelta, incluso cuando el protocolo no es handshake, ya que el ESP
        # siempre espera a recibir una respuesta del servidor, esto está hecho así para que el ESP no vaya a
        # cerrar la conexión antes de tiempo y cause que no lleguen todos los datos (si pasa xd)
        id_protocol, transport_layer = modelos.get_db_config()
        response = headers.Header(
            packet_id = 0,
            mac = MAC,
            transport_layer = transport_layer,
            id_protocol = id_protocol,
            packet_len = headers.header_len
        )
        conn.sendall(response.pack())

        conn.shutdown(socket.SHUT_WR)

        if header.id_protocol == headers.Protocol.HANDSHAKE:
            id_device = cast(int, struct.unpack('<I', packet[headers.header_len:])[0])

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

    modelos.update_loss(id_device, header.packet_id, data.timestamp)


sel = selectors.DefaultSelector()

tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcp_sock.setblocking(False)
tcp_sock.bind((HOST, PORT))
tcp_sock.listen()

udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
udp_sock.setblocking(False)
udp_sock.bind((HOST, PORT))

_ = sel.register(tcp_sock, selectors.EVENT_READ, handle_tcp)
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

