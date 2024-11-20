# Trabalho Prático de Algoritmos II

#### Integrantes:
* Samira Malaquias       2022107580
* Victoria Estanislau    2021037490

---

O presente trabalho teve como o objetivo a implementação de duas versões do algoritmo de compressão e descompressão LZW, baseado em árvores de prefixos. A primeira versão, a versão fixa, faz uso de tamanhos fixos para os códigos de saída LZW, enquanto a versão variável faz uso de tamanhos variáveis para os códigos de saída. Em ambos os casos, o número máximo de bits foi determidado como 12, de acordo com as especificações do trabalho prático.

Link do relatório em página/blog: https://stream-kwkckn4pxfwmz2kffsfck3.streamlit.app/

---

## Implementação

Nesse repositório você poderá encontrar duas pastas: 'samples' e 'out'. A primeira pasta, 'samples', é referente a amostras de arquivos para teste. Nela, você poderá encontrar um conjunto de 6 pastas contento pelo menos três amostras em cada para cada tipo de arquivo. Os tipos presentes são txt, bmp, csv, json, pdf e png. Para a segunda pasta, 'out', ela irá armazenar aos outputs obtidos na compressão e descompressão dos arquivos, além dos relatórios e gráficos gerados. Quanto aos arquivos de script, temos:

* main.py: é o arquivo principal para a execução de todo o algoritmo e suas variações;
* trie.py: contém a classe Trie utilizada por ambas versões do LZW;
* lzw_fixed.py: contém os métodos da versão fixa do LZW;
* lzw_variable.py: contém os métodos da versão variável do LZW;
* utils.py: contém classes auxiliares para leitura e escrita de bits;
* report.py: contém um pipeline de execução de testes para geração de um relatório json;
* generate.py contém métodos auxiliares para geração de arquivos para teste. Pode executar o arquivo separadamente para gerar a quantidade desejada de amostras.
* graphs.py: contém métodos de geração de gráficos por meio dos relatórios gerados com report.py

### LZW Fixo

Na versão com comprimento fixo, todos os códigos gerados para representar as sequências no dicionário possuem o mesmo número de bits, que é determinado no início do processo. O dicionário é inicializado com os códigos ASCII básicos (0 a 255) e, à medida que novas sequências são encontradas, códigos adicionais são atribuídos até o limite permitido pelo número de bits especificado. Quando o dicionário atinge sua capacidade máxima, não é mais possível adicionar novas sequências, então o algoritmo continua a codificar apenas as entradas já existentes. Essa abordagem é eficiente em cenários onde o tamanho do dicionário não cresce significativamente ou onde a simplicidade de implementação é uma prioridade.

### LZW Variável

A versão com comprimento variável permite que o número de bits utilizado para representar os códigos seja ajustado dinamicamente durante o processo de compressão. Inicialmente, o algoritmo começa com um número pequeno de bits, como 9, e aumenta gradualmente o tamanho do código à medida que o dicionário cresce, até atingir o limite especificado. Isso proporciona maior flexibilidade, pois permite a expansão do dicionário em cenários onde sequências mais complexas ou longas precisam ser codificadas. Essa abordagem é particularmente vantajosa para arquivos com alta entropia, nos quais o crescimento progressivo do dicionário contribui para uma compressão mais eficiente, mantendo um balanço entre o uso de memória e a qualidade da compressão.

---

## Como executar o código?

Para a execução você deve utilizar o arquivo main.py. Quanto aos comandos possíveis, temos:

### Compressão

Para o método fixo, basta fazer da seguinte maneira:
~~~
python3 main.py c {caminho_do_arquivo_entrada} 
~~~

Para o método variável, pode adicionar o argumento 'variable'

~~~
python3 main.py c {caminho_do_arquivo_entrada} --variable
~~~

Para ambas versões, pode-se determinar também o tamanho máximo dos bits usando o argumento bits_max. Por padrão, seu valor é 12 para ambas versões.

~~~
python3 main.py c {caminho_do_arquivo_entrada} --bits_max 9
~~~

Você pode também utilizar o argumento de teste para exibir as métricas para ambas versões do algoritmo:

~~~
python3 main.py c {caminho_do_arquivo_entrada} --teste
~~~

### Descompressão

Para a descompressão, basta digitar o seguinte comando (para ele, não há diferenciação do método fixo ou variável, pois o dado ficará armazenado no header do arquivo comprimido):

~~~
python3 main.py d {caminho_do_arquivo_comprimido}
~~~

* O argumento de teste também funciona para o método de descompressão.

### Relatório

O método r irá gerar resultados de teste para um conjunto de arquivos disposto em 'samples', e irá armazenar os resultados em um json no caminho 'out/report/'. Ele irá gerar as métricas para ambas versões do algoritmo e retornar dois jsons distintos.

~~~
python3 main.py r
~~~

Você pode definir também o argumento de bits_max para geração do relatório. Além dele, pode-se definir mais um argumento:

~~~
python3 main.py r --type_file
~~~

O parâmetro type_file irá gerar os relatórios para todas as amostras do tipo de arquivo desejado na pasta de samples. O padrão é arquivos txt.

### Exemplos

1. Compressão do arquivo txt_sample1.txt no método variável, exibindo as métricas:

~~~
python3 main.py c samples/txt_sample1.txt --variable --teste
~~~

2. Descompressão do arquivo txt_sample1.lzw, exibindo as métricas:

~~~
python3 main.py c out/compressed/txt_sample1.lzw --teste
~~~

3. Gerando relatório json para os arquivos csv disponíveis:

~~~
python3 main.py r --type_file csv
~~~

--- 
