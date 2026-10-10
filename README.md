# chhf — Compresión Huffman + Cifrado Caótico

Proyecto educativo que implementa **compresión de datos real (Huffman)** y un **cifrado por flujo pseudo-aleatorio** basado en un generador caótico (mapa logístico), con el flujo completo: compresión → cifrado → transmisión simulada → descifrado → descompresión.

## ⚠️ Aviso de seguridad (léelo)

El `ChaoticKeystreamGenerator` (mapa logístico) es **inseguro para uso real**: es determinista, tiene parámetros públicos y se rompe con análisis de спектр/recuperación de estado. Es una demostración didáctica de *stream cipher + XOR*, nada más. Para producción usá `cryptography` (AES-GCM / ChaCha20-Poly1305).

## Estado del revival (2026-10)

Este repo vivió años como un solo script sin tests. El revival trajo:

- **🐛 Bug fixeado**: la compresión de textos con **un solo símbolo único** (`"aaaa"`, `"a"`) descomprimía a `""` — pérdida total de datos. El árbol de hoja única recibe ahora un código `"0"` explícito y `decompress` maneja ese caso. Regresión cubierta por tests.
- **🧪 Suite de tests**: 18 tests (round-trip, formato wire, casos borde, keystream caótico).
- **🖥️ CLI**: comprimí/descomprimí archivos de texto desde la terminal.
- **📦 Packaging**: proyecto Python instalable (`pyproject.toml`), paquete `chhf`.
- **🧹 Higiene**: `__pycache__` fuera del repo, `.gitignore`, licencia MIT.

## Instalación

```bash
pip install .        # o: pip install -e .   para desarrollo
```

## Uso

### Demo end-to-end

```bash
python -m chhf demo
```

### CLI de archivos

```bash
python -m chhf compress original.txt salida.chhf
python -m chhf decompress salida.chhf recuperado.txt
```

Solo archivos de **texto UTF-8** (la implementación Huffman opera sobre `str`).

### Uso programático

```python
from chhf import HuffmanCompression, ChaoticKeystreamGenerator

h = HuffmanCompression()
comprimido = h.compress("seguridad, seguridad, seguridad")   # -> bytearray
original = h.decompress(comprimido)                          # -> str

gen = ChaoticKeystreamGenerator(x0=0.7351, r_param=3.999)
keystream = [gen.next_byte() for _ in range(16)]
```

## Tests

```bash
python -m unittest discover -s tests -v
```

Cubren:
- Round-trip idéntico: vacío, 1 símbolo, símbolo repetido, ASCII, Unicode/emoji, newlines, texto largo.
- Ratio de compresión real en datos redundantes.
- Formato wire `[padding][árbol][datos]` y errores ante árbol corrupto.
- Keystream caótico: determinismo, rango de bytes, rechazo de `r` fuera del rango caótico (3.5699, 4.0].

## Arquitectura

```
chhf/
├── __init__.py     # HuffmanCompression + ChaoticKeystreamGenerator + process_data
└── __main__.py     # CLI (compress / decompress / demo)
tests/
└── test_chhf.py    # 18 tests, stdlib unittest (sin dependencias)
```

- **HuffmanCompression**: construcción de árbol, códigos, serialización/deserialización del árbol y empaquetado de bits.
  - Formato: `[1 byte padding] + [árbol serializado] + [bits empaquetados]`
  - Serialización de hoja: `0x01 [len] [bytes UTF-8]`; nodo interno: `0x00 [subárbol izq] [subárbol der]`.
- **ChaoticKeystreamGenerator**: keystream de bytes desde el mapa logístico `x = r·x·(1−x)`, tomando 1 bit por iteración.

## Requisitos

- Python ≥ 3.8. **Cero dependencias externas** (solo biblioteca estándar).

## Licencia

MIT — ver [LICENSE](LICENSE).

## Autor

[FernandoMay](https://github.com/FernandoMay)
