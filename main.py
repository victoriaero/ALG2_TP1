import argparse
import sys
import os
import struct
import time
from lzw import lzw_encoder, lzw_decoder

OUTPUT_PATH = "out/"

if not os.path.exists(OUTPUT_PATH):
    os.makedirs(OUTPUT_PATH)

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
    
    args = parser.parse_args()
    
    if args.compress:
        modo = 'compress'
    else:
        modo = 'decompress'
    
    arquivo_entrada = args.arquivo_entrada
    arquivo_saida = args.arquivo_saida
    bits_max = args.bits_max
    
    if modo == "compress":
        if not arquivo_saida:
            base_name = os.path.splitext(os.path.basename(arquivo_entrada))[0]
            arquivo_saida = os.path.join(OUTPUT_PATH, f"{base_name}_compressed.z78")
        
        _, ext = os.path.splitext(arquivo_entrada)
        ext = ext[1:]  # Remove o ponto
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
        encoded = lzw_encoder(data, bits_max=bits_max)
        fim_compressao = time.time()

        try:
            with open(arquivo_saida, 'wb') as f:
                if ext_length > 255:
                    raise ValueError("Extensão muito longa para ser armazenada no cabeçalho.")
                f.write(struct.pack('B', ext_length))
                f.write(ext_bytes)
                for code in encoded:
                    if 0 <= code <= 65535:
                        f.write(struct.pack('>H', code))
                    else:
                        raise ValueError(f"Código LZW {code} excede o limite de 65535.")
        except Exception as e:
            print(f"Erro ao escrever o arquivo comprimido: {e}")
            sys.exit(1)

        tamanho_original = len(data)
        tamanho_comprimido = 1 + ext_length + len(encoded) * 2
        taxa_compressao = calculate_compression_ratio(tamanho_original, tamanho_comprimido)

        print("\n--- Estatísticas de Compressão ---")
        print(f"Tamanho original: {tamanho_original} bytes")
        print(f"Tamanho comprimido: {tamanho_comprimido} bytes")
        print(f"Taxa de compressão: {taxa_compressao * 100:.2f}%")
        print(f"Tempo de compressão: {fim_compressao - inicio_compressao:.2f}s")
        print(f"Arquivo comprimido salvo em: {arquivo_saida}")

    elif modo == "decompress":
        if not arquivo_saida:
            try:
                with open(arquivo_entrada, 'rb') as f:
                    ext_length_packed = f.read(1)
                    if not ext_length_packed:
                        raise ValueError("Arquivo comprimido corrompido ou formato inválido.")
                    ext_length = struct.unpack('B', ext_length_packed)[0]
                    ext_bytes = f.read(ext_length)
                    ext = ext_bytes.decode('utf-8') if ext_length > 0 else ''
                    encoded = []
                    while True:
                        chunk = f.read(2)
                        if not chunk:
                            break
                        if len(chunk) != 2:
                            raise ValueError("Arquivo comprimido corrompido ou formato inválido.")
                        code = struct.unpack('>H', chunk)[0]
                        encoded.append(code)
            except FileNotFoundError:
                print(f"Erro: Arquivo de entrada '{arquivo_entrada}' não encontrado.")
                sys.exit(1)
            except Exception as e:
                print(f"Erro ao ler o arquivo comprimido: {e}")
                sys.exit(1)

            base_name = os.path.splitext(os.path.basename(arquivo_entrada))[0]
            if ext:
                arquivo_saida = os.path.join(OUTPUT_PATH, f"{base_name}_decompressed.{ext}")
            else:
                arquivo_saida = os.path.join(OUTPUT_PATH, f"{base_name}_decompressed")
        else:
            try:
                with open(arquivo_entrada, 'rb') as f:
                    ext_length_packed = f.read(1)
                    if not ext_length_packed:
                        raise ValueError("Arquivo comprimido corrompido ou formato inválido.")
                    ext_length = struct.unpack('B', ext_length_packed)[0]
                    f.read(ext_length)
                    encoded = []
                    while True:
                        chunk = f.read(2)
                        if not chunk:
                            break
                        if len(chunk) != 2:
                            raise ValueError("Arquivo comprimido corrompido ou formato inválido.")
                        code = struct.unpack('>H', chunk)[0]
                        encoded.append(code)
            except FileNotFoundError:
                print(f"Erro: Arquivo de entrada '{arquivo_entrada}' não encontrado.")
                sys.exit(1)
            except Exception as e:
                print(f"Erro ao ler o arquivo comprimido: {e}")
                sys.exit(1)

        print("Iniciando descompressão...")
        inicio_descompressao = time.time()
        
        try:
            decoded = lzw_decoder(encoded, bits_max=bits_max)
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
