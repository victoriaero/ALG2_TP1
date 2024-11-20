import trie as t

def lzw_encoder(data, bits_max=12):
    trie = t.Trie()
    max_code = (1 << bits_max) - 1
    next_code = 256
    for byte in range(256):
        trie.insert(bytes([byte]), byte)
    
    sequence = b""
    encoded = []
    bit_length = 9  # Inicialmente 9 bits para modo variável
    dynamic = (mode == 'variable')

    for byte in data:
        new_sequence = sequence + bytes([byte])
        if trie.search(new_sequence) is not None:
            sequence = new_sequence
        else:
            code = trie.search(sequence)
            if code is not None:
                encoded.append(code)
            if next_code <= max_code:
                trie.insert(new_sequence, next_code)
                next_code += 1
                if dynamic and next_code >= (1 << bit_length) and bit_length < bits_max:
                    bit_length += 1
            sequence = bytes([byte])
    
    if sequence:
        code = trie.search(sequence)
        if code is not None:
            encoded.append(code)
    
    return encoded, bits_max

def lzw_decoder(encoded, bits_max=12):
    if not encoded:
        return b""
    
    max_code = (1 << bits_max) - 1
    code_to_sequence = {i: bytes([i]) for i in range(256)}
    next_code = 256
    bit_length = 9
    dynamic = (mode == 'variable')
    
    # Iniciar com o primeiro código
    first_code = encoded[0]
    if first_code not in code_to_sequence:
        raise ValueError("Código inválido no início da decodificação")
    sequence = code_to_sequence[first_code]
    decoded = bytearray(sequence)
    
    for code in encoded[1:]:
        if code in code_to_sequence:
            entry = code_to_sequence[code]
        elif code == next_code:
            entry = sequence + bytes([sequence[0]])
        else:
            raise ValueError("Código inválido durante a decodificação")
        
        decoded.extend(entry)
        
        if next_code <= max_code:
            code_to_sequence[next_code] = sequence + bytes([entry[0]])
            next_code += 1
            if dynamic and next_code >= (1 << bit_length) and bit_length < bits_max:
                bit_length += 1
        sequence = entry
    
    return bytes(decoded)


def lzw_encoder_variable(data, bits_max=12):
    trie = t.Trie()
    bits = 9
    max_code = (1 << bits) - 1 # maior numero q pode ser representado em 9 bits
    next_code = 256

    for byte in range(256):
        trie.insert(bytes([byte]), byte)
    
    sequence = b""
    encoded = []
    
    for byte in data:
        new_sequence = sequence + bytes([byte]) # concatenação
        if trie.search(new_sequence) is not None:
            sequence = new_sequence
        else:
            code = trie.search(sequence) # refazendo por robustez (pra garantir que ta de fato)
            if code is not None: 
                encoded.append(code) 
            if next_code <= max_code:
                trie.insert(new_sequence, next_code)
                next_code += 1
            else:
                if bits < bits_max:
                    bits += 1
                    max_code = (1 << bits) - 1
            sequence = bytes([byte])
    
    if sequence:
        code = trie.search(sequence)
        if code is not None:
            encoded.append(code)
    
    # print("bits:", bits, "e max_code:", max_code)
    return encoded, bits

def lzw_decoder_variable(encoded, bits_max=16):
    if not encoded:
        return b""
    
    bits = 9
    max_code = (1 << bits) - 1
    code_to_sequence = {i: bytes([i]) for i in range(256)}
    next_code = 256

    sequence = code_to_sequence[encoded[0]]
    decoded = bytearray(sequence)

    for code in encoded[1:]:
        if code in code_to_sequence:
            entry = code_to_sequence[code]
        elif code == next_code:
            entry = sequence + bytes([sequence[0]])
        else:
            raise ValueError("Código inválido durante a decodificação")
        
        decoded.extend(entry)
        if next_code <= max_code:
            code_to_sequence[next_code] = sequence + bytes([entry[0]])
            next_code += 1
        else:
            if bits < bits_max:
                bits += 1
                max_code = (1 << bits) - 1
        sequence = entry
    
    return bytes(decoded)


if __name__ == "__main__":
    # EXEMPLO DE USO DA ESTRUTURA DE ÁRVORE DE PREFIXOS    
    text = "ABABABABAABABABABAABABABABA".encode('utf-8')
    print("Texto original:", text)
    
    encoded = lzw_encoder(text)
    print("\nTexto codificado:")
    print(encoded)
    
    decoded = lzw_decoder(encoded)
    print("\nTexto decodificado:")
    print(decoded.decode('utf-8'))
    
    if text == decoded:
        print("\nA decodificação corresponde ao texto original!")
    else:
        print("\nErro: A decodificação não corresponde ao texto original.")
