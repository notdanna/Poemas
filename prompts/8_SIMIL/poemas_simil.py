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
MAX_REINTENTOS = 2

ENFOQUES = [
    "Tono: Nostálgico y otoñal",
    "Tono: Violento y repentino",
    "Estilo: Observación de la naturaleza",
    "Estilo: Metáforas industriales",
    "Perspectiva: El paso del tiempo",
    "Perspectiva: La fragilidad humana",
    "Contexto: El cosmos y las estrellas"
]

def generar_poema(palabra, enfoque):
    # Prompt enfocado exclusivamente en el nexo "como"
    prompt = f"""Eres un poeta experto en retórica.
OBJETIVO: Escribir un poema de 4 versos utilizando SÍMILES sobre: '{palabra}'.

REGLAS ABSOLUTAS:
1. PALABRA CLAVE: La palabra '{palabra}' DEBE aparecer escrita literalmente en el poema.
2. RECURSO: Cada verso debe contener una comparación usando la palabra 'como'.
3. ESTRUCTURA: Exactamente 4 versos.
4. ESTILO: {enfoque}.
5. No pongas títulos ni notas. Escribe solo el poema.

EJEMPLO:
"El {palabra} es como un mapa de venas,
late como un tambor en la sombra,
su calor es como el fuego de la tierra,
y su fuerza como el acero que no dobla."

TU TURNO. Palabra obligatoria: '{palabra}' y usar 'como'
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

def validar_simil_simple(poema, palabra_objetivo):
    """Verifica estructura, presencia de palabra y uso de 'como'."""
    if not poema:
        return False
        
    lineas = [l.strip().lower() for l in poema.split('\n') if l.strip()]
    
    if len(lineas) < 4:
        return False
    
    if palabra_objetivo.lower() not in poema.lower():
        return False

    for linea in lineas[:4]:
        if " como " not in f" {linea} ":
            return False

    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("lote_nums", type=int, nargs="+", help="Números de lote")
    args = parser.parse_args()

    out_dir = "resultados_simil"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    for lote_num in args.lote_nums:
        str_lote = f"{lote_num:03d}"
        lote_file = f"lotes/lote_{str_lote}.txt"
        out_file = f"{out_dir}/simil_lote_{str_lote}.txt"

        if not os.path.exists(lote_file):
            print(f"\n[ERROR] No existe el archivo: {lote_file}.")
            continue

        with open(out_file, 'w', encoding='utf-8') as f:
            pass

        print(f"\n>>> INICIANDO PROCESO - LOTE: {str_lote}")

        with open(lote_file, 'r', encoding='utf-8') as f_in:
            palabras_lote = [line.strip() for line in f_in if line.strip()]

        with open(out_file, 'a', encoding='utf-8') as f_out:
            for palabra in palabras_lote:
                print(f"=== Procesando: '{palabra}' ===")
                f_out.write(f"======[{palabra.upper()}]\n\n")
                
                for i in range(POEMAS_POR_PALABRA):
                    enfoque_actual = ENFOQUES[i % len(ENFOQUES)]
                    poema_final = ""
                    intentos = 0
                    
                    while True:
                        poema_generado = generar_poema(palabra, enfoque_actual)
                        
                        if validar_simil_simple(poema_generado, palabra):
                            poema_final = poema_generado
                            break
                        else:
                            intentos += 1
                            if intentos <= MAX_REINTENTOS:
                                print(f"    [R] Reintento {intentos} para '{palabra}'...")
                                continue
                            else:
                                poema_final = poema_generado if poema_generado else "[FALLO]"
                                break

                    f_out.write(f"{poema_final}\n\n")
                    f_out.write("---\n\n")
                    f_out.flush()
                    print(f"  ✓ [{i+1}/7] Generado")
                    
                    time.sleep(TIEMPO_ESPERA)

                f_out.write("\n")

    print(f"\n[PROCESO COMPLETO]")

if __name__ == "__main__":
    main()