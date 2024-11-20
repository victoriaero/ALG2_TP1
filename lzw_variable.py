import trie as t

def lzw_encoder_variable(data, writer, bits_max=16):
    trie = t.Trie()
    bits = 9
    max_code = (1 << bits) - 1
    next_code = 256

    for byte in range(256):
        trie.insert(bytes([byte]), byte)
    
    sequence = b""

    for byte in data:
        new_sequence = sequence + bytes([byte])
        if trie.search(new_sequence) is not None:
            sequence = new_sequence
        else:
            code = trie.search(sequence)
            if code is not None:
                writer.write_bits(code, bits)
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
    
    if sequence:
        code = trie.search(sequence)
        if code is not None:
            writer.write_bits(code, bits)
    
    writer.flush()

def lzw_decoder_variable(reader, bits_max=16):
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
            code_to_sequence[next_code] = sequence + bytes([entry[0]])
            next_code += 1
            if next_code > max_code and bits < bits_max:
                bits += 1
                max_code = (1 << bits) - 1
            sequence = entry
        except EOFError:
            break
    
    return bytes(decoded)