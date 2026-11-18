
import sys
import socket

def create_packet(parsed_IP_packet):
    ip, puerto, ttl, mensaje = parsed_IP_packet

    ip_bytes = bytes(map(int, ip.split(".")))
    puerto_bytes = puerto.to_bytes(2, byteorder="big")
    ttl_bytes = ttl.to_bytes(1, byteorder="big")
    mensaje_bytes = mensaje.encode("utf-8")

    return ip_bytes + puerto_bytes + ttl_bytes + mensaje_bytes


headers = sys.argv[1].split(";")

ip_destino = headers[0]
puerto_destino = int(headers[1])
ttl = int(headers[2])

ip_envio = sys.argv[2]
puerto_envio = int(sys.argv[3])

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

for linea in sys.stdin:
    mensaje = linea.rstrip("\n")

    parsed_packet = (ip_destino, puerto_destino, ttl, mensaje)
    packet = create_packet(parsed_packet)

    sock.sendto(packet, (ip_envio, puerto_envio))

sock.close()