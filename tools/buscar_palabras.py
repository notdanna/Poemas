import fasttext
import numpy as np
import os

# Carpeta de salida
OUT_DIR = "palabras"

# Crear la carpeta si no existe
os.makedirs(OUT_DIR, exist_ok=True)


TEMAS_BASE = [
    # Emociones positivas
    "alma", "corazón", "sueño", "anhelo", "pasión", "olvido", "recuerdo",
    "ausencia", "silencio", "vacío", "abismo", "llanto", "lágrima", "suspiro",
    "éxtasis", "agonía", "congoja", "melancolía", "nostalgia", "añoranza",
    
    # Naturaleza
    "luna", "estrella", "noche", "alba", "ocaso", "aurora", "crepúsculo",
    "amanecer", "atardecer", "brisa", "tormenta", "relámpago", "trueno",
    "mar", "cielo", "tierra", "fuego", "viento", "río", "bosque", "montaña",
    "lluvia", "niebla", "rocío", "escarcha", "nevada",
    
    # Luz y sombra
    "luz", "sombra", "penumbra", "claridad", "oscuridad", "resplandor",
    "destello", "fulgor", "brillo", "centelleo",
    
    # Poesía y arte
    "verso", "rima", "estrofa", "canto", "melodía", "armonía", "musa",
    "lira", "poeta", "cantor", "trovador",
    
    # Tiempo
    "tiempo", "eterno", "efímero", "instante", "momento", "eternidad",
    "infinito", "fugaz", "perecedero",
    
    # Abstractos
    "belleza", "fealdad", "verdad", "mentira", "sueño", "realidad",
    "esperanza", "desesperanza", "libertad", "destino", "azar"
]

# ------------------------------
# Cargar vocabulario
# ------------------------------
def cargar_vocab(path):
    # Verificación simple para evitar errores si no existe
    if not os.path.exists(path):
        print(f"Error: No se encuentra el archivo {path}")
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

# Asegúrate de que este archivo exista en el mismo directorio que el script
vocab = cargar_vocab("vocab_poetico.txt")

if not vocab:
    print("El vocabulario está vacío o no se pudo cargar. Saliendo.")
    exit()

# ------------------------------
# Embeddings
# ------------------------------
print("Cargando modelo FastText (esto puede tardar un poco)...")
# Asegúrate de tener el archivo .bin en el directorio
try:
    model = fasttext.load_model("cc.es.300.bin")
except Exception as e:
    print(f"Error al cargar el modelo FastText: {e}")
    exit()

def emb(palabra):
    return model.get_word_vector(palabra)

# ------------------------------
# Cosine similarity
# ------------------------------
def cos(a, b):
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0
    return np.dot(a, b) / (norm_a * norm_b)

# ------------------------------
# Filtrar palabras relacionadas
# ------------------------------
def palabras_relacionadas(vocabulario, vec_tema, umbral=0.45):
    resultado = []
    # Pre-calculamos la norma del tema para no hacerlo en cada iteración
    norm_tema = np.linalg.norm(vec_tema)
    
    for w in vocabulario:
        v = emb(w)
        norm_v = np.linalg.norm(v)
        
        if norm_v == 0 or norm_tema == 0:
            s = 0
        else:
            s = np.dot(v, vec_tema) / (norm_v * norm_tema)
            
        if s >= umbral:
            resultado.append((w, s))
            
    resultado.sort(key=lambda x: -x[1])
    return resultado

# ------------------------------
# Procesar cada tema individual
# ------------------------------
print(f"Iniciando procesamiento. Los archivos se guardarán en: {os.path.abspath(OUT_DIR)}")

for tema_palabra in TEMAS_BASE:
    print(f"Procesando tema: {tema_palabra}")
    
    vec_tema = emb(tema_palabra)
    candidatas = palabras_relacionadas(vocab, vec_tema, umbral=0.45)
    
    # Construir ruta dentro de la carpeta 'palabras'
    safe_filename = f"palabras_{tema_palabra.replace(' ', '_')}.txt"
    filepath = os.path.join(OUT_DIR, safe_filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        for w, s in candidatas:
            # Solo guardamos la palabra para que sea fácil de leer por el script de Bash/PS1
            # Si necesitas el score, cambia la línea de abajo por: f.write(f"{w}\t{s:.4f}\n")
            f.write(f"{w}\n") 
    
    print(f"  → {len(candidatas)} palabras guardadas en {filepath}")

print()
print("==================================================")
print("Proceso completado.")
print(f"Archivos generados en la carpeta: /{OUT_DIR}")