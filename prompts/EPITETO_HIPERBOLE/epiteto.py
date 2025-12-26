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
    "ESTRUCTURA: Epíteto antepuesto (adjetivo + sustantivo)",
    "ESTRUCTURA: Epíteto pospuesto (sustantivo + adjetivo)",
    "ESTRUCTURA: Epíteto doble (dos adjetivos inherentes)",
    "ESTRUCTURA: Epíteto reiterado (mismo sustantivo en cada verso)"
    "TONO: Neutro descriptivo",
    "TONO: Solemne",
    "TONO: Melancólico contenido",
    "TONO: Sereno"
    "ESTILO: Clásico sobrio",
    "ESTILO: Minimalista",
    "ESTILO: Elevado",
    "ESTILO: Arcaizante moderado"
    "PERSPECTIVA: Natural (paisaje o fenómeno)",
    "PERSPECTIVA: Temporal (paso del tiempo)",
    "PERSPECTIVA: Espacial (cercanía / lejanía)",
    "PERSPECTIVA: Abstracta concreta (idea sin metáfora)"
    "REGISTRO: Lengua literaria estándar",
    "REGISTRO: Tradición poética española",
]

def generar_poema(palabra, enfoque):
    prompt = f"""Eres un poeta experto en retórica clasica española.

OBJETIVO:
Escribir un poema de 4 versos centrado exclusivamente en el USO DE EPÍTETOS
(adjetivo calificativo + sustantivo) de carácter DESCRIPTIVO sobre: '{palabra}'.


DEFINICIÓN OPERATIVA:
Un epíteto estructural es un adjetivo calificativo NO RESTRICTIVO
que acompaña a un sustantivo concreto y lo describe sin interpretarlo.

REGLAS DE ORO (ESTRICTO):
1. ESTRUCTURA DEL VERSO:
   Cada verso DEBE contener al menos UN sintagma:
   [ADJETIVO + SUSTANTIVO] claramente identificable.

2. SUSTANTIVOS:
   Usa solo sustantivos CONCRETOS y FÍSICOS
   (cuerpo, naturaleza, objetos materiales).

3. ADJETIVOS:
   Usa solo adjetivos DESCRIPTIVOS FÍSICOS
   (forma, textura, tamaño, temperatura, estado).
   Prohibidos adjetivos emocionales, psicológicos o abstractos.

4. POSICIÓN:
   El adjetivo debe ir preferentemente ANTEPUESTO al sustantivo.

5. VERBOS:
   - O bien NO uses verbo en el verso,
   - o usa SOLO verbos conjugados en forma personal
     de esta lista: yace, se alza, se extiende, reposa, permanece.
   PROHIBIDO el infinitivo.

6. PERSONIFICACIÓN:
   Prohibida cualquier acción humana o emocional.

7. PRIORIDAD RETÓRICA:
   El centro del verso debe ser el EPÍTETO, no la acción verbal.

8. REPETICIÓN:
   Se permite la repetición léxica como recurso estructural.

9. LÉXICO:
   Usa solo palabras existentes en el diccionario de la RAE.

INSTRUCCIONES ESPECÍFICAS:
Contexto/Tipo de epíteto: {enfoque}
Palabra obligatoria: '{palabra}' (puede aparecer como sustantivo principal).

FORMATO:
Cuatro versos, sin explicación, sin títulos, sin comentarios.

EJEMPLO DE ESTRUCTURA RIGUROSA:
La blanca nieve cae,
la fría noche avanza,
el lento tiempo pasa,
el viejo mundo calla.

AUTOVERIFICACIÓN (INTERNA, NO ESCRIBIRLA):
Antes de responder, comprueba que:
- todos los versos tienen epíteto,
- no hay infinitivos,
- no hay personificación.

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

    out_dir = "resultados_epiteto"
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    for lote_num in args.lote_nums:
        str_lote = f"{lote_num:03d}"
        lote_file = f"lotes/lote_{str_lote}.txt"
        out_file = f"{out_dir}/epiteto_lote_{str_lote}.txt"

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