import argparse
import sys
import os
import struct
import time
import math
import json
from lzw import lzw_encoder, lzw_decoder, lzw_decoder_variable, lzw_encoder_variable
from utils import BitStreamWriter, BitStreamReader

# Definição dos modos de compressão
MODE_FIXED = 0
MODE_VARIABLE = 1

OUTPUT_PATH = "out/"
COMPRESSED_PATH = f"{OUTPUT_PATH}compressed/"
DECOMPRESSED_PATH = f"{OUTPUT_PATH}decompressed/"

if not os.path.exists(COMPRESSED_PATH): os.makedirs(COMPRESSED_PATH)
if not os.path.exists(DECOMPRESSED_PATH): os.makedirs(DECOMPRESSED_PATH)

def calculate_compression_ratio(original_size, compressed_size):
    return 1 - (compressed_size / original_size)

def main():
    parser = argparse.ArgumentParser(description="Compressão e Descompressão de Arquivos usando LZW")
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-c', '--compress', action='store_true', help="Modo de compressão")
    group.add_argument('-x', '--decompress', action='store_true', help="Modo de descompressão")
    
    parser.add_argument('arquivo_entrada', help="Caminho para o arquivo de entrada")
    parser.add_argument('arquivo_saida', nargs='?', default=None, help="Caminho para o arquivo de saída (opcional)")
    
    parser.add_argument('--bits_max', type=int, default=12, help="Número máximo de bits para os códigos LZW (opcional, padrão=12)")
    parser.add_argument('--variable', action='store_true', help="Usar codificação de tamanho variável (opcional)")
    
    args = parser.parse_args()
    
    if args.compress:
        modo = 'compress'
    else:
        modo = 'decompress'
    
    arquivo_entrada = args.arquivo_entrada
    arquivo_saida = args.arquivo_saida
    bits_max = args.bits_max
    modo_codificacao = 'variable' if args.variable else 'fixed'
    
    if modo == "compress":
        if not arquivo_saida:
            base_name = os.path.splitext(os.path.basename(arquivo_entrada))[0]
            arquivo_saida = os.path.join(COMPRESSED_PATH, f"{base_name}.lzw")
        
        _, ext = os.path.splitext(arquivo_entrada)
        ext = ext[1:]
        ext_bytes = ext.encode('utf-8')
        ext_length = len(ext_bytes)

        try:
            with open(arquivo_entrada, 'rb') as f:
                data = f.read()
        except FileNotFoundError:
            print(f"Erro: Arquivo de entrada '{arquivo_entrada}' não encontrado.")
            sys.exit(1)
        except Exception as e:
            print(f"Erro ao ler o arquivo de entrada: {e}")
            sys.exit(1)

        print("Iniciando compressão...")
        inicio_compressao = time.time()
        if modo_codificacao == 'variable':
            encoded = lzw_encoder_variable(data, bits_max=bits_max)
        else:
            encoded = lzw_encoder(data, bits_max=bits_max)

        fim_compressao = time.time()

        try:
            with open(arquivo_saida, 'wb') as f:
                if ext_length > 255:
                    raise ValueError("Extensão muito longa para ser armazenada no cabeçalho.")
                f.write(struct.pack('B', ext_length))
                f.write(ext_bytes)
                mode_byte = MODE_VARIABLE if modo_codificacao == 'variable' else MODE_FIXED
                f.write(struct.pack('B', mode_byte))  # Escreve o modo
                
                writer = BitStreamWriter(f)
                current_bit_length = 9 if modo_codificacao == 'variable' else bits_max
                for code in encoded:
                    writer.write_bits(code, current_bit_length)
                    if modo_codificacao == 'variable' and code >= (1 << current_bit_length) - 1 and current_bit_length < bits_max:
                        current_bit_length += 1
                writer.flush()
        except Exception as e:
            print(f"Erro ao escrever o arquivo comprimido: {e}")
            sys.exit(1)

        tamanho_original = len(data)
        tamanho_comprimido = os.path.getsize(arquivo_saida)
        taxa_compressao = calculate_compression_ratio(tamanho_original, tamanho_comprimido)

        print("\n--- Estatísticas de Compressão ---")
        print(f"Tamanho original: {tamanho_original} bytes")
        print(f"Tamanho comprimido: {tamanho_comprimido} bytes")
        print(f"Taxa de compressão: {taxa_compressao * 100:.2f}%")
        print(f"Tempo de compressão: {fim_compressao - inicio_compressao:.2f}s")
        print(f"Arquivo comprimido salvo em: {arquivo_saida}")

    elif modo == "decompress":
        print('descompressão')
        if not arquivo_saida:
            try:
                with open(arquivo_entrada, 'rb') as f:
                    ext_length_packed = f.read(1)
                    if not ext_length_packed:
                        raise ValueError("Arquivo comprimido corrompido ou formato inválido.")
                    ext_length = struct.unpack('B', ext_length_packed)[0]
                    ext_bytes = f.read(ext_length)
                    ext = ext_bytes.decode('utf-8') if ext_length > 0 else ''
                    mode_byte_packed = f.read(1)
                    if not mode_byte_packed:
                        raise ValueError("Arquivo comprimido corrompido ou formato inválido.")
                    mode_byte = struct.unpack('B', mode_byte_packed)[0]
                    modo_codificacao = 'fixed' if mode_byte == MODE_FIXED else 'variable'
                    reader = BitStreamReader(f)
                    encoded = []
                    current_bit_length = 9 if modo_codificacao == 'variable' else bits_max
                    while True:
                            try:
                                code = reader.read_bits(current_bit_length)
                            except EOFError:
                                break
                            encoded.append(code)
                            # print(encoded)
                            # print(current_bit_length)

                            if modo_codificacao == 'variable' and code >= (1 << current_bit_length) - 1 and current_bit_length < bits_max:
                                current_bit_length += 1
                
                    print(current_bit_length)
                    with open('teste.txt', 'w') as teste:
                        teste.writelines(str(encoded))
                        
            except FileNotFoundError:
                print(f"Erro: Arquivo de entrada '{arquivo_entrada}' não encontrado.")
                sys.exit(1)
            except Exception as e:
                print(f"Erro ao ler o arquivo comprimido: {e}")
                sys.exit(1)

            base_name = os.path.splitext(os.path.basename(arquivo_entrada))[0]
            if ext:
                arquivo_saida = os.path.join(DECOMPRESSED_PATH, f"{base_name}.{ext}")
            else:
                arquivo_saida = os.path.join(DECOMPRESSED_PATH, f"{base_name}")
        else:
            try:
                with open(arquivo_entrada, 'rb') as f:
                    ext_length_packed = f.read(1)
                    if not ext_length_packed:
                        raise ValueError("Arquivo comprimido corrompido ou formato inválido.")
                    ext_length = struct.unpack('B', ext_length_packed)[0]
                    f.read(ext_length)
                    mode_byte_packed = f.read(1)
                    if not mode_byte_packed:
                        raise ValueError("Arquivo comprimido corrompido ou formato inválido.")
                    mode_byte = struct.unpack('B', mode_byte_packed)[0]
                    modo_codificacao = 'fixed' if mode_byte == MODE_FIXED else 'variable'
                    reader = BitStreamReader(f)
                    encoded = []
                    current_bit_length = 9 if modo_codificacao == 'variable' else bits_max
                    while True:
                        # print("leitura dos codes, caminho 2")
                        code = reader.read_bits(current_bit_length)
                        if code is None:
                            break
                        encoded.append(code)
                        if modo_codificacao == 'variable' and code >= (1 << current_bit_length) - 1 and current_bit_length < bits_max:
                            current_bit_length += 1
            except FileNotFoundError:
                print(f"Erro: Arquivo de entrada '{arquivo_entrada}' não encontrado.")
                sys.exit(1)
            except Exception as e:
                print(f"Erro ao ler o arquivo comprimido: {e}")
                sys.exit(1)

        print("Iniciando descompressão...")
        inicio_descompressao = time.time()
        
        try:
            decoded = lzw_decoder_variable(encoded, bits_max=bits_max)
        except Exception as e:
            print(f"Erro durante a descompressão: {e}")
            sys.exit(1)
        
        fim_descompressao = time.time()

        try:
            with open(arquivo_saida, 'wb') as f:
                f.write(decoded)
        except Exception as e:
            print(f"Erro ao escrever o arquivo descomprimido: {e}")
            sys.exit(1)

        print("\n--- Estatísticas de Descompressão ---")
        print(f"Tamanho do arquivo descomprimido: {len(decoded)} bytes")
        print(f"Tempo de descompressão: {fim_descompressao - inicio_descompressao:.2f}s")
        print(f"Arquivo descomprimido salvo em: {arquivo_saida}")

if __name__ == "__main__":
    main()
