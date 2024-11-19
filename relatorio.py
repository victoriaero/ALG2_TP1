import json
import matplotlib.pyplot as plt

def ler_estatisticas(arquivo):
    estatisticas = []
    with open(arquivo, 'r') as f:
        for linha in f:
            estatisticas.append(json.loads(linha))
    return estatisticas

def plot_taxa_compressao(estatisticas):
    taxa = [e['taxa_compressao_percentual'] for e in estatisticas]
    indices = list(range(1, len(taxa) + 1))
    plt.plot(indices, taxa, marker='o')
    plt.title('Taxa de Compressão ao Longo das Execuções')
    plt.xlabel('Execução')
    plt.ylabel('Taxa de Compressão (%)')
    plt.grid(True)
    plt.savefig('taxa_compressao.png')
    plt.show()

def plot_tempo_compressao(estatisticas):
    tempo = [e['tempo_compressao_s'] for e in estatisticas]
    indices = list(range(1, len(tempo) + 1))
    plt.plot(indices, tempo, marker='x', color='red')
    plt.title('Tempo de Compressão ao Longo das Execuções')
    plt.xlabel('Execução')
    plt.ylabel('Tempo (s)')
    plt.grid(True)
    plt.savefig('tempo_compressao.png')
    plt.show()

def main():
    estatisticas_compressao = ler_estatisticas('estatisticas_compressao.json')
    if estatisticas_compressao:
        plot_taxa_compressao(estatisticas_compressao)
        plot_tempo_compressao(estatisticas_compressao)
    else:
        print("Nenhuma estatística de compressão encontrada.")

if __name__ == "__main__":
    main()
