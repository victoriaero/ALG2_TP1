
class Bit_writer:
    # classe que auxilia a escrita de dados para o lzw variavel
    def __init__(self, file):
        self.file = file
        self.buffer = 0
        self.nbits = 0
    
    # adiciona em um buffer com deslocamento a esq para liberar espaço pra mais bits
    def write_bits(self, value, bit_length):
        self.buffer = (self.buffer << bit_length) | value
        self.nbits += bit_length
        while self.nbits >= 8: 
            self.nbits -= 8
            # extrai o byte mais significativo do buffer
            byte = (self.buffer >> self.nbits) & 0xFF
            self.file.write(byte.to_bytes(1, byteorder='big')) # escreve no arquivo
    
    def flush(self): # esvazia o buffer
        # preenche os bits restantes com zeros na dir para formar um byte
        if self.nbits > 0: 
            byte = (self.buffer << (8 - self.nbits)) & 0xFF
            self.file.write(byte.to_bytes(1, byteorder='big')) # escreve
            self.buffer = 0
            self.nbits = 0

class Bit_reader:
    # classe que auxilia a leitura de dados para o lzw variavel
    def __init__(self, file):
        self.file = file
        self.buffer = 0
        self.nbits = 0
    
    def read_bits(self, bit_length):
        while self.nbits < bit_length:
            byte = self.file.read(1) # le um byte
            if not byte: # final do arquivo atingido
                if self.nbits == 0:
                    return None
                else:
                    raise EOFError("Final inesperado do arquivo.")
            # adiciona byte ao buffer, deslocando os bits atuais pra esq
            self.buffer = (self.buffer << 8) | byte[0]
            self.nbits += 8
        self.nbits -= bit_length # remove os bits lidos do contador
        value = (self.buffer >> self.nbits) & ((1 << bit_length) - 1) # pega o valor
        return value
