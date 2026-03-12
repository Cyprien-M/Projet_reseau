import socket, struct, zlib, argparse, sys
from urllib.parse import urlsplit
import time
class Client :
    def __init__(self, url:str, save_path : str="llm.model"):
        self.sock = socket.socket(socket.AF_INET6,socket.SOCK_DGRAM)
        self.hostname, self.port, self.path = self.parse_url(url)
        self.save_path = save_path
        self.peer_addr = (self.hostname, self.port)
        self.sock.connect(self.peer_addr)


    def parse_url(self, url: str) :
        url_parse = urlsplit(url)

        hostname = url_parse.hostname
        port = url_parse.port
        path = url_parse.path
        return hostname, port, path

    
    def encode_packet(self, type:int, window:int, seqnum:int, length:int, timestamp:int, payload=b'') :
        premiere_ligne = (type << 30) | (window << 24) | (length << 11) | seqnum 
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
    

    def send_and_receive(self, timeout: float = 5.0):
        self.sock.settimeout(timeout) #5.0 ici parce que j'ai envie
        payload = self.path.encode("utf-8")
        timestamp = int(time.time()) & 0xFFFFFFFF

        paquet= self.encode_packet(
            type=1,
            window= 4,
            seqnum=0,
            length=len(payload),
            timestamp=timestamp,
            payload=payload
        )
        self.sock.send(paquet)
        print("envoyé")
        print(f"{self.path}")
        try:
            data= self.sock.recv(65535)
            # décode  la réponse
            bits= bin(int(data.hex(), 16))[2:].zfill(len(data) *8)
            length_recu = int(bits[8:21], 2)
            payload_bits =bits[96: 96 +length_recu* 8]
            if payload_bits:
                payload_bytes= int(payload_bits, 2).to_bytes(length_recu, byteorder='big')
                print(f"reçu :'{payload_bytes.decode('utf-8')}'")

        except socket.timeout:
            print("timeout")
        finally:
            self.sock.close()




if __name__ == "__main__" :
    arg_parse = argparse.ArgumentParser()
    arg_parse.add_argument("url")
    arg_parse.add_argument("--save", default="llm.model")
    args = arg_parse.parse_args()
    client = Client(args.url, args.save)
    client.send_and_receive()