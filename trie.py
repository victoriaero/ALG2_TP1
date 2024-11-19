class TrieNode:
    def __init__(self):
        self.children = {}
        self.value = None

class Trie:
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, sequence, value):
        node = self.root
        for byte in sequence:
            if byte not in node.children:
                node.children[byte] = TrieNode()
            node = node.children[byte]
        node.value = value
    
    def search(self, sequence):
        node = self.root
        for byte in sequence:
            if byte not in node.children:
                return None
            node = node.children[byte]
        return node.value
    
    def delete_recursive(self, node, sequence, depth):
        if depth == len(sequence):
            if node.value is not None:
                node.value = None
            return not bool(node.children)
        byte = sequence[depth]
        if byte in node.children and self.delete_recursive(node.children[byte], sequence, depth + 1):
            del node.children[byte]
            return not bool(node.children) and node.value is None
        return False
    
    def delete(self, sequence):
        self.delete_recursive(self.root, sequence, 0)
    
    def print_tree_recursive(self, node, prefix):
        if node.value is not None:
            print(f"{prefix}: {node.value}")
        for byte, child in node.children.items():
            self.print_tree_recursive(child, prefix + format(byte, '02x'))
    
    def print_tree(self):
        self.print_tree_recursive(self.root, "")

if __name__ == "__main__":
    # EXEMPLO DE USO DA ESTRUTURA DE ÁRVORE DE PREFIXOS    
    trie = Trie()

    trie.insert("abc", 1)
    trie.insert("abcd", 2)
    trie.insert("xyz", 3)

    print("Antes da remoção:")
    trie.print_tree()

    trie.delete("abcd")

    print("\nDepois da remoção:")
    trie.print_tree()

    print("\nBusca:")
    print("abc:", trie.search("abc"))
    print("abcd:", trie.search("abcd"))
    print("xyz:", trie.search("xyz"))