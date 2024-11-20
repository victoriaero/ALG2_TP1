class TrieNode:
    def __init__(self):
        self.children = {} # dicionario de filhos
        self.value = None # valor associado ao no se for o fim da seq

class Trie:
    def __init__(self):
        self.root = TrieNode() # raiz
        self.size = 0 # num seq armazenadas

    def insert(self, sequence, value):
        node = self.root
        for byte in sequence: # percorre os bytes da seq
            if byte not in node.children: # cria no filho se preciso
                node.children[byte] = TrieNode()
            node = node.children[byte]
        if node.value is None: # se a seq for nova, incrementa o tamanho
            self.size += 1
        node.value = value # associa o valor ao final da seq

    def search(self, sequence):
        node = self.root
        for byte in sequence: # percorre os bytes da seq
            if byte not in node.children:
                return None
            node = node.children[byte]
        return node.value # retorna o valor associado

    def delete_recursive(self, node, sequence, depth): 
        if depth == len(sequence): # caso base: final da seq
            if node.value is not None: # remove valor associado se existir 
                node.value = None
                self.size -= 1
            return not bool(node.children) # true se nao tiver filhos
        byte = sequence[depth] # byte atual
        # continua remocao do filho correspondente
        if byte in node.children and self.delete_recursive(node.children[byte], sequence, depth + 1):
            del node.children[byte] # remove filho se ele for vazio
            return not bool(node.children) and node.value is None # verifica se o no pode ser removido
        return False # o no nao pode ser removido

    def delete(self, sequence):
        self.delete_recursive(self.root, sequence, 0)

    def get_size(self):
        return self.size

    def print_tree_recursive(self, node, prefix):
        if node.value is not None:
            print(f"{prefix}: {node.value}")
        for byte, child in node.children.items():
            self.print_tree_recursive(child, prefix + format(byte, '02x'))

    def print_tree(self):
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
