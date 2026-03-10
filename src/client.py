import socket, struct, zlib
from urllib.parse import urlsplit
class Client :
    def __init__(self, msg):
        self.msg = msg

    def parse_url(self, url: str) :
        url_parse = urlsplit(url)

        hostname = url_parse.hostname
        port = url_parse.port
        path = url_parse.path
        return hostname, port, path

    def create_and_send_message(self, server_addr: str, server_port: int):
        sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        peer_addr = (server_addr, server_port)
        sock.connect(peer_addr)
        
        data = self.msg.encode("utf-8")

        sock.send(data)

        sock.close()
    
    def encode_packet(self, type:int, window:int, seqnum:int, length:int, timestamp:int, payload=b'') :
        premiere_ligne = (type << 30) | (window << 24) | (seqnum << 13) | length
        header_sansCRC1 = struct.pack("!II", premiere_ligne, timestamp)
        CRC1_unmasked = zlib.crc32(header_sansCRC1)
        crc1 = CRC1_unmasked & 0xFFFFFFFF # Cela évite d'avoir des valeurs négatives, ce qui causerait un overflowerror
        header = header_sansCRC1 + struct.pack("!I", crc1) # On fait pas un grand struct.pack avec les deux car header_sansCRC1 est déjà en byte, on aurait une erreur "received byte, wished for int"

        if payload :
            crc2_unmasked = zlib.crc32(payload)
            crc2 = crc2_unmasked & 0xFFFFFFFF # Pareil qu'avant, on applique un masque pour éviter les valeurs négatives
            packet = header + payload + struct.pack("!I", crc2)
            return packet
        return header # On retourne juste le header si payload est vide



if __name__ == "__main__" :
    client = Client("hello")
    client.create_and_send_message("::1", 8080)