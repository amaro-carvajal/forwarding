import sys
import socket

def parse_packet(IP_packet: bytes):
    ip_bytes = IP_packet[:4]
    puerto_bytes = IP_packet[4:6]
    ttl_bytes = IP_packet[6:7]
    mensaje_bytes = IP_packet[7:]

    ip = ".".join(map(str, ip_bytes))
    puerto = int.from_bytes(puerto_bytes, byteorder="big")
    ttl = int.from_bytes(ttl_bytes, byteorder="big")
    mensaje = mensaje_bytes.decode("utf-8")

    return (ip, puerto, ttl, mensaje)

def create_packet(parsed_IP_packet):
    ip, puerto, ttl, mensaje = parsed_IP_packet
    ip_bytes = bytes(map(int, ip.split(".")))
    puerto_bytes = puerto.to_bytes(2, byteorder="big")
    ttl_bytes = ttl.to_bytes(1, byteorder="big")
    mensaje_bytes = mensaje.encode("utf-8")

    return ip_bytes + puerto_bytes + ttl_bytes + mensaje_bytes

indices_rutas = {}

def check_routes(routes_file_name: str, destination_address: tuple[str, int]) -> tuple[str, int] | None:
    ip_destino, puerto_destino = destination_address

    rutas_posibles = []
    clave = None

    with open(routes_file_name, "r") as file:
        for linea in file:
            datos = linea.split()

            if not datos or datos[0].startswith("#"):
                continue

            red = datos[0]
            puerto_inicial = int(datos[1])
            puerto_final = int(datos[2])
            ip_siguiente = datos[3]
            puerto_siguiente = int(datos[4])

            ip_coincide = ip_destino == red.split("/")[0]
            puerto_coincide = puerto_inicial <= puerto_destino <= puerto_final

            if ip_coincide and puerto_coincide:
                clave_actual = (red, puerto_inicial, puerto_final)

                if clave is None:
                    clave = clave_actual

                if clave_actual == clave:
                    rutas_posibles.append((ip_siguiente, puerto_siguiente))

    if not rutas_posibles:
        return None

    indice = indices_rutas.get(clave, 0)
    next_hop = rutas_posibles[indice]

    indices_rutas[clave] = (indice + 1) % len(rutas_posibles)

    return next_hop

router_ip = sys.argv[1]
router_puerto = int(sys.argv[2])
router_rutas = sys.argv[3]

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((router_ip, router_puerto))

print(f"Router escuchando en {router_ip}:{router_puerto}")

while True:
    packet, sender_address = sock.recvfrom(4096)

    ip_destino, puerto_destino, ttl, mensaje = parse_packet(packet)

    if ttl == 0:
        print(f"Se recibió paquete {packet} con TTL 0")
        continue

    if (ip_destino, puerto_destino) == (router_ip, router_puerto):
        print(mensaje)
    else:
        destination_address = (ip_destino, puerto_destino)
        next_hop = check_routes(router_rutas, destination_address)

        if next_hop is not None:
            ttl = ttl - 1
            packet = create_packet((ip_destino, puerto_destino, ttl, mensaje))
            sock.sendto(packet, next_hop)
            print(f"redirigiendo paquete {packet} con destino final {destination_address} desde {(router_ip, router_puerto)} hacia {next_hop}")
            
        else:
            print(f"No hay rutas hacia {destination_address} para paquete {packet}")
