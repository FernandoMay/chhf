import sys
import heapq
import collections

# --- Implementación Real de Compresión Huffman (Sin cambios) ---
class HuffmanNode:
    def __init__(self, char=None, freq=0, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right
    def __lt__(self, other):
        return self.freq < other.freq

class HuffmanCompression:
    def _build_tree(self, text: str) -> HuffmanNode:
        if not text: return None
        frequency = collections.Counter(text)
        priority_queue = [HuffmanNode(char, freq) for char, freq in frequency.items()]
        heapq.heapify(priority_queue)
        while len(priority_queue) > 1:
            left = heapq.heappop(priority_queue)
            right = heapq.heappop(priority_queue)
            merged = HuffmanNode(freq=left.freq + right.freq, left=left, right=right)
            heapq.heappush(priority_queue, merged)
        return priority_queue[0]

    def _build_codes(self, root: HuffmanNode) -> dict:
        codes = {}
        def _traverse(node, current_code):
            if node is None: return
            if node.char is not None:
                # Single-leaf tree (text with one unique symbol): the natural
                # empty code is unusable for decoding, so assign an explicit
                # "0" bit per symbol. Fixes data loss on single-symbol input.
                codes[node.char] = current_code if current_code else "0"
                return
            _traverse(node.left, current_code + "0")
            _traverse(node.right, current_code + "1")
        _traverse(root, "")
        return codes

    def _serialize_tree(self, root: HuffmanNode) -> bytearray:
        if not root: return bytearray()
        def _serialize(node):
            if node.char is not None:
                char_bytes = node.char.encode('utf-8')
                length = len(char_bytes)
                if length > 255:
                    raise ValueError("Character encoding too long to serialize")
                return bytearray([1, length]) + bytearray(char_bytes)
            else:
                return bytearray([0]) + _serialize(node.left) + _serialize(node.right)
        return _serialize(root)

    def compress(self, text: str) -> bytearray:
        if not text: return bytearray()
        root = self._build_tree(text)
        codes = self._build_codes(root)
        encoded_bitstring = "".join(codes[char] for char in text)
        serialized_tree = self._serialize_tree(root)
        padding = (8 - len(encoded_bitstring) % 8) % 8
        encoded_bitstring += '0' * padding
        packed_data = bytearray(int(encoded_bitstring[i:i+8], 2) for i in range(0, len(encoded_bitstring), 8))
        return bytearray([padding]) + serialized_tree + packed_data

    def _deserialize_tree(self, data: bytearray, index: int = 0) -> (HuffmanNode, int):
        if index >= len(data): return None, index
        flag = data[index]
        index += 1
        if flag == 1:
            if index >= len(data):
                raise ValueError("Invalid serialized tree: missing length")
            length = data[index]
            index += 1
            if index + length > len(data):
                raise ValueError("Invalid serialized tree: incomplete character bytes")
            char_bytes = bytes(data[index:index+length])
            char = char_bytes.decode('utf-8')
            index += length
            return HuffmanNode(char=char), index
        else:
            left_node, index = self._deserialize_tree(data, index)
            right_node, index = self._deserialize_tree(data, index)
            return HuffmanNode(left=left_node, right=right_node), index

    def decompress(self, data: bytearray) -> str:
        if not data: return ""
        padding = data[0]
        root, tree_data_end_index = self._deserialize_tree(data, 1)
        packed_bitstream = data[tree_data_end_index:]
        bitstring = "".join(f'{byte:08b}' for byte in packed_bitstream)
        if padding > 0: bitstring = bitstring[:-padding]
        decoded_text = []
        current_node = root
        for bit in bitstring:
            # Single-leaf tree: every bit decodes one symbol (there is no
            # child to descend to).
            if current_node.char is not None:
                decoded_text.append(current_node.char)
                continue
            current_node = current_node.left if bit == '0' else current_node.right
            if current_node.char is not None:
                decoded_text.append(current_node.char)
                current_node = root
        return "".join(decoded_text)

# --- Generador de Flujo de Clave Caótico (Sin cambios) ---
class ChaoticKeystreamGenerator:
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

# --- Función Principal de Procesamiento (Mejorada) ---
def process_data(message: str):
    original_bytes = message.encode('utf-8')
    print("--- MENSAJE ORIGINAL ---")
    print(f"Texto: \"{message[:100]}...\"") # Mostrar solo una parte del texto largo
    print(f"Tamaño: {len(original_bytes)} bytes\n")

    # 1. Compresión REAL con Huffman
    huffman_compressor = HuffmanCompression()
    compressed_data = huffman_compressor.compress(message)
    
    print("--- ETAPA 1: COMPRESIÓN ---")
    print(f"Tamaño original: {len(original_bytes)} bytes")
    print(f"Tamaño comprimido: {len(compressed_data)} bytes")
    if len(original_bytes) > 0:
        compression_ratio = len(original_bytes) / len(compressed_data)
        print(f"Ratio de Compresión: {compression_ratio:.2f}:1 (¡Más de 1 es bueno!)\n")

    # 2. Encriptación
    secret_x0 = 0.7351
    secret_r = 3.999
    generator = ChaoticKeystreamGenerator(secret_x0, secret_r)
    ciphertext = bytearray()
    for data_byte in compressed_data:
        ciphertext.append(data_byte ^ generator.next_byte())
    
    print("--- ETAPA 2: ENCRIPTACIÓN ---")
    print(f"Clave Secreta (x0, r): ({secret_x0}, {secret_r})")
    print(f"Datos Cifrados (Hex): {ciphertext.hex()}")
    print(f"Tamaño del ciphertext: {len(ciphertext)} bytes\n")

    # --- (Simular Transmisión) ---

    # 3. Desencriptación
    receiver_generator = ChaoticKeystreamGenerator(secret_x0, secret_r)
    recovered_compressed_data = bytearray()
    for cipher_byte in ciphertext:
        recovered_compressed_data.append(cipher_byte ^ receiver_generator.next_byte())
    
    print("--- ETAPA 3: DESENCRIPTACIÓN ---")
    print(f"Tamaño recuperado: {len(recovered_compressed_data)} bytes\n")

    # 4. Descompresión REAL con Huffman
    recovered_message = huffman_compressor.decompress(recovered_compressed_data)
    
    print("--- ETAPA 4: DESCOMPRESIÓN ---")
    print(f"Texto recuperado: \"{recovered_message[:50]}...\"")
    print(f"Tamaño final: {len(recovered_message.encode('utf-8'))} bytes\n")
    
    # Verificación final
    if message == recovered_message:
        print("✅ VERIFICACIÓN EXITOSA: El proceso funcionó perfectamente.")
    else:
        print("❌ ERROR DE VERIFICACIÓN: Los datos recuperados no coinciden.")

# --- Punto de Entrada del Script ---
if __name__ == "__main__":
    # Usamos un texto largo y repetitivo para que Huffman sea efectivo
    original_message = """
    En el corazón de la vasta y silenciosa noche, un único faro enviaba su rayo de luz
    sobre las olas oscuras y espumosas del mar. El faro, un centinela de piedra y
    metal, había resistido innumerables tormentas, su luz una promesa constante de
    seguridad para los barcos que se aventuraban en la oscuridad. Cada giro de su
    poderoso haz era un latido en la inmensidad, un susurro de guía para los
    navegantes perdidos. La seguridad era su única y más importante misión.
    La seguridad, la seguridad, la seguridad. Sin seguridad no hay nada.
    Los montañistas entraron en la cabaña. No era muy grande pero era acogedora,
    con sus grandes ventanales y sus sillones. Javier prendió la chimenea para que se calentara el ambiente y Sandra comenzó a preparar unos bocadillos.
    Cenaron sentados junto al fuego porque hacía mucho frío. (párrafo literario narrativo)
    Miguel nunca antes había visto un objeto así. Era una caja azul brillante que no parecía poder abrirse ya que no tenía fisuras o un lugar donde colocar una llave.
    Parecía ser hueca, porque él la golpeó y retumbó un poco. Parecía que no tenía nada dentro, porque él la agitó y no se escuchaba nada. 
    Era una caja muy misteriosa y Miguel no entendía por qué se la habían dejado en la entrada de su casa. (párrafo literario descriptivo)
    Enzo le preguntó la hora a su colega, pero este no le respondió porque no lo había escuchado. Enzo le hizo la misma pregunta otra vez y su colega le contestó que eran las dos y media.
    Enzo le dijo que se tenían que apresurar para terminar el trabajo, porque tenían que presentárselo al jefe en menos de una hora, pero su colega, muy tranquilamente, le contestó que tendrían todo listo en diez minutos.
    El marinero fue hacia la popa, se dio cuenta de que se avecinaba una tormenta y fue corriendo hasta donde estaba el capitán para avisarle que tenían que cambiar de rumbo.
    El capitán decidió que irían a una isla que conocía y que quedaba cerca del lugar donde estaban. Por suerte, el viento soplaba a favor del nuevo rumbo y no tardaron mucho en llegar.
    El campo estaba en un valle rodeado de montañas nevadas. Era muy colorido porque había plantaciones de muchos tipos de flores y, por eso, olía muy bien. A la izquierda del camino que cruzaba este extenso lugar había una cabaña que tenía una chimenea que echaba humo. Al lado de la cabaña había dos caballos que tomaban agua de un pequeño arroyo. No había personas fuera de la casa, pero la puerta estaba abierta. (párrafo literario descriptivo)
    —Buenos días, ¿sabe si este tren se dirige al norte? —le preguntó Carmen a un hombre en la estación. (párrafo literario de diálogo uno)
    —No estoy seguro, no soy de este lugar, pero puede preguntar en esa ventanilla —dijo el hombre señalando a la boletería de la estación— sé que se detiene en la estación principal de París.
    —¡Qué bueno! Porque tengo que ir allí. Gracias.
    El cazador había perdido todas sus herramientas de caza, pero se dio cuenta de que no las necesitaba porque podía alimentarse de las frutas que crecían en los árboles. Se puso muy contento con esta determinación y decidió que,
    cuando llegara a la ciudad, les diría a sus amigos que no practicaría esta actividad nunca más, porque había aprendido a respetar a la naturaleza. (párrafo literario narrativo)
    Todas las personas caminaban rápido cuando pasaban por la entrada de la casa abandonada y realmente entiendo el porqué; la casa era aterradora. La entrada tenía una reja pintada de blanco,
    pero que estaba muy oxidada. En el jardín delantero el pasto estaba quemado y había un camino de piedras hasta la puerta. La puerta tenía dos hojas de madera de dos metros, que se notaba que en algún momento habían sido muy hermosas, pero ya no lo eran. Había cuatro ventanas, dos en la planta baja y dos en la planta alta, que estaban tapiadas. Nadie sabía de quién había sido la casa, era como si siempre hubiera estado así, abandonada. (párrafo literario descriptivo)
    Sonó el timbre y Estela atendió, preguntó quién era, pero nadie contestó. Después se oyó una voz que decía que era Pedro. Estela contestó que no conocía a ningún Pedro y que creía que se estaba confundiendo de timbre. Pedro le preguntó al encargado del edificio si allí vivía Marcos y el portero le contestó que no conocía a nadie con ese nombre que viviera en ese edificio. (párrafo literario de diálogo)
    Gabriela salió a caminar, hizo media cuadra y dobló a la derecha. Vio cómo abrían las tiendas y cómo el sol comenzaba a calentar el asfalto. Siguió caminando hacia el sur,
    donde se terminaba el asfalto y, por lo tanto, donde se terminaba el pueblo. Al pisar el pasto se sintió mejor porque sabía que ya le faltaba poco para llegar al bosque. Caminó un kilómetro más, hasta que vio los primeros árboles y la orilla del lago. (párrafo narrativo)
    """
    # Limpiamos el texto para un conteo preciso
    original_message = original_message.strip()
    process_data(original_message)