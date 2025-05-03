import socket
import os
import sys

HOST = '0.0.0.0'  # Escucha en todas las interfaces disponibles
PORT = int(os.getenv('SERVER_PORT', '1234'))

# Crea un socket para IPv4 y conexión TCP
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()

    print(f"El servidor está esperando conexiones en el puerto {PORT}", file=sys.stderr)

    while True:
        conn, addr = s.accept()  # Espera una conexión
        with conn:
            print(f"Conección recibida de {addr}", file=sys.stderr)
            data = conn.recv(1024)  # Recibe hasta 1024 bytes del cliente
            if data:
                print(f"Mensaje: {data.decode('utf-8')}", end='', file=sys.stderr)
                respuesta = "tu mensaje es: " + data.decode('utf-8')
                conn.sendall(respuesta.encode('utf-8'))  # Envía la respuesta al cliente
