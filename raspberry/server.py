import socket
import os
import sys
import time
import atexit
import selectors
import struct

import modelos
import datos
import macaddr
import headers

ADDR = os.getenv('SERVER_ADDR', '0.0.0.0')
PORT = int(os.getenv('SERVER_PORT', '1234'))

network_interface = macaddr.get_iface_by_addr(ADDR, PORT)
if network_interface == None:
    print(f"No se encontró una interfaz de red que corresponda a la dirección {ADDR}", file=sys.stderr)
    exit(1)

mac_address = macaddr.get_mac_by_iface_name(network_interface)
if mac_address == None:
    print(f"No se encontró una dirección MAC correspondiente a la interfaz de red {network_interface}", file=sys.stderr)
    exit(1)

def handle_tcp(sock: socket.socket):
    conn, addr = sock.accept()
    print(f"Conexión TCP recibida de {addr}.")

    with conn:
        packet = conn.recv(datos.max_packet_size)
        header = headers.Header.unpack(packet)

        if header.id_protocol == headers.Protocol.HANDSHAKE:
            id_device = struct.unpack('<I', packet[headers.header_len:])[0]
            id_protocol, transport_layer = modelos.get_db_config()
            response = headers.Header(
                packet_id = 0,
                mac = mac_address,
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
    print(f"Paquete UDP recibido de {addr}.")

    header = headers.Header.unpack(packet)
    id_device = modelos.get_id_device(header.mac)

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
        mac = mac_address,
        transport_layer = transport_layer,
        id_protocol = id_protocol,
        packet_len = headers.header_len
    )

    sock.sendto(response.pack(), addr)


sel = selectors.DefaultSelector()

tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcp_sock.bind((ADDR, PORT))
tcp_sock.listen()
tcp_sock.setblocking(False)
sel.register(tcp_sock, selectors.EVENT_READ, handle_tcp)

udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
udp_sock.bind((ADDR, PORT))
udp_sock.setblocking(False)
sel.register(udp_sock, selectors.EVENT_READ, handle_udp)

atexit.register(tcp_sock.close)
atexit.register(udp_sock.close)

print(f"El servidor está esperando conexiones en el puerto {PORT}", file=sys.stderr)

while True:
    for key, _ in sel.select():
        # try:
            callback = key.data
            callback(key.fileobj)
        # except Exception as e:
        #     print(f"Ocurrió un error:\n{e.with_traceback}", file=sys.stderr)

