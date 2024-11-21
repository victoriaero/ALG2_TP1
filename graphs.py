import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

REPORT_DIR = "out/report/"
GRAPH_DIR = "out/graphs/"

def create_graph_dir():
    if not os.path.exists(GRAPH_DIR):
        os.makedirs(GRAPH_DIR)

# Função para carregar os relatórios JSON para coletar as métricas e gerar os gráficos
def load_reports(report_dir):
    data = []
    for root, _, files in os.walk(report_dir):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                with open(file_path, "r") as f:
                    report_data = json.load(f)
                    for command, stats in report_data.items():
                        if "main.py c" in command:
                            entry = {
                                "command": command,
                                "report_file": file,
                                "file_type": command.split(" ")[3].split("/")[-1].split("_")[0],  # Extrair tipo do arquivo
                                "bits_max": int(command.split("--bits_max")[1].split()[0]) if "--bits_max" in command else None,
                                "compression_memory_usage": int(stats.get("memory_usage", "0 bytes").split()[0]),
                                "compression_execution_time": float(stats.get("execution_time", "0.0 segundos").split()[0]),
                                "compression_dictionary_size": int(stats.get("dictionary_size", "0 entradas").split()[0]),
                                "compression_rate": float(stats.get("compression_rate", "0%").strip('%')),
                                "compression_ratio": float(stats.get("compression_ratio", "0")),
                            }
                        elif "main.py d" in command:
                            entry = {
                                "command": command,
                                "report_file": file,
                                "file_type": command.split(" ")[3].split("/")[-1].split("_")[0],
                                "bits_max": None,
                                "decompression_memory_usage": int(stats.get("memory_usage", "0 bytes").split()[0]),
                                "decompression_execution_time": float(stats.get("execution_time", "0.0 segundos").split()[0]),
                                "decompression_dictionary_size": int(stats.get("dictionary_size", "0 entradas").split()[0]),
                                "decompression_ratio": float(stats.get("decompression_ratio", "0")),
                            }
                        else:
                            continue
                        
                        data.append(entry)
    return pd.DataFrame(data)

def generate_graphs(data):
    
    create_graph_dir()
    
    # Adicionar colunas para análises
    data['file_type'] = data['report_file'].str.extract(r'_(\w+)_')[0]
    data['bits_max'] = data['report_file'].str.extract(r'_(\d+)bits')[0].astype(int)

    # Gráfico 1: Taxa de Compressão por Tipo de Arquivo e Bits Máximos
    avg_compression_rate = data.groupby(['file_type', 'bits_max'])['compression_rate'].mean().reset_index()
    plt.figure(figsize=(10, 6))
    for file_type in avg_compression_rate['file_type'].unique():
        subset = avg_compression_rate[avg_compression_rate['file_type'] == file_type]
        plt.plot(subset['bits_max'], subset['compression_rate'], marker='o', label=file_type)
    plt.title("Taxa de Compressão por Tipo de Arquivo e Bits Máximos")
    plt.xlabel("Bits Máximos")
    plt.ylabel("Taxa de Compressão (%)")
    plt.legend()
    plt.grid()
    plt.savefig(os.path.join(GRAPH_DIR, "compression_rate_vs_bits.png"))
    plt.close()

    # Gráfico 2: Tempo de Execução por Tipo de Arquivo e Bits Máximos
    avg_execution_time = data.groupby(['file_type', 'bits_max'])['compression_execution_time'].mean().reset_index()
    plt.figure(figsize=(10, 6))
    for file_type in avg_execution_time['file_type'].unique():
        subset = avg_execution_time[avg_execution_time['file_type'] == file_type]
        plt.plot(subset['bits_max'], subset['compression_execution_time'], marker='o', label=file_type)
    plt.title("Tempo de Execução por Tipo de Arquivo e Bits Máximos")
    plt.xlabel("Bits Máximos")
    plt.ylabel("Tempo de Execução (s)")
    plt.legend()
    plt.grid()
    plt.savefig(os.path.join(GRAPH_DIR, "execution_time_vs_bits.png"))
    plt.close()

    # Gráfico 3: Razão de Compressão por Tipo de Arquivo
    avg_compression_ratio = data.groupby(['file_type', 'bits_max'])['compression_ratio'].mean().reset_index()
    plt.figure(figsize=(10, 6))
    for file_type in avg_compression_ratio['file_type'].unique():
        subset = avg_compression_ratio[avg_compression_ratio['file_type'] == file_type]
        plt.plot(subset['bits_max'], subset['compression_ratio'], marker='o', label=file_type)
    plt.title("Razão de Compressão por Tipo de Arquivo")
    plt.xlabel("Bits Máximos")
    plt.ylabel("Razão de Compressão")
    plt.legend()
    plt.grid()
    plt.savefig(os.path.join(GRAPH_DIR, "compression_ratio_vs_bits.png"))
    plt.close()

    # Gráfico 4: Crescimento do Dicionário para Compressão Variável
    variable_data = data[data['report_file'].str.contains("variable")]
    avg_dict_size_variable = variable_data.groupby(['file_type', 'bits_max'])['compression_dictionary_size'].mean().reset_index()
    plt.figure(figsize=(10, 6))
    for file_type in avg_dict_size_variable['file_type'].unique():
        subset = avg_dict_size_variable[avg_dict_size_variable['file_type'] == file_type]
        plt.plot(subset['bits_max'], subset['compression_dictionary_size'], marker='o', label=file_type)
    plt.title("Crescimento do Dicionário - Compressão Variável")
    plt.xlabel("Bits Máximos")
    plt.ylabel("Tamanho do Dicionário (Entradas)")
    plt.legend()
    plt.grid()
    plt.savefig(os.path.join(GRAPH_DIR, "dictionary_growth_variable.png"))
    plt.close()

    # Gráfico 5: Crescimento do Dicionário para Compressão Fixa
    fixed_data = data[data['report_file'].str.contains("fixed")]
    avg_dict_size_fixed = fixed_data.groupby(['file_type', 'bits_max'])['compression_dictionary_size'].mean().reset_index()
    plt.figure(figsize=(10, 6))
    for file_type in avg_dict_size_fixed['file_type'].unique():
        subset = avg_dict_size_fixed[avg_dict_size_fixed['file_type'] == file_type]
        plt.plot(subset['bits_max'], subset['compression_dictionary_size'], marker='o', label=file_type)
    plt.title("Crescimento do Dicionário - Compressão Fixa")
    plt.xlabel("Bits Máximos")
    plt.ylabel("Tamanho do Dicionário (Entradas)")
    plt.legend()
    plt.grid()
    plt.savefig(os.path.join(GRAPH_DIR, "dictionary_growth_fixed.png"))
    plt.close()

    # Gráfico 6: Taxa de Compressão x Tempo - Compressão Variável
    plt.figure(figsize=(10, 6))
    for file_type in variable_data['file_type'].unique():
        subset = variable_data[variable_data['file_type'] == file_type]
        plt.scatter(subset['compression_execution_time'], subset['compression_rate'], label=file_type)
    plt.title("Taxa de Compressão x Tempo de Compressão - Compressão Variável")
    plt.xlabel("Tempo de Compressão (s)")
    plt.ylabel("Taxa de Compressão (%)")
    plt.legend()
    plt.grid()
    plt.savefig(os.path.join(GRAPH_DIR, "compression_rate_vs_time_variable.png"))
    plt.close()

    # Gráfico 7: Taxa de Compressão x Tempo - Compressão Fixa
    plt.figure(figsize=(10, 6))
    for file_type in fixed_data['file_type'].unique():
        subset = fixed_data[fixed_data['file_type'] == file_type]
        plt.scatter(subset['compression_execution_time'], subset['compression_rate'], label=file_type)
    plt.title("Taxa de Compressão x Tempo de Compressão - Compressão Fixa")
    plt.xlabel("Tempo de Compressão (s)")
    plt.ylabel("Taxa de Compressão (%)")
    plt.legend()
    plt.grid()
    plt.savefig(os.path.join(GRAPH_DIR, "compression_rate_vs_time_fixed.png"))
    plt.close()

    # Novo Heatmap: Taxa de Compressão por Tipo de Arquivo e Bits Máximos
    heatmap_data = data.pivot_table(index='file_type', columns='bits_max', values='compression_rate', aggfunc='mean')
    plt.figure(figsize=(10, 6))
    sns.heatmap(heatmap_data, annot=True, fmt=".2f", cmap="coolwarm", cbar_kws={'label': 'Taxa de Compressão (%)'})
    plt.title("Heatmap: Taxa de Compressão por Tipo de Arquivo e Bits Máximos")
    plt.xlabel("Bits Máximos")
    plt.ylabel("Tipo de Arquivo")
    plt.savefig(os.path.join(GRAPH_DIR, "heatmap_compression_rate.png"))
    plt.close()

    # Uso de Memória por Tipo de Arquivo (Compressão)
    plt.figure(figsize=(10, 6))
    avg_memory_compression = data.groupby(['file_type', 'bits_max'])['compression_memory_usage'].mean().reset_index()
    for file_type in avg_memory_compression['file_type'].unique():
        subset = avg_memory_compression[avg_memory_compression['file_type'] == file_type]
        plt.plot(subset['bits_max'], subset['compression_memory_usage'], marker='o', label=file_type)
    plt.title("Uso de Memória na Compressão por Tipo de Arquivo")
    plt.xlabel("Bits Máximos")
    plt.ylabel("Memória Utilizada (bytes)")
    plt.legend()
    plt.grid()
    plt.savefig(os.path.join(GRAPH_DIR, "memory_usage_compression.png"))
    plt.close()

def generate_decompression_graphs(data):
    create_graph_dir()

    data['file_type'] = data['report_file'].str.extract(r'_(\w+)_')[0]
    data['bits_max'] = data['report_file'].str.extract(r'_(\d+)bits')[0].astype(int)

    # Crescimento do Dicionário para Descompressão
    plt.figure(figsize=(10, 6))
    avg_dict_size = data.groupby(['file_type', 'bits_max'])['decompression_dictionary_size'].mean().reset_index()
    for file_type in avg_dict_size['file_type'].unique():
        subset = avg_dict_size[avg_dict_size['file_type'] == file_type]
        plt.plot(subset['bits_max'], subset['decompression_dictionary_size'], marker='o', label=file_type)
    plt.title("Crescimento do Dicionário - Descompressão")
    plt.xlabel("Bits Máximos")
    plt.ylabel("Tamanho do Dicionário (Entradas)")
    plt.legend()
    plt.grid()
    plt.savefig(os.path.join(GRAPH_DIR, "decompression_dictionary_growth.png"))
    plt.close()

    # Tempo de Execução para Descompressão
    plt.figure(figsize=(10, 6))
    avg_execution_time = data.groupby(['file_type', 'bits_max'])['decompression_execution_time'].mean().reset_index()
    for file_type in avg_execution_time['file_type'].unique():
        subset = avg_execution_time[avg_execution_time['file_type'] == file_type]
        plt.plot(subset['bits_max'], subset['decompression_execution_time'], marker='o', label=file_type)
    plt.title("Tempo de Execução - Descompressão")
    plt.xlabel("Bits Máximos")
    plt.ylabel("Tempo de Execução (s)")
    plt.legend()
    plt.grid()
    plt.savefig(os.path.join(GRAPH_DIR, "decompression_execution_time.png"))
    plt.close()

    # Uso de Memória por Tipo de Arquivo
    plt.figure(figsize=(10, 6))
    avg_memory_decompression = data.groupby(['file_type', 'bits_max'])['decompression_memory_usage'].mean().reset_index()
    for file_type in avg_memory_decompression['file_type'].unique():
        subset = avg_memory_decompression[avg_memory_decompression['file_type'] == file_type]
        plt.plot(subset['bits_max'], subset['decompression_memory_usage'], marker='o', label=file_type)
    plt.title("Uso de Memória na Descompressão por Tipo de Arquivo")
    plt.xlabel("Bits Máximos")
    plt.ylabel("Memória Utilizada (bytes)")
    plt.legend()
    plt.grid()
    plt.savefig(os.path.join(GRAPH_DIR, "memory_usage_decompression.png"))
    plt.close()

if __name__ == "__main__":
    df = load_reports(REPORT_DIR)
    if df.empty:
        print("Nenhum relatório encontrado!")
    else:
        print("Relatórios carregados com sucesso!")
        generate_graphs(df)
        generate_decompression_graphs(df)
        print(f"Gráficos gerados e salvos no diretório: {GRAPH_DIR}")
