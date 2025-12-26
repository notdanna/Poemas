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
TIEMPO_ESPERA = 10

# Configuración de reintentos
USAR_REINTENTOS = False   
MAX_REINTENTOS = 3       

ENFOQUES = [
    "Atmósfera: Melancólica y suave (sugiere sonidos suaves como S, L, M)",
    "Atmósfera: Violenta y de odio (sugiere sonidos fuertes como R, T, G, Z, P)",
    "Atmósfera: Etérea y onírica (sugiere sonidos fluidos como F, H, S)",
    "Atmósfera: Industrial y urbana (sugiere sonidos metálicos como G, T, R)",
    "Atmósfera: Orgánica y viva (sugiere sonidos vibrantes como B, V, M)",
    "Estilo: Minimalista (frases cortas, sonido muy marcado)",
    "Estilo: Gótico (sugiere sonidos oscuros y profundos como O, U, R)",
    "Perspectiva: Desde lo microscópico (sonidos pequeños y rápidos como I, T, C)",
    "Perspectiva: Cósmica (sonidos vastos y abiertos como A, O)",
    "Tono: Nostálgico (sonidos lentos y arrastrados)"
]

def generar_poema(palabra, enfoque):
    # --- PROMPT DISEÑADO PARA ALITERACIÓN ---
    prompt = f"""Eres un poeta experto en fonética y recursos sonoros.

OBJETIVO: Escribir un poema de 4 versos con fuerte ALITERACIÓN sobre: '{palabra}'.
DEFINICIÓN: La aliteración consiste en repetir el mismo sonido consonante al principio de las palabras o dentro de ellas para crear un efecto musical o rítmico.

INSTRUCCIONES DE ESTILO:
Contexto: {enfoque}
* Basado en el contexto anterior, elige UNA letra o sonido dominante (ej: la 'R' para fuerza, la 'S' para silencio) y satura el poema con ella.

EJEMPLO PERFECTO (Si la palabra fuera 'VIENTO' y el sonido 'S'):
El suave susurro silba su secreto
Sobre la sabana sola y sombría
Sopla sereno sin soltar su aliento
Siseando sueños de sabiduría

REGLAS ABSOLUTAS:
1. La palabra '{palabra}' DEBE aparecer escrita literalmente dentro del poema.
2. NO pongas comillas alrededor de la palabra '{palabra}'.
3. Longitud: Exactamente 4 líneas.
4. PRIORIDAD: Maximiza la repetición de sonidos consonantes similares en cada verso. Que el poema tenga una musicalidad evidente al leerse en voz alta.
5. No inventes palabras.

TU TURNO.
Palabra objetivo: {palabra}
Poema:"""

    payload = {
        "model": MODELO,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.75,    # Un poco menos creativo para que se centre en la regla fonética
            "top_p": 0.9,
            "repeat_penalty": 1.05, # Bajamos penalización para permitir repetir sonidos/palabras si es necesario por la aliteración
            "num_predict": 110,
            "stop": ["\n\n", "Nota:", "Análisis:", "Verso 5", "EJEMPLO"]
        }
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        return response.json().get('response', '').strip()
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión con Ollama: {e}")
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("lote_num", type=int, nargs="?", default=1)
    args = parser.parse_args()

    str_lote = f"{args.lote_num:03d}"
    lote_file = f"lotes/lote_{str_lote}.txt"
    # CAMBIO: Nombre del archivo de salida para aliteración
    out_file = f"resultados_aliteracion/aliteracion_lote_{str_lote}.txt"

    if not os.path.exists(lote_file):
        print(f"[ERROR] No existe el archivo: {lote_file}")
        sys.exit(1)

    if not os.path.exists("resultados_aliteracion"):
        os.makedirs("resultados_aliteracion")

    # Limpiar archivo de salida al inicio
    with open(out_file, 'w', encoding='utf-8') as f:
        pass

    modo_txt = "CON REINTENTOS" if USAR_REINTENTOS else "SIN REINTENTOS"
    print(f"Iniciando generación de ALITERACIONES ({modo_txt})...")

    with open(lote_file, 'r', encoding='utf-8') as f_in:
        palabras = [line.strip() for line in f_in if line.strip()]

    with open(out_file, 'a', encoding='utf-8') as f_out:
        for palabra in palabras:
            print(f"=== Procesando: '{palabra}' ===")
            
            for i in range(POEMAS_POR_PALABRA):
                idx_enfoque = i % len(ENFOQUES)
                enfoque_actual = ENFOQUES[idx_enfoque]

                poema = ""
                intentos = 0
                
                while True:
                    poema = generar_poema(palabra, enfoque_actual)
                    
                    if not poema:
                        print("  ✗ ERROR: Respuesta vacía.")
                        break

                    # Chequeo si contiene la palabra
                    if palabra.lower() in poema.lower():
                        break
                    else:
                        if USAR_REINTENTOS and intentos < MAX_REINTENTOS:
                            intentos += 1
                            print(f"    [R] Falta palabra clave. Reintentando ({intentos}/{MAX_REINTENTOS})...")
                            continue 
                        else:
                            print(f"    [!] Alerta: El modelo olvidó usar la palabra '{palabra}'.")
                            break 

                if poema:
                    f_out.write("---\n")
                    f_out.write(f"{poema}\n\n")
                    f_out.flush()
                    print(f"  ✓ Poema {i+1} generado ({enfoque_actual})")
                
                time.sleep(TIEMPO_ESPERA)

            f_out.write("\n===============================================\n\n")

    print(f"Proceso finalizado. Salida en: {out_file}")

if __name__ == "__main__":
    main()