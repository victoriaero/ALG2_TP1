import subprocess
import argparse
import json
import os

RESULTS_PATH = "out/report/"
if not os.path.exists(RESULTS_PATH):
    os.makedirs(RESULTS_PATH)

# dicionario auxiliar para formatação do json
key_map = {
    "Caminho do arquivo comprimido": "compressed_file_path",
    "Tamanho do arquivo original": "original_file_size",
    "Tamanho do arquivo comprimido": "compressed_file_size",
    "Taxa de compress\u00e3o": "compression_rate",
    "Raz\u00e3o de compress\u00e3o": "compression_ratio",
    "Tamanho do Dicion\u00e1rio": "dictionary_size",
    "Uso de Mem\u00f3ria": "memory_usage",
    "Tempo de Execu\u00e7\u00e3o": "execution_time",
    "Caminho do arquivo descomprimido": "decompressed_file_path",
    "Tamanho do Arquivo Original (Comprimido)": "original_compressed_file_size",
    "Tamanho do Arquivo Descomprimido": "decompressed_file_size",
    "Raz\u00e3o de Descompress\u00e3o": "decompression_ratio"
}

# Função que irá executar no main.py o conjunto de comandos desejados para a formação do relatório json
def run(commands):
    results = {}

    for command in commands:
        try:
            output = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT)
            results[command] = output
        except subprocess.CalledProcessError as e:
            results[command] = e.output
    
    return results

# manipulação da saída dos comandos
def output_to_dict(output):
    result_dict = {}
    for line in output.splitlines():
        if ":" in line:
            key, value = map(str.strip, line.split(":", 1))
            result_dict[key] = value
    return result_dict

# função auxiliar para renomear chaves do dicionario
def rename_keys(data, key_map):
    if isinstance(data, dict):
        return {
            key_map.get(key, key): rename_keys(value, key_map)
            for key, value in data.items()
        }
    elif isinstance(data, list):
        return [rename_keys(item, key_map) for item in data]
    else:
        return data

# salvando o arquivo json
def save_file(results, filename="report.json"):
    filepath = os.path.join(RESULTS_PATH, filename)
    with open(filepath, "w") as file:
        json.dump(results, file, indent=4, ensure_ascii=False)  # ensure_ascii=False para UTF-8
    print(f"Relatório salvo em {filepath}")

def main():

    # definição e coleta dos parâmetros    
    parser = argparse.ArgumentParser(description="Gerando Relatório")
    parser.add_argument("--type_files", type=str, default='txt', help="Tipo de arquivo a ser gerado (txt, bmp, csv, json, pdf, png - padrão txt)")
    parser.add_argument('--bits_max', type=int, default=12, help='Número máximo de bits (padrão 12)')

    args = parser.parse_args()

    # etapa para definir o tipo de arquivo que será analisado
    file_type = args.type_files

    if file_type == 'txt' or file_type == 'TXT':
        FILES_PATH = "samples/txt/"
    elif file_type == 'bmp' or file_type == 'BMP':
        FILES_PATH = "samples/bmp/"
    elif file_type == 'csv' or file_type == 'CSV':
        FILES_PATH = "samples/csv/"
    elif file_type == 'json' or file_type == 'JSON':
        FILES_PATH = "samples/json/"
    elif file_type == 'pdf' or file_type == 'PDF':
        FILES_PATH = "samples/pdf/"
    elif file_type == 'png' or file_type == 'PNG':
        FILES_PATH = "samples/png/"
    else:
        print(f"Erro: tipo de arquivo inválido!")
        print("Os tipos de arquivo disponíveis são: txt, bmp, csv, json, pdf, png - padrão txt")
        return

    # formação dos comandos baseado no conjunto de arquivos
    file_paths = []
    for root, _, files in os.walk(FILES_PATH):
        for file in files:
            file_paths.append(os.path.join(root, file))

    commands_fixed = []
    for file in file_paths:
        file_with_extension = os.path.basename(file)
        file_base_name = os.path.splitext(file_with_extension)[0]
        commands_fixed.append(f"python3 main.py c {file} --test")
        commands_fixed.append(f"python3 main.py d out/compressed/{file_base_name}.lzw --test")

    commands_variable = []
    for file in file_paths:
        file_with_extension = os.path.basename(file)
        file_base_name = os.path.splitext(file_with_extension)[0]
        commands_variable.append(f"python3 main.py c {file} --variable --test")
        commands_variable.append(f"python3 main.py d out/compressed/{file_base_name}.lzw --test")

    # formando relatório para versão fixa
    raw_results_fixed = run(commands_fixed)
    structured_results_fixed = {cmd: output_to_dict(output) for cmd, output in raw_results_fixed.items()}
    renamed_data_fixed = rename_keys(structured_results_fixed, key_map)
    save_file(renamed_data_fixed, filename=f"report_fixed_{file_type}.json")

    # formando relatório para versão variada
    raw_results_fixed = run(commands_variable)
    structured_results_variable = {cmd: output_to_dict(output) for cmd, output in raw_results_fixed.items()}
    renamed_data_variable = rename_keys(structured_results_variable, key_map)
    save_file(renamed_data_variable, filename=f"report_variable_{file_type}.json")

if __name__ == "__main__":
    main()