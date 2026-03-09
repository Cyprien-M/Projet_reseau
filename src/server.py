import struct
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

    m.type = int(bits[0:2],2)
    m.window = int(bits[2:8],2)
    m.length = int(bits[8:21],2)
    m.seqnum = int(bits[21:32],2)

    m.timestamp = int(bits[32:64],2)
    m.crc1 = int(bits[64:96],2)

    payload_start = 96
    payload_end = payload_start + m.length*8

    m.payload = bits[payload_start:payload_end]

    crc2_start = payload_end
    crc2_end = crc2_start + 32

    m.crc2 = int(bits[crc2_start:crc2_end],2)

    print(hex(int(m.payload, 2)))

coupage(b'J\x00(\x00\x124Vx\x9f\xa1+<hello6\x10\xa6\x86')