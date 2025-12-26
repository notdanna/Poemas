# words_clean_complete.py
from wordfreq import top_n_list, zipf_frequency
import spacy
import unicodedata
import regex as re
from collections import OrderedDict
import requests
from pathlib import Path

# parámetros
LANG = "es"
N_WORDS_WORDFREQ = 50_000
MIN_LEN = 3
MAX_LEN = 20
MIN_ZIPF = 1.8
ALLOWED_POS = {"NOUN", "VERB", "ADJ", "ADV", "PROPN"}
ONLY_LATIN = True

# palabras poéticas manualmente curadas
POETICAS_EXTRAS = {
    # Emociones y sentimientos
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
}

latin_re = re.compile(r"^[\p{Latin}\-´`ʼ']+$")
multiple_hyphen_re = re.compile(r'--+')

def normalize_word(w):
    w = w.strip()
    w = unicodedata.normalize("NFC", w)
    return w

def looks_spanish(word):
    if re.search(r'\d', word):
        return False
    if multiple_hyphen_re.search(word):
        return False
    if ONLY_LATIN and not latin_re.match(word):
        return False
    if word.startswith('-') or word.endswith('-'):
        return False
    return True

def cargar_corpus_poetico():
    """Carga corpus de poesía española desde Project Gutenberg"""
    corpus_words = set()
    
    # URLs de obras poéticas clásicas en español (dominio público)
    urls_gutenberg = [
        "https://www.gutenberg.org/cache/epub/2000/pg2000.txt",  # Don Quijote
        "https://www.gutenberg.org/files/15532/15532-0.txt",     # Rimas - Bécquer
        "https://www.gutenberg.org/files/50208/50208-0.txt",     # Soledades - Góngora
    ]
    
    print("Descargando corpus poético desde Project Gutenberg...")
    for url in urls_gutenberg:
        try:
            print(f"  Descargando: {url.split('/')[-1]}")
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                texto = response.text
                # Extraer palabras simples (solo alfabéticas)
                palabras = re.findall(r'\b[\p{Latin}]+\b', texto.lower())
                corpus_words.update(palabras)
                print(f"    → {len(palabras)} palabras extraídas")
        except Exception as e:
            print(f"    ✗ Error descargando {url}: {e}")
    
    print(f"Corpus poético: {len(corpus_words)} palabras únicas\n")
    return corpus_words

def cargar_palabras_frecuentes_literatura():
    """Lista manual de palabras comunes en literatura española"""
    return {
        "amor", "muerte", "vida", "dolor", "alegría", "tristeza", "esperanza",
        "sueño", "día", "noche", "tiempo", "mundo", "cielo", "tierra", "mar",
        "alma", "corazón", "ojo", "mano", "palabra", "silencio", "voz", "canto",
        "luz", "sombra", "sol", "luna", "estrella", "viento", "agua", "fuego",
        "flor", "rosa", "jardín", "árbol", "pájaro", "ave", "campo", "monte",
        "casa", "puerta", "ventana", "camino", "calle", "ciudad", "pueblo",
        "hombre", "mujer", "niño", "madre", "padre", "amigo", "amante",
        "ser", "estar", "ir", "venir", "hacer", "decir", "ver", "mirar",
        "sentir", "pensar", "saber", "querer", "amar", "morir", "vivir",
        "nuevo", "viejo", "grande", "pequeño", "hermoso", "bello", "triste",
        "dulce", "amargo", "blanco", "negro", "rojo", "azul", "verde"
    }

def main():
    # 1. Cargar desde wordfreq
    print("1. Cargando palabras desde wordfreq...")
    words_wf = set(top_n_list(LANG, N_WORDS_WORDFREQ))
    print(f"   → {len(words_wf)} palabras\n")
    
    # 2. Cargar corpus poético
    corpus_words = cargar_corpus_poetico()
    
    # 3. Cargar palabras literarias manuales
    print("2. Cargando vocabulario literario manual...")
    lit_words = cargar_palabras_frecuentes_literatura()
    print(f"   → {len(lit_words)} palabras\n")
    
    # 4. Combinar todas las fuentes
    print("3. Combinando fuentes...")
    all_words = words_wf | corpus_words | lit_words | POETICAS_EXTRAS
    print(f"   → {len(all_words)} palabras totales\n")
    
    # 5. Filtrar con spaCy
    print("4. Cargando spaCy para filtrado...")
    nlp = spacy.load("es_core_news_md", disable=["ner", "parser"])
    kept = OrderedDict()
    
    batch_size = 5000
    total = len(all_words)
    processed = 0
    
    print("5. Procesando y filtrando vocabulario...")
    for doc in nlp.pipe(all_words, batch_size=batch_size, n_process=1):
        token = doc[0]
        w = normalize_word(token.text)
        lw = w.lower()
        
        if len(lw) < MIN_LEN or len(lw) > MAX_LEN:
            continue
        if not looks_spanish(lw):
            continue
        
        freq = zipf_frequency(lw, LANG)
        
        # Permitir palabras poéticas/literarias aunque tengan frecuencia baja
        if lw in POETICAS_EXTRAS or lw in lit_words:
            pass  # siempre incluir
        elif freq < MIN_ZIPF:
            continue
        
        if token.pos_ not in ALLOWED_POS:
            continue
        
        if re.search(r'(.)\1\1\1', lw):
            continue
        
        if lw not in kept:
            kept[lw] = freq
        
        processed += 1
        if processed % 10000 == 0:
            print(f"   Procesadas: {processed}/{total}")
    
    print(f"\n6. Filtrado completo: {len(kept)} palabras válidas")
    
    # 6. Ordenar y guardar
    print("7. Ordenando por frecuencia...")
    sorted_items = sorted(kept.items(), key=lambda x: -x[1])
    
    output_file = "vocab_poetico.txt"
    print(f"8. Guardando en {output_file}...")
    with open(output_file, "w", encoding="utf-8") as f:
        for w, freq in sorted_items:
            f.write(f"{w}\n")
    
    print(f"\n✓ Completado: {len(sorted_items)} palabras guardadas")
    print(f"  Archivo: {output_file}")

if __name__ == "__main__":
    main()