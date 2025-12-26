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
    "Atmósfera: Melancólica y suave (usa luz tenue, polvo, calma)",
    "Atmósfera: Violenta y cruda (usa frío, hierro, impacto)",
    "Atmósfera: Etérea y onírica (usa niebla, sueño, irrealidad)",
    "Atmósfera: Industrial y urbana (usa concreto, gris, óxido)",
    "Atmósfera: Orgánica y viva (usa raíces, savia, tierra húmeda)",
    "Estilo: Minimalista (frases muy cortas, casi haiku)",
    "Estilo: Gótico (usa sombras, noche, decadencia o desgracia)",
    "Perspectiva: Desde lo microscópico (detalles invisibles)",
    "Perspectiva: Cósmica (vacío, estrellas, lejanía)",
    "Tono: Nostálgico (recuerdos, pasado, huellas)"
]

def generar_poema(palabra, enfoque):
    prompt = f"""Eres una IA experta en poesía contemporánea y lenguaje figurado.

OBJETIVO: Escribir un poema de 4 versos que sea una METÁFORA PURA sobre: '{palabra}'.
INSTRUCCIÓN CLAVE: No describas el objeto literalmente ni des su definición. Transforma '{palabra}' en una imagen sensorial, un paisaje o una acción abstracta.

CONTEXTO DE ESTILO:
{enfoque}

EJEMPLO PERFECTO (Si la palabra fuera 'TIEMPO'):
El tiempo se deshace en los relojes de arena
Cae como polvo sobre párpados cerrados
Nadie detiene la marcha de lo invisible
Solo queda el eco de un segundo perdido

REGLAS ABSOLUTAS:
1. La palabra '{palabra}' DEBE aparecer escrita literalmente dentro del poema.
2. NO pongas comillas alrededor de la palabra '{palabra}'.
3. Longitud: Exactamente 4 líneas.
4. PROHIBIDO usar comparaciones débiles ('como', 'parece', 'cual', 'significa'). Usa metáfora directa.
5. PROHIBIDO descripciones obvias o de diccionario.

TU TURNO.
Palabra objetivo: {palabra}
Poema:"""

    payload = {
        "model": MODELO,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.85,
            "top_p": 0.9,
            "repeat_penalty": 1.15,
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
    out_file = f"resultados/metafora_lote_{str_lote}.txt"

    if not os.path.exists(lote_file):
        print(f"[ERROR] No existe el archivo: {lote_file}")
        sys.exit(1)

    if not os.path.exists("resultados"):
        os.makedirs("resultados")

    # Limpiar archivo de salida al inicio
    with open(out_file, 'w', encoding='utf-8') as f:
        pass

    modo_txt = "CON REINTENTOS" if USAR_REINTENTOS else "SIN REINTENTOS"
    print(f"Iniciando generación ({modo_txt})...")

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
                        # Fallo: no contiene la palabra
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