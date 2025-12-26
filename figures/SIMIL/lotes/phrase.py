import os
import glob
import re
import json

# --- CONFIGURACIÓN DE RUTAS ---
directorio_actual = os.getcwd()

if os.path.basename(directorio_actual) == "lotes":
    path_lotes = directorio_actual
    path_resultados = os.path.dirname(directorio_actual)
else:
    path_lotes = os.path.join(directorio_actual, "lotes")
    path_resultados = os.path.join(directorio_actual, "simi")

print(f"📂 Directorio de Lotes: {path_lotes}")
print(f"📂 Directorio de Resultados: {path_resultados}")

tokenizer_eos = "<|endoftext|>"
dataset_list = []

def get_lote_id(filename):
    match = re.search(r'(\d{3})', filename)
    return match.group(1) if match else None

archivos_lotes = sorted(glob.glob(os.path.join(path_lotes, "lote_*.txt")))

print(f"--- Iniciando procesamiento de {len(archivos_lotes)} lotes ---\n")

for archivo_palabras in archivos_lotes:
    lote_id = get_lote_id(os.path.basename(archivo_palabras))
    
    if not lote_id:
        continue

    patron_busqueda = os.path.join(path_resultados, f"simil_lote_{lote_id}*.txt")
    archivos_poemas = sorted(glob.glob(patron_busqueda))

    if not archivos_poemas:
        continue

    # Leer las PALABRAS
    with open(archivo_palabras, 'r', encoding='utf-8', errors='ignore') as f:
        palabras = [line.strip() for line in f if line.strip()]

    # Leer los POEMAS
    contenido_poemas_completo = ""
    for ap in archivos_poemas:
        try:
            with open(ap, 'r', encoding='utf-8') as f:
                contenido_poemas_completo += "\n" + f.read()
        except UnicodeDecodeError:
            with open(ap, 'r', encoding='cp1252') as f:
                contenido_poemas_completo += "\n" + f.read()

    # --- CORRECCIÓN AQUÍ ---
    # La regex r'={3,}\[.*?\]' busca:
    # ={3,}   -> 3 o más signos de igual
    # \[      -> Un corchete de apertura literal
    # .*?     -> Cualquier texto (el nombre de la figura) de forma no ambiciosa
    # \]      -> Un corchete de cierre literal
    bloques_poemas = [b.strip() for b in re.split(r'={3,}\[.*?\]', contenido_poemas_completo) if b.strip()]

    # VALIDACIÓN
    cantidad_procesar = min(len(palabras), len(bloques_poemas))
    
    if cantidad_procesar == 0:
        print(f"❌ Lote {lote_id}: 0 pares (Palabras: {len(palabras)} | Bloques: {len(bloques_poemas)})")
        continue

    print(f"✅ Lote {lote_id}: {cantidad_procesar} pares encontrados")

    # CREAR ENTRADAS
    for i in range(cantidad_procesar):
        palabra_clave = palabras[i]
        bloque_texto = bloques_poemas[i]
        
        # Separar versiones por "---"
        versiones_poema = [p.strip() for p in bloque_texto.split("---") if p.strip()]
        
        for poema in versiones_poema:
            if len(poema) < 10: continue

            entry = {
                "text": f"""Escribe un poema usando la figura retórica "simil" con la palabra "{palabra_clave}".
Poema:
{poema}
{tokenizer_eos}"""
            }
            dataset_list.append(entry)

# --- GUARDADO ---
print("\n" + "="*40)
print(f"TOTAL EJEMPLOS GENERADOS: {len(dataset_list)}")
print("="*40)

output_file = "dataset_final_simil.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(dataset_list, f, ensure_ascii=False, indent=2)

print(f"¡Listo! Se ha creado '{output_file}'")