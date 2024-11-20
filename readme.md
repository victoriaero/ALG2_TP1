# Trabalho Prático de Algoritmos II

#### Integrantes:
* Samira Malaquias       2022107580
* Victoria Estanislau    2021037490
---

# LZW Tool - Compressão e Descompressão

Este script implementa a compressão e descompressão usando o algoritmo LZW com suporte a comprimentos de bits variáveis e fixos. Ele pode ser usado para processar arquivos e salvar os resultados em diretórios específicos.

## Samples para teste

Como foram selecionados?
* BMP: https://people.math.sc.edu/Burkardt/data/bmp/bmp.html
* txt: contos coletados na internet

Na pasta samples temos uma pasta de arquivos BMP e outra de arquivos txt, que podem ser usados para teste.

## Compressão

- Variável:
'''
python lzw_tool.py -c samples/txt/sample1.txt --bits_max 14 --variable
'''

Para usar o método fixo, não selecione o --variable.

O parâmetro --bits_max é opicional.

## Descompressão:

python lzw_tool.py -d out/compressed/exemplo.lzw




