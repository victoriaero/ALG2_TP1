import hashlib
import sys

def calcular_hash(file_path, hash_algo='sha256', bloco_tamanho=65536):
    hash_obj = hashlib.new(hash_algo)
    try:
        with open(file_path, 'rb') as f:
            while True:
                bloco = f.read(bloco_tamanho)
                if not bloco:
                    break
                hash_obj.update(bloco)
        return hash_obj.hexdigest()
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {file_path}")
        return None
    except Exception as e:
        print(f"Erro ao calcular hash: {e}")
        return None

def comparar_hashes(file1, file2, hash_algo='sha256'):
    hash1 = calcular_hash(file1, hash_algo)
    hash2 = calcular_hash(file2, hash_algo)
    
    if hash1 is None or hash2 is None:
        return False
    
    if hash1 == hash2:
        print("Os arquivos são iguais.")
        return True
    else:
        print("Os arquivos são diferentes.")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python comparar_arquivos.py <arquivo1> <arquivo2>")
        sys.exit(1)
    
    arquivo1 = sys.argv[1]
    arquivo2 = sys.argv[2]
    
    comparar_hashes(arquivo1, arquivo2)
