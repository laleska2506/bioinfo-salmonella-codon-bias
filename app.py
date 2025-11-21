"""
Frontend Web para SalmoAvianLight - Versión Final Ultra Rápida
Con descripciones específicas y cache optimizado
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
    </style>
""", unsafe_allow_html=True)

# CACHE ULTRA RÁPIDO
@st.cache_data(ttl=3600, show_spinner=False)
def get_available_charts():
    """Cache de la lista de gráficos disponibles"""
    return [
        {
            "id": "histograma_longitud",
            "name": "Histograma de Longitudes", 
            "category": "Distribuciones Básicas",
            "description": "Distribución de frecuencias de longitudes de secuencias",
            "fast": True,
            "desc_id": "DESCRIPCION_G1"
        },
        {
            "id": "distribucion_gc",
            "name": "Distribución de Contenido GC", 
            "category": "Distribuciones Básicas",
            "description": "Distribución del porcentaje de contenido GC en las secuencias",
            "fast": True,
            "desc_id": "DESCRIPCION_G2"
        },
        {
            "id": "frecuencia_codones",
            "name": "Frecuencia de Uso de Codones",
            "category": "Análisis de Codones", 
            "description": "Frecuencia relativa de uso de cada codón en las secuencias",
            "fast": True,
            "desc_id": "DESCRIPCION_G3"
        },
        {
            "id": "comparativa_codones",
            "name": "Comparativa de Uso de Codones",
            "category": "Análisis de Codones",
            "description": "Comparación del uso de codones entre las dos especies", 
            "fast": True,
            "desc_id": "DESCRIPCION_G4"
        },
        {
            "id": "correlacion_codones", 
            "name": "Correlación de Uso de Codones",
            "category": "Análisis de Codones",
            "description": "Análisis de correlación en el uso de codones entre especies",
            "fast": False,
            "desc_id": "DESCRIPCION_G5"
        },
        {
            "id": "boxplot_longitud",
            "name": "Distribución de Longitudes por Especie", 
            "category": "Comparativas Estadísticas",
            "description": "Comparación de distribuciones de longitud mediante diagramas de caja",
            "fast": True,
            "desc_id": "DESCRIPCION_G6"
        },
        {
            "id": "pca",
            "name": "Análisis de Componentes Principales",
            "category": "Análisis Multivariado", 
            "description": "Reducción de dimensionalidad basada en patrones de uso de codones",
            "fast": False,
            "desc_id": "DESCRIPCION_G7"
        },
        {
            "id": "heatmap", 
            "name": "Mapa de Calor de Similitudes",
            "category": "Análisis Multivariado",
            "description": "Visualización de similitudes entre secuencias mediante gradientes de color",
            "fast": False,
            "desc_id": "DESCRIPCION_G8"
        },
        {
            "id": "scatter_gc_longitud",
            "name": "Relación GC vs Longitud",
            "category": "Análisis de Relaciones", 
            "description": "Análisis de la relación entre contenido GC y longitud de secuencias",
            "fast": True,
            "desc_id": "DESCRIPCION_G9"
        }
    ]

@st.cache_data(ttl=3600, show_spinner=False)
def get_chart_descriptions():
    """Cache del diccionario de descripciones con las descripciones específicas"""
    return {
        "DESCRIPCION_G1": "El histograma de longitudes muestra la distribución de los valores asociados a la variable de tamaño dentro del conjunto de datos. Cada barra representa la frecuencia con la que aparece un rango específico de longitudes, permitiendo identificar concentraciones, dispersiones y posibles extremos. Este gráfico facilita observar si la distribución es simétrica, sesgada o multimodal. Además, permite comparar visualmente la densidad relativa entre diferentes intervalos. El histograma es útil para comprender la variabilidad general, detectar patrones subyacentes y evaluar si los datos siguen una tendencia particular, lo cual resulta fundamental para análisis posteriores o decisiones basadas en la estructura.",
        
        "DESCRIPCION_G2": "La distribución del contenido GC presenta cómo se comportan los porcentajes de guanina y citosina a lo largo de todas las secuencias analizadas. A través del gráfico, es posible visualizar la variabilidad, identificar valores centrales y detectar regiones con alto o bajo contenido GC. Esta representación permite evaluar si la distribución es uniforme, sesgada o presenta agrupamientos particulares. Además, ayuda a reconocer patrones globales y diferencias entre elementos dentro del conjunto. Con esta información, se puede inferir estabilidad relativa, complejidad de composición y posibles características estructurales relevantes para estudios comparativos o análisis posteriores sobre composición general.",
        
        "DESCRIPCION_G3": "La visualización de frecuencia de uso de codones muestra cuántas veces aparece cada codón dentro del conjunto de secuencias analizadas. Permite identificar cuáles codones son más comunes y cuáles se utilizan menos, facilitando la detección de posibles sesgos o preferencias en el sistema estudiado. El gráfico ayuda a observar patrones globales y variaciones significativas entre codones individuales. Asimismo, es útil para comparar la distribución general y evaluar si existe uniformidad o concentración en determinados grupos. Esta información resulta valiosa para estudios de optimización, análisis evolutivo o comprensión de características funcionales relacionadas con el uso específico observado.",
        
        "DESCRIPCION_G4": "La gráfica comparativa de uso de codones permite evaluar diferencias en frecuencia entre múltiples grupos, muestras o categorías. Muestra cómo varía la utilización de cada codón en distintos contextos, facilitando la identificación de patrones divergentes o coincidencias significativas. Este tipo de comparación ayuda a determinar si existen preferencias específicas, posibles adaptaciones o sesgos diferenciados. También revela la magnitud de las diferencias, destacando codones que muestran comportamientos similares o contrastantes. Esta visualización es especialmente útil para análisis comparativos, estudios evolutivos o evaluaciones de optimización, proporcionando una perspectiva clara sobre cómo se distribuye el uso en diferentes condiciones.",
        
        "DESCRIPCION_G5": "El gráfico de correlación de uso de codones muestra el grado de asociación entre los patrones de frecuencia de diferentes codones dentro del conjunto analizado. Utiliza una matriz o representación equivalente para visualizar cómo se relaciona cada codón con los demás, indicando si existe una correlación positiva, negativa o nula. Esta herramienta permite identificar grupos de codones que comparten comportamientos similares, así como detectar relaciones inusuales. Además, facilita comprender la estructura interna del uso codón y posibles dependencias. Es especialmente útil para análisis estadísticos, inferencias funcionales y exploración de patrones que no son evidentes individualmente.",
        
        "DESCRIPCION_G6": "El boxplot de longitudes ofrece una representación clara de la distribución de tamaños dentro del conjunto de datos. Muestra la mediana, los cuartiles y posibles valores atípicos, facilitando la comprensión de la variabilidad y la dispersión. Este gráfico permite identificar simetrías, asimetrías y rangos intercuartílicos, proporcionando una visión rápida del comportamiento central y extremo de las longitudes. Es especialmente útil para comparar múltiples grupos o categorías bajo la misma métrica, permitiendo evaluar diferencias estructurales. Además, ayuda a detectar anomalías importantes y a comprender la estabilidad relativa del conjunto, sirviendo como base para análisis más profundos.",
        
        "DESCRIPCION_G7": "El gráfico de análisis PCA representa la reducción de dimensionalidad del conjunto de datos, mostrando cómo se agrupan o separan los elementos en un espacio compuesto por componentes principales. Cada punto refleja una combinación lineal de variables originales, optimizada para capturar la mayor variabilidad posible. La visualización facilita identificar patrones, similitudes, separaciones y tendencias globales entre muestras. También permite evaluar qué tanto contribuye cada componente a la variación total, interpretando relaciones subyacentes. Este gráfico es fundamental para explorar estructuras complejas, detectar agrupamientos naturales y comprender la organización interna antes de aplicar análisis más detallados o métodos adicionales.",
        
        "DESCRIPCION_G8": "El heatmap de similitudes muestra visualmente el grado de semejanza entre pares de elementos del conjunto de datos mediante una escala de colores. Cada celda representa la similitud relativa entre dos entidades, permitiendo identificar patrones agrupados, bloques cohesivos o regiones contrastantes. Este tipo de visualización facilita detectar clústeres naturales, relaciones inesperadas o comportamientos divergentes. Además, ayuda a comprender la estructura global del conjunto y a evaluar qué tan homogéneas o diversas son las muestras. Es una herramienta valiosa para análisis comparativos, clasificación, detección de patrones y exploraciones iniciales en conjuntos complejos o de alta dimensionalidad.",
        
        "DESCRIPCION_G9": "El gráfico de dispersión GC vs longitud muestra la relación entre el contenido GC y la longitud de cada secuencia analizada. Cada punto representa una secuencia, permitiendo observar si existe una tendencia, correlación o patrón claro entre ambas variables. El gráfico ayuda a identificar agrupamientos, dispersiones y posibles outliers que puedan indicar comportamientos inusuales. Además, permite visualizar si el contenido GC se mantiene estable, aumenta o disminuye según la longitud. Esta representación es útil para explorar dependencias y evaluar si las variaciones en composición tienen conexión con el tamaño de las secuencias dentro del conjunto estudiado."
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
        'processing_start_time': None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

@st.cache_data(ttl=300, show_spinner=False)
def validar_archivo_fasta_rapido(archivo) -> Tuple[bool, Optional[str]]:
    """Validación ultrarrápida de archivos FASTA con cache"""
    if archivo is None:
        return False, "Archivo requerido"
    
    # Validación rápida
    nombre = archivo.name.lower()
    if not (nombre.endswith('.fa') or nombre.endswith('.fasta')):
        return False, "Extensión .fa o .fasta requerida"
    
    if archivo.size == 0:
        return False, "Archivo vacío"
    
    # Validación de formato rápido
    try:
        primeros_bytes = archivo.read(50)
        archivo.seek(0)
        if not primeros_bytes.startswith(b'>'):
            return False, "Formato FASTA inválido"
    except Exception as e:
        return False, f"Error de lectura: {str(e)}"
    
    return True, None

def procesamiento_ultra_rapido(salmonella_file, gallus_file):
    """Procesamiento ultra rápido con paralelismo"""
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_sal = executor.submit(leer_archivo_rapido, salmonella_file)
            future_gall = executor.submit(leer_archivo_rapido, gallus_file)
            
            salmonella_content = future_sal.result(timeout=10)
            gallus_content = future_gall.result(timeout=10)
        
        return salmonella_content, gallus_content
        
    except concurrent.futures.TimeoutError:
        raise Exception("Timeout: Archivos demasiado grandes")
    except Exception as e:
        raise Exception(f"Error en procesamiento: {str(e)}")

def leer_archivo_rapido(file):
    """Lee archivo de manera ultra rápida"""
    return file.read()

def mostrar_seleccion_graficos_rapida():
    """Selección rápida de gráficos con datos cacheados"""
    st.markdown('<div class="section-header">Selección Rápida de Gráficos</div>', unsafe_allow_html=True)
    
    # Obtener datos cacheados
    available_charts = get_available_charts()
    
    # Modo turbo para máxima velocidad
    modo_turbo = st.checkbox(
        "🚀 Modo Turbo (Gráficos Rápidos)", 
        value=True,
        help="Selecciona automáticamente solo los gráficos de procesamiento más rápido"
    )
    
    if modo_turbo:
        st.session_state.selected_charts = [chart["id"] for chart in available_charts if chart["fast"]]
        st.success("✅ Modo Turbo activado: Procesamiento máximo velocidad")
        return
    
    # Selección manual optimizada
    categorias = {}
    for chart in available_charts:
        if chart["category"] not in categorias:
            categorias[chart["category"]] = []
        categorias[chart["category"]].append(chart)
    
    for categoria, charts in categorias.items():
        st.markdown(f'<div class="category-header">{categoria}</div>', unsafe_allow_html=True)
        
        cols = st.columns(3)
        for idx, chart in enumerate(charts):
            with cols[idx % 3]:
                selected = st.checkbox(
                    chart["name"],
                    value=chart["id"] in st.session_state.selected_charts,
                    key=f"chart_{chart['id']}",
                    help=chart["description"]
                )
                
                if selected:
                    if chart["id"] not in st.session_state.selected_charts:
                        st.session_state.selected_charts.append(chart["id"])
                else:
                    if chart["id"] in st.session_state.selected_charts:
                        st.session_state.selected_charts.remove(chart["id"])

def ejecutar_analisis_turbo(salmonella_file, gallus_file, params: Dict):
    """Ejecuta análisis en modo turbo"""
    try:
        st.session_state.processing_start_time = time.time()
        
        # Validación ultrarrápida
        salmonella_valido, msg_sal = validar_archivo_fasta_rapido(salmonella_file)
        gallus_valido, msg_gall = validar_archivo_fasta_rapido(gallus_file)
        
        if not salmonella_valido or not gallus_valido:
            raise ValueError(f"Salmonella: {msg_sal}, Gallus: {msg_gall}")
        
        # Información rápida
        tamaño_sal = salmonella_file.size / (1024 * 1024)
        tamaño_gall = gallus_file.size / (1024 * 1024)
        num_charts = len(st.session_state.selected_charts)
        
        st.write(f"**Procesamiento Turbo Activado:**")
        st.write(f"- Archivo Salmonella: {tamaño_sal:.1f}MB")
        st.write(f"- Archivo Gallus: {tamaño_gall:.1f}MB")
        st.write(f"- Gráficos seleccionados: {num_charts}")
        
        # Procesamiento ultra rápido
        with st.spinner("🚀 Procesamiento turbo en curso..."):
            salmonella_content, gallus_content = procesamiento_ultra_rapido(
                salmonella_file, gallus_file
            )
        
        # Parámetros optimizados
        params['selected_charts'] = st.session_state.selected_charts
        params['turbo_mode'] = True
        
        # Ejecutar análisis
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
        
        # Cache rápido
        st.session_state.last_params = {
            'salmonella_file': salmonella_file,
            'gallus_file': gallus_file,
            'params': params
        }
        
        # Historial rápido
        st.session_state.execution_history.append({
            'timestamp': time.strftime("%H:%M:%S"),
            'status': st.session_state.analysis_status,
            'duration': time.time() - st.session_state.processing_start_time
        })
        
        return True
        
    except Exception as e:
        processing_time = time.time() - st.session_state.processing_start_time if st.session_state.processing_start_time else 0
        st.session_state.error_message = f"Error en {processing_time:.1f}s: {str(e)}"
        st.session_state.analysis_status = 'FAILED'
        st.error(f"❌ Error: {str(e)}")
        return False

def mostrar_graficos_rapidos_con_descripciones(images: List):
    """Muestra gráficos rápidos con descripciones correctas usando cache"""
    st.markdown('<div class="section-header">📊 Resultados Gráficos Generados</div>', unsafe_allow_html=True)
    
    if not images:
        st.info("No se generaron gráficos con la configuración actual")
        return
    
    # Obtener datos cacheados
    available_charts = get_available_charts()
    chart_descriptions = get_chart_descriptions()
    
    # Mapeo preciso entre imágenes y gráficos seleccionados
    chart_image_mapping = {}
    for i, chart_id in enumerate(st.session_state.selected_charts):
        if i < len(images):
            chart_image_mapping[chart_id] = images[i]
    
    # Mostrar en grid rápido
    charts_per_row = 2
    chart_items = []
    
    for chart_id in st.session_state.selected_charts:
        if chart_id in chart_image_mapping:
            chart_info = next((c for c in available_charts if c["id"] == chart_id), None)
            if chart_info:
                chart_items.append((chart_info, chart_image_mapping[chart_id]))
    
    # Mostrar en filas
    for i in range(0, len(chart_items), charts_per_row):
        row_items = chart_items[i:i + charts_per_row]
        cols = st.columns(charts_per_row)
        
        for idx, (chart_info, image_path) in enumerate(row_items):
            with cols[idx]:
                with st.container():
                    st.markdown(f'<div class="chart-container">', unsafe_allow_html=True)
                    st.markdown(f'<div class="chart-title">{chart_info["name"]}</div>', unsafe_allow_html=True)
                    
                    # Gráfico
                    try:
                        if st.session_state.analysis_client.mode == "API":
                            import requests
                            response = requests.get(image_path, timeout=5)
                            st.image(response.content, use_container_width=True)
                        else:
                            if Path(image_path).exists():
                                st.image(image_path, use_container_width=True)
                    except Exception as e:
                        st.error(f"Error cargando gráfico: {e}")
                    
                    # DESCRIPCIÓN CORRECTA usando el diccionario cacheados
                    descripcion = chart_descriptions.get(chart_info["desc_id"], "Descripción no disponible.")
                    st.markdown(f'<div class="chart-description">{descripcion}</div>', unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)

def mostrar_resultados_turbo(resultados: Dict):
    """Muestra resultados en modo turbo"""
    st.markdown('<div class="section-header">📈 Resultados del Análisis</div>', unsafe_allow_html=True)
    
    # Métricas rápidas
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Resumen de Métricas")
        try:
            if st.session_state.analysis_client.mode == "API":
                import requests
                resumen_csv_url = resultados.get('resumen_csv_url')
                response = requests.get(resumen_csv_url, timeout=5)
                df_metricas = pd.read_csv(io.StringIO(response.text))
            else:
                df_metricas = pd.read_csv(resultados.get('resumen_csv_path'))
            
            st.dataframe(df_metricas.head(15), use_container_width=True)
            
            csv_metricas = df_metricas.to_csv(index=False)
            st.download_button(
                label="📥 Descargar Métricas",
                data=csv_metricas,
                file_name="metricas.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"Error cargando métricas: {e}")
    
    with col2:
        st.subheader("🧬 Uso de Codones")
        try:
            if st.session_state.analysis_client.mode == "API":
                import requests
                codon_csv_url = resultados.get('codon_csv_url')
                response = requests.get(codon_csv_url, timeout=5)
                df_codones = pd.read_csv(io.StringIO(response.text))
            else:
                df_codones = pd.read_csv(resultados.get('codon_csv_path'))
            
            st.dataframe(df_codones.head(15), use_container_width=True)
            
            csv_codones = df_codones.to_csv(index=False)
            st.download_button(
                label="📥 Descargar Codones",
                data=csv_codones,
                file_name="codones.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"Error cargando datos de codones: {e}")
    
    # Gráficos rápidos
    images = resultados.get('images', [])
    mostrar_graficos_rapidos_con_descripciones(images)

def main():
    """Aplicación principal ultra rápida con cache"""
    init_session_state()
    
    # Header rápido
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
    
    st.markdown('<div class="main-header">SalmoAvianLight Turbo</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheader">Análisis Ultra Rápido de Secuencias Genéticas</div>', unsafe_allow_html=True)
    
    # Indicadores de velocidad
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("⚡ Procesamiento Turbo")
    with col2:
        st.info("🚀 Resultados Inmediatos")
    with col3:
        st.info("💾 Optimizado con Cache")
    
    # Sección 1: Carga ultrarrápida
    st.markdown('<div class="section-header">📁 Carga Rápida de Archivos FASTA</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Salmonella")
        salmonella_file = st.file_uploader(
            "Selecciona el archivo FASTA de Salmonella",
            type=['fa', 'fasta'],
            key="salmonella_fast"
        )
        if salmonella_file:
            es_valido, mensaje = validar_archivo_fasta_rapido(salmonella_file)
            if es_valido:
                tamaño_mb = salmonella_file.size / (1024 * 1024)
                st.success(f"✅ {salmonella_file.name} ({tamaño_mb:.1f}MB)")
            else:
                st.error(f"❌ {mensaje}")
    
    with col2:
        st.subheader("Gallus")
        gallus_file = st.file_uploader(
            "Selecciona el archivo FASTA de Gallus", 
            type=['fa', 'fasta'],
            key="gallus_fast"
        )
        if gallus_file:
            es_valido, mensaje = validar_archivo_fasta_rapido(gallus_file)
            if es_valido:
                tamaño_mb = gallus_file.size / (1024 * 1024)
                st.success(f"✅ {gallus_file.name} ({tamaño_mb:.1f}MB)")
            else:
                st.error(f"❌ {mensaje}")
    
    # Sección 2: Configuración turbo
    st.markdown('<div class="section-header">⚙️ Configuración Rápida</div>', unsafe_allow_html=True)
    
    mostrar_seleccion_graficos_rapida()
    
    # Parámetros rápidos
    col1, col2, col3 = st.columns(3)
    with col1:
        min_len = st.number_input("Longitud mínima", value=0, help="Filtro rápido por longitud")
    with col2:
        limpiar_ns = st.checkbox("Limpiar Ns", value=True, help="Normalización rápida")
    with col3:
        top_codons = st.slider("Top codones", 5, 30, 15, help="Análisis de codones principales")
    
    params = {'min_len': min_len, 'limpiar_ns': limpiar_ns, 'top_codons': top_codons}
    
    # Sección 3: Ejecución turbo
    st.markdown('<div class="section-header">🚀 Ejecución Turbo</div>', unsafe_allow_html=True)
    
    ejecutar_btn = st.button(
        "EJECUTAR ANÁLISIS TURBO", 
        type="primary",
        use_container_width=True,
        disabled=not (salmonella_file and gallus_file)
    )
    
    if ejecutar_btn:
        if salmonella_file and gallus_file:
            # Limpieza rápida
            st.session_state.analysis_results = None
            st.session_state.analysis_status = None
            st.session_state.error_message = None
            
            # Ejecución turbo
            with st.spinner("🚀 Iniciando análisis turbo..."):
                if ejecutar_analisis_turbo(salmonella_file, gallus_file, params):
                    st.success("✅ Análisis iniciado correctamente")
                    st.rerun()
                else:
                    st.error(f"❌ Error al ejecutar análisis: {st.session_state.error_message}")
    
    # Sección 4: Resultados rápidos
    if st.session_state.analysis_status:
        st.markdown('<div class="section-header">📊 Progreso del Análisis</div>', unsafe_allow_html=True)
        
        status = st.session_state.analysis_status
        
        if status == 'SUBMITTED':
            st.info("⏳ Análisis en cola de procesamiento...")
        elif status == 'RUNNING':
            st.info("🔄 Procesamiento en curso...")
            st.progress(0.7)
        elif status == 'COMPLETED':
            st.success("✅ Análisis completado exitosamente!")
            
            if st.session_state.analysis_client.mode == "API" and st.session_state.job_id:
                try:
                    resultados = st.session_state.analysis_client.get_results(st.session_state.job_id)
                    st.session_state.analysis_results = resultados
                except Exception as e:
                    st.error(f"Error obteniendo resultados: {e}")
            
            if st.session_state.analysis_results:
                mostrar_resultados_turbo(st.session_state.analysis_results)
            else:
                st.warning("Los resultados no están disponibles aún.")
        
        elif status == 'FAILED':
            st.error("❌ Error en el análisis")
            if st.session_state.error_message:
                st.error(st.session_state.error_message)

if __name__ == "__main__":
    main()
