"""
Frontend Web para SalmoAvianLight - Salmonella vs Gallus
Aplicación Streamlit para analistas de laboratorio
"""
import streamlit as st
import pandas as pd
import os
import time
import shutil
from pathlib import Path
from typing import Optional, Dict, Tuple, List
import sys
import io

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from services.analysis_client import AnalysisClient
from utils.zipper import crear_zip_resultados

st.set_page_config(
    page_title="SalmoAvianLight",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    .subheader {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #333;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #1f77b4;
    }
    .graph-container {
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        background-color: #ffffff;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .graph-image-container {
        border: 1px solid #ddd;
        border-radius: 6px;
        padding: 8px;
        background-color: #f8f9fa;
        text-align: center;
    }
    .graph-description {
        background-color: #f8f9fa;
        padding: 1.2rem;
        border-radius: 6px;
        border-left: 4px solid #1f77b4;
        font-size: 0.92rem;
        line-height: 1.5;
        height: 100%;
    }
    .likert-scale {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .file-info {
        background-color: #e8f4fd;
        padding: 0.75rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 3px solid #1f77b4;
    }
    .success-message {
        background-color: #d4edda;
        padding: 0.75rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 3px solid #28a745;
    }
    .error-message {
        background-color: #f8d7da;
        padding: 0.75rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 3px solid #dc3545;
    }
    .warning-message {
        background-color: #fff3cd;
        padding: 0.75rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 3px solid #ffc107;
    }
    .status-running {
        background-color: #cce5ff;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #007bff;
    }
    .status-completed {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #28a745;
    }
    .status-failed {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #dc3545;
    }
    .graph-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

if 'analysis_client' not in st.session_state:
    st.session_state.analysis_client = AnalysisClient()
if 'job_id' not in st.session_state:
    st.session_state.job_id = None
if 'analysis_status' not in st.session_state:
    st.session_state.analysis_status = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'last_params' not in st.session_state:
    st.session_state.last_params = None
if 'error_message' not in st.session_state:
    st.session_state.error_message = None
if 'execution_history' not in st.session_state:
    st.session_state.execution_history = []
if 'last_used_params' not in st.session_state:
    st.session_state.last_used_params = None
if 'selected_graphs' not in st.session_state:
    st.session_state.selected_graphs = []

GRAPH_CONFIG = {
    'hist_longitud_secuencias': {
        'name': 'Histograma de Longitud de Secuencias',
        'filename_patterns': ['histograma_longitud', 'length_histogram', 'hist_longitud'],
        'order': 1
    },
    'distribucion_gc': {
        'name': 'Distribución de Contenido GC',
        'filename_patterns': ['distribucion_gc', 'gc_distribution', 'gc_content'],
        'order': 2
    },
    'frecuencia_codones': {
        'name': 'Frecuencia de Uso de Codones',
        'filename_patterns': ['frecuencia_codones', 'codon_frequency', 'codon_usage_freq'],
        'order': 3
    },
    'comparativa_uso_codones': {
        'name': 'Comparativa de Uso de Codones entre Especies',
        'filename_patterns': ['comparativa_codones', 'codon_comparison', 'compare_codons'],
        'order': 4
    },
    'correlacion_uso_codones': {
        'name': 'Correlación de Uso de Codones',
        'filename_patterns': ['correlacion_codones', 'codon_correlation', 'correlation_plot'],
        'order': 5
    },
    'pca_secuencias': {
        'name': 'Análisis PCA de Secuencias',
        'filename_patterns': ['pca_secuencias', 'pca_analysis', 'principal_components'],
        'order': 6
    },
    'heatmap_correlacion': {
        'name': 'Heatmap de Correlación',
        'filename_patterns': ['heatmap_correlacion', 'correlation_heatmap', 'heatmap'],
        'order': 7
    },
    'boxplot_longitud_por_especie': {
        'name': 'Boxplot de Longitud por Especie',
        'filename_patterns': ['boxplot_longitud', 'length_boxplot', 'boxplot_species'],
        'order': 8
    },
    'scatter_gc_vs_longitud': {
        'name': 'Scatter Plot: GC vs Longitud',
        'filename_patterns': ['scatter_gc_longitud', 'gc_vs_length', 'scatter_plot'],
        'order': 9
    }
}

GRAPH_DESCRIPTIONS = {
    'hist_longitud_secuencias': """
    Este histograma muestra la distribución de longitudes de secuencias en el conjunto de datos analizado. 
    Permite identificar patrones específicos como la presencia de secuencias cortas o largas predominantes, 
    la variabilidad general en tamaño y posibles agrupaciones naturales. La forma de la distribución puede 
    ser normal, sesgada o bimodal, proporcionando información valiosa sobre la homogeneidad del conjunto de 
    datos. Una distribución simétrica sugiere uniformidad en las longitudes, mientras que múltiples picos 
    pueden revelar la presencia de diferentes tipos de secuencias o elementos genómicos con características 
    estructurales distintas. Este análisis inicial es fundamental para entender la composición general del 
    genoma y detectar anomalías o características específicas de interés biológico.
    """,
    
    'distribucion_gc': """
    El gráfico de distribución de contenido GC muestra el porcentaje relativo de bases Guanina y Citosina 
    presentes en las secuencias analizadas. Una distribución normal y centrada sugiere homogeneidad genética 
    entre las muestras, mientras que distribuciones multimodales o asimétricas pueden indicar la presencia de 
    múltiples especies, cepas distintas o diferentes regiones genómicas con composiciones variables. El contenido 
    GC es un marcador taxonómico importante utilizado en clasificación y filogenia. Su análisis ayuda a 
    caracterizar la composición genómica global, identificar adaptaciones ambientales específicas, y detectar 
    posibles contaminaciones o heterogeneidades en las muestras. Valores extremos pueden indicar regiones 
    codificantes versus no codificantes, o reflejar presiones selectivas particulares en diferentes contextos 
    evolutivos y ecológicos.
    """,
    
    'frecuencia_codones': """
    Este gráfico de barras representa la frecuencia relativa de uso de cada codón en las secuencias del 
    conjunto de datos. Muestra claramente las preferencias en el uso de codones, fenómeno conocido como 
    sesgo de uso de codones, lo que puede reflejar adaptaciones genómicas o presiones evolutivas específicas. 
    Los codones más frecuentemente utilizados generalmente están asociados con una expresión génica más 
    eficiente y abundante disponibilidad de ARN de transferencia correspondiente. Las diferencias significativas 
    en los patrones de uso entre especies pueden indicar distintos mecanismos de regulación de la expresión 
    génica, niveles variables de optimización traslacional, o adaptaciones específicas a diferentes nichos 
    ecológicos. Este análisis es fundamental para estudios de expresión génica, ingeniería genética y 
    biología sintética.
    """,
    
    'comparativa_uso_codones': """
    Este gráfico comparativo horizontal muestra las diferencias absolutas en el uso de codones entre las dos 
    especies analizadas. Permite identificar fácilmente codones preferencialmente utilizados por cada organismo, 
    lo que puede reflejar adaptaciones evolutivas específicas y divergencias en las estrategias de expresión 
    génica. Las barras que se extienden hacia la derecha indican mayor uso en Salmonella, mientras que las que 
    se extienden hacia la izquierda indican preferencia en Gallus. Las divergencias significativas pueden 
    indicar diferentes presiones selectivas actuando sobre cada linaje, mecanismos distintos de regulación de 
    la expresión génica, o variaciones en la disponibilidad de ARN de transferencia. Este tipo de análisis 
    comparativo es esencial para entender la evolución molecular, diseñar sistemas de expresión heteróloga 
    eficientes y estudiar relaciones filogenéticas entre organismos.
    """,
    
    'correlacion_uso_codones': """
    Este gráfico de dispersión explora sistemáticamente la relación cuantitativa entre el uso de codones en 
    las dos especies comparadas. Cada punto representa un codón específico, posicionado según su frecuencia 
    en ambas especies. Una correlación positiva fuerte, evidenciada por puntos agrupados cerca de una línea 
    diagonal, indica patrones de uso similares entre especies, sugiriendo conservación evolutiva profunda en 
    los mecanismos de traducción. Los puntos que se desvían significativamente de la línea de tendencia 
    representan codones con uso diferencial marcado, potencialmente asociados a adaptaciones específicas de 
    cada especie, diferencias en composición genómica, o distintos mecanismos regulatorios post-transcripcionales. 
    La pendiente de la línea de regresión y el coeficiente de correlación proporcionan métricas cuantitativas 
    de la similitud global en estrategias de uso de codones.
    """,
    
    'pca_secuencias': """
    El análisis de Componentes Principales (PCA) reduce la alta dimensionalidad de los datos de uso de codones 
    para visualizar patrones complejos en un espacio bidimensional interpretable. Esta técnica multivariada 
    extrae las direcciones de máxima varianza en el conjunto de datos, permitiendo identificar las principales 
    fuentes de variación. Los agrupamientos claramente definidos indican similitudes fundamentales entre 
    secuencias o especies, mientras que la separación espacial sugiere diferencias significativas en los perfiles 
    de uso de codones. La proximidad de puntos representa similitudes en los patrones multidimensionales de 
    uso de codones, permitiendo identificar agrupaciones naturales, detectar valores atípicos que pueden 
    representar contaminación o errores, y visualizar relaciones filogenéticas. Los porcentajes de varianza 
    explicada por cada componente principal indican la importancia relativa de cada eje en la estructura de 
    los datos.
    """,
    
    'heatmap_correlacion': """
    Este heatmap de correlación visualiza las relaciones entre diferentes variables mediante una escala de 
    colores intuitiva y gradiente. Los tonos cálidos (rojos y naranjas) indican correlaciones positivas fuertes 
    entre variables, mientras que los tonos fríos (azules y verdes) representan correlaciones negativas o 
    ausencia de relación. Los patrones de bloques contiguos del mismo color sugieren agrupaciones de variables 
    que covarían juntas, indicando posibles relaciones funcionales o regulatorias compartidas. Esta visualización 
    matricial ayuda a identificar rápidamente relaciones complejas y patrones de co-variación en el conjunto de 
    datos de manera intuitiva y visualmente atractiva. Es especialmente útil para detectar redundancias entre 
    variables, identificar grupos de codones con comportamiento similar, y generar hipótesis sobre mecanismos 
    biológicos subyacentes que controlan la expresión génica coordinada.
    """,
    
    'boxplot_longitud_por_especie': """
    Los boxplots o diagramas de caja y bigotes comparan estadísticamente la distribución completa de longitudes 
    de secuencias entre las dos especies analizadas. Cada caja muestra la mediana (línea central), los cuartiles 
    inferior y superior (límites de la caja), y los valores extremos (bigotes), permitiendo identificar de manera 
    visual diferencias significativas en la variabilidad, tendencia central y presencia de valores atípicos. 
    La superposición parcial o total de las cajas indica similitudes estadísticas en las longitudes de secuencias, 
    mientras que la separación clara sugiere diferencias significativas y consistentes entre los organismos 
    comparados. Los puntos individuales fuera de los bigotes representan valores atípicos que merecen atención 
    especial. Este tipo de visualización robusta es fundamental para comparaciones estadísticas formales y para 
    entender la variabilidad natural dentro de cada especie versus las diferencias entre especies.
    """,
    
    'scatter_gc_vs_longitud': """
    Este gráfico de dispersión bidimensional explora sistemáticamente la posible relación entre el contenido GC 
    y la longitud de las secuencias analizadas. Cada punto representa una secuencia individual, posicionada según 
    sus valores en ambas dimensiones. Los patrones de distribución observables pueden revelar si existe correlación 
    positiva, negativa o ausencia de relación entre estas dos variables fundamentales. Agrupamientos específicos 
    en regiones del gráfico pueden indicar diferentes clases funcionales de secuencias (genes housekeeping versus 
    específicos, regiones codificantes versus regulatorias) o distintos elementos genómicos con propiedades 
    características. La ausencia de un patrón claro sugiere independencia estadística entre el contenido GC y la 
    longitud de las secuencias, indicando que estos dos parámetros son determinados por factores evolutivos o 
    funcionales distintos e independientes en los genomas analizados.
    """
}


def validar_archivo_fasta(archivo) -> Tuple[bool, Optional[str]]:
    """Valida que el archivo subido sea un FASTA válido."""
    if archivo is None:
        return False, "Por favor, sube un archivo FASTA"
    
    nombre_archivo = archivo.name.lower()
    if not (nombre_archivo.endswith('.fa') or nombre_archivo.endswith('.fasta')):
        return False, "El archivo debe tener extensión .fa o .fasta"
    
    if archivo.size == 0:
        return False, "El archivo está vacío"
    
    tamaño_mb = archivo.size / (1024 * 1024)
    limite_mb = 200
    
    if tamaño_mb > limite_mb:
        return False, f"El archivo es demasiado grande ({tamaño_mb:.2f} MB). El límite máximo es {limite_mb} MB."
    
    try:
        primeros_bytes = archivo.read(100)
        archivo.seek(0)
        if not primeros_bytes.startswith(b'>'):
            return False, "El archivo no parece ser un FASTA válido (debe empezar con '>')"
    except Exception as e:
        return False, f"Error al leer el archivo: {str(e)}"
    
    return True, None


def mostrar_seleccion_graficos():
    """Muestra la interfaz de selección de gráficos."""
    st.markdown('<div class="section-header">Selección de Gráficos</div>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    <div class="likert-scale">
    <p><strong>Selecciona los gráficos que deseas generar:</strong></p>
    <p>Marca las casillas correspondientes a los gráficos que necesitas para tu análisis.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    selected_graphs = []
    
    with col1:
        st.subheader("Gráficos Básicos")
        for graph_key in ['hist_longitud_secuencias', 'distribucion_gc', 'frecuencia_codones']:
            if st.checkbox(GRAPH_CONFIG[graph_key]['name'], key=graph_key):
                selected_graphs.append(graph_key)
    
    with col2:
        st.subheader("Gráficos Comparativos")
        for graph_key in ['comparativa_uso_codones', 'correlacion_uso_codones', 'boxplot_longitud_por_especie']:
            if st.checkbox(GRAPH_CONFIG[graph_key]['name'], key=graph_key):
                selected_graphs.append(graph_key)
    
    with col3:
        st.subheader("Gráficos Avanzados")
        for graph_key in ['pca_secuencias', 'heatmap_correlacion', 'scatter_gc_vs_longitud']:
            if st.checkbox(GRAPH_CONFIG[graph_key]['name'], key=graph_key):
                selected_graphs.append(graph_key)
    
    if selected_graphs:
        st.markdown(f'<div class="success-message">{len(selected_graphs)} gráfico(s) seleccionado(s)</div>', 
                   unsafe_allow_html=True)
        with st.expander("Ver gráficos seleccionados"):
            for graph_key in selected_graphs:
                st.write(f"- {GRAPH_CONFIG[graph_key]['name']}")
    else:
        st.markdown('<div class="warning-message">No se han seleccionado gráficos. No se generarán visualizaciones.</div>', 
                   unsafe_allow_html=True)
    
    return selected_graphs


def encontrar_imagen_grafico(images: List[str], graph_key: str) -> Optional[str]:
    """Encuentra la imagen correspondiente a un tipo de gráfico."""
    if not images:
        return None
    
    patterns = GRAPH_CONFIG[graph_key]['filename_patterns']
    
    for img_path in images:
        img_name = Path(img_path).stem.lower()
        
        for pattern in patterns:
            if pattern in img_name:
                return img_path
        
        if graph_key in img_name:
            return img_path
    
    return None


def ejecutar_analisis(salmonella_file, gallus_file, params: Dict, selected_graphs: List[str]):
    """Ejecuta el análisis genético."""
    try:
        if salmonella_file is None:
            raise ValueError("El archivo de Salmonella no está disponible")
        if gallus_file is None:
            raise ValueError("El archivo de Gallus no está disponible")
        
        tamaño_sal = salmonella_file.size / (1024 * 1024)
        tamaño_gall = gallus_file.size / (1024 * 1024)
        
        st.write("**Información del análisis:**")
        st.write(f"- Archivo Salmonella: {salmonella_file.name} ({tamaño_sal:.2f} MB)")
        st.write(f"- Archivo Gallus: {gallus_file.name} ({tamaño_gall:.2f} MB)")
        st.write(f"- Gráficos seleccionados: {len(selected_graphs)}")
        st.write(f"- Parámetros: min_len={params.get('min_len', 0)}, limpiar_ns={params.get('limpiar_ns', True)}, top_codons={params.get('top_codons', 20)}")
        
        with st.spinner("Leyendo archivos FASTA..."):
            salmonella_content = salmonella_file.getvalue()
            gallus_content = gallus_file.getvalue()
        
        params['selected_graphs'] = selected_graphs
        
        with st.spinner("Ejecutando análisis genético..."):
            resultado = st.session_state.analysis_client.start_analysis(
                salmonella_content,
                gallus_content,
                params
            )
            st.session_state.analysis_status = resultado.get('status', 'COMPLETED')
            st.session_state.analysis_results = resultado
        
        st.session_state.last_params = {
            'salmonella_file': salmonella_file,
            'gallus_file': gallus_file,
            'params': params
        }
        
        st.session_state.last_used_params = params.copy()
        st.session_state.selected_graphs = selected_graphs
        
        st.session_state.execution_history.append({
            'job_id': st.session_state.job_id or 'LOCAL',
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'status': st.session_state.analysis_status,
            'graphs': len(selected_graphs)
        })
        
        return True
        
    except Exception as e:
        error_msg = str(e)
        st.session_state.error_message = error_msg
        st.session_state.analysis_status = 'FAILED'
        st.markdown(f'<div class="error-message">Error al ejecutar análisis: {error_msg}</div>', 
                   unsafe_allow_html=True)
        return False


def mostrar_grafico_con_descripcion(imagen_path: str, graph_key: str, graph_name: str):
    """Muestra un gráfico con su descripción en el layout solicitado."""
    st.markdown('<div class="graph-container">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="graph-image-container">', unsafe_allow_html=True)
        try:
            if Path(imagen_path).exists():
                st.image(imagen_path, use_container_width=True)
            else:
                st.markdown(f'<div class="error-message">Archivo no encontrado: {imagen_path}</div>', 
                           unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div class="error-message">Error al cargar imagen: {str(e)}</div>', 
                       unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'<div class="graph-title">{graph_name}</div>', unsafe_allow_html=True)
        if graph_key in GRAPH_DESCRIPTIONS:
            st.markdown(
                f'<div class="graph-description">{GRAPH_DESCRIPTIONS[graph_key]}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown('<div class="warning-message">Descripción no disponible</div>', 
                       unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


def mostrar_resultados(resultados: Dict):
    """Muestra los resultados del análisis."""
    st.markdown('<div class="section-header">Resultados del Análisis</div>', 
                unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Resumen de Métricas")
        try:
            df_metricas = None
            resumen_csv_path = resultados.get('resumen_csv_path')
            if resumen_csv_path and Path(resumen_csv_path).exists():
                df_metricas = pd.read_csv(resumen_csv_path)
            else:
                st.markdown('<div class="warning-message">No se encontró el archivo de métricas</div>', 
                           unsafe_allow_html=True)
            
            if df_metricas is not None and not df_metricas.empty:
                st.dataframe(df_metricas, use_container_width=True)
                csv_metricas = df_metricas.to_csv(index=False)
                st.download_button(
                    label="Descargar resumen_metricas.csv",
                    data=csv_metricas,
                    file_name="resumen_metricas.csv",
                    mime="text/csv"
                )
        except Exception as e:
            st.markdown(f'<div class="error-message">Error al cargar métricas: {e}</div>', 
                       unsafe_allow_html=True)
    
    with col2:
        st.subheader("Uso de Codones")
        try:
            df_codones = None
            codon_csv_path = resultados.get('codon_csv_path')
            if codon_csv_path and Path(codon_csv_path).exists():
                df_codones = pd.read_csv(codon_csv_path)
            else:
                st.markdown('<div class="warning-message">No se encontró el archivo de codones</div>', 
                           unsafe_allow_html=True)
            
            if df_codones is not None and not df_codones.empty:
                st.dataframe(df_codones, use_container_width=True)
                csv_codones = df_codones.to_csv(index=False)
                st.download_button(
                    label="Descargar codon_usage.csv",
                    data=csv_codones,
                    file_name="codon_usage.csv",
                    mime="text/csv"
                )
        except Exception as e:
            st.markdown(f'<div class="error-message">Error al cargar codones: {e}</div>', 
                       unsafe_allow_html=True)
    
    st.markdown('<div class="section-header">Gráficos Generados</div>', 
                unsafe_allow_html=True)
    
    images = resultados.get('images', [])
    
    if not images:
        st.markdown('<div class="warning-message">No se generaron gráficos en el análisis</div>', 
                   unsafe_allow_html=True)
        return
    
    if not st.session_state.selected_graphs:
        st.markdown('<div class="warning-message">No se seleccionaron gráficos para mostrar</div>', 
                   unsafe_allow_html=True)
        return
    
    displayed_graphs = 0
    for graph_key in sorted(GRAPH_CONFIG.keys(), key=lambda x: GRAPH_CONFIG[x]['order']):
        if graph_key in st.session_state.selected_graphs:
            imagen_path = encontrar_imagen_grafico(images, graph_key)
            
            if imagen_path:
                mostrar_grafico_con_descripcion(
                    imagen_path, 
                    graph_key, 
                    GRAPH_CONFIG[graph_key]['name']
                )
                displayed_graphs += 1
            else:
                st.markdown(f'<div class="warning-message">No se encontró el gráfico: {GRAPH_CONFIG[graph_key]["name"]}</div>', 
                           unsafe_allow_html=True)
    
    if displayed_graphs == 0:
        st.markdown('<div class="error-message">No se pudieron cargar ninguno de los gráficos seleccionados</div>', 
                   unsafe_allow_html=True)
        st.markdown(f'<div class="warning-message">Archivos disponibles: {[Path(img).name for img in images]}</div>', 
                   unsafe_allow_html=True)
    
    zip_path = resultados.get('zip_path')
    if zip_path and Path(zip_path).exists():
        st.markdown('<div class="section-header">Descarga de Resultados</div>', 
                    unsafe_allow_html=True)
        with open(zip_path, 'rb') as f:
            st.download_button(
                label="Descargar todos los resultados (ZIP)",
                data=f.read(),
                file_name="resultados_analisis.zip",
                mime="application/zip",
                type="primary",
                use_container_width=True
            )


def main():
    """Función principal de la aplicación."""
    
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    st.markdown('<div style="text-align: center; font-size: 3rem; margin: 1rem 0;">🧬</div>', 
               unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="main-header">SalmoAvianLight</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheader">Comparación de Secuencias: Salmonella vs Gallus</div>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; color: #666; margin-bottom: 2rem;">
    Herramienta de análisis genético para comparar secuencias de Salmonella y Gallus.<br>
    Sube archivos FASTA, selecciona los gráficos requeridos y ejecuta el análisis.
    </div>
    """, unsafe_allow_html=True)
    
    st.info("Modo Local: Ejecutando análisis en este servidor")
    
    st.markdown('<div class="section-header">Carga de Archivos FASTA</div>', 
                unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Salmonella")
        salmonella_file = st.file_uploader(
            "Selecciona el archivo FASTA de Salmonella",
            type=['fa', 'fasta'],
            key="salmonella_uploader",
            help="Archivo FASTA con secuencias de Salmonella"
        )
        if salmonella_file:
            tamaño_mb = salmonella_file.size / (1024 * 1024)
            st.markdown(f'<div class="file-info">Archivo detectado: {salmonella_file.name} ({tamaño_mb:.2f} MB)</div>', 
                       unsafe_allow_html=True)
            
            es_valido, mensaje = validar_archivo_fasta(salmonella_file)
            if not es_valido:
                st.markdown(f'<div class="error-message">Error: {mensaje}</div>', 
                           unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="success-message">Archivo válido: {salmonella_file.name} ({tamaño_mb:.2f} MB)</div>', 
                           unsafe_allow_html=True)
    
    with col2:
        st.subheader("Gallus")
        gallus_file = st.file_uploader(
            "Selecciona el archivo FASTA de Gallus",
            type=['fa', 'fasta'],
            key="gallus_uploader",
            help="Archivo FASTA con secuencias de Gallus"
        )
        if gallus_file:
            tamaño_mb = gallus_file.size / (1024 * 1024)
            st.markdown(f'<div class="file-info">Archivo detectado: {gallus_file.name} ({tamaño_mb:.2f} MB)</div>', 
                       unsafe_allow_html=True)
            
            es_valido, mensaje = validar_archivo_fasta(gallus_file)
            if not es_valido:
                st.markdown(f'<div class="error-message">Error: {mensaje}</div>', 
                           unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="success-message">Archivo válido: {gallus_file.name} ({tamaño_mb:.2f} MB)</div>', 
                           unsafe_allow_html=True)
    
    selected_graphs = mostrar_seleccion_graficos()
    
    st.markdown('<div class="section-header">Parámetros de Análisis</div>', 
                unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        limpiar_ns = st.checkbox(
            "Normalizar/limpiar Ns",
            value=True,
            help="Elimina o normaliza caracteres N en las secuencias"
        )
    
    with col2:
        min_len = st.number_input(
            "Longitud mínima por secuencia",
            min_value=0,
            value=0,
            step=1,
            help="Filtra secuencias con longitud menor a este valor"
        )
    
    with col3:
        top_codons = st.slider(
            "Top codones para gráfico comparativo",
            min_value=5,
            max_value=30,
            value=20,
            step=1,
            help="Número de codones a mostrar en el gráfico comparativo"
        )
    
    params = {
        'limpiar_ns': limpiar_ns,
        'min_len': min_len,
        'top_codons': top_codons
    }
    
    params_changed = False
    if st.session_state.last_used_params is not None:
        params_changed = st.session_state.last_used_params != params
    
    if params_changed and st.session_state.analysis_status == 'COMPLETED':
        st.markdown('<div class="warning-message">Parámetros modificados: Los resultados mostrados fueron generados con parámetros diferentes. Ejecuta un nuevo análisis para ver los resultados con los parámetros actuales.</div>', 
                   unsafe_allow_html=True)
    
    st.markdown('<div class="section-header">Ejecutar Análisis</div>', 
                unsafe_allow_html=True)
    
    ejecutar_btn = st.button(
        "Iniciar Análisis",
        type="primary",
        use_container_width=True,
        disabled=(salmonella_file is None or gallus_file is None)
    )
    
    if ejecutar_btn:
        if salmonella_file and gallus_file:
            salmonella_valido, msg_sal = validar_archivo_fasta(salmonella_file)
            gallus_valido, msg_gall = validar_archivo_fasta(gallus_file)
            
            if not salmonella_valido:
                st.markdown(f'<div class="error-message">Error en archivo Salmonella: {msg_sal}</div>', 
                           unsafe_allow_html=True)
            elif not gallus_valido:
                st.markdown(f'<div class="error-message">Error en archivo Gallus: {msg_gall}</div>', 
                           unsafe_allow_html=True)
            else:
                st.session_state.analysis_results = None
                st.session_state.analysis_status = None
                st.session_state.error_message = None
                
                with st.spinner("Ejecutando análisis..."):
                    if ejecutar_analisis(salmonella_file, gallus_file, params, selected_graphs):
                        st.markdown('<div class="success-message">Análisis completado correctamente</div>', 
                                   unsafe_allow_html=True)
                        st.rerun()
                    else:
                        st.markdown(f'<div class="error-message">Error al ejecutar análisis: {st.session_state.error_message}</div>', 
                                   unsafe_allow_html=True)
    
    if st.session_state.analysis_status:
        st.markdown('<div class="section-header">Estado del Análisis</div>', 
                    unsafe_allow_html=True)
        
        status = st.session_state.analysis_status
        
        if status == 'COMPLETED':
            st.markdown('<div class="status-completed">Análisis completado exitosamente</div>', 
                       unsafe_allow_html=True)
            
            if st.session_state.analysis_results:
                mostrar_resultados(st.session_state.analysis_results)
        
        elif status == 'FAILED':
            st.markdown('<div class="status-failed">El análisis ha fallado</div>', 
                       unsafe_allow_html=True)
            if st.session_state.error_message:
                st.markdown(f'<div class="error-message">Error: {st.session_state.error_message}</div>', 
                           unsafe_allow_html=True)
        
        else:
            st.markdown(f'<div class="status-running">Estado: {status}</div>', 
                       unsafe_allow_html=True)
    
    if st.session_state.execution_history:
        with st.expander("Historial de Ejecuciones"):
            for idx, exec_record in enumerate(reversed(st.session_state.execution_history[-5:])):
                st.write(f"**Ejecución {len(st.session_state.execution_history) - idx}**")
                st.write(f"- Hora: {exec_record['timestamp']}")
                st.write(f"- Estado: {exec_record['status']}")
                st.write(f"- Gráficos: {exec_record['graphs']}")
                st.write("---")


if __name__ == "__main__":
    main()
