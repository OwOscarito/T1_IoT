import socket
import os
import sys
import struct

HOST = '0.0.0.0'  # Escucha en todas las interfaces disponibles
PORT = int(os.getenv('SERVER_PORT', '1234'))

# Crea un socket para IPv4 y conexión TCP
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()

    print(f"El servidor está esperando conexiones en el puerto {PORT}", file=sys.stderr)

    conn, addr = s.accept()

    print(f"Conección recibida de {addr}", file=sys.stderr)

    with conn:
        data = conn.recv(1024)
        if len(data) == 15:
            print(struct.unpack("<BIBIBf", data))

        else:
            print(f"Volumen de datos recibidos incorrecta: {len(data)} (esperado: 15)")

        respuesta = struct.pack("<BIBIBf", 83, 82371, 9, 10230, 222, 99188.293)
        conn.sendall(respuesta)


