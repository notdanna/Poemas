import os
import glob
import re
from datasets import Dataset

# --- CONFIGURACIÓN DE RUTAS (AUTOMÁTICA) ---

# Detectamos dónde se está ejecutando el script
directorio_actual = os.getcwd()

# Lógica para encontrar las carpetas basándonos en tu 'ls'
# Si corres el script desde la carpeta 'lotes':
if os.path.basename(directorio_actual) == "lotes":
    path_lotes = directorio_actual
    # 'resultados' está un nivel arriba y luego entramos a resultados
    path_resultados = os.path.join(os.path.dirname(directorio_actual), "resultados")
else:
    # Si por casualidad lo corres desde la carpeta padre 'Palabras'
    path_lotes = os.path.join(directorio_actual, "lotes")
    path_resultados = os.path.join(directorio_actual, "resultados")

print(f"📂 Directorio de Lotes: {path_lotes}")
print(f"📂 Directorio de Resultados: {path_resultados}")

tokenizer_eos = "<|endoftext|>"
dataset_list = []

# Función para extraer el número del lote (ej: "005" de "lote_005.txt")
def get_lote_id(filename):
    match = re.search(r'(\d{3})', filename)
    return match.group(1) if match else None

# 1. Identificar todos los archivos de palabras (lotes)
archivos_lotes = sorted(glob.glob(os.path.join(path_lotes, "lote_*.txt")))

print(f"--- Iniciando procesamiento de {len(archivos_lotes)} lotes potenciales ---\n")

for archivo_palabras in archivos_lotes:
    lote_id = get_lote_id(os.path.basename(archivo_palabras))
    
    if not lote_id:
        continue

    # 2. Buscar los archivos de poemas correspondientes en 'resultados'
    patron_busqueda = os.path.join(path_resultados, f"anafora_lote_{lote_id}*.txt")
    archivos_poemas = sorted(glob.glob(patron_busqueda))

    if not archivos_poemas:
        # Esto es normal si tienes más lotes que resultados generados
        # print(f"⚠️ Salta Lote {lote_id}: No hay resultados aún.") 
        continue

    # 3. Leer las PALABRAS
    with open(archivo_palabras, 'r', encoding='utf-8', errors='ignore') as f:
        palabras = [line.strip() for line in f if line.strip()]

    # 4. Leer y juntar los POEMAS
    contenido_poemas_completo = ""
    for ap in archivos_poemas:
        try:
            with open(ap, 'r', encoding='utf-8') as f:
                contenido_poemas_completo += "\n" + f.read()
        except UnicodeDecodeError:
            with open(ap, 'r', encoding='cp1252') as f:
                contenido_poemas_completo += "\n" + f.read()

    # Separar por los bloques de TEMA (===)
    bloques_poemas = [b.strip() for b in contenido_poemas_completo.split("===============================================") if b.strip()]

    # 5. VALIDACIÓN Y EMPAREJAMIENTO
    cantidad_procesar = min(len(palabras), len(bloques_poemas))
    
    if cantidad_procesar == 0:
        continue

    print(f"✅ Lote {lote_id}: {cantidad_procesar} pares")

    # 6. CREAR LAS ENTRADAS DEL DATASET
    for i in range(cantidad_procesar):
        palabra_clave = palabras[i]
        bloque_texto = bloques_poemas[i]
        
        versiones_poema = [p.strip() for p in bloque_texto.split("---") if p.strip()]
        
        for poema in versiones_poema:
            entry = {
                "text": 
f"""Escribe un poema usando la figura retórica "anáfora" con la palabra "{palabra_clave}".
Poema:
{poema}
{tokenizer_eos}"""
            }
            dataset_list.append(entry)

# --- RESUMEN FINAL ---
print("\n" + "="*40)
print(f"TOTAL EJEMPLOS GENERADOS: {len(dataset_list)}")
print("="*40)

# GUARDAR JSON PARA LUEGO SUBIRLO A COLAB
# Como estás en local, no podemos crear la variable 'hf_dataset' directamente si no tienes
# la librería 'datasets' instalada. Mejor guardamos un JSON.
import json

output_file = "dataset_final_anafora.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(dataset_list, f, ensure_ascii=False, indent=2)

print(f"¡Listo! Se ha creado el archivo '{output_file}'")
print("Sube este archivo a tu Google Drive para entrenar.")