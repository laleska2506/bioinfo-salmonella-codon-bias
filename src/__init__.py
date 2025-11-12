# Importaciones desde el módulo de procesamiento
from .procesamiento import (
    cargar_secuencias, 
    calcular_metricas_basicas, 
    validar_secuencias
)

# Importaciones desde el módulo de análisis
from .analisis import (
    calcular_uso_codones, 
    analizar_bias_codones, 
    comparar_uso_codones_especies, 
    generar_tabla_codones_aminoacidos
)

# Importaciones desde el módulo de visualización
from .visualizacion import (
    grafico_gc,
    distribucion_longitudes,
    distribucion_gc,
    relacion_longitud_gc,
    uso_codones_top20,
    correlacion_codones,
    heatmap_codones,
    distribucion_acumulativa_longitudes,
    generar_todos_los_graficos
)

# Metadatos del paquete
__version__ = "1.0.0"
__author__ = "Analista de Secuencias"

# Lista de funciones disponibles para importación con wildcard
__all__ = [
    # Funciones de procesamiento
    'cargar_secuencias',
    'calcular_metricas_basicas',
    'validar_secuencias',
    
    # Funciones de análisis
    'calcular_uso_codones',
    'analizar_bias_codones',
    'comparar_uso_codones_especies',
    'generar_tabla_codones_aminoacidos',
    
    # Funciones de visualización
    'grafico_gc',
    'distribucion_longitudes',
    'distribucion_gc',
    'relacion_longitud_gc',
    'uso_codones_top20',
    'correlacion_codones',
    'heatmap_codones',
    'distribucion_acumulativa_longitudes',
    'generar_todos_los_graficos'
]

# Mensaje informativo al importar el paquete
print("Paquete src version {} cargado correctamente".format(__version__))
print("Modulos disponibles: procesamiento, analisis, visualizacion")