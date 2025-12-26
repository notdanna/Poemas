import re
import os

def limpiar_texto_poemas(texto_crudo):
    """
    Limpia texto de poemas para entrenamiento de LLM/Transformers.
    Elimina números romanos, espacios extra y estandariza separadores.
    """
    
    lines = texto_crudo.splitlines()
    cleaned_lines = []
    
    # Patrón para detectar números romanos solos en una línea (ej: " III ", "IV")
    # Detecta I, V, X, L, C, D, M
    patron_romanos = re.compile(r'^\s*[IVXLCDM]+\s*$', re.IGNORECASE)

    for line in lines:
        # 1. Eliminar espacios en blanco invisibles (non-breaking spaces) y tabs
        # \xa0 es el código para el espacio de no separación común en copias de web
        linea_limpia = line.replace('\xa0', ' ').strip()
        
        # 2. Si la línea está vacía, la guardamos como cadena vacía para conservar estrofas
        if not linea_limpia:
            cleaned_lines.append("")
            continue

        # 3. Detectar si es un número de capítulo (Romano)
        if patron_romanos.match(linea_limpia):
            # Reemplazamos el número de capítulo por el separador estándar
            # Solo agregamos el separador si no acabamos de agregar uno
            if cleaned_lines and cleaned_lines[-1] != "---":
                cleaned_lines.append("")
                cleaned_lines.append("---")
                cleaned_lines.append("")
            continue
            
        # 4. Limpieza de símbolos extraños específicos si es necesario
        # Nota: En poesía, "idïoma" con diéresis es métrica válida (rompe el diptongo).
        # Se recomienda NO eliminar puntuación (¡!¿?,.;) ya que da entonación al modelo.
        
        cleaned_lines.append(linea_limpia)

    # 5. Reconstruir el texto y eliminar excesos de líneas en blanco
    texto_procesado = "\n".join(cleaned_lines)
    
    # Reducir múltiples saltos de línea a máximo 2 (para separar estrofas)
    # y asegurar que el separador '---' tenga aire alrededor.
    texto_procesado = re.sub(r'\n{3,}', '\n\n', texto_procesado)
    
    return texto_procesado

# --- BLOQUE PRINCIPAL PARA LEER ARCHIVOS ---

# Nombres de archivo configurables
archivo_entrada = "Rimas.txt"
archivo_salida = "poemas_limpios.txt"

if __name__ == "__main__":
    if os.path.exists(archivo_entrada):
        try:
            print(f"Leyendo archivo '{archivo_entrada}'...")
            
            # Abrir con encoding utf-8 para soportar acentos y ñ
            with open(archivo_entrada, "r", encoding="utf-8") as f:
                contenido = f.read()
            
            # Ejecutar la limpieza
            resultado = limpiar_texto_poemas(contenido)
            
            # Guardar resultado
            with open(archivo_salida, "w", encoding="utf-8") as f:
                f.write(resultado)
                
            print(f"¡Éxito! El texto limpio se ha guardado en '{archivo_salida}'.")
            
        except Exception as e:
            print(f"Ocurrió un error al procesar el archivo: {e}")
    else:
        print(f"Error: No se encontró el archivo '{archivo_entrada}'.")
        print("Por favor, crea un archivo llamado 'poemas.txt' y pega ahí tus poemas.")