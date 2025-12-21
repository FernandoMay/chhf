import sys
import heapq
import collections
import os

# --- Implementación Real de Compresión Huffman ---

class HuffmanNode:
    """Un nodo en el árbol de Huffman."""
    def __init__(self, char=None, freq=0, left=None, right=None):
        self.char = char  # Carácter para nodos hoja
        self.freq = freq  # Frecuencia del carácter o suma de hijos
        self.left = left  # Hijo izquierdo
        self.right = right # Hijo derecho

    # Definir comparadores para la cola de prioridad (min-heap)
    def __lt__(self, other):
        return self.freq < other.freq

class HuffmanCompression:
    """
    Implementa compresión y descompresión usando el algoritmo de Huffman.
    """
    def _build_tree(self, text: str) -> HuffmanNode:
        """Construye el árbol de Huffman a partir del texto de entrada."""
        if not text:
            return None
        
        # Contar la frecuencia de cada carácter
        frequency = collections.Counter(text)
        
        # Crear una cola de prioridad (min-heap) con nodos hoja
        priority_queue = [HuffmanNode(char, freq) for char, freq in frequency.items()]
        heapq.heapify(priority_queue)
        
        # Construir el árbol combinando los dos nodos de menor frecuencia
        while len(priority_queue) > 1:
            left = heapq.heappop(priority_queue)
            right = heapq.heappop(priority_queue)
            
            # Crear un nuevo nodo interno con la suma de frecuencias
            merged = HuffmanNode(freq=left.freq + right.freq, left=left, right=right)
            heapq.heappush(priority_queue, merged)
            
        return priority_queue[0] # La raíz del árbol

    def _build_codes(self, root: HuffmanNode) -> dict:
        """Genera los códigos de Huffman para cada carácter."""
        codes = {}
        def _traverse(node, current_code):
            if node is None:
                return
            if node.char is not None: # Es un nodo hoja
                codes[node.char] = current_code
                return
            _traverse(node.left, current_code + "0")
            _traverse(node.right, current_code + "1")
        
        _traverse(root, "")
        return codes

    def _serialize_tree(self, root: HuffmanNode) -> bytearray:
        """
        Serializa el árbol de Huffman en un formato de pre-orden.
        Formato: '1' + byte_del_carácter para hojas, '0' para nodos internos.
        """
        if not root:
            return bytearray()
        
        def _serialize(node):
            if node.char is not None: # Nodo hoja
                return bytearray([1, ord(node.char)])
            else: # Nodo interno
                return bytearray([0]) + _serialize(node.left) + _serialize(node.right)
        
        return _serialize(root)

    def compress(self, text: str) -> bytearray:
        """Comprime un texto de entrada y devuelve un bytearray."""
        if not text:
            return bytearray()
        
        root = self._build_tree(text)
        codes = self._build_codes(root)
        
        # Codificar el texto en una cadena de bits
        encoded_bitstring = "".join(codes[char] for char in text)
        
        # Serializar el árbol para que el descompresor lo reconstruya
        serialized_tree = self._serialize_tree(root)
        
        # Empaquetar la cadena de bits en bytes
        # Añadimos padding al final si es necesario
        padding = (8 - len(encoded_bitstring) % 8) % 8
        encoded_bitstring += '0' * padding
        
        packed_data = bytearray()
        for i in range(0, len(encoded_bitstring), 8):
            byte = encoded_bitstring[i:i+8]
            packed_data.append(int(byte, 2))
            
        # Formato final: [padding_byte] + [serialized_tree] + [packed_data]
        return bytearray([padding]) + serialized_tree + packed_data

    def _deserialize_tree(self, data: bytearray, index: int = 0) -> (HuffmanNode, int):
        """Deserializa el árbol a partir de un bytearray."""
        if index >= len(data):
            return None, index
            
        flag = data[index]
        index += 1
        
        if flag == 1: # Nodo hoja
            char = chr(data[index])
            index += 1
            return HuffmanNode(char=char), index
        else: # Nodo interno
            left_node, index = self._deserialize_tree(data, index)
            right_node, index = self._deserialize_tree(data, index)
            return HuffmanNode(left=left_node, right=right_node), index

    def decompress(self, data: bytearray) -> str:
        """Descomprime un bytearray y devuelve el texto original."""
        if not data:
            return ""
            
        padding = data[0]
        tree_data_end_index = 1
        # El fin del árbol se encuentra cuando el deserializador termina
        root, tree_data_end_index = self._deserialize_tree(data, 1)
        
        packed_bitstream = data[tree_data_end_index:]
        
        # Desempaquetar los bytes a una cadena de bits
        bitstring = "".join(f'{byte:08b}' for byte in packed_bitstream)
        
        # Quitar el padding añadido durante la compresión
        if padding > 0:
            bitstring = bitstring[:-padding]
        
        # Decodificar la cadena de bits usando el árbol
        decoded_text = []
        current_node = root
        for bit in bitstring:
            current_node = current_node.left if bit == '0' else current_node.right
            
            if current_node.char is not None: # Llegamos a un nodo hoja
                decoded_text.append(current_node.char)
                current_node = root # Reiniciar para el siguiente carácter
                
        return "".join(decoded_text)

# --- Generador de Flujo de Clave Caótico (Sin cambios) ---
class ChaoticKeystreamGenerator:
    """Genera un flujo de bytes pseudo-aleatorios usando el mapa logístico."""
    def __init__(self, x0: float, r_param: float):
        if not (3.5699 < r_param <= 4.0):
            raise ValueError("El parámetro 'r' debe estar en el rango caótico (ej. 3.999).")
        self.x = x0
        self.r = r_param

    def next_byte(self) -> int:
        keystream_byte = 0
        for _ in range(8):
            self.x = self.r * self.x * (1.0 - self.x)
            scaled_val = int(self.x * 1e8)
            extracted_bit = (scaled_val >> 7) & 1
            keystream_byte = (keystream_byte << 1) | extracted_bit
        return keystream_byte

# --- Función Principal de Procesamiento (Ahora funcional) ---
def process_data(message: str):
    """
    Orquesta el proceso completo de compresión, encriptación,
    transmisión simulada, desencriptación y descompresión.
    """
    print(f"--- MENSAJE ORIGINAL ---")
    print(f"Texto: \"{message}\"")
    print(f"Tamaño: {len(message.encode('utf-8'))} bytes\n")

    # 1. Compresión REAL con Huffman
    huffman_compressor = HuffmanCompression()
    compressed_data = huffman_compressor.compress(message)
    
    print(f"--- DESPUÉS DE LA COMPRESIÓN ---")
    print(f"Tamaño: {len(compressed_data)} bytes")
    if len(message.encode('utf-8')) > 0:
        compression_ratio = len(message.encode('utf-8')) / len(compressed_data)
        print(f"Ratio de Compresión: {compression_ratio:.2f}:1\n")

    # 2. Encriptación
    secret_x0 = 0.7351
    secret_r = 3.999
    generator = ChaoticKeystreamGenerator(secret_x0, secret_r)

    ciphertext = bytearray()
    for data_byte in compressed_data:
        ciphertext.append(data_byte ^ generator.next_byte())
    
    print(f"--- DESPUÉS DE LA ENCRIPTACIÓN ---")
    print(f"Tamaño (sin cambios): {len(ciphertext)} bytes\n")

    # --- (Simular Transmisión) ---

    # 3. Desencriptación
    receiver_generator = ChaoticKeystreamGenerator(secret_x0, secret_r)
    recovered_compressed_data = bytearray()
    for cipher_byte in ciphertext:
        recovered_compressed_data.append(cipher_byte ^ receiver_generator.next_byte())
    
    print(f"--- DESPUÉS DE LA DESENCRIPTACIÓN ---")
    print(f"Tamaño: {len(recovered_compressed_data)} bytes\n")

    # 4. Descompresión REAL con Huffman
    recovered_message = huffman_compressor.decompress(recovered_compressed_data)
    
    print(f"--- MENSAJE RECUPERADO ---")
    print(f"Texto: \"{recovered_message}\"")
    print(f"Tamaño: {len(recovered_message.encode('utf-8'))} bytes\n")
    
    # Verificación final
    if message == recovered_message:
        print("✅ VERIFICACIÓN EXITOSA: El proceso de compresión, encriptación y descompresión funcionó perfectamente.")
    else:
        print("❌ ERROR DE VERIFICACIÓN: Los datos recuperados no coinciden.")

# --- Punto de Entrada del Script ---
if __name__ == "__main__":
    # Usamos un texto más largo y con caracteres repetidos para que Huffman sea efectivo
    original_message = "Este es un mensaje secreto para una transmisión segura y rápida. La seguridad es primordial."
    process_data(original_message)