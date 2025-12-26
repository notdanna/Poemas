import os
import sys
import time
import json
import requests
import argparse

# --- CONFIGURACIÓN ---
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODELO = "qwen2.5:7b"
POEMAS_POR_PALABRA = 7
TIEMPO_ESPERA = 1

USAR_REINTENTOS = True  
MAX_REINTENTOS = 3      

ENFOQUES = [
    "Estructura: Comparativa (Como X... como Y...)",
    "Estructura: Condicional (Si X... entonces Y... / Si A... entonces B...)",
    "Estructura: Anáfora (Misma palabra al inicio de cada verso)",
    "Estructura: Sintáctica (Sujeto + Verbo + Adjetivo)",
    "Tono: Litúrgico (Repetición de súplicas o estados)",
    "Tono: Antítesis (En el día X / En la noche Y)",
    "Estilo: Minimalista (Versos breves, ritmo seco)",
    "Perspectiva: Localización (En el pecho X / En el alma Y)",
    "Perspectiva: Temporal (Ayer fue X / Mañana será Y)",
    "Tono: Volitivo (Deseo X / Anhelo Y)"
]

def generar_poema(palabra, enfoque):
    prompt = f"""Eres un poeta experto en retórica y gramática española.

OBJETIVO: Escribir un poema de 4 versos con PARALELISMO RIGUROSO sobre: '{palabra}'.

REGLAS DE ORO (ESTRICTO):
1. PROHIBICIÓN LÉXICA: No inventes palabras. Usa solo términos existentes en el diccionario de la RAE.
2. CONCORDANCIA: Revisa el género y número. (Ejemplo correcto: 'Las almas', 'El agua fría').
3. SIMETRÍA CONDICIONAL: Si usas 'Si...', el verso debe completarse con una acción simétrica. No dejes frases colgadas.
4. COHERENCIA LÓGICA: Las imágenes deben ser elegantes y tener sentido. No mezcles anatomía con objetos mundanos sin sentido lírico.
5. PARALELISMO: Cada verso debe tener la misma estructura gramatical que el anterior.

INSTRUCCIONES ESPECÍFICAS:
Contexto/Estructura: {enfoque}
Palabra obligatoria: '{palabra}' (puede ir en cualquier posición).

EJEMPLO DE ESTRUCTURA RIGUROSA:
En el silencio nace la duda,
en el estruendo muere la calma,
en el olvido crece la sombra,
en el recuerdo brilla la llama.

TU TURNO (Escribe solo el poema de 4 versos):
Poema:"""

    payload = {
        "model": MODELO,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
            "repeat_penalty": 1.0,
            "num_predict": 120,
            "stop": ["\n\n", "Nota:", "Análisis:", "Palabra:"]
        }
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        return response.json().get('response', '').strip()
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")
        return None

def main():
    parser = argparse.ArgumentParser()
    # nargs='+' permite capturar uno o más números de lote
    parser.add_argument("lote_nums", type=int, nargs="+", help="Lista de números de lote (ej: 1 2 3)")
    args = parser.parse_args()

    out_dir = "resultados_paralelismo"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    for lote_num in args.lote_nums:
        str_lote = f"{lote_num:03d}"
        lote_file = f"lotes/lote_{str_lote}.txt"
        out_file = f"{out_dir}/paralelismo_lote_{str_lote}.txt"

        if not os.path.exists(lote_file):
            print(f"[ERROR] No existe el archivo: {lote_file}. Saltando lote...")
            continue

        # Limpiar archivo de salida antes de empezar el lote
        with open(out_file, 'w', encoding='utf-8') as f:
            pass

        print(f"\n>>> PROCESANDO LOTE: {str_lote}")

        with open(lote_file, 'r', encoding='utf-8') as f_in:
            palabras = [line.strip() for line in f_in if line.strip()]

        with open(out_file, 'a', encoding='utf-8') as f_out:
            for palabra in palabras:
                print(f"=== Palabra: {palabra} ===")
                
                f_out.write(f"======[{palabra.upper()}]\n\n")
                
                for i in range(POEMAS_POR_PALABRA):
                    enfoque_actual = ENFOQUES[i % len(ENFOQUES)]
                    poema = ""
                    intentos = 0
                    
                    while True:
                        poema = generar_poema(palabra, enfoque_actual)
                        if not poema: break
                        
                        if palabra.lower() in poema.lower():
                            break
                            
                        if USAR_REINTENTOS and intentos < MAX_REINTENTOS:
                            intentos += 1
                            continue 
                        break 

                    if poema:
                        f_out.write(f"{poema}\n\n")
                        f_out.write("---\n\n")
                        f_out.flush()
                        print(f"  ✓ [{i+1}/{POEMAS_POR_PALABRA}] Generado")
                    
                    time.sleep(TIEMPO_ESPERA)

                f_out.write("\n")

        print(f"Lote {str_lote} finalizado. Salida en: {out_file}")

    print("\n[PROCESO COMPLETO]")

if __name__ == "__main__":
    main()