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
import base64

# Agregar el directorio raíz al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from services.analysis_client import AnalysisClient
from utils.zipper import crear_zip_resultados

# Configuración de la página
st.set_page_config(
    page_title="SalmoAvianLight",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS personalizados
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

# Inicializar session state
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

# Diccionario de gráficos disponibles con mapeo de nombres de archivo
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

# Diccionario de descripciones de gráficos
GRAPH_DESCRIPTIONS = {
    'hist_longitud_secuencias': """
    Este histograma muestra la distribución de longitudes de secuencias en el conjunto de datos. 
    Permite identificar patrones como la presencia de secuencias cortas o largas predominantes, 
    la variabilidad en tamaño y posibles agrupaciones. La forma de la distribución (normal, 
    sesgada o bimodal) proporciona información sobre la homogeneidad del conjunto de datos 
    y puede revelar la presencia de múltiples tipos de secuencias con características distintas.
    """,
    
    'distribucion_gc': """
    El gráfico de distribución de contenido GC muestra el porcentaje de bases Guanina y Citosina 
    en las secuencias. Una distribución normal sugiere homogeneidad genética, mientras que 
    distribuciones multimodales pueden indicar la presencia de múltiples especies o cepas. 
    El contenido GC es un marcador taxonómico importante y su análisis ayuda a caracterizar 
    la composición genómica y adaptaciones ambientales de los organismos estudiados.
    """,
    
    'frecuencia_codones': """
    Este gráfico de barras representa la frecuencia relativa de uso de cada codón en las secuencias. 
    Muestra preferencias en el uso de codones, lo que puede reflejar sesgos genómicos o adaptaciones 
    evolutivas. Los codones más frecuentes suelen estar asociados con una expresión génica más 
    eficiente. Las diferencias en los patrones de uso entre especies pueden indicar distintos 
    mecanismos de regulación de la expresión génica.
    """,
    
    'comparativa_uso_codones': """
    Gráfico comparativo que muestra las diferencias en el uso de codones entre las dos especies. 
    Permite identificar codones preferencialmente utilizados por cada organismo, lo que puede 
    reflejar adaptaciones evolutivas específicas. Las divergencias significativas pueden indicar 
    diferentes presiones selectivas o mecanismos de regulación de la expresión génica entre 
    las especies comparadas.
    """,
    
    'correlacion_uso_codones': """
    Este gráfico de dispersión explora la relación entre el uso de codones en las dos especies. 
    Una correlación positiva fuerte indica patrones de uso similares, sugiriendo conservación 
    evolutiva. Los puntos que se desvían de la línea de tendencia representan codones con uso 
    diferencial, potencialmente asociados a adaptaciones específicas de cada especie o a 
    diferentes mecanismos regulatorios.
    """,
    
    'pca_secuencias': """
    El análisis de Componentes Principales (PCA) reduce la dimensionalidad de los datos para 
    visualizar patrones en el uso de codones. Los agrupamientos indicant similitudes entre 
    secuencias, mientras que la separación sugiere diferencias significativas. La proximidad 
    de puntos representa similitudes en los patrones de uso de codones, permitiendo identificar 
    agrupaciones naturales y valores atípicos en el conjunto de datos.
    """,
    
    'heatmap_correlacion': """
    Este heatmap muestra las correlaciones entre diferentes variables mediante una escala de colores. 
    Los tonos cálidos indican correlaciones positivas fuertes, mientras que los tonos fríos 
    representan correlaciones negativas. Los patrones de bloques sugieren agrupaciones de variables 
    relacionadas. Esta visualización ayuda a identificar relaciones complejas y patrones de 
    co-variación en el conjunto de datos de manera intuitiva.
    """,
    
    'boxplot_longitud_por_especie': """
    Los boxplots comparan la distribución de longitudes de secuencias entre especies. 
    Cada caja muestra la mediana, cuartiles y valores extremos, permitiendo identificar 
    diferencias en la variabilidad y tendencia central. La superposición o separación de 
    las cajas indica similitudes o diferencias significativas en las longitudes de secuencias 
    entre los organismos comparados.
    """,
    
    'scatter_gc_vs_longitud': """
    Este gráfico de dispersión explora la relación entre el contenido GC y la longitud de las 
    secuencias. Los patrones de distribución pueden revelar si existe correlación entre estas 
    variables. Agrupamientos específicos pueden indicar diferentes clases de secuencias o 
    elementos genómicos. La ausencia de patrón claro sugiere independencia entre el contenido 
    GC y la longitud de las secuencias analizadas.
    """
}


def validar_archivo_fasta(archivo) -> Tuple[bool, Optional[str]]:
    """
    Valida que el archivo subido sea un FASTA válido.
    """
    if archivo is None:
        return False, "Por favor, sube un archivo FASTA"
    
    nombre_archivo = archivo.name.lower()
    if not (nombre_archivo.endswith('.fa') or nombre_archivo.endswith('.fasta')):
        return False, "El archivo debe tener extensión .fa o .fasta"
    
    if archivo.size == 0:
        return False, "El archivo está vacío"
    
    tamaño_mb = archivo.size / (1024 * 1024)
    
    es_streamlit_cloud = os.environ.get("STREAMLIT_SHARING_MODE") == "true" or "streamlit.app" in os.environ.get("SERVER_NAME", "")
    es_render = os.environ.get("RENDER") == "true" or "render.com" in os.environ.get("SERVER_NAME", "")
    es_local = not es_streamlit_cloud and not es_render
    
    if es_streamlit_cloud:
        limite_mb = 100
    elif es_render:
        limite_mb = 50
    else:
        limite_mb = 200
    
    if not es_local and tamaño_mb > limite_mb:
        return False, f"El archivo es demasiado grande ({tamaño_mb:.2f} MB). El límite máximo recomendado es {limite_mb} MB por archivo."
    
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
        
        # Buscar por patrones específicos
        for pattern in patterns:
            if pattern in img_name:
                return img_path
        
        # Buscar por clave del gráfico
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
        
        # Leer archivos
        with st.spinner("Leyendo archivos FASTA..."):
            # Usar getvalue() para obtener el contenido como bytes
            salmonella_content = salmonella_file.getvalue()
            gallus_content = gallus_file.getvalue()
        
        # Agregar gráficos seleccionados a los parámetros
        params['selected_graphs'] = selected_graphs
        
        # Ejecutar análisis
        with st.spinner("Ejecutando análisis genético..."):
            if st.session_state.analysis_client.mode == "API":
                resultado = st.session_state.analysis_client.start_analysis(
                    salmonella_content,
                    gallus_content,
                    params
                )
                if 'jobId' in resultado:
                    st.session_state.job_id = resultado.get('jobId')
                    st.session_state.analysis_status = 'SUBMITTED'
                else:
                    st.session_state.analysis_status = 'FAILED'
                    st.session_state.error_message = "El backend no devolvió un ID de trabajo válido"
                    return False
            else:
                # Modo local
                resultado = st.session_state.analysis_client.start_analysis(
                    salmonella_content,
                    gallus_content,
                    params
                )
                st.session_state.analysis_status = resultado.get('status', 'COMPLETED')
                st.session_state.analysis_results = resultado
        
        # Guardar parámetros
        st.session_state.last_params = {
            'salmonella_file': salmonella_file,
            'gallus_file': gallus_file,
            'params': params
        }
        
        st.session_state.last_used_params = params.copy()
        st.session_state.selected_graphs = selected_graphs
        
        # Agregar a historial
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
            if st.session_state.analysis_client.mode == "API":
                import requests
                response = requests.get(imagen_path)
                if response.status_code == 200:
                    st.image(response.content, use_container_width=True)
                else:
                    st.markdown(f'<div class="error-message">Error al cargar imagen: HTTP {response.status_code}</div>', 
                               unsafe_allow_html=True)
            else:
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
    
    # Mostrar tablas CSV
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Resumen de Métricas")
        try:
            df_metricas = None
            if st.session_state.analysis_client.mode == "API":
                import requests
                resumen_csv_url = resultados.get('resumen_csv_url')
                if resumen_csv_url:
                    response = requests.get(resumen_csv_url)
                    if response.status_code == 200:
                        df_metricas = pd.read_csv(io.StringIO(response.text))
                    else:
                        st.markdown(f'<div class="warning-message">Error al descargar métricas: HTTP {response.status_code}</div>', 
                                   unsafe_allow_html=True)
                else:
                    st.markdown('<div class="warning-message">No se proporcionó URL para el archivo de métricas</div>', 
                               unsafe_allow_html=True)
            else:
                resumen_csv_path = resultados.get('resumen_csv_path')
                if resumen_csv_path and Path(resumen_csv_path).exists():
                    df_metricas = pd.read_csv(resumen_csv_path)
                else:
                    st.markdown('<div class="warning-message">No se encontró el archivo de métricas en la ruta especificada</div>', 
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
            if st.session_state.analysis_client.mode == "API":
                import requests
                codon_csv_url = resultados.get('codon_csv_url')
                if codon_csv_url:
                    response = requests.get(codon_csv_url)
                    if response.status_code == 200:
                        df_codones = pd.read_csv(io.StringIO(response.text))
                    else:
                        st.markdown(f'<div class="warning-message">Error al descargar codones: HTTP {response.status_code}</div>', 
                                   unsafe_allow_html=True)
                else:
                    st.markdown('<div class="warning-message">No se proporcionó URL para el archivo de codones</div>', 
                               unsafe_allow_html=True)
            else:
                codon_csv_path = resultados.get('codon_csv_path')
                if codon_csv_path and Path(codon_csv_path).exists():
                    df_codones = pd.read_csv(codon_csv_path)
                else:
                    st.markdown('<div class="warning-message">No se encontró el archivo de codones en la ruta especificada</div>', 
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
    
    # Mostrar gráficos
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
    
    # Mostrar gráficos en el orden definido
    displayed_graphs = 0
    for graph_key in GRAPH_CONFIG.keys():
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


def main():
    """Función principal de la aplicación."""
    
    # Logo centrado
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    logo_path = Path(__file__).parent / "assets" / "logo.png"
    if logo_path.exists():
        st.image(str(logo_path), width=200)
    else:
        st.markdown('<div style="text-align: center; font-size: 3rem; margin: 1rem 0;">🧬</div>', 
                   unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Título y subtítulo
    st.markdown('<div class="main-header">SalmoAvianLight</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheader">Comparación de Secuencias: Salmonella vs Gallus</div>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; color: #666; margin-bottom: 2rem;">
    Herramienta de análisis genético para comparar secuencias de Salmonella y Gallus.<br>
    Sube archivos FASTA, selecciona los gráficos requeridos y ejecuta el análisis.
    </div>
    """, unsafe_allow_html=True)
    
    # Indicador de modo
    modo = st.session_state.analysis_client.mode
    if modo == "API":
        st.info(f"Modo API: Conectado a {st.session_state.analysis_client.base_url}")
    else:
        st.info("Modo Local: Ejecutando análisis en este servidor")
    
    # Sección 1: Carga de archivos
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
    
    # Sección 2: Selección de gráficos
    selected_graphs = mostrar_seleccion_graficos()
    
    # Sección 3: Parámetros
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
    
    # Verificar si los parámetros han cambiado
    params_changed = False
    if st.session_state.last_used_params is not None:
        params_changed = st.session_state.last_used_params != params
    
    if params_changed and st.session_state.analysis_status == 'COMPLETED':
        st.markdown('<div class="warning-message">Parámetros modificados: Los resultados mostrados fueron generados con parámetros diferentes. Ejecuta un nuevo análisis para ver los resultados con los parámetros actuales.</div>', 
                   unsafe_allow_html=True)
    
    # Sección 4: Ejecutar análisis
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
                # Limpiar resultados anteriores
                st.session_state.analysis_results = None
                st.session_state.analysis_status = None
                st.session_state.error_message = None
                
                # Limpiar directorio temporal
                if st.session_state.analysis_client.temp_dir:
                    try:
                        if os.path.exists(st.session_state.analysis_client.temp_dir):
                            shutil.rmtree(st.session_state.analysis_client.temp_dir, ignore_errors=True)
                    except Exception:
                        pass
                
                # Ejecutar análisis
                with st.spinner("Ejecutando análisis..."):
                    if ejecutar_analisis(salmonella_file, gallus_file, params, selected_graphs):
                        st.markdown('<div class="success-message">Análisis iniciado correctamente</div>', 
                                   unsafe_allow_html=True)
                        st.rerun()
                    else:
                        st.markdown(f'<div class="error-message">Error al ejecutar análisis: {st.session_state.error_message}</div>', 
                                   unsafe_allow_html=True)
    
    # Sección 5: Estado y progreso
    if st.session_state.analysis_status:
        st.markdown('<div class="section-header">Estado del Análisis</div>', 
                    unsafe_allow_html=True)
        
        status = st.session_state.analysis_status
        
        if status == 'SUBMITTED':
            st.markdown('<div class="status-running">Análisis enviado. Esperando procesamiento...</div>', 
                       unsafe_allow_html=True)
            if st.session_state.analysis_client.mode == "API" and st.session_state.job_id:
                if st.button("Actualizar estado", key="refresh_status"):
                    try:
                        status_response = st.session_state.analysis_client.get_status(st.session_state.job_id)
                        nuevo_status = status_response.get('status')
                        st.session_state.analysis_status = nuevo_status
                        if status_response.get('message'):
                            st.write(status_response.get('message'))
                        st.rerun()
                    except Exception as e:
                        st.markdown(f'<div class="error-message">Error al actualizar estado: {e}</div>', 
                                   unsafe_allow_html=True)
        
        elif status == 'RUNNING':
            st.markdown('<div class="status-running">Análisis en progreso...</div>', 
                       unsafe_allow_html=True)
            progress_bar = st.progress(0.5)
            st.write("Procesando secuencias y generando gráficos...")
            
            if st.session_state.analysis_client.mode == "API" and st.session_state.job_id:
                if st.button("Actualizar estado", key="refresh_running"):
                    try:
                        status_response = st.session_state.analysis_client.get_status(st.session_state.job_id)
                        nuevo_status = status_response.get('status')
                        st.session_state.analysis_status = nuevo_status
                        if status_response.get('message'):
                            st.write(status_response.get('message'))
                        st.rerun()
                    except Exception as e:
                        st.markdown(f'<div class="error-message">Error al actualizar estado: {e}</div>', 
                                   unsafe_allow_html=True)
        
        elif status == 'COMPLETED':
            st.markdown('<div class="status-completed">Análisis completado exitosamente</div>', 
                       unsafe_allow_html=True)
            
            # Obtener resultados si estamos en modo API
            if st.session_state.analysis_client.mode == "API" and st.session_state.job_id:
                try:
                    resultados = st.session_state.analysis_client.get_results(st.session_state.job_id)
                    st.session_state.analysis_results = resultados
                except Exception as e:
                    st.markdown(f'<div class="error-message">Error al obtener resultados: {e}</div>', 
                               unsafe_allow_html=True)
                    st.session_state.analysis_results = None
            
            if st.session_state.analysis_results:
                mostrar_resultados(st.session_state.analysis_results)
            else:
                st.markdown('<div class="warning-message">Los resultados no están disponibles aún.</div>', 
                           unsafe_allow_html=True)
        
        elif status == 'FAILED':
            st.markdown('<div class="status-failed">El análisis falló</div>', 
                       unsafe_allow_html=True)
            if st.session_state.error_message:
                st.markdown(f'<div class="error-message">Error: {st.session_state.error_message}</div>', 
                           unsafe_allow_html=True)
            
            if st.session_state.last_params:
                if st.button("Reintentar análisis"):
                    st.session_state.analysis_status = None
                    st.session_state.error_message = None
                    st.rerun()
    
    # Sección 6: Historial
    if st.session_state.execution_history:
        with st.expander("Historial de Ejecuciones"):
            hist_df = pd.DataFrame(st.session_state.execution_history)
            st.dataframe(hist_df, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; font-size: 0.9rem;">
    Herramienta de Análisis Genético - Salmonella vs Gallus<br>
    Para analistas de laboratorio
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
