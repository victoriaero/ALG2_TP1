from lzw_variable import lzw_encoder_variable, lzw_decoder_variable
from lzw_fixed import lzw_encoder, lzw_decoder
from utils import Bit_reader, Bit_writer
import subprocess
import argparse
import struct
import os

COMPRESSED_PATH = "out/compressed/"
COMPRESSED_EXT = ".lzw"

DECOMPRESSED_PATH = "out/decompressed/"

if not os.path.exists(COMPRESSED_PATH):
    os.makedirs(COMPRESSED_PATH)
if not os.path.exists(DECOMPRESSED_PATH):
    os.makedirs(DECOMPRESSED_PATH)


# Função principal para a execução da compressão.
# Além dela redirecionar para o método de fixo ou variável,
# ela escreve no header do arquivo comprimido a extensão do arquivo original,
# o tamanho máximo de bits usado na compressão e o método de compressão (fixo/variável).
def compress_file(input_filename, bits_max, variable=True, eh_teste=False):
    file_name, extension = os.path.splitext(input_filename)
    extension = extension.lstrip(".")
    ext_bytes = extension.encode('utf-8')
    ext_length = len(ext_bytes)
    if ext_length > 255:
        raise ValueError("A extensão é muito longa. Máximo suportado: 255 bytes.")
    
    if bits_max < 9 or bits_max > 12:
        raise ValueError("O valor de bits_max deve estar entre 9 e 12.")
    
    with open(input_filename, 'rb') as file:
        data = file.read()
    
    file_name = os.path.basename(file_name)
    # Início da compressão de fato.
    with open(f"{COMPRESSED_PATH}{file_name}{COMPRESSED_EXT}", 'wb') as comp:
        comp.write(struct.pack('B', ext_length))
        comp.write(ext_bytes)
        comp.write(struct.pack('B', bits_max))
        comp.write(struct.pack('B', 1 if variable else 0))
        
        # redireciona para a versão do LZW a ser usada
        if variable:
            writer = Bit_writer(comp) # método auxiliar para excrita
            metrics = lzw_encoder_variable(data, writer, bits_max)
        else:
            encoded, metrics = lzw_encoder(data, bits_max)
            for code in encoded: # vai converter cada código para byte
                # calculo do numero necessario de bytes pra armazenar cada código e conversão
                comp.write(code.to_bytes((bits_max + 7) // 8, byteorder='big'))
    print('\n')
    print("Compressão realizada com sucesso!")
    print(f"Caminho do arquivo comprimido: {COMPRESSED_PATH}{file_name}{COMPRESSED_EXT}")

    if eh_teste:

        original_size = os.path.getsize(input_filename)
        compressed_size = os.path.getsize(f"{COMPRESSED_PATH}{file_name}{COMPRESSED_EXT}")
        compression_rate = 1 - (compressed_size / original_size)
        compression_ratio = original_size / compressed_size

        print('\n')
        print("MÉTRICAS DE TESTE")

        print(f"Tamanho do arquivo original: {original_size} bytes")
        print(f"Tamanho do arquivo comprimido: {compressed_size} bytes")
        print(f"Taxa de compressão: {compression_rate:.2%}")
        print(f"Razão de compressão: {compression_ratio:.2f}")
        print(f"Tamanho do Dicionário: {metrics['dictionary_size']} entradas")
        print(f"Uso de Memória: {metrics['memory_usage']} bytes")
        print(f"Tempo de Execução: {metrics['execution_time']:.6f} segundos")

# Função que lê o header do arquivo comprimido e direciona para o método correto de
# descompressão, baseado na versão de compressão usada (fixo/variável). No caso do método
# variável, é usada a classe auxiliar Bit_reader.
def decompress_file(input_filename, eh_teste=False):
    with open(input_filename, "rb") as input_file:
        ext_length_packed = input_file.read(1)
        if not ext_length_packed:
            raise ValueError("Arquivo comprimido corrompido ou formato inválido.")
        ext_length = struct.unpack('B', ext_length_packed)[0]

        ext_bytes = input_file.read(ext_length)
        extension = ext_bytes.decode('utf-8') if ext_length > 0 else ''

        bits_max_packed = input_file.read(1)
        if not bits_max_packed:
            raise ValueError("Arquivo comprimido corrompido: bits_max não encontrado.")
        bits_max = struct.unpack('B', bits_max_packed)[0]

        method_packed = input_file.read(1)
        if not method_packed:
            raise ValueError("Arquivo comprimido corrompido: tipo de método não encontrado.")
        method = struct.unpack('B', method_packed)[0]
        
        if method == 1:
            reader = Bit_reader(input_file)
            decoded, metrics = lzw_decoder_variable(reader, bits_max=bits_max)
        elif method == 0:
            encoded = []
            code_size = (bits_max + 7) // 8
            while (chunk := input_file.read(code_size)):
                code = int.from_bytes(chunk, byteorder='big')
                if code >= (1 << bits_max):
                    raise ValueError(f"Código fora do limite para {bits_max} bits: {code}")
                encoded.append(code)
            decoded, metrics = lzw_decoder(encoded, bits_max=bits_max)
        else:
            raise ValueError(f"Tipo de método inválido: {method}")

        file_name = os.path.splitext(input_filename)[0]
        file_name = os.path.basename(file_name)
        with open(f"{DECOMPRESSED_PATH}{file_name}.{extension}", 'wb') as f:
            f.write(decoded)

    print('\n')
    print("Descompressão realizada com sucesso!")
    print(f"Caminho do arquivo descomprimido: {DECOMPRESSED_PATH}{file_name}.{extension}")

    if eh_teste:

        original_size = os.path.getsize(input_filename)
        decompressed_size = os.path.getsize(f"{DECOMPRESSED_PATH}{file_name}.{extension}")
        decompression_ratio = decompressed_size / original_size

        print('\n')
        print("MÉTRICAS DE TESTE")

        print(f"Tamanho do Arquivo Original (Comprimido): {original_size} bytes")
        print(f"Tamanho do Arquivo Descomprimido: {decompressed_size} bytes")
        print(f"Razão de Descompressão: {decompression_ratio:.2f}")
        print(f"Tamanho do Dicionário: {metrics['dictionary_size']} entradas")
        print(f"Uso de Memória: {metrics['memory_usage']} bytes")
        print(f"Tempo de Execução: {metrics['execution_time']:.6f} segundos")

def main():
    
    # Definição e coleta dos comandos e argumentos usados pelo usuário no terminal
    # para a definição dos parâmetros usados no algoritmo.
    parser = argparse.ArgumentParser(description="COMPRESSÃO E DESCOMPRESSÃO - LZW")
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')

    parser_compress = subparsers.add_parser('c', help='Comprimir um arquivo')
    parser_compress.add_argument('input', help='Arquivo de entrada a ser comprimido')
    parser_compress.add_argument('--bits_max', type=int, default=12, help='Número máximo de bits (padrão 12)')
    parser_compress.add_argument('--variable', action='store_true', help='Usar o método de compressão com comprimento de bits variável')
    parser_compress.add_argument('--test', action='store_true', help='Coletar métricas da Compressão')

    parser_decompress = subparsers.add_parser('d', help='Descomprimir um arquivo')
    parser_decompress.add_argument('input', help='Arquivo comprimido a ser descomprimido')
    parser_decompress.add_argument('--test', action='store_true', help='Coletar métricas da Descompressão')

    parser_report = subparsers.add_parser('r', help='Gerar relatórios')
    parser_report.add_argument("--type_files", type=str, default='txt', help="Tipo de arquivo a ser gerado (txt, bmp, csv, json, pdf, png - padrão txt)")
    parser_report.add_argument('--bits_max', type=int, default=12, help='Número máximo de bits (padrão 12)')

    args = parser.parse_args()
    if args.command == 'c':
        if not os.path.isfile(args.input):
            print(f"Erro: O arquivo de entrada '{args.input}' não existe.")
            return
        
        print("Iniciando compressão...")
        if args.variable:
            if args.test:
                compress_file(args.input, bits_max=args.bits_max, eh_teste=args.test)
            else:
                compress_file(args.input, bits_max=args.bits_max)
        else:
            if args.test:
                compress_file(args.input, bits_max=args.bits_max, variable=False, eh_teste=args.test)
            else:
                compress_file(args.input, bits_max=args.bits_max, variable=False)

    elif args.command == 'd':
        if not os.path.isfile(args.input):
            print(f"Erro: O arquivo comprimido '{args.input}' não existe.")
            return
    
        print("Iniciando Descompressão...")
        if args.test:
            decompress_file(args.input, eh_teste=args.test)
        else:
            decompress_file(args.input)
    elif args.command == 'r':
        # executa o comando abaixo para obter os relatórios com o report.py
        execution_comand = f"python3 report.py --type_files {args.type_files} --bits_max {args.bits_max}"
        output = subprocess.check_output(execution_comand, shell=True, text=True, stderr=subprocess.STDOUT)
        print(output)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()