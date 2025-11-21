"""
Frontend Web para SalmoAvianLight - Versión Corregida
Descripciones precisas para cada gráfico generado
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

# Configuración de la página
st.set_page_config(
    page_title="SalmoAvianLight",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS profesionales
st.markdown("""
    <style>
    /* Estilo para centrar el logo */
    .logo-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        margin: 0 auto;
        padding: 0;
    }
    .logo-wrapper img {
        display: block;
        margin: 0 auto;
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
    /* Asegurar que el logo esté centrado incluso con el padding de Streamlit */
    div[data-testid="stMarkdownContainer"]:has(.logo-wrapper) {
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Inicialización del session state
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
if 'selected_charts' not in st.session_state:
    st.session_state.selected_charts = []

# Configuración de gráficos disponibles con descripciones técnicas CORREGIDAS
AVAILABLE_CHARTS = [
    {
        "id": "histograma_longitud",
        "name": "Histograma de Longitudes",
        "category": "Distribuciones Básicas",
        "description": "Distribución de frecuencias de longitudes de secuencias",
        "technical_description": "Este histograma muestra la distribución de longitudes de las secuencias genéticas analizadas. Cada barra representa la cantidad de secuencias que caen dentro de un rango específico de longitud. La altura de las barras indica la frecuencia relativa. Una distribución normal sugiere homogeneidad en el tamaño de las secuencias, mientras que múltiples picos pueden indicar la presencia de diferentes tipos de secuencias o fragmentos. Los valores atípicos aparecen como barras aisladas en los extremos del gráfico."
    },
    {
        "id": "distribucion_gc",
        "name": "Distribución de Contenido GC", 
        "category": "Distribuciones Básicas",
        "description": "Distribución del porcentaje de contenido GC en las secuencias",
        "technical_description": "Este gráfico de densidad muestra la distribución del contenido de guanina y citosina en las secuencias analizadas. La curva representa la frecuencia relativa de secuencias con diferentes porcentajes de composición GC. Un pico pronunciado indica que la mayoría de las secuencias tienen un contenido GC similar, mientras que una distribución amplia sugiere variabilidad composicional. Valores típicos para bacterias como Salmonella suelen estar entre 50-55%, mientras que Gallus puede mostrar diferentes patrones."
    },
    {
        "id": "frecuencia_codones",
        "name": "Frecuencia de Uso de Codones",
        "category": "Análisis de Codones", 
        "description": "Frecuencia relativa de uso de cada codón en las secuencias",
        "technical_description": "Este gráfico de barras muestra la frecuencia de uso de cada uno de los 64 codones posibles en el conjunto de secuencias analizado. Cada barra representa un codón específico y su altura indica qué tan frecuentemente aparece en las secuencias. Codones con frecuencias notablemente más altas pueden indicar preferencias de uso específicas de la especie. Patrones similares entre Salmonella y Gallus sugieren conservación evolutiva, mientras diferencias marcadas pueden reflejar adaptaciones específicas."
    },
    {
        "id": "comparativa_codones",
        "name": "Comparativa de Uso de Codones",
        "category": "Análisis de Codones",
        "description": "Comparación del uso de codones entre las dos especies",
        "technical_description": "Este gráfico de barras comparativas muestra las diferencias en el uso de codones entre Salmonella y Gallus. Para cada codón, se muestran dos barras adyacentes que representan su frecuencia en cada especie. Esto permite identificar visualmente codones que son preferidos por una especie sobre la otra. Diferencias significativas pueden indicar adaptaciones evolutivas, presiones de selección diferentes o optimizaciones traducionales específicas de cada organismo."
    },
    {
        "id": "correlacion_codones", 
        "name": "Correlación de Uso de Codones",
        "category": "Análisis de Codones",
        "description": "Análisis de correlación en el uso de codones entre especies",
        "technical_description": "Este gráfico de dispersión examina la relación entre los patrones de uso de codones de Salmonella y Gallus. Cada punto representa un codón específico, con su posición en el eje X mostrando su frecuencia en Salmonella y en el eje Y su frecuencia en Gallus. Puntos cercanos a la línea diagonal indican uso similar entre especies, mientras desviaciones sugieren diferencias en preferencias. Una correlación fuerte sugiere conservación evolutiva en el uso de codones."
    },
    {
        "id": "boxplot_longitud",
        "name": "Distribución de Longitudes por Especie", 
        "category": "Comparativas Estadísticas",
        "description": "Comparación de distribuciones de longitud mediante diagramas de caja",
        "technical_description": "Este diagrama de cajas compara las distribuciones de longitud de secuencias entre Salmonella y Gallus. Cada caja muestra la mediana (línea central), los cuartiles 25% y 75% (extremos de la caja), y el rango de valores normales (bigotes). Cajas que se superponen indican similitud en las distribuciones de longitud, mientras cajas separadas sugieren diferencias significativas. Valores atípicos individuales representan secuencias con longitudes excepcionales."
    }
]

# Diccionario rápido de descripciones CORREGIDO
CHART_DESCRIPTIONS = {chart["id"]: chart["technical_description"] for chart in AVAILABLE_CHARTS}

def validar_archivo_fasta(archivo) -> Tuple[bool, Optional[str]]:
    """Validación eficiente de archivos FASTA."""
    if archivo is None:
        return False, "Por favor, sube un archivo FASTA"
    
    nombre_archivo = archivo.name.lower()
    if not (nombre_archivo.endswith('.fa') or nombre_archivo.endswith('.fasta')):
        return False, "El archivo debe tener extensión .fa o .fasta"
    
    if archivo.size == 0:
        return False, "El archivo está vacío"
    
    try:
        primeros_bytes = archivo.read(100)
        archivo.seek(0)
        if not primeros_bytes.startswith(b'>'):
            return False, "El archivo no parece ser un FASTA válido (debe empezar con '>')"
    except Exception as e:
        return False, f"Error al leer el archivo: {str(e)}"
    
    return True, None

def mostrar_seleccion_graficos():
    """Interfaz de selección de gráficos organizada por categorías."""
    st.markdown('<div class="section-header">Selección de Gráficos para Análisis</div>', unsafe_allow_html=True)
    st.markdown("Selecciona los tipos de gráficos que deseas incluir en el análisis:")
    
    # Inicializar selección si está vacía
    if not st.session_state.selected_charts:
        st.session_state.selected_charts = [chart["id"] for chart in AVAILABLE_CHARTS]
    
    # Organizar por categorías
    categorias = {}
    for chart in AVAILABLE_CHARTS:
        if chart["category"] not in categorias:
            categorias[chart["category"]] = []
        categorias[chart["category"]].append(chart)
    
    # Mostrar selección por categorías
    for categoria, charts in categorias.items():
        st.markdown(f'<div class="category-header">{categoria}</div>', unsafe_allow_html=True)
        
        cols = st.columns(3)
        col_idx = 0
        
        for chart in charts:
            with cols[col_idx]:
                selected = st.checkbox(
                    f"**{chart['name']}**",
                    value=chart["id"] in st.session_state.selected_charts,
                    key=f"chart_{chart['id']}",
                    help=chart["description"]
                )
                
                if selected and chart["id"] not in st.session_state.selected_charts:
                    st.session_state.selected_charts.append(chart["id"])
                elif not selected and chart["id"] in st.session_state.selected_charts:
                    st.session_state.selected_charts.remove(chart["id"])
            
            col_idx = (col_idx + 1) % 3
        
        st.markdown("---")

def procesamiento_paralelo_archivos(salmonella_file, gallus_file):
    """Procesamiento paralelo de archivos para mayor velocidad."""
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_sal = executor.submit(procesar_archivo_individual, salmonella_file)
            future_gall = executor.submit(procesar_archivo_individual, gallus_file)
            
            salmonella_content = future_sal.result(timeout=30)
            gallus_content = future_gall.result(timeout=30)
        
        return salmonella_content, gallus_content
        
    except concurrent.futures.TimeoutError:
        raise Exception("Timeout en el procesamiento de archivos")
    except Exception as e:
        raise Exception(f"Error en procesamiento paralelo: {str(e)}")

def procesar_archivo_individual(file):
    """Procesa un archivo individual de manera eficiente."""
    return file.read()

def ejecutar_analisis_optimizado(salmonella_file, gallus_file, params: Dict):
    """Ejecuta el análisis de manera optimizada."""
    try:
        # Validación rápida
        salmonella_valido, msg_sal = validar_archivo_fasta(salmonella_file)
        gallus_valido, msg_gall = validar_archivo_fasta(gallus_file)
        
        if not salmonella_valido or not gallus_valido:
            raise ValueError(f"Salmonella: {msg_sal}, Gallus: {msg_gall}")
        
        # Información del análisis
        tamaño_sal = salmonella_file.size / (1024 * 1024)
        tamaño_gall = gallus_file.size / (1024 * 1024)
        num_charts = len(st.session_state.selected_charts)
        
        st.write(f"**Información del análisis:**")
        st.write(f"- Archivo Salmonella: {salmonella_file.name} ({tamaño_sal:.1f} MB)")
        st.write(f"- Archivo Gallus: {gallus_file.name} ({tamaño_gall:.1f} MB)")
        st.write(f"- Gráficos seleccionados: {num_charts}")
        
        # Procesamiento optimizado
        with st.spinner("Procesando archivos FASTA..."):
            salmonella_content, gallus_content = procesamiento_paralelo_archivos(
                salmonella_file, gallus_file
            )
        
        # Configurar parámetros
        params['selected_charts'] = st.session_state.selected_charts
        
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
        
        # Guardar estado
        st.session_state.last_params = {
            'salmonella_file': salmonella_file,
            'gallus_file': gallus_file,
            'params': params
        }
        
        st.session_state.last_used_params = params.copy()
        
        # Historial
        st.session_state.execution_history.append({
            'job_id': st.session_state.job_id or 'LOCAL',
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'status': st.session_state.analysis_status
        })
        
        return True
        
    except Exception as e:
        st.session_state.error_message = str(e)
        st.session_state.analysis_status = 'FAILED'
        st.error(f"Error en el análisis: {str(e)}")
        return False

def mostrar_graficos_con_descripciones(images: List):
    """Muestra los gráficos con sus descripciones técnicas CORREGIDAS."""
    st.markdown('<div class="section-header">Resultados Gráficos</div>', unsafe_allow_html=True)
    
    if not images:
        st.info("No se generaron gráficos con la configuración actual")
        return
    
    # Crear mapeo CORRECTO entre imágenes y gráficos seleccionados
    chart_image_mapping = {}
    for i, chart_id in enumerate(st.session_state.selected_charts):
        if i < len(images):
            chart_image_mapping[chart_id] = images[i]
    
    # Organizar por categorías para mejor presentación
    categorias = {}
    for chart_id in st.session_state.selected_charts:
        if chart_id not in chart_image_mapping:
            continue
            
        chart_info = next((c for c in AVAILABLE_CHARTS if c["id"] == chart_id), None)
        if chart_info:
            categoria = chart_info["category"]
            if categoria not in categorias:
                categorias[categoria] = []
            categorias[categoria].append((chart_info, chart_image_mapping[chart_id]))
    
    # Mostrar por categorías
    for categoria, charts in categorias.items():
        st.subheader(categoria)
        
        for chart_info, image_path in charts:
            with st.container():
                st.markdown(f'<div class="chart-container">', unsafe_allow_html=True)
                st.markdown(f'<div class="chart-title">{chart_info["name"]}</div>', unsafe_allow_html=True)
                
                # Dos columnas: gráfico y descripción
                col_grafico, col_desc = st.columns([1, 1])
                
                with col_grafico:
                    try:
                        if st.session_state.analysis_client.mode == "API":
                            import requests
                            response = requests.get(image_path, timeout=10)
                            st.image(response.content, use_container_width=True)
                        else:
                            if Path(image_path).exists():
                                st.image(image_path, use_container_width=True)
                        st.caption(f"Gráfico: {chart_info['name']}")
                    except Exception as e:
                        st.error(f"Error al cargar el gráfico: {e}")
                
                with col_desc:
                    descripcion = CHART_DESCRIPTIONS.get(chart_info["id"], "Descripción no disponible.")
                    st.markdown(f'<div class="chart-description">{descripcion}</div>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)

def mostrar_resultados_completos(resultados: Dict):
    """Muestra todos los resultados del análisis."""
    st.markdown('<div class="section-header">Resultados del Análisis</div>', unsafe_allow_html=True)
    
    # Métricas y datos tabulares
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
            
            st.dataframe(df_metricas.head(30), use_container_width=True)
            
            csv_metricas = df_metricas.to_csv(index=False)
            st.download_button(
                label="Descargar Resumen de Métricas",
                data=csv_metricas,
                file_name="resumen_metricas.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"Error al cargar métricas: {e}")
    
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
            
            st.dataframe(df_codones.head(30), use_container_width=True)
            
            csv_codones = df_codones.to_csv(index=False)
            st.download_button(
                label="Descargar Uso de Codones",
                data=csv_codones,
                file_name="codon_usage.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"Error al cargar datos de codones: {e}")
    
    # Gráficos con descripciones CORREGIDAS
    images = resultados.get('images', [])
    mostrar_graficos_con_descripciones(images)
    
    # Descarga completa
    st.subheader("Descarga de Resultados Completos")
    try:
        if st.session_state.analysis_client.mode == "API":
            zip_url = resultados.get('zip_url')
            if zip_url:
                st.markdown(f"**[Descargar archivo ZIP con todos los resultados]({zip_url})**")
        else:
            resumen_csv_path = resultados.get('resumen_csv_path')
            if resumen_csv_path:
                resultados_dir = Path(resumen_csv_path).parent
                zip_path = crear_zip_resultados(str(resultados_dir))
                
                if Path(zip_path).exists():
                    with open(zip_path, 'rb') as f:
                        st.download_button(
                            label="Descargar ZIP Completo",
                            data=f.read(),
                            file_name="resultados_analisis.zip",
                            mime="application/zip"
                        )
    except Exception as e:
        st.error(f"Error al preparar descarga: {e}")

def main():
    """Aplicación principal con selección de gráficos y logo."""
    
    # Logo centrado en la parte superior
    logo_path = Path(__file__).parent / "assets" / "logo.png"
    
    # Contenedor centrado para el logo
    if logo_path.exists():
        try:
            with open(logo_path, "rb") as img_file:
                img_data = base64.b64encode(img_file.read()).decode()
            
            # Mostrar logo centrado con HTML/CSS
            st.markdown(
                f"""
                <div style="text-align: center; width: 100%; margin: 1rem 0;">
                    <img src="data:image/png;base64,{img_data}" style="max-width: 150px; height: auto; margin: 0 auto; display: inline-block;">
                </div>
                """,
                unsafe_allow_html=True
            )
        except Exception as e:
            # Si hay error cargando la imagen, usar st.image como fallback
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                st.image(str(logo_path), width=150)
    else:
        # Si no hay logo, mostrar emoji como fallback
        st.markdown(
            "<div style='text-align: center; font-size: 3rem; margin-bottom: 1rem;'>🧬</div>", 
            unsafe_allow_html=True
        )
    
    # Título y subtítulo centrados debajo del logo
    st.markdown('<div class="main-header">SalmoAvianLight</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheader">Comparación de Secuencias: Salmonella vs Gallus</div>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; color: #888; margin-bottom: 2rem;">
    Esta herramienta te permite analizar y comparar secuencias genéticas de dos especies.<br>
    Sube tus archivos FASTA, define los parámetros y obtén resultados detallados en minutos.
    </div>
    """, unsafe_allow_html=True)
    
    # Indicador de modo
    modo = st.session_state.analysis_client.mode
    if modo == "API":
        st.info(f"Modo API: Conectado a {st.session_state.analysis_client.base_url}")
    else:
        st.info("Modo Local: Ejecutando análisis en este servidor")
    
    # Sección 1: Carga de archivos
    st.markdown('<div class="section-header">Carga de Archivos FASTA</div>', unsafe_allow_html=True)
    
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
            es_valido, mensaje = validar_archivo_fasta(salmonella_file)
            if not es_valido:
                st.error(f"Error: {mensaje}")
            else:
                st.success(f"Archivo válido: {salmonella_file.name} ({tamaño_mb:.1f} MB)")
    
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
            es_valido, mensaje = validar_archivo_fasta(gallus_file)
            if not es_valido:
                st.error(f"Error: {mensaje}")
            else:
                st.success(f"Archivo válido: {gallus_file.name} ({tamaño_mb:.1f} MB)")
    
    # Sección 2: Selección de gráficos
    mostrar_seleccion_graficos()
    
    # Sección 3: Parámetros de análisis
    st.markdown('<div class="section-header">Parámetros de Análisis</div>', unsafe_allow_html=True)
    
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
            "Top codones para análisis",
            min_value=5,
            max_value=30,
            value=20,
            step=1,
            help="Número de codones a incluir en análisis comparativos"
        )
    
    params = {
        'limpiar_ns': limpiar_ns,
        'min_len': min_len,
        'top_codons': top_codons
    }
    
    # Sección 4: Ejecución
    st.markdown('<div class="section-header">Ejecución del Análisis</div>', unsafe_allow_html=True)
    
    ejecutar_btn = st.button(
        "Ejecutar Análisis",
        type="primary",
        use_container_width=True,
        disabled=(salmonella_file is None or gallus_file is None)
    )
    
    if ejecutar_btn:
        if salmonella_file and gallus_file:
            # Validación final
            salmonella_valido, msg_sal = validar_archivo_fasta(salmonella_file)
            gallus_valido, msg_gall = validar_archivo_fasta(gallus_file)
            
            if not salmonella_valido:
                st.error(f"Error en archivo Salmonella: {msg_sal}")
            elif not gallus_valido:
                st.error(f"Error en archivo Gallus: {msg_gall}")
            else:
                # Limpiar estado anterior
                st.session_state.analysis_results = None
                st.session_state.analysis_status = None
                st.session_state.error_message = None
                
                # Ejecutar análisis
                with st.spinner("Iniciando análisis..."):
                    if ejecutar_analisis_optimizado(salmonella_file, gallus_file, params):
                        st.success("Análisis iniciado correctamente")
                        st.rerun()
                    else:
                        st.error(f"Error al ejecutar análisis: {st.session_state.error_message}")
    
    # Sección 5: Resultados
    if st.session_state.analysis_status:
        st.markdown('<div class="section-header">Estado del Análisis</div>', unsafe_allow_html=True)
        
        status = st.session_state.analysis_status
        
        if status == 'SUBMITTED':
            st.info("Análisis enviado. Esperando procesamiento...")
        
        elif status == 'RUNNING':
            st.info("Análisis en progreso...")
            st.progress(0.5)
        
        elif status == 'COMPLETED':
            st.success("Análisis completado exitosamente")
            
            # Obtener resultados si estamos en modo API
            if st.session_state.analysis_client.mode == "API" and st.session_state.job_id:
                try:
                    resultados = st.session_state.analysis_client.get_results(st.session_state.job_id)
                    st.session_state.analysis_results = resultados
                except Exception as e:
                    st.error(f"Error al obtener resultados: {e}")
                    st.session_state.analysis_results = None
            
            # Mostrar resultados
            if st.session_state.analysis_results:
                mostrar_resultados_completos(st.session_state.analysis_results)
            else:
                st.warning("Los resultados no están disponibles aún.")
        
        elif status == 'FAILED':
            st.error("El análisis falló")
            if st.session_state.error_message:
                st.error(f"Error: {st.session_state.error_message}")
            
            if st.session_state.last_params:
                if st.button("Reintentar análisis"):
                    st.session_state.analysis_status = None
                    st.session_state.error_message = None
                    st.rerun()
    
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
