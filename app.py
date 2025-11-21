"""
Frontend Web para SalmoAvianLight - Versión Ordenada y Corregida
Conexión exacta entre gráficos y descripciones - ORDEN ESPECÍFICO: GF1, GF8, GF2, GF7, GF3, GF6, GF4, GF5, GF9
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
import concurrent.futures
import base64

# Agregar el directorio raíz al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from services.analysis_client import AnalysisClient
from utils.zipper import crear_zip_resultados

# Configuración de la página para máximo rendimiento
st.set_page_config(
    page_title="SalmoAvianLight",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS optimizados
st.markdown("""
    <style>
    .logo-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        margin: 0 auto;
        padding: 0;
    }
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
    .chart-container {
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        padding: 15px;
        margin: 15px 0;
        background-color: #fafafa;
    }
    .chart-title {
        font-size: 1.3rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 15px;
        text-align: center;
    }
    .chart-description {
        font-size: 0.95rem;
        line-height: 1.5;
        color: #555;
        text-align: justify;
        padding: 12px;
        background-color: #f8f9fa;
        border-left: 3px solid #3498db;
        border-radius: 5px;
    }
    .category-header {
        font-size: 1.1rem;
        font-weight: bold;
        color: #2c3e50;
        margin: 10px 0;
        padding: 8px;
        background-color: #e8f4fd;
        border-radius: 5px;
    }
    .stButton button {
        width: 100%;
    }
    div[data-testid="stMarkdownContainer"]:has(.logo-wrapper) {
        text-align: center;
    }
    .fast-upload {
        border: 2px dashed #4CAF50;
        border-radius: 10px;
        padding: 20px;
        background-color: #f8fff8;
    }
    .upload-success {
        color: #4CAF50;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# CACHE ULTRA RÁPIDO
@st.cache_data(ttl=3600, show_spinner=False)
def get_available_charts():
    """Cache de la lista de gráficos disponibles en ORDEN ESPECÍFICO: GF1, GF8, GF2, GF7, GF3, GF6, GF4, GF5, GF9"""
    return [
        {
            "id": "GF1",
            "name": "GF1 - Distribución del Contenido GC (Gallus)", 
            "category": "Distribuciones de GC",
            "description": "Distribución del contenido GC en Gallus",
            "fast": True,
            "desc_id": "DESCRIPCION_G1"
        },
        {
            "id": "GF8", 
            "name": "GF8 - Heatmap de Uso de Codones en Salmonella",
            "category": "Análisis de Codones",
            "description": "Heatmap de uso de codones específico para Salmonella",
            "fast": False,
            "desc_id": "DESCRIPCION_G8"
        },
        {
            "id": "GF2",
            "name": "GF2 - Distribución del Contenido GC (Salmonella)", 
            "category": "Distribuciones de GC",
            "description": "Distribución del contenido GC en Salmonella",
            "fast": True,
            "desc_id": "DESCRIPCION_G2"
        },
        {
            "id": "GF7",
            "name": "GF7 - Correlación del Uso de Codones entre Salmonella y Gallus",
            "category": "Análisis de Codones", 
            "description": "Correlación en uso de codones entre especies",
            "fast": False,
            "desc_id": "DESCRIPCION_G7"
        },
        {
            "id": "GF3",
            "name": "GF3 - Distribución del Contenido GC (Comparativa)",
            "category": "Distribuciones de GC", 
            "description": "Comparativa de distribución GC entre especies",
            "fast": True,
            "desc_id": "DESCRIPCION_G3"
        },
        {
            "id": "GF6",
            "name": "GF6 - Top 15 Codones Más Frecuentes (Comparación entre Especies)", 
            "category": "Análisis de Codones",
            "description": "Comparación de codones más frecuentes entre especies",
            "fast": True,
            "desc_id": "DESCRIPCION_G6"
        },
        {
            "id": "GF4",
            "name": "GF4 - Distribución Acumulativa de Longitudes de Genes",
            "category": "Distribuciones de Longitud",
            "description": "Distribución acumulativa de longitudes génicas", 
            "fast": True,
            "desc_id": "DESCRIPCION_G4"
        },
        {
            "id": "GF5", 
            "name": "GF5 - Distribución de Longitudes de Secuencias",
            "category": "Distribuciones de Longitud",
            "description": "Distribución general de longitudes de secuencias",
            "fast": True,
            "desc_id": "DESCRIPCION_G5"
        },
        {
            "id": "GF9",
            "name": "GF9 - Relación entre Longitud y Contenido GC",
            "category": "Análisis de Relaciones", 
            "description": "Relación entre longitud de secuencias y contenido GC",
            "fast": True,
            "desc_id": "DESCRIPCION_G9"
        }
    ]

@st.cache_data(ttl=3600, show_spinner=False)
def get_chart_descriptions():
    """Cache del diccionario de descripciones en orden correcto"""
    return {
        "DESCRIPCION_G1": "La distribución del contenido GC en Gallus permite evaluar la composición nucleotídica general de sus genes y detectar posibles sesgos genómicos característicos de la especie. Al observar la forma de la distribución, se identifican zonas de mayor frecuencia que indican rangos de GC preferidos por el organismo. Este análisis proporciona información relevante sobre estabilidad estructural del ADN, presión evolutiva y posibles implicaciones funcionales en la expresión genética. Además, sirve como referencia inicial para comparar el contenido GC con el de otras especies y explorar relaciones con características estructurales como la longitud de los genes o la organización genómica.",
        
        "DESCRIPCION_G2": "La gráfica muestra cómo se distribuye el contenido GC en las secuencias de Salmonella, permitiendo identificar tendencias composicionales propias del organismo. La forma de la distribución revela si existe un sesgo definido hacia valores altos o bajos de GC, así como la presencia de subpoblaciones con composiciones diferenciadas. Esta información es fundamental para comprender la arquitectura del genoma bacteriano, su estabilidad frente a condiciones ambientales y su potencial eficiencia en procesos celulares. Además, la visualización facilita comparaciones posteriores con Gallus, permitiendo evaluar divergencias evolutivas y analizar cómo la composición GC influye en el uso de codones y características estructurales.",
        
        "DESCRIPCION_G3": "Este gráfico compara directamente la distribución del contenido GC entre Gallus y Salmonella, permitiendo observar diferencias claras o similitudes notorias en su composición genética. La comparación revela patrones evolutivos, preferencias nucleotídicas y posibles adaptaciones asociadas a sus entornos o funciones biológicas. Analizar ambas curvas juntas facilita identificar rangos de GC compartidos, así como zonas donde una especie presenta mayor variabilidad o sesgo composicional. Este análisis comparativo es esencial para conectar la composición genómica con posteriores diferencias en el uso de codones, eficiencia translacional y organización estructural. Además, prepara el terreno para interpretar análisis más avanzados como correlaciones y PCA.",
        
        "DESCRIPCION_G4": "Este gráfico muestra la distribución acumulativa de las longitudes génicas, permitiendo visualizar la proporción de secuencias que se encuentran por debajo de diversos umbrales de longitud. La curva revela si la mayoría de los genes se concentra en rangos cortos, medios o largos, y permite identificar colas extensas que indiquen la presencia de secuencias atípicamente grandes. Esta visión acumulativa facilita comparar estructuras genómicas entre especies y evaluar la variabilidad global del tamaño génico. Además, complementa análisis más detallados de variación estructural y sirve como base para relacionar la longitud con otras métricas, como la composición GC o el uso codonal.",
        
        "DESCRIPCION_G5": "La gráfica representa la distribución general de las longitudes de las secuencias analizadas, mostrando cuántos genes se encuentran en cada rango de tamaño. La forma de la distribución permite identificar patrones como concentración alrededor de longitudes específicas, presencia de múltiples picos, alta variabilidad o existencia de valores extremos. Esta información es crucial para comprender la arquitectura básica del genoma y reconocer posibles clases funcionales o estructurales asociadas a longitudes particulares. Además, el análisis sirve como referencia para comparaciones entre especies, exploraciones de relaciones con el contenido GC y evaluaciones de posibles efectos sobre la expresión, estabilidad y regulación génica.",
        
        "DESCRIPCION_G6": "Este gráfico compara los quince codones más frecuentes utilizados por cada especie, proporcionando una visión clara de sus preferencias codonales. Observar estas diferencias o coincidencias permite evaluar sesgos en el uso del código genético, asociados tanto a la composición GC como a presiones evolutivas específicas. La presencia de codones dominantes puede indicar optimización para la traducción, eficiencia en la expresión génica o adaptaciones a su maquinaria celular. Comparar Gallus y Salmonella facilita identificar patrones compartidos o divergentes, revelando información relevante para estudios evolutivos, análisis funcionales y comprensión profunda de la biología molecular de ambas especies.",
        
        "DESCRIPCION_G7": "Este gráfico muestra la relación entre los niveles de uso de cada codón en Salmonella y Gallus, permitiendo evaluar si existe correlación significativa entre ambas especies. Una correlación alta indica patrones codonales similares, posiblemente asociados a presiones evolutivas compartidas o funciones conservadas. Una correlación baja revela divergencia marcada en las preferencias codonales, reflejando adaptaciones propias de cada organismo. La posición de los puntos evidencia codones sobreutilizados o subutilizados en comparación entre especies. Este análisis es fundamental para comprender diferencias funcionales, eficiencia translacional y variaciones genómicas, además de servir como puente entre análisis individuales y representaciones multivariadas como el PCA.",
        
        "DESCRIPCION_G8": "El heatmap presenta la intensidad del uso de codones en Salmonella, visualizada mediante una escala de colores que destaca frecuencias altas, medias y bajas. Esta representación facilita identificar codones preferidos, subutilizados y patrones grupales que pueden reflejar tanto la composición GC como presiones evolutivas específicas. La organización del mapa permite detectar regiones coherentes de uso codonal, evidenciando sesgos característicos de la especie. Este tipo de análisis es muy útil para comprender la eficiencia de traducción, la organización funcional del genoma y la relación entre codones y expresión génica. Además, prepara la base para estudios comparativos y análisis PCA.",
        
        "DESCRIPCION_G9": "Este gráfico examina la relación entre la longitud de las secuencias y su contenido GC, permitiendo evaluar si existe correlación entre estas dos características fundamentales. La dispersión de los puntos muestra patrones que indican si los genes más largos tenden a tener mayor GC o si no existe relación clara. Identificar tendencias ayuda a comprender cómo se estructuran los genes y qué factores influyen en su composición. El análisis también sirve para integrar información obtenida previamente en las distribuciones individuales de longitud y GC, proporcionando una visión más completa del comportamiento genómico y posibilitando interpretaciones evolutivas, funcionales y estructurales."
    }

# Inicialización del session state optimizada
def init_session_state():
    defaults = {
        'analysis_client': AnalysisClient(),
        'job_id': None,
        'analysis_status': None,
        'analysis_results': None,
        'last_params': None,
        'error_message': None,
        'execution_history': [],
        'last_used_params': None,
        'selected_charts': [],
        'file_cache': {},
        'processing_start_time': None,
        'files_validated': False
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

@st.cache_data(ttl=300, show_spinner=False)
def validar_archivo_fasta_ultra_rapido(archivo) -> Tuple[bool, Optional[str]]:
    """Validación ULTRARRÁPIDA de archivos FASTA con cache"""
    if archivo is None:
        return False, "Archivo requerido"
    
    # Validación ultra rápida
    nombre = archivo.name.lower()
    if not (nombre.endswith('.fa') or nombre.endswith('.fasta')):
        return False, "Extensión .fa o .fasta requerida"
    
    if archivo.size == 0:
        return False, "Archivo vacío"
    
    # Validación de formato ultra rápida (solo primeros bytes)
    try:
        primeros_bytes = archivo.read(100)  # Solo 100 bytes para validar
        archivo.seek(0)  # Resetear posición
        if not primeros_bytes.startswith(b'>'):
            return False, "Formato FASTA inválido - debe comenzar con '>'"
        
        # Verificar que tenga al menos una secuencia
        if b'\n>' in primeros_bytes or b'\r>' in primeros_bytes:
            return True, None  # Múltiples secuencias
        elif b'\n' in primeros_bytes and len(primeros_bytes) > 50:
            return True, None  # Al menos una secuencia válida
            
    except Exception as e:
        return False, f"Error de lectura: {str(e)}"
    
    return True, None

def procesamiento_ultra_rapido(salmonella_file, gallus_file):
    """Procesamiento ULTRA rápido con paralelismo optimizado"""
    try:
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_sal = executor.submit(leer_archivo_ultra_rapido, salmonella_file)
            future_gall = executor.submit(leer_archivo_ultra_rapido, gallus_file)
            
            salmonella_content = future_sal.result(timeout=5)
            gallus_content = future_gall.result(timeout=5)
        
        processing_time = time.time() - start_time
        st.success(f"Archivos procesados en {processing_time:.2f} segundos")
        
        return salmonella_content, gallus_content
        
    except concurrent.futures.TimeoutError:
        raise Exception("Timeout: Archivos demasiado grandes para procesamiento rápido")
    except Exception as e:
        raise Exception(f"Error en procesamiento: {str(e)}")

def leer_archivo_ultra_rapido(file):
    """Lee archivo de manera ULTRA rápida"""
    return file.getvalue()

def mostrar_seleccion_graficos_ordenada():
    """Selección ordenada de gráficos manteniendo el orden específico: GF1, GF8, GF2, GF7, GF3, GF6, GF4, GF5, GF9"""
    st.markdown('<div class="section-header">Selección de Gráficos para Análisis</div>', unsafe_allow_html=True)
    
    # Obtener datos cacheados en el orden específico
    available_charts = get_available_charts()
    
    # Selección manual manteniendo el orden específico
    st.markdown("**Selecciona los gráficos que deseas generar:**")
    
    # Organizar por categorías manteniendo orden específico
    categorias = {}
    for chart in available_charts:
        if chart["category"] not in categorias:
            categorias[chart["category"]] = []
        categorias[chart["category"]].append(chart)
    
    # Mostrar en orden específico por categorías
    for categoria, charts in categorias.items():
        st.markdown(f'<div class="category-header">{categoria}</div>', unsafe_allow_html=True)
        
        # Mostrar checkboxes en filas de 3 manteniendo orden específico
        cols = st.columns(3)
        for idx, chart in enumerate(charts):
            with cols[idx % 3]:
                selected = st.checkbox(
                    chart["name"],
                    value=chart["id"] in st.session_state.selected_charts,
                    key=f"chart_{chart['id']}",
                    help=chart["description"]
                )
                
                if selected and chart["id"] not in st.session_state.selected_charts:
                    st.session_state.selected_charts.append(chart["id"])
                elif not selected and chart["id"] in st.session_state.selected_charts:
                    st.session_state.selected_charts.remove(chart["id"])

def ejecutar_analisis_ordenado(salmonella_file, gallus_file, params: Dict):
    """Ejecuta análisis manteniendo orden específico"""
    try:
        st.session_state.processing_start_time = time.time()
        
        # Validación ULTRA rápida
        salmonella_valido, msg_sal = validar_archivo_fasta_ultra_rapido(salmonella_file)
        gallus_valido, msg_gall = validar_archivo_fasta_ultra_rapido(gallus_file)
        
        if not salmonella_valido or not gallus_valido:
            raise ValueError(f"Salmonella: {msg_sal}, Gallus: {msg_gall}")
        
        # Información del análisis
        tamaño_sal = salmonella_file.size / (1024 * 1024)
        tamaño_gall = gallus_file.size / (1024 * 1024)
        num_charts = len(st.session_state.selected_charts)
        
        # Mostrar información de procesamiento
        with st.status("Procesando análisis...", expanded=True) as status:
            st.write(f"**Información del análisis:**")
            st.write(f"Archivo Salmonella: {salmonella_file.name} ({tamaño_sal:.1f}MB)")
            st.write(f"Archivo Gallus: {gallus_file.name} ({tamaño_gall:.1f}MB)")
            st.write(f"Gráficos seleccionados: {num_charts}")
            
            # Procesamiento ULTRA rápido
            st.write("Procesando archivos FASTA...")
            salmonella_content, gallus_content = procesamiento_ultra_rapido(
                salmonella_file, gallus_file
            )
            
            # Parámetros optimizados
            params['selected_charts'] = st.session_state.selected_charts
            
            # Ejecutar análisis
            st.write("Ejecutando análisis genético...")
            if st.session_state.analysis_client.mode == "API":
                resultado = st.session_state.analysis_client.start_analysis(
                    salmonella_content,
                    gallus_content,
                    params
                )
                st.session_state.job_id = resultado.get('jobId')
                st.session_state.analysis_status = 'SUBMITTED'
            else:
                resultado = st.session_state.analysis_client.start_analysis(
                    salmonella_content,
                    gallus_content,
                    params
                )
                st.session_state.analysis_status = resultado.get('status')
                st.session_state.analysis_results = resultado.get('results')
            
            status.update(label="Análisis completado!", state="complete")
        
        # Cache rápido
        st.session_state.last_params = {
            'salmonella_file': salmonella_file,
            'gallus_file': gallus_file,
            'params': params
        }
        
        # Historial rápido
        processing_time = time.time() - st.session_state.processing_start_time
        st.session_state.execution_history.append({
            'timestamp': time.strftime("%H:%M:%S"),
            'status': st.session_state.analysis_status,
            'duration': processing_time
        })
        
        st.success(f"Análisis ejecutado exitosamente en {processing_time:.1f} segundos")
        return True
        
    except Exception as e:
        processing_time = time.time() - st.session_state.processing_start_time if st.session_state.processing_start_time else 0
        st.session_state.error_message = f"Error en {processing_time:.1f}s: {str(e)}"
        st.session_state.analysis_status = 'FAILED'
        st.error(f"Error: {str(e)}")
        return False

def mostrar_graficos_conexion_exacta(images: List):
    """Muestra gráficos con conexión EXACTA entre gráfico y descripción manteniendo orden específico"""
    st.markdown('<div class="section-header">Resultados Gráficos Generados</div>', unsafe_allow_html=True)
    
    if not images:
        st.info("No se generaron gráficos con la configuración actual")
        return
    
    # Obtener datos cacheados
    available_charts = get_available_charts()
    chart_descriptions = get_chart_descriptions()
    
    # CONEXIÓN EXACTA: Mapear cada gráfico seleccionado con su imagen y descripción
    chart_image_pairs = []
    
    # Primero crear pares manteniendo el ORDEN ESPECÍFICO de selected_charts
    for chart_id in st.session_state.selected_charts:
        # Buscar la información exacta del gráfico
        chart_info = next((c for c in available_charts if c["id"] == chart_id), None)
        if chart_info:
            # Buscar la imagen correspondiente (por índice)
            chart_index_in_selected = st.session_state.selected_charts.index(chart_id)
            if chart_index_in_selected < len(images):
                chart_image_pairs.append((chart_info, images[chart_index_in_selected]))
    
    # Mostrar en ORDEN ESPECÍFICO manteniendo la conexión exacta
    for chart_info, image_path in chart_image_pairs:
        with st.container():
            st.markdown(f'<div class="chart-container">', unsafe_allow_html=True)
            st.markdown(f'<div class="chart-title">{chart_info["name"]}</div>', unsafe_allow_html=True)
            
            # Gráfico
            try:
                if st.session_state.analysis_client.mode == "API":
                    import requests
                    response = requests.get(image_path, timeout=10)
                    if response.status_code == 200:
                        st.image(response.content, use_container_width=True)
                    else:
                        st.error(f"Error cargando gráfico: HTTP {response.status_code}")
                else:
                    if Path(image_path).exists():
                        st.image(image_path, use_container_width=True)
                    else:
                        st.error(f"Archivo no encontrado: {image_path}")
            except Exception as e:
                st.error(f"Error cargando gráfico {chart_info['name']}: {e}")
            
            # DESCRIPCIÓN EXACTA correspondiente al gráfico
            descripcion = chart_descriptions.get(chart_info["desc_id"], "Descripción no disponible.")
            st.markdown(f'<div class="chart-description">{descripcion}</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

def mostrar_resultados_ordenados(resultados: Dict):
    """Muestra resultados manteniendo orden específico y conexiones exactas"""
    st.markdown('<div class="section-header">Resultados del Análisis</div>', unsafe_allow_html=True)
    
    # Métricas rápidas
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Resumen de Métricas")
        try:
            if st.session_state.analysis_client.mode == "API":
                import requests
                resumen_csv_url = resultados.get('resumen_csv_url')
                response = requests.get(resumen_csv_url, timeout=10)
                df_metricas = pd.read_csv(io.StringIO(response.text))
            else:
                df_metricas = pd.read_csv(resultados.get('resumen_csv_path'))
            
            st.dataframe(df_metricas.head(15), use_container_width=True)
            
            csv_metricas = df_metricas.to_csv(index=False)
            st.download_button(
                label="Descargar Métricas (CSV)",
                data=csv_metricas,
                file_name="metricas_salmoavian.csv",
                mime="text/csv",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Error cargando métricas: {e}")
    
    with col2:
        st.subheader("Uso de Codones")
        try:
            if st.session_state.analysis_client.mode == "API":
                import requests
                codon_csv_url = resultados.get('codon_csv_url')
                response = requests.get(codon_csv_url, timeout=10)
                df_codones = pd.read_csv(io.StringIO(response.text))
            else:
                df_codones = pd.read_csv(resultados.get('codon_csv_path'))
            
            st.dataframe(df_codones.head(15), use_container_width=True)
            
            csv_codones = df_codones.to_csv(index=False)
            st.download_button(
                label="Descargar Codones (CSV)",
                data=csv_codones,
                file_name="codones_salmoavian.csv",
                mime="text/csv",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Error cargando datos de codones: {e}")
    
    # Gráficos con conexión exacta en orden específico
    images = resultados.get('images', [])
    mostrar_graficos_conexion_exacta(images)

def validar_y_cargar_archivos_rapido():
    """Validación y carga ULTRA rápida de archivos"""
    st.markdown('<div class="section-header">Carga Rápida de Archivos FASTA</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="fast-upload">', unsafe_allow_html=True)
        st.subheader("Salmonella")
        salmonella_file = st.file_uploader(
            "Selecciona el archivo FASTA de Salmonella",
            type=['fa', 'fasta'],
            key="salmonella_ultra_fast",
            help="Archivo FASTA con secuencias de Salmonella"
        )
        if salmonella_file:
            es_valido, mensaje = validar_archivo_fasta_ultra_rapido(salmonella_file)
            if es_valido:
                tamaño_mb = salmonella_file.size / (1024 * 1024)
                st.markdown(f'<p class="upload-success">Válido: {salmonella_file.name} ({tamaño_mb:.1f}MB)</p>', unsafe_allow_html=True)
                st.session_state.files_validated = True
            else:
                st.error(f"{mensaje}")
                st.session_state.files_validated = False
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="fast-upload">', unsafe_allow_html=True)
        st.subheader("Gallus")
        gallus_file = st.file_uploader(
            "Selecciona el archivo FASTA de Gallus", 
            type=['fa', 'fasta'],
            key="gallus_ultra_fast",
            help="Archivo FASTA con secuencias de Gallus"
        )
        if gallus_file:
            es_valido, mensaje = validar_archivo_fasta_ultra_rapido(gallus_file)
            if es_valido:
                tamaño_mb = gallus_file.size / (1024 * 1024)
                st.markdown(f'<p class="upload-success">Válido: {gallus_file.name} ({tamaño_mb:.1f}MB)</p>', unsafe_allow_html=True)
                st.session_state.files_validated = True
            else:
                st.error(f"{mensaje}")
                st.session_state.files_validated = False
        st.markdown('</div>', unsafe_allow_html=True)
    
    return salmonella_file, gallus_file

def main():
    """Aplicación principal ordenada específicamente: GF1, GF8, GF2, GF7, GF3, GF6, GF4, GF5, GF9"""
    init_session_state()
    
    # Header
    logo_path = Path(__file__).parent / "assets" / "logo.png"
    
    if logo_path.exists():
        try:
            with open(logo_path, "rb") as img_file:
                img_data = base64.b64encode(img_file.read()).decode()
            
            st.markdown(
                f"""
                <div style="text-align: center; width: 100%; margin: 1rem 0;">
                    <img src="data:image/png;base64,{img_data}" style="max-width: 150px; height: auto; margin: 0 auto; display: inline-block;">
                </div>
                """,
                unsafe_allow_html=True
            )
        except Exception:
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                st.image(str(logo_path), width=150)
    
    st.markdown('<div class="main-header">SalmoAvianLight</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheader">Análisis Comparativo de Secuencias Genéticas</div>', unsafe_allow_html=True)
    
    # Sección 1: Carga rápida
    salmonella_file, gallus_file = validar_y_cargar_archivos_rapido()
    
    # Sección 2: Configuración de gráficos
    st.markdown('<div class="section-header">Configuración de Análisis</div>', unsafe_allow_html=True)
    
    mostrar_seleccion_graficos_ordenada()
    
    # Parámetros rápidos
    col1, col2, col3 = st.columns(3)
    with col1:
        min_len = st.number_input("Longitud mínima", value=0, help="Filtro rápido por longitud")
    with col2:
        limpiar_ns = st.checkbox("Limpiar Ns", value=True, help="Normalización rápida")
    with col3:
        top_codons = st.slider("Top codones", 5, 30, 15, help="Análisis de codones principales")
    
    params = {'min_len': min_len, 'limpiar_ns': limpiar_ns, 'top_codons': top_codons}
    
    # Sección 3: Ejecución
    st.markdown('<div class="section-header">Ejecución del Análisis</div>', unsafe_allow_html=True)
    
    # Botón de ejecución con validación
    archivos_listos = salmonella_file and gallus_file and st.session_state.files_validated
    ejecutar_btn = st.button(
        "EJECUTAR ANÁLISIS", 
        type="primary",
        use_container_width=True,
        disabled=not archivos_listos,
        help="Ejecuta el análisis con la configuración actual"
    )
    
    if ejecutar_btn and archivos_listos:
        # Limpieza rápida
        st.session_state.analysis_results = None
        st.session_state.analysis_status = None
        st.session_state.error_message = None
        
        # Ejecución ordenada
        if ejecutar_analisis_ordenado(salmonella_file, gallus_file, params):
            st.rerun()
        else:
            st.error(f"Error al ejecutar análisis: {st.session_state.error_message}")
    
    # Sección 4: Resultados
    if st.session_state.analysis_status:
        st.markdown('<div class="section-header">Progreso del Análisis</div>', unsafe_allow_html=True)
        
        status = st.session_state.analysis_status
        
        if status == 'SUBMITTED':
            st.info("Análisis en cola de procesamiento...")
            st.progress(0.3)
        elif status == 'RUNNING':
            st.info("Procesamiento en curso...")
            st.progress(0.7)
        elif status == 'COMPLETED':
            st.success("Análisis completado exitosamente!")
            
            if st.session_state.analysis_client.mode == "API" and st.session_state.job_id:
                try:
                    with st.spinner("Obteniendo resultados..."):
                        resultados = st.session_state.analysis_client.get_results(st.session_state.job_id)
                        st.session_state.analysis_results = resultados
                except Exception as e:
                    st.error(f"Error obteniendo resultados: {e}")
            
            if st.session_state.analysis_results:
                mostrar_resultados_ordenados(st.session_state.analysis_results)
            else:
                st.warning("Los resultados no están disponibles aún.")
        
        elif status == 'FAILED':
            st.error("Error en el análisis")
            if st.session_state.error_message:
                st.error(st.session_state.error_message)

if __name__ == "__main__":
    main()
