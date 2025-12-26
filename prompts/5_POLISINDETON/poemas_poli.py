import os
import sys
import time
import json
import requests
import argparse
import string

# --- CONFIGURACIÓN ---
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODELO = "qwen2.5:7b"
POEMAS_POR_PALABRA = 7
TIEMPO_ESPERA = 1

USAR_REINTENTOS = True  
MAX_REINTENTOS = 3      

ENFOQUES = [
    "Tono: Agotamiento y pesadez",
    "Tono: Enumeración infinita",
    "Tono: Solemne y sagrado",
    "Perspectiva: La acumulación del tiempo",
    "Perspectiva: Elementos de la naturaleza",
    "Estilo: Barroco y recargado",
    "Estilo: Ansiedad urbana"
]

def generar_poema(palabra, enfoque):
    prompt = f"""Eres un poeta experto en retórica.
OBJETIVO: Escribir un poema de 4 versos con POLISÍNDETON sobre: '{palabra}'.

DEFINICIÓN DE POLISÍNDETON: Repetir varias veces la conjunción 'y' en un mismo verso para crear un ritmo lento y acumulativo.

REGLAS ABSOLUTAS:
1. REPETICIÓN: Cada verso debe usar la letra 'y' al menos dos o tres veces para unir conceptos.
2. ESTRUCTURA: 4 versos exactamente.
3. TEMA: El poema debe girar en torno a '{palabra}'.
4. No incluyas notas ni comentarios.

EJEMPLO:
Y el {palabra} y el viento y el frío y la noche,
y llora y grita y calla y espera,
y la sombra y el miedo y el sueño y el vacío,
y todo se acaba y nada se olvida.

Poema:"""

    payload = {
        "model": MODELO,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.75,
            "top_p": 0.9,
            "num_predict": 120,
            "stop": ["\n\n", "Nota:", "Análisis:"]
        }
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        return response.json().get('response', '').strip()
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")
        return None

def validar_polisindeton(poema):
    lineas = [l.strip().lower() for l in poema.split('\n') if l.strip()]
    if len(lineas) < 4:
        return False
        
    for linea in lineas[:4]:
        palabras = linea.split()
        conteo_y = palabras.count('y')
        if conteo_y < 2:
            return False
    return True

def main():
    parser = argparse.ArgumentParser()
    # Soporta múltiples enteros como argumentos
    parser.add_argument("lote_nums", type=int, nargs="+", help="Números de lote a procesar")
    args = parser.parse_args()

    out_dir = "resultados_polisindeton"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    for lote_num in args.lote_nums:
        str_lote = f"{lote_num:03d}"
        lote_file = f"lotes/lote_{str_lote}.txt"
        out_file = f"{out_dir}/polisindeton_lote_{str_lote}.txt"

        if not os.path.exists(lote_file):
            print(f"\n[ERROR] No existe el archivo: {lote_file}. Saltando...")
            continue

        # Inicializar el archivo de salida para este lote
        with open(out_file, 'w', encoding='utf-8') as f:
            pass

        print(f"\n>>> INICIANDO LOTE: {str_lote}")

        with open(lote_file, 'r', encoding='utf-8') as f_in:
            palabras_lote = [line.strip() for line in f_in if line.strip()]

        with open(out_file, 'a', encoding='utf-8') as f_out:
            for palabra in palabras_lote:
                print(f"=== Procesando: {palabra} ===")
                
                f_out.write(f"======[{palabra.upper()}]\n\n")
                
                for i in range(POEMAS_POR_PALABRA):
                    enfoque_actual = ENFOQUES[i % len(ENFOQUES)]
                    poema_final = ""
                    intentos = 0
                    
                    while True:
                        poema_generado = generar_poema(palabra, enfoque_actual)
                        if not poema_generado: break

                        if validar_polisindeton(poema_generado):
                            poema_final = poema_generado
                            break
                        else:
                            intentos += 1
                            if intentos <= MAX_REINTENTOS:
                                print(f"    [R] Reintento {intentos}...")
                                continue
                            else:
                                poema_final = poema_generado if poema_generado else "[FALLO]"
                                break

                    if poema_final:
                        f_out.write(f"{poema_final}\n\n")
                        f_out.write("---\n\n")
                        f_out.flush()
                        print(f"  ✓ [{i+1}/7] Generado")
                    
                    time.sleep(TIEMPO_ESPERA)

                f_out.write("\n")

        print(f"Lote {str_lote} finalizado. Salida en: {out_file}")

    print("\n[PROCESO DE TODOS LOS LOTES COMPLETADO]")

if __name__ == "__main__":
    main()