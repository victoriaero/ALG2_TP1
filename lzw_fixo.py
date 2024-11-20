import trie as t

def lzw_encoder(data, bits_max):
    trie = t.Trie()
    max_code = (1 << bits_max) - 1
    next_code = 256
    for byte in range(256):
        trie.insert(bytes([byte]), byte)
    
    sequence = b""
    encoded = []
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
            sequence = bytes([byte])
    
    if sequence:
        code = trie.search(sequence)
        if code is not None:
            encoded.append(code)
    
    return encoded

def lzw_decoder(encoded, bits_max):
    if not encoded:
        return b""
    
    max_code = (1 << bits_max) - 1
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
        sequence = entry
    
    return bytes(decoded)

if __name__ == "__main__":
    # EXEMPLO DE USO DO ENCODER/DECODER FIXOS  
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
