# trie.py

class TrieNode:
    def __init__(self):
        """
        Inicializa um nó da Trie com um dicionário vazio de filhos e nenhum valor associado.
        """
        self.children = {}
        self.value = None

class Trie:
    def __init__(self):
        """
        Inicializa a Trie com uma raiz vazia e tamanho zero.
        """
        self.root = TrieNode()
        self.size = 0  # Contador de entradas

    def insert(self, sequence, value):
        """
        Insere uma sequência de bytes na Trie com o valor associado.
        Incrementa o tamanho se for uma nova entrada.
        """
        node = self.root
        for byte in sequence:
            if byte not in node.children:
                node.children[byte] = TrieNode()
            node = node.children[byte]
        if node.value is None:
            self.size += 1  # Incrementa apenas se for uma nova entrada
        node.value = value

    def search(self, sequence):
        """
        Pesquisa uma sequência de bytes na Trie.
        Retorna o valor associado se a sequência existir, caso contrário, retorna None.
        """
        node = self.root
        for byte in sequence:
            if byte not in node.children:
                return None
            node = node.children[byte]
        return node.value

    def delete_recursive(self, node, sequence, depth):
        """
        Método auxiliar recursivo para deletar uma sequência da Trie.
        """
        if depth == len(sequence):
            if node.value is not None:
                node.value = None
                self.size -= 1  # Decrementa o contador
            return not bool(node.children)
        byte = sequence[depth]
        if byte in node.children and self.delete_recursive(node.children[byte], sequence, depth + 1):
            del node.children[byte]
            return not bool(node.children) and node.value is None
        return False

    def delete(self, sequence):
        """
        Deleta uma sequência de bytes da Trie.
        """
        self.delete_recursive(self.root, sequence, 0)

    def get_size(self):
        """
        Retorna o número atual de entradas na Trie.
        """
        return self.size

    def print_tree_recursive(self, node, prefix):
        """
        Método auxiliar recursivo para imprimir a Trie.
        """
        if node.value is not None:
            print(f"{prefix}: {node.value}")
        for byte, child in node.children.items():
            self.print_tree_recursive(child, prefix + format(byte, '02x'))

    def print_tree(self):
        """
        Imprime a Trie inteira.
        """
        self.print_tree_recursive(self.root, "")

# EXEMPLO DE USO DA ESTRUTURA DE ÁRVORE DE PREFIXOS    
if __name__ == "__main__":
    trie = Trie()

    trie.insert(b"abc", 1)
    trie.insert(b"abcd", 2)
    trie.insert(b"xyz", 3)

    print("Antes da remoção:")
    trie.print_tree()

    trie.delete(b"abcd")

    print("\nDepois da remoção:")
    trie.print_tree()

    print("\nBusca:")
    print("abc:", trie.search(b"abc"))
    print("abcd:", trie.search(b"abcd"))
    print("xyz:", trie.search(b"xyz"))
