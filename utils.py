# bitstream.py

class BitStreamWriter:
    def __init__(self, file):
        self.file = file
        self.buffer = 0
        self.nbits = 0
    
    def write_bits(self, value, bit_length):
        self.buffer = (self.buffer << bit_length) | value
        self.nbits += bit_length
        while self.nbits >= 8:
            self.nbits -= 8
            byte = (self.buffer >> self.nbits) & 0xFF
            self.file.write(byte.to_bytes(1, byteorder='big'))
    
    def flush(self):
        if self.nbits > 0:
            byte = (self.buffer << (8 - self.nbits)) & 0xFF
            self.file.write(byte.to_bytes(1, byteorder='big'))
            self.buffer = 0
            self.nbits = 0

class BitStreamReader:
    def __init__(self, file):
        self.file = file
        self.buffer = 0
        self.nbits = 0
    
    def read_bits(self, bit_length):
        while self.nbits < bit_length:
            byte = self.file.read(1)
            if not byte:
                if self.nbits == 0:
                    return None
                else:
                    raise EOFError("Unexpected end of file.")
            self.buffer = (self.buffer << 8) | byte[0]
            self.nbits += 8
        self.nbits -= bit_length
        value = (self.buffer >> self.nbits) & ((1 << bit_length) - 1)
        return value
