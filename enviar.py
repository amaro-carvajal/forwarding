
import sys
import socket

def create_packet(parsed_IP_packet):
    ip, puerto, mensaje = parsed_IP_packet
    ip_bytes = bytes(map(int, ip.split(".")))
    puerto_bytes = puerto.to_bytes(2, byteorder="big")
    mensaje_bytes = mensaje.encode("utf-8")

    return ip_bytes + puerto_bytes + mensaje_bytes


ip_destino = sys.argv[1]
puerto_destino = int(sys.argv[2])
mensaje = sys.argv[3]

ip_envio = sys.argv[4]
puerto_envio = int(sys.argv[5])

parsed_packet = (ip_destino, puerto_destino, mensaje)
packet = create_packet(parsed_packet)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(packet, (ip_envio, puerto_envio))
sock.close()
