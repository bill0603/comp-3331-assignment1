import struct

class packet:
    def __init__(self, seq, ACK, ack, syn, fin, payload):
        self.seq = seq
        self.ACK = ACK
        self.flag = 0
        self.ack = ack
        self.syn = syn
        self.fin = fin
        if ack: 
            self.flag = self.flag | 4
        if syn:
            self.flag = self.flag | 2
        if fin:
            self.flag = self.flag | 1
        self.header = (self.seq, self.ACK, self.flag)
        self.payload = payload 
        self.byte_packet = struct.pack('3i', self.seq, self.ACK, self.flag) + self.payload
    
    def show_packet(self):
        print(
            'seq:', self.seq, 
            '\nACK:', self.ACK, 
            '\nack:', self.ack, 
            '\nsyn:', self.syn, 
            '\nfin:', self.fin, 
            '\npayload:', str(self.payload, encoding = 'utf-8')
        )

def parse_packet(received_byte_message):
    header = struct.unpack('3i', received_byte_message[:12])
    seq, ACK, flag = header
    ack = (flag & 4) >> 2
    syn = (flag & 2) >> 1
    fin = flag & 1
    payload = received_byte_message[12:]
    p = packet(seq, ACK, ack, syn, fin, payload)
    #p.show_packet()
    return p