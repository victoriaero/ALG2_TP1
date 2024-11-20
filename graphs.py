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
                        entry = {
                            "command": command,
                            "report_file": file,
                            "compressed_file_path": stats.get("compressed_file_path"),
                            "original_file_size": int(stats.get("original_file_size", "0 bytes").split()[0]),
                            "compressed_file_size": int(stats.get("compressed_file_size", "0 bytes").split()[0]),
                            "compression_rate": float(stats.get("compression_rate", "0%").strip('%')),
                            "compression_ratio": float(stats.get("compression_ratio", "0")),
                            "dictionary_size": int(stats.get("dictionary_size", "0 entradas").split()[0]),
                            "memory_usage": int(stats.get("memory_usage", "0 bytes").split()[0]),
                            "execution_time": float(stats.get("execution_time", "0.0 segundos").split()[0]),
                        }
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
    avg_execution_time = data.groupby(['file_type', 'bits_max'])['execution_time'].mean().reset_index()
    plt.figure(figsize=(10, 6))
    for file_type in avg_execution_time['file_type'].unique():
        subset = avg_execution_time[avg_execution_time['file_type'] == file_type]
        plt.plot(subset['bits_max'], subset['execution_time'], marker='o', label=file_type)
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
    avg_dict_size_variable = variable_data.groupby(['file_type', 'bits_max'])['dictionary_size'].mean().reset_index()
    plt.figure(figsize=(10, 6))
    for file_type in avg_dict_size_variable['file_type'].unique():
        subset = avg_dict_size_variable[avg_dict_size_variable['file_type'] == file_type]
        plt.plot(subset['bits_max'], subset['dictionary_size'], marker='o', label=file_type)
    plt.title("Crescimento do Dicionário - Compressão Variável")
    plt.xlabel("Bits Máximos")
    plt.ylabel("Tamanho do Dicionário (Entradas)")
    plt.legend()
    plt.grid()
    plt.savefig(os.path.join(GRAPH_DIR, "dictionary_growth_variable.png"))
    plt.close()

    # Gráfico 5: Crescimento do Dicionário para Compressão Fixa
    fixed_data = data[data['report_file'].str.contains("fixed")]
    avg_dict_size_fixed = fixed_data.groupby(['file_type', 'bits_max'])['dictionary_size'].mean().reset_index()
    plt.figure(figsize=(10, 6))
    for file_type in avg_dict_size_fixed['file_type'].unique():
        subset = avg_dict_size_fixed[avg_dict_size_fixed['file_type'] == file_type]
        plt.plot(subset['bits_max'], subset['dictionary_size'], marker='o', label=file_type)
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
        plt.scatter(subset['execution_time'], subset['compression_rate'], label=file_type)
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
        plt.scatter(subset['execution_time'], subset['compression_rate'], label=file_type)
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

if __name__ == "__main__":
    df = load_reports(REPORT_DIR)
    if df.empty:
        print("Nenhum relatório encontrado!")
    else:
        print("Relatórios carregados com sucesso!")
        generate_graphs(df)
        print(f"Gráficos gerados e salvos no diretório: {GRAPH_DIR}")
