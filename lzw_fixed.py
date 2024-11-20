import trie as t
import time
import sys

def lzw_encoder(data, bits_max):
    start_time = time.time()
    trie = t.Trie()
    max_code = (1 << bits_max) - 1
    next_code = 256
    for byte in range(256):
        trie.insert(bytes([byte]), byte) # inserindo na trie os primeiros bytes
    
    sequence = b""
    encoded = []
    for byte in data: 
        # o loop irá percorrer os dados em busca das maiores sequencias que ja estao no trie
        # se ele chegar em uma seq que nao está na trie, adiciona o codigo da lista atual no encoded
        # e insere nova seq no trie com o prox cod disponível
        # por fim reinicia sequencia para o byte atual
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

    trie_size = trie.get_size()
    memory_usage = sys.getsizeof(trie)
    execution_time = time.time() - start_time

    metrics = {
        "dictionary_size": trie_size,
        "memory_usage": memory_usage,
        "execution_time": execution_time
    }

    return encoded, metrics

def lzw_decoder(encoded, bits_max):
    start_time = time.time()
    if not encoded:
        return b""
    
    max_code = (1 << bits_max) - 1
    code_to_sequence = {i: bytes([i]) for i in range(256)} # inicia dicionario
    next_code = 256

    sequence = code_to_sequence[encoded[0]]
    decoded = bytearray(sequence) # reconstroi seq original

    for code in encoded[1:]:
        # se o codigo ja existir no dicionario, usa a sequencia existente
        # se o codigo for o proximo esperado, concatena a primeira letra da seq anterior
        # adiciona a seq decodificada em decoded e atualiza o dicionario com nova entrada 

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
    
    dictionary_size = len(code_to_sequence)
    memory_usage = sys.getsizeof(code_to_sequence)
    execution_time = time.time() - start_time

    metrics = {
        "dictionary_size": dictionary_size,
        "memory_usage": memory_usage,
        "execution_time": execution_time
    } 

    return bytes(decoded), metrics