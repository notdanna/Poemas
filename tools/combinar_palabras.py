from pathlib import Path
from collections import Counter

# Contar palabras en todos los archivos
todas_palabras = []
palabras_por_archivo = {}

archivos = list(Path('.').glob('palabras/palabras_*.txt'))

for archivo in archivos:
    palabras_archivo = []
    with open(archivo, 'r', encoding='utf-8') as f:
        for linea in f:
            palabra = linea.strip().split('\t')[0]
            if palabra:
                palabras_archivo.append(palabra)
                todas_palabras.append(palabra)
    palabras_por_archivo[archivo.name] = len(palabras_archivo)
    print(f"{archivo.name}: {len(palabras_archivo)} palabras")

# Contar duplicados
contador = Counter(todas_palabras)
palabras_unicas = set(todas_palabras)

total_palabras = len(todas_palabras)
total_unicas = len(palabras_unicas)
repetidas = total_palabras - total_unicas

print(f"\n{'='*50}")
print(f"Total de palabras (con repeticiones): {total_palabras}")
print(f"Palabras únicas: {total_unicas}")
print(f"Repeticiones: {repetidas}")

# Guardar sin duplicados
with open('palabras_todas_unicas.txt', 'w', encoding='utf-8') as f:
    for palabra in sorted(palabras_unicas):
        f.write(f"{palabra}\n")

print(f"\nGuardadas en: palabras_todas_unicas.txt")