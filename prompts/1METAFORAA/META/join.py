import os
import glob

def juntar_archivos_normalizando():
    nombre_salida = "poemas_completos_utf8.txt"
    archivos = sorted(glob.glob("*.txt"))
    
    # Abrimos el archivo final forzando UTF-8
    with open(nombre_salida, 'w', encoding='utf-8') as archivo_final:
        print(f"Generando {nombre_salida}...")
        
        for nombre_archivo in archivos:
            if nombre_archivo == nombre_salida:
                continue
            
            contenido = ""
            encoding_usado = ""
            
            # INTENTO 1: Leer como UTF-8 (Estándar Linux/Mac)
            try:
                with open(nombre_archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                    encoding_usado = "UTF-8"
            except UnicodeDecodeError:
                # INTENTO 2: Si falla, leer como Windows-1252 (Estándar Windows antiguo/ANSI)
                # 'cp1252' es la codificación típica de Windows en occidente.
                try:
                    with open(nombre_archivo, 'r', encoding='cp1252') as f:
                        contenido = f.read()
                        encoding_usado = "Windows-1252"
                except:
                    print(f"ERROR: No se pudo leer {nombre_archivo} con ningún formato estándar.")
                    continue

            print(f"Procesando: {nombre_archivo} (Detectado: {encoding_usado})")
            
            # Escribir en el archivo final (que ya está abierto como UTF-8)
            archivo_final.write(contenido)
            
            # Asegurar salto de línea entre archivos si no lo tienen
            if contenido and not contenido.endswith('\n'):
                archivo_final.write('\n')

    print("------------------------------------------------")
    print(f"Terminado. Abre '{nombre_salida}' en tu Mac y los acentos deberían verse bien.")

if __name__ == "__main__":
    juntar_archivos_normalizando()
