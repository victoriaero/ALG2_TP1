# lzw.py

import trie as t

def lzw_encoder(data):
    trie = t.Trie()
    next_code = 256
    for byte in range(256):
        trie.insert(bytes([byte]), byte)
    
    sequence = b""
    encoded = []
    for byte in data:
        # Cria uma nova sequência adicionando o byte atual
        new_sequence = sequence + bytes([byte])
        if trie.search(new_sequence) is not None:
            sequence = new_sequence
        else:
            # Adiciona o código da sequência atual ao resultado codificado
            code = trie.search(sequence)
            if code is not None:
                encoded.append(code)
            # Adiciona a nova sequência à Trie
            trie.insert(new_sequence, next_code)
            next_code += 1
            # Reinicia a sequência com o byte atual
            sequence = bytes([byte])
    
    # Adiciona o último código, se houver
    if sequence:
        code = trie.search(sequence)
        if code is not None:
            encoded.append(code)
    
    return encoded

def lzw_decoder(encoded):
    if not encoded:
        return b""
    
    code_to_sequence = {i: bytes([i]) for i in range(256)}
    next_code = 256

    # Inicializa com a primeira sequência
    sequence = code_to_sequence[encoded[0]]
    decoded = bytearray(sequence)

    for code in encoded[1:]:
        if code in code_to_sequence:
            entry = code_to_sequence[code]
        elif code == next_code:
            # Caso especial conforme o algoritmo LZW
            entry = sequence + bytes([sequence[0]])
        else:
            raise ValueError("Código inválido durante a decodificação")
        
        decoded.extend(entry)
        # Adiciona uma nova sequência à tabela
        code_to_sequence[next_code] = sequence + bytes([entry[0]])
        next_code += 1
        # Atualiza a sequência atual
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
