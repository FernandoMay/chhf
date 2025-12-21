chhf — Compresión Huffman + Cifrado Caótico (ejemplo)

**Resumen**
- **Descripción**: Proyecto de ejemplo que implementa compresión de datos mediante el algoritmo de Huffman y un cifrado por flujo pseudo-aleatorio basado en un generador caótico (mapa logístico). El script demuestra el flujo completo: compresión -> cifrado -> transmisión simulada -> descifrado -> descompresión.

**Características**
- **Compresión**: Implementación completa de Huffman (construcción de árbol, generación de códigos, serialización/deserialización).
- **Cifrado**: Flujo de bytes pseudo-aleatorio generado por un mapa logístico (chaotic keystream) y aplicado mediante XOR.
- **Demo**: Punto de entrada que ejecuta un ejemplo end-to-end y verifica la integridad del mensaje recuperado.

**Requisitos**
- **Python**: 3.8 o superior.
- **Dependencias**: Ninguna externa; solo la biblioteca estándar de Python.

**Instalación**
- Clona o descarga el repositorio y sitúate en la carpeta del proyecto.

```bash
git clone <repo-url>   # opcional
cd chhf
```

**Uso**
- Ejecutar el script de demostración:

```bash
python chhf.py
```

- Importar y usar programáticamente (ejemplo interactivo):

```bash
python -c "from chhf import process_data; process_data('Mensaje de prueba para compresión y cifrado.')"
```

**Archivos clave**
- **Script principal**: [chhf.py](chhf.py#L1-L400) — contiene la implementación de `HuffmanCompression`, `ChaoticKeystreamGenerator` y la función `process_data`.

**API rápida**
- **`HuffmanCompression`**: Clase con métodos `compress(text: str) -> bytearray` y `decompress(data: bytearray) -> str`.
- **`ChaoticKeystreamGenerator`**: Generador de bytes pseudo-aleatorios a partir del mapa logístico; inicializar con `x0` y `r_param` (r en rango caótico).
- **`process_data(message: str)`**: Función que orquesta compresión, cifrado, simulación de transmisión, descifrado y descompresión, imprimiendo resultados.

**Ejemplos y notas**
- El parámetro `r` del generador caótico debe estar en el rango caótico (por ejemplo `3.999`).
- El formato interna de los datos comprimidos es: `[padding_byte] + [árbol_serializado] + [datos_empaquetados]`.

**Contribuir**
- Sugerencias, mejoras y correcciones son bienvenidas. Abre un issue o un pull request con cambios propuestos.

**Licencia**
- No se incluye un archivo de licencia en el repositorio. Añade un `LICENSE` si quieres publicar con una licencia específica (p. ej. MIT).

**Autor / Mantenimiento**
- Mantenimiento: fmayf (usuario local). Para ayuda o preguntas, abre un issue en el repositorio o contacta al mantenedor.

