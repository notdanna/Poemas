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
    "ESTRUCTURA: Cantidad imposible (números, multitudes, infinitud)",
    "ESTRUCTURA: Duración extrema (tiempo exagerado)",
    "ESTRUCTURA: Magnitud absoluta (peso, tamaño, extensión)",
    "ESTRUCTURA: Reiteración hiperbólica (misma exageración en cada verso)"
    "TONO: Trágico",
    "TONO: Enfático",
    "TONO: Desesperado",
    "TONO: Grandilocuente"
    "ESTILO: Directo y explícito",
    "ESTILO: Clásico solemne",
    "ESTILO: Excesivo controlado",
    "ESTILO: Retórico"
    "PERSPECTIVA: Subjetiva (voz en primera persona)",
    "PERSPECTIVA: Universal (alcance cósmico)",
    "PERSPECTIVA: Corporal (cuerpo llevado al extremo)",
    "PERSPECTIVA: Emocional absoluta"
    "REGISTRO: Lengua literaria estándar",
    "REGISTRO: Tradición poética española"

]

def generar_poema(palabra, enfoque):
    prompt = f"""Eres un poeta experto en retórica española.

OBJETIVO: Escribir un poema de 4 versos que use EXCLUSIVAMENTE la figura retórica
de la HIPÉRBOLE PURA sobre: '{palabra}'. sobre: '{palabra}'.

DEFINICIÓN OBLIGATORIA:
La HIPÉRBOLE es una exageración intencional, evidente y desproporcionada.
Debe expresar cantidades imposibles, duraciones infinitas o magnitudes absolutas,
sin recurrir a metáforas, símbolos ni personificación.

REGLAS DE ORO (ESTRICTO):
1. LÉXICO:
   Usa solo palabras existentes en el diccionario de la RAE.
   No inventes términos.

2. HIPÉRBOLE REAL:
   Cada verso DEBE contener una exageración explícita y extrema.
   El exceso debe ser el núcleo del verso.

3. ESTRUCTURA DEL EXCESO:
   Cada verso debe usar al menos UNO de estos recursos:
   - números imposibles o totales (mil, infinito, todo, ningún),
   - duraciones extremas (siglos, eternidades, jamás),
   - magnitudes absolutas (todo el mundo, el universo entero).

4. PROHIBICIONES ABSOLUTAS:
   - Prohibidas TODAS las metáforas.
   - Prohibidas las comparaciones (*como, más que, menos que*).
   - Prohibida la personificación (nada actúa salvo el yo).
   - Prohibido el simbolismo poético.
   - Prohibido mezclar figuras retóricas.

5. SUJETO:
   Usa exclusivamente:
   - primera persona (yo / he / me),
   o
   - una voz universal impersonal (todo, nadie, el mundo entero).

6. COHERENCIA:
   La exageración debe ser directa, clara y comprensible sin interpretación.

7. UNIDAD RETÓRICA:
   Todo el poema debe sostener UNA SOLA figura: HIPÉRBOLE.

INSTRUCCIONES ESPECÍFICAS:
Contexto/Tipo de hipérbole: {enfoque}
Palabra obligatoria: '{palabra}'.

FORMATO:
Cuatro versos, sin explicación, sin títulos, sin comentarios.

EJEMPLO CORRECTO:
He llorado mares enteros,
he esperado mil siglos,
mi voz llenó el mundo,
mi pena pesó más que la tierra.

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

    out_dir = "resultados_hiperbole"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    for lote_num in args.lote_nums:
        str_lote = f"{lote_num:03d}"
        lote_file = f"lotes/lote_{str_lote}.txt"
        out_file = f"{out_dir}/hiperbole_lote_{str_lote}.txt"

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