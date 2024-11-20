import trie as t
import struct

class BitStreamWriter:
    def __init__(self, file):
        self.file = file
        self.buffer = 0
        self.nbits = 0
    
    def write_bits(self, value, bit_length):
        """Escreve `bit_length` bits do valor `value` no fluxo de bits."""
        self.buffer = (self.buffer << bit_length) | value
        self.nbits += bit_length
        while self.nbits >= 8:
            self.nbits -= 8
            byte = (self.buffer >> self.nbits) & 0xFF
            self.file.write(byte.to_bytes(1, byteorder='big'))
    
    def flush(self):
        """Flusha os bits restantes no buffer."""
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
        """Lê `bit_length` bits do fluxo de bits."""
        while self.nbits < bit_length:
            byte = self.file.read(1)
            if not byte:
                if self.nbits == 0:
                    return None
                else:
                    raise EOFError("Final inesperado do arquivo.")
            self.buffer = (self.buffer << 8) | byte[0]
            self.nbits += 8
        self.nbits -= bit_length
        value = (self.buffer >> self.nbits) & ((1 << bit_length) - 1)
        return value

def lzw_encoder_variable(data, writer, bits_max=16):
    """
    Codifica os dados usando o algoritmo LZW com bit-length variável e escreve diretamente no BitStreamWriter.
    
    :param data: Dados binários a serem codificados.
    :param writer: Instância de BitStreamWriter para escrever os códigos.
    :param bits_max: Bit-length máximo.
    """
    trie = t.Trie()
    bits = 9
    max_code = (1 << bits) - 1  # Inicialmente 511 para 9 bits
    next_code = 256

    # Inicializa o dicionário com todos os bytes possíveis
    for byte in range(256):
        trie.insert(bytes([byte]), byte)
    
    sequence = b""

    for byte in data:
        new_sequence = sequence + bytes([byte])  # Concatenando
        if trie.search(new_sequence) is not None:
            sequence = new_sequence
        else:
            code = trie.search(sequence)
            if code is not None:
                writer.write_bits(code, bits)  # Escreve o código com o bit-length atual
            if next_code <= max_code and bits <= bits_max:
                trie.insert(new_sequence, next_code)
                next_code += 1
            else:
                if bits < bits_max:
                    bits += 1
                    max_code = (1 << bits) - 1
                    if next_code <= max_code:
                        trie.insert(new_sequence, next_code)
                        next_code += 1
            sequence = bytes([byte])
    
    # Escreve o último código restante
    if sequence:
        code = trie.search(sequence)
        if code is not None:
            writer.write_bits(code, bits)
    
    writer.flush()

def lzw_decoder_variable(reader, bits_max=16):
    """
    Decodifica os dados usando o algoritmo LZW com bit-length variável lendo diretamente do BitStreamReader.
    
    :param reader: Instância de BitStreamReader para ler os códigos.
    :param bits_max: Bit-length máximo.
    :return: Dados decodificados em bytes.
    """
    bits = 9
    max_code = (1 << bits) - 1
    code_to_sequence = {i: bytes([i]) for i in range(256)}
    next_code = 256

    first_code = reader.read_bits(bits)
    if first_code is None:
        return b""
    sequence = code_to_sequence.get(first_code, None)
    if sequence is None:
        raise ValueError("Código inválido no início da decodificação.")
    decoded = bytearray(sequence)
    
    while True:
        try:
            code = reader.read_bits(bits)
            if code is None:
                break
            if code in code_to_sequence:
                entry = code_to_sequence[code]
            elif code == next_code:
                entry = sequence + bytes([sequence[0]])
            else:
                raise ValueError(f"Código inválido durante a decodificação: {code}")
            decoded.extend(entry)
            # Adiciona nova entrada ao dicionário
            code_to_sequence[next_code] = sequence + bytes([entry[0]])
            next_code += 1
            # Atualiza bit-length se necessário
            if next_code > max_code and bits < bits_max:
                bits += 1
                max_code = (1 << bits) - 1
            sequence = entry
        except EOFError:
            break
    
    return bytes(decoded)

if __name__ == "__main__":
    # Definir nomes de arquivos
    arquivo_entrada = "teste2.txt"
    arquivo_comprimido = "compressed2.lzw"
    arquivo_saida = "arquivo_saida2"

    # EXTENSÃO DO ARQUIVO ORIGINAL
    ext = 'txt'
    ext_bytes = ext.encode('utf-8')
    ext_length = len(ext_bytes)

    # Compressão
    with open(arquivo_entrada, 'rb') as file:
        data = file.read()

    with open(arquivo_comprimido, 'wb') as comp:
        # Escrever o comprimento da extensão (1 byte)
        comp.write(struct.pack('B', ext_length))
        # Escrever a extensão
        comp.write(ext_bytes)
        # Escrever os códigos comprimidos com bit-length variável
        writer = BitStreamWriter(comp)
        lzw_encoder_variable(data, writer, bits_max=16)

    # Descompressão
    with open(arquivo_comprimido, "rb") as input_file:
        # Ler o comprimento da extensão (1 byte)
        ext_length_packed = input_file.read(1)
        if not ext_length_packed:
            raise ValueError("Arquivo comprimido corrompido ou formato inválido.")
        ext_length = struct.unpack('B', ext_length_packed)[0]

        # Ler a extensão
        ext_bytes = input_file.read(ext_length)
        ext = ext_bytes.decode('utf-8') if ext_length > 0 else ''

        # Ler os códigos comprimidos
        reader = BitStreamReader(input_file)
        decoded = lzw_decoder_variable(reader, bits_max=16)

        # Escrever o arquivo descomprimido
        with open(f"{arquivo_saida}.{ext}", 'wb') as f:
            f.write(decoded)

    print("Compressão e descompressão concluídas com sucesso.")
