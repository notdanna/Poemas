#!/usr/bin/env bash

LOTE_NUM=${1:-1}  # Número de lote como argumento (default: 1)
LOTE_FILE="lotes/lote_$(printf "%03d" $LOTE_NUM).txt"
OUT="resultados/anafora_lote_$(printf "%03d" $LOTE_NUM).txt"
POEMAS_POR_PALABRA=10

if [ ! -f "$LOTE_FILE" ]; then
    echo "[ERROR] No existe el archivo: $LOTE_FILE"
    exit 1
fi

mkdir -p resultados

> "$OUT"

echo "GENERACIÓN DE POEMAS CON ANÁFORA - LOTE $(printf "%03d" $LOTE_NUM)"
echo "Archivo de entrada: $LOTE_FILE"
echo "Archivo de salida: $OUT"
echo "Poemas por palabra: $POEMAS_POR_PALABRA"
echo

# Contar total de palabras en el lote
TOTAL_PALABRAS=$(wc -l < "$LOTE_FILE")
TOTAL_POEMAS=$((TOTAL_PALABRAS * POEMAS_POR_PALABRA))

echo "Total de palabras en lote: $TOTAL_PALABRAS"
echo "Total de poemas a generar: $TOTAL_POEMAS"
echo
echo "Iniciando generación..."
echo

palabra_num=0

# Leer cada palabra del lote
while IFS= read -r PALABRA; do
    palabra_num=$((palabra_num + 1))
    
    echo "PALABRA [$palabra_num/$TOTAL_PALABRAS]: $PALABRA"

    # Generar N poemas para esta palabra
    for i in $(seq 1 $POEMAS_POR_PALABRA); do
        echo "  → Poema $i/$POEMAS_POR_PALABRA para '$PALABRA'..."
        
        # Construir prompt con la palabra específica
        PROMPT="INSTRUCCIÓN: Escribe exactamente 4 versos sobre '$PALABRA'. 

REGLAS:
1. TODOS los 4 versos deben comenzar con LA MISMA palabra o frase, esta regla es FUNDAMENTAL
2. Esa palabra inicial puede ser cualquiera (NO tiene que ser '$PALABRA')
3. La palabra '$PALABRA' DEBE aparecer al menos 1 vez en el poema
4. NO uses puntos suspensivos (...)
5. Cada verso debe tener entre 8-12 palabras (versos largos y descriptivos)

FORMATO:
[Palabra X] resto largo y descriptivo del verso 1
[Palabra X] resto largo y descriptivo del verso 2  
[Palabra X] resto largo y descriptivo del verso 3
[Palabra X] resto largo y descriptivo del verso 4

EJEMPLOS:

El tiempo guarda huellas del pasado entre sombras olvidadas
El tiempo borra nombres de aquellos que se fueron sin volver
El tiempo cura heridas profundas que dejaron cicatrices eternas
El tiempo nunca vuelve sobre pasos dados en noches de tormenta

La noche trae ecos perdidos de voces que ya no hablan
La noche cubre lágrimas secas con un manto de silencio frío
La noche guarda secretos rotos en rincones donde nadie mira
La noche nunca miente ni perdona los errores del ayer

Escribe 4 versos largos sobre '$PALABRA':"

        JSON_PROMPT=$(printf "%s" "$PROMPT" | jq -Rs .)
        
        read -r -d '' JSON <<EOF
{
  "model": "qwen2.5:7b",
  "prompt": $JSON_PROMPT,
  "stream": false,
  "options": {
    "temperature": 0.5,
    "top_p": 0.8,
    "num_predict": 160,
    "repeat_penalty": 1.1,
    "stop": ["\n\n", "EJEMPLO", "AHORA", "Segundo", "Tercer", "Cuarto", "Primer verso:"]
  }
}
EOF

        # Llamar a Ollama
        RESPONSE=$(curl -s http://127.0.0.1:11434/api/generate \
            -H "Content-Type: application/json" \
            -d "$JSON")
        
        POEMA=$(echo "$RESPONSE" | jq -r '.response // empty')
        
        if [ -z "$POEMA" ]; then
            echo "  ✗ ERROR: Respuesta vacía del modelo"
            {
                echo "<!-- ERROR: Sin respuesta del modelo -->"
                echo
            } >> "$OUT"
        else
            # Guardar poema
            {
                echo "---"
                echo "$POEMA"
                echo
            } >> "$OUT"
            
            echo "  ✓ Poema guardado"
        fi
        
        # Esperar entre poemas (excepto el último)
        if [ $i -lt $POEMAS_POR_PALABRA ]; then
            sleep 3
        fi
    done
    
    # Separador entre palabras
    {
        echo
        echo "==============================================="
        echo
    } >> "$OUT"
    
    # Espera más larga entre palabras
    if [ $palabra_num -lt $TOTAL_PALABRAS ]; then
        echo "  Esperando 10 segundos antes de siguiente palabra..."
        sleep 10
    fi
    
    echo
    
done < "$LOTE_FILE"

echo "================================================================"
echo "✓ PROCESO COMPLETADO"
echo "================================================================"
echo "Lote procesado: $(printf "%03d" $LOTE_NUM)"
echo "Palabras procesadas: $TOTAL_PALABRAS"
echo "Poemas generados: $TOTAL_POEMAS (esperados)"
echo "Resultado guardado en: $OUT"
echo "================================================================"