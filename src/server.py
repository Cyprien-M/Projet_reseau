import struct
import socket
import zlib
# 256
class messages:
    def __init__(self):
        self.type = None
        self.window = None
        self.seqnum = None
        self.length = None
        self.timestamp = None
        self.crc1 = None
        self.payload = None
        self.crc2 = None

def coupage(data):
    # m = messages()
    # hex = data.hex()
    # d = int(hex,16)
    # bits = bin(d)[2:]
    # m.type = int(bits[0:2],2)
    # m.window = int(bits[2:8],2)
    # m.seqnum = int(bits[8:19],2)
    # m.length = int(bits[19:32],2)
    # m.timestamp = int(bits[32:64],2)
    # m.crc1 = int(bits[64:96],2)
    # m.payload = int(bits[96:96+(1024*8)],2)
    # m.crc2 = int(bits[96+(1024*8):(96+(1024*8)+(4*8))],2)
    # print(m.type)
    m = messages()

    hexa = data.hex()
    d = int(hexa,16)
    bits = bin(d)[2:].zfill(len(data)*8)

    m.type = int(bits[0:2],2) #2 bits
    m.window = int(bits[2:8],2) #6 bits
    m.length = int(bits[8:21],2) #13 bits
    m.seqnum = int(bits[21:32],2) #11bits

    m.timestamp = int(bits[32:64],2) #32 bits
    m.crc1 = int(bits[64:96],2) #32 bits

    payload_start = 96
    payload_end = payload_start + m.length*8

    m.payload = bits[payload_start:payload_end]

    crc2_start = payload_end
    crc2_end = crc2_start + 32

    if len(bits[crc2_start:crc2_end]) == 32:
        m.crc2 = int(bits[crc2_start:crc2_end],2)
    if m.payload:
        print(hex(int(m.payload, 2)))
    return m #rajouter ça pour l'utiliser


def encode_packet(type:int, window:int, seqnum:int, length:int, timestamp:int, payload=b'') :
    premiere_ligne = (type << 30) | (window << 24) | (length<< 11) |seqnum  #modfié length en 11 au lieu de 13
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

def verify_crc1(data: bytes):
    header_sansCRC1 = data[:8]
    crc1_recu =struct.unpack("!I", data[8:12])[0]
    crc1_calcule = zlib.crc32(header_sansCRC1) & 0xFFFFFFFF
    return crc1_recu == crc1_calcule

def verify_crc2(payload_bytes: bytes, data: bytes, length: int):
    crc2_offset = 12 + length
    if len(data) < crc2_offset + 4:
        return False
    crc2_recu = struct.unpack("!I", data[crc2_offset:crc2_offset + 4])[0]
    crc2_calcule = zlib.crc32(payload_bytes) & 0xFFFFFFFF
    return crc2_recu == crc2_calcule

def start_server(host: str = "::1", port: int = 8080):
    sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    sock.bind((host, port, 0, 0))
    while True:
        data, addr = sock.recvfrom(65535)
        print(addr)
        print("reçu")
        try:
            if not verify_crc1(data):
                print("CRC1 invalide, paquet ignoré")
                continue
            msg = coupage(data)
            # Décode le payload en texte si ya un message
            if msg.payload:
                payload_bytes = int(msg.payload, 2).to_bytes(msg.length, byteorder='big')
                if not verify_crc2(payload_bytes, data, msg.length):
                    print("CRC2 invalide, payload ignoré")
                    continue
                try:
                    texte = payload_bytes.decode("utf-8")
                    print(f"message reçu: {texte}")
                except UnicodeDecodeError:
                    texte = None
                # encode le message et le renvoie au client
                reponse = encode_packet(
                    type=msg.type,
                    window=msg.window,
                    seqnum=msg.seqnum,
                    length=msg.length,
                    timestamp=msg.timestamp,
                    payload=payload_bytes
                )
                print(f"{reponse}")
                print(f"{addr}")   #addresse à laquelle il renvoie
                sock.sendto(reponse, addr)
                
        except Exception as e:
            print(f"erreur : {e}")


if __name__ == "__main__":
    start_server()

coupage(b'J\x00(\x00\x124Vx\x9f\xa1+<hello6\x10\xa6\x86')