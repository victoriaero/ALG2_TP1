import struct
import os
from utils import Bit_reader, Bit_writer
from lzw_variable import lzw_encoder_variable, lzw_decoder_variable
from lzw_fixo import lzw_encoder, lzw_decoder
import argparse
import os

def compress_file(input_filename, bits_max, variable=True):
    file_name, extension = os.path.splitext(input_filename)
    extension = extension.lstrip(".")
    ext_bytes = extension.encode('utf-8')
    ext_length = len(ext_bytes)
    if ext_length > 255:
        raise ValueError("A extensão é muito longa. Máximo suportado: 255 bytes.")
    
    if bits_max < 9 or bits_max > 16:
        raise ValueError("O valor de bits_max deve estar entre 9 e 16.")
    
    with open(input_filename, 'rb') as file:
        data = file.read()
    
    file_name = os.path.basename(file_name)
    with open(f"out/compressed/{file_name}.lzw", 'wb') as comp:
        comp.write(struct.pack('B', ext_length))
        comp.write(ext_bytes)
        comp.write(struct.pack('B', bits_max))
        comp.write(struct.pack('B', 1 if variable else 0))
        
        if variable:
            writer = Bit_writer(comp)
            lzw_encoder_variable(data, writer, bits_max)
        else:
            encoded = lzw_encoder(data, bits_max)
            for code in encoded:
                comp.write(code.to_bytes((bits_max + 7) // 8, byteorder='big'))

def decompress_file(input_filename):
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
            decoded = lzw_decoder_variable(reader, bits_max=bits_max)
        elif method == 0:
            encoded = []
            code_size = (bits_max + 7) // 8
            while (chunk := input_file.read(code_size)):
                code = int.from_bytes(chunk, byteorder='big')
                if code >= (1 << bits_max):
                    raise ValueError(f"Código fora do limite para {bits_max} bits: {code}")
                encoded.append(code)
            decoded = lzw_decoder(encoded, bits_max=bits_max)
        else:
            raise ValueError(f"Tipo de método inválido: {method}")

        file_name = os.path.splitext(input_filename)[0]
        file_name = os.path.basename(file_name)
        with open(f"out/decompressed/{file_name}.{extension}", 'wb') as f:
            f.write(decoded)

def main():
    
    parser = argparse.ArgumentParser(description="Compressão e Descompressão LZW com Bit-Length Variável.")
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')

    parser_compress = subparsers.add_parser('c', help='Comprimir um arquivo')
    parser_compress.add_argument('input', help='Arquivo de entrada a ser comprimido')
    parser_compress.add_argument('--bits_max', type=int, default=12, help='Número máximo de bits (padrão: 16)')
    parser_compress.add_argument('--variable', action='store_true', help='Usar o método de compressão com comprimento de bits variável')

    parser_decompress = subparsers.add_parser('d', help='Descomprimir um arquivo')
    parser_decompress.add_argument('input', help='Arquivo comprimido a ser descomprimido')

    args = parser.parse_args()
    if args.command == 'c':
        if not os.path.isfile(args.input):
            print(f"Erro: O arquivo de entrada '{args.input}' não existe.")
            return
        try:
            if args.variable:
                compress_file(args.input, bits_max=args.bits_max)
            else:
                compress_file(args.input, bits_max=args.bits_max, variable=False)
                
        except Exception as e:
            print(f"Erro durante a compressão: {e}")

    elif args.command == 'd':
        if not os.path.isfile(args.input):
            print(f"Erro: O arquivo comprimido '{args.input}' não existe.")
            return
    try:
        decompress_file(args.input)
    except Exception as e:
            print(f"Erro durante a descompressão: {e}")


    else:
        parser.print_help()

main()