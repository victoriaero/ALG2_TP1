import trie as t

def lzw_encoder(data):
    trie = t.Trie()
    next_code = 256
    for i in range(256):
        trie.insert(chr(i), i)

    sequence = ""
    encoded = []
    for char in data:
        if trie.search(sequence + char) is not None:
            sequence += char
        else:
            encoded.append(trie.search(sequence))
            trie.insert(sequence + char, next_code)
            next_code += 1
            sequence = char

    if sequence:
        encoded.append(trie.search(sequence))

    return encoded

def lzw_decoder(encoded):
    code_to_sequence = {i: chr(i) for i in range(256)}
    next_code = 256

    sequence = code_to_sequence[encoded[0]]
    decoded = [sequence]

    for code in encoded[1:]:
        if code in code_to_sequence:
            entry = code_to_sequence[code]
        else:
            entry = sequence + sequence[0]

        decoded.append(entry)
        code_to_sequence[next_code] = sequence + entry[0]
        next_code += 1
        sequence = entry

    return "".join(decoded)

if __name__ == "__main__":
    # EXEMPLO DE USO DA ESTRUTURA DE ÁRVORE DE PREFIXOS    
    text = "ABABABABAABABABABAABABABABA"
    print("Texto original:", text)

    encoded = lzw_encoder(text)
    print("\nTexto codificado:")
    print(encoded)

    decoded = lzw_decoder(encoded)
    print("\nTexto decodificado:")
    print(decoded)

    if text == decoded:
        print("\nA decodificação corresponde ao texto original!")
    else:
        print("\nErro: A decodificação não corresponde ao texto original.")