import socket
import os
import sys
import time

import modelos
import datos
import macaddr

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


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((ADDR, PORT))
s.listen()

print(f"El servidor está esperando conexiones en el puerto {PORT}", file=sys.stderr)

conn, addr = s.accept()

print(f"Conección recibida de {addr}", file=sys.stderr)

packet = conn.recv(1024)
header = datos.Header.unpack(packet)
id_device = modelos.get_id_device(header.mac)
if id_device == None: 
    print(f"Id del dispositivo no encontrado (MAC: {header.mac})", file=sys.stderr)
    exit(1)


if (header.transport_layer == datos.TransportLayer.TCP and header.id_protocol == datos.Protocol.PROTOCOL4):
    data = datos.unpack_protocol_4(packet, int(time.time()), id_device, header.mac)


respuesta = b'0123456789'
conn.sendall(respuesta)

conn.close()

s.close()

