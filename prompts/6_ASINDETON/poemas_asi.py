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
    # Prompt diseñado para Asíndeton: eliminación de nexos
    prompt = f"""Eres un poeta experto en retórica.
OBJETIVO: Escribir un poema de 4 versos con ASÍNDETON sobre: '{palabra}'.

DEFINICIÓN DE ASÍNDETON: Eliminar todas las conjunciones (y, o, ni) y sustituirlas por comas para crear un ritmo rápido y directo.

REGLAS ABSOLUTAS:
1. OMISIÓN: No uses nunca las palabras 'y', 'o' o 'ni' para unir conceptos. Usa solo comas.
2. ESTRUCTURA: 4 versos exactamente. Cada verso debe ser una lista de acciones o imágenes separadas por comas.
3. TEMA: El poema debe girar en torno a '{palabra}'.
4. No incluyas notas ni comentarios.

EJEMPLO:
El {palabra}, el viento, el frío, la noche,
llora, grita, calla, espera,
la sombra, el miedo, el sueño, el vacío,
todo se acaba, nada se olvida, el fin.

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

def validar_asindeton(poema):
    """Verifica la ausencia de conjunciones y la presencia de comas."""
    lineas = [l.strip().lower() for l in poema.split('\n') if l.strip()]
    if len(lineas) < 4:
        return False
        
    conjunciones_prohibidas = [' y ', ' e ', ' o ', ' u ', ' ni ']
    
    for linea in lineas[:4]:
        # 1. Comprobar que no existan conjunciones
        if any(conj in f" {linea} " for conj in conjunciones_prohibidas):
            return False
        
        # 2. Comprobar que haya al menos dos comas por verso para garantizar el recurso
        if linea.count(',') < 2:
            return False
            
    return True

def main():
    parser = argparse.ArgumentParser()
    # Cambio: Ahora acepta una lista de enteros
    parser.add_argument("lote_nums", type=int, nargs="+", help="Lista de números de lote (ej: 1 2 3)")
    args = parser.parse_args()

    out_dir = "resultados_asindeton"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # Bucle para procesar cada lote solicitado
    for lote_num in args.lote_nums:
        str_lote = f"{lote_num:03d}"
        lote_file = f"lotes/lote_{str_lote}.txt"
        out_file = f"{out_dir}/asindeton_lote_{str_lote}.txt"

        if not os.path.exists(lote_file):
            print(f"\n[ERROR] No existe el archivo: {lote_file}. Saltando lote...")
            continue

        # Limpiar/crear archivo de salida para el lote actual
        with open(out_file, 'w', encoding='utf-8') as f:
            pass

        print(f"\n>>> INICIANDO PROCESO - LOTE: {str_lote}")

        with open(lote_file, 'r', encoding='utf-8') as f_in:
            palabras_lote = [line.strip() for line in f_in if line.strip()]

        with open(out_file, 'a', encoding='utf-8') as f_out:
            for palabra in palabras_lote:
                print(f"=== Procesando: {palabra} ===")
                
                # Encabezado de la palabra
                f_out.write(f"======[{palabra.upper()}]\n\n")
                
                for i in range(POEMAS_POR_PALABRA):
                    enfoque_actual = ENFOQUES[i % len(ENFOQUES)]
                    poema_final = ""
                    
                    intentos = 0
                    while True:
                        poema_generado = generar_poema(palabra, enfoque_actual)
                        if not poema_generado: break

                        if validar_asindeton(poema_generado):
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
                        # Contenido del poema
                        f_out.write(f"{poema_final}\n\n")
                        # Separador después de cada poema
                        f_out.write("---\n\n")
                        f_out.flush()
                        print(f"  ✓ [{i+1}/7] Generado")
                    
                    time.sleep(TIEMPO_ESPERA)

                # Salto entre bloques de palabras
                f_out.write("\n")

        print(f"Lote {str_lote} finalizado. Resultados en: {out_file}")

    print("\n[PROCESO COMPLETO]")

if __name__ == "__main__":
    main()