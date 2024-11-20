import trie as t
import time
import sys

def lzw_encoder_variable(data, writer, bits_max=16):
    start_time = time.time()
    trie = t.Trie()
    bits = 9
    max_code = (1 << bits) - 1
    next_code = 256

    for byte in range(256):
        trie.insert(bytes([byte]), byte) # forma a trie
    
    sequence = b""

    for byte in data: # percorre os dados procurando a maior sequência que já existe na trie
        new_sequence = sequence + bytes([byte]) # concatena prox bite com sequência atual
        if trie.search(new_sequence) is not None: # se existir no dicionario, expande ela
            sequence = new_sequence
        else:
            code = trie.search(sequence)
            if code is not None:
                writer.write_bits(code, bits)
            if next_code <= max_code and bits <= bits_max:
                trie.insert(new_sequence, next_code)
                next_code += 1
            else:
                # se o dicionario está cheio e ainda podemos aumentar os bits
                if bits < bits_max:
                    bits += 1
                    max_code = (1 << bits) - 1 # atualiza o maior codigo possivel com novos bits
                    # insere a prox sequencia com o mesmo codigo se ainda for possível
                    if next_code <= max_code:
                        trie.insert(new_sequence, next_code)
                        next_code += 1
            sequence = bytes([byte])
    
    if sequence:
        code = trie.search(sequence)
        if code is not None:
            writer.write_bits(code, bits)
    
    writer.flush()

    execution_time = time.time() - start_time
    dictionary_size = trie.get_size()
    memory_usage = sys.getsizeof(trie)

    metrics = {
        "dictionary_size": dictionary_size,
        "memory_usage": memory_usage,
        "execution_time": execution_time
    }

    return metrics


def lzw_decoder_variable(reader, bits_max=16):
    start_time = time.time()
    bits = 9
    max_code = (1 << bits) - 1
    code_to_sequence = {i: bytes([i]) for i in range(256)}
    next_code = 256

    first_code = reader.read_bits(bits)
    if first_code is None:
        return b""
    sequence = code_to_sequence.get(first_code, None) # seq inicial a partir do primeiro codigo
    if sequence is None:
        raise ValueError("Código inválido no início da decodificação.")
    decoded = bytearray(sequence)
    
    # processando proximos codigos
    while True:
        try:
            code = reader.read_bits(bits)
            if code is None:
                break
            if code in code_to_sequence: # verifica se esta no dicionario
                entry = code_to_sequence[code] # obtem seq correspondente
            elif code == next_code:
                entry = sequence + bytes([sequence[0]]) # se o codigo for igual ao prox disponivel, concatena
            else:
                raise ValueError(f"Código inválido durante a decodificação: {code}")
            decoded.extend(entry)
            # adiciona nova seq ao dicionario
            code_to_sequence[next_code] = sequence + bytes([entry[0]])
            next_code += 1

            # ajuste dinamico do num de bits se preciso
            if next_code > max_code and bits < bits_max:
                bits += 1
                max_code = (1 << bits) - 1 # atualiza maior codigo possivel com novos bits
            sequence = entry
        except EOFError:
            break

    execution_time = time.time() - start_time
    dictionary_size = len(code_to_sequence)
    memory_usage = sys.getsizeof(code_to_sequence)
    
    metrics = {
        "dictionary_size": dictionary_size,
        "memory_usage": memory_usage,
        "execution_time": execution_time
    }

    return bytes(decoded), metrics