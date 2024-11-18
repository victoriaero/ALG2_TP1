# main.py

import sys
import time
from lzw import lzw_encoder, lzw_decoder
import os
import struct

OUTPUT_PATH = "out/"

if not os.path.exists(OUTPUT_PATH):
    os.makedirs(OUTPUT_PATH)

def calculate_compression_ratio(original_size, compressed_size):
    return 1 - (compressed_size / original_size)

def main():
    if len(sys.argv) < 4:
        print("Uso: python main.py -c|-x <arquivo_entrada> <arquivo_saida> [bits_max=12]")
        sys.exit(1)

    modo = sys.argv[1]
    arquivo_entrada = sys.argv[2]
    arquivo_saida = sys.argv[3] if len(sys.argv) > 3 else None
    bits_max = int(sys.argv[4]) if len(sys.argv) > 4 else 12

    if modo == "-c":
        if not arquivo_saida:
            arquivo_saida = os.path.splitext(arquivo_entrada)[0] + "_compressed.z78"
        
        with open(arquivo_entrada, 'rb') as f:
            data = f.read()

        print("Iniciando compressão...")
        inicio_compressao = time.time()
        encoded = lzw_encoder(data)
        fim_compressao = time.time()

        with open(f"{OUTPUT_PATH}{arquivo_saida}", 'wb') as f:
            for code in encoded:
                f.write(struct.pack('>H', code))

        tamanho_original = len(data)
        tamanho_comprimido = len(encoded) * 2  # Cada código é armazenado em 2 bytes
        taxa_compressao = calculate_compression_ratio(tamanho_original, tamanho_comprimido)

        print("\n--- Estatísticas de Compressão ---")
        print(f"Tamanho original: {tamanho_original} bytes")
        print(f"Tamanho comprimido: {tamanho_comprimido} bytes")
        print(f"Taxa de compressão: {taxa_compressao * 100:.2f}%")
        print(f"Tempo de compressão: {fim_compressao - inicio_compressao:.2f}s")
        print(f"Arquivo comprimido salvo em: {OUTPUT_PATH}{arquivo_saida}")

    elif modo == "-x":
        if not arquivo_saida:
            arquivo_saida = os.path.splitext(arquivo_entrada)[0] + "_decompressed.txt"
        
        print("Iniciando descompressão...")
        inicio_descompressao = time.time()
        
        with open(arquivo_entrada, 'rb') as f:
            encoded = []
            while True:
                chunk = f.read(2)
                if not chunk:
                    break
                if len(chunk) != 2:
                    raise ValueError("Arquivo comprimido corrompido ou formato inválido.")
                encoded.append(struct.unpack('>H', chunk)[0])

        decoded = lzw_decoder(encoded)
        fim_descompressao = time.time()

        with open(f"{OUTPUT_PATH}{arquivo_saida}", 'wb') as f:
            f.write(decoded)

        print("\n--- Estatísticas de Descompressão ---")
        print(f"Tamanho do arquivo descomprimido: {len(decoded)} bytes")
        print(f"Tempo de descompressão: {fim_descompressao - inicio_descompressao:.2f}s")
        print(f"Arquivo descomprimido salvo em: {OUTPUT_PATH}{arquivo_saida}")

    else:
        print("Modo inválido. Use '-c' para compressão ou '-x' para descompressão.")
        sys.exit(1)

if __name__ == "__main__":
    main()
