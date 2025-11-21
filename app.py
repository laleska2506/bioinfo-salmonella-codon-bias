"""
Frontend Web para SalmoAvianLight - Versión Reorganizada
Orden exacto: GF1, GF8, GF2, GF7, GF3, GF6, GF4, GF5, GF9
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

# Estilos CSS
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

# ORDEN EXACTO DE GRÁFICOS: GF1, GF8, GF2, GF7, GF3, GF6, GF4, GF5, GF9
CHART_ORDER = ["GF1", "GF8", "GF2", "GF7", "GF3", "GF6", "GF4", "GF5", "GF9"]

@st.cache_data(ttl=3600, show_spinner=False)
def get_available_charts():
    """Gráficos disponibles en el ORDEN EXACTO requerido"""
    return [
        # GF1 - Distribución GC Gallus
        {
            "id": "GF1",
            "name": "GF1 - Distribución del Contenido GC (Gallus)", 
            "category": "Composición Genómica",
            "description": "Distribución del contenido GC en Gallus",
            "fast": True,
            "desc_id": "DESCRIPCION_G1"
        },
        # GF8 - Heatmap Salmonella
        {
            "id": "GF8", 
            "name": "GF8 - Heatmap de Uso de Codones en Salmonella",
            "category": "Análisis de Codones",
            "description": "Heatmap de uso de codones específico para Salmonella",
            "fast": False,
            "desc_id": "DESCRIPCION_G8"
        },
        # GF2 - Distribución GC Salmonella
        {
            "id": "GF2",
            "name": "GF2 - Distribución del Contenido GC (Salmonella)", 
            "category": "Composición Genómica",
            "description": "Distribución del contenido GC en Salmonella",
            "fast": True,
            "desc_id": "DESCRIPCION_G2"
        },
        # GF7 - Correlación codones
        {
            "id": "GF7",
            "name": "GF7 - Correlación del Uso de Codones entre Salmonella y Gallus",
            "category": "Análisis de Codones", 
            "description": "Correlación en uso de codones entre especies",
            "fast": False,
            "desc_id": "DESCRIPCION_G7"
        },
        # GF3 - Comparativa GC
        {
            "id": "GF3",
            "name": "GF3 - Distribución del Contenido GC (Comparativa)",
            "category": "Composición Genómica", 
            "description": "Comparativa de distribución GC entre especies",
            "fast": True,
            "desc_id": "DESCRIPCION_G3"
        },
        # GF6 - Top codones
        {
            "id": "GF6",
            "name": "GF6 - Top 15 Codones Más Frecuentes (Comparación entre Especies)", 
            "category": "Análisis de Codones",
            "description": "Comparación de codones más frecuentes entre especies",
            "fast": True,
            "desc_id": "DESCRIPCION_G6"
        },
        # GF4 - Distribución acumulativa longitudes
        {
            "id": "GF4",
            "name": "GF4 - Distribución Acumulativa de Longitudes de Genes",
            "category": "Distribución de Longitudes",
            "description": "Distribución acumulativa de longitudes génicas", 
            "fast": True,
            "desc_id": "DESCRIPCION_G4"
        },
        # GF5 - Distribución general longitudes
        {
            "id": "GF5", 
            "name": "GF5 - Distribución de Longitudes de Secuencias",
            "category": "Distribución de Longitudes",
            "description": "Distribución general de longitudes de secuencias",
            "fast": True,
            "desc_id": "DESCRIPCION_G5"
        },
        # GF9 - Relación longitud-GC
        {
            "id": "GF9",
            "name": "GF9 - Relación entre Longitud y Contenido GC",
            "category": "Análisis Integrado", 
            "description": "Relación entre longitud de secuencias y contenido GC",
            "fast": True,
            "desc_id": "DESCRIPCION_G9"
        }
    ]

@st.cache_data(ttl=3600, show_spinner=False)
def get_chart_descriptions():
    """Descripciones específicas para cada gráfico"""
    return {
        "DESCRIPCION_G1": "**Distribución del Contenido GC en Gallus** - Muestra la frecuencia de los valores de contenido GC en las secuencias de Gallus. Permite identificar patrones composicionales característicos de la especie aviar y establecer comparaciones con la composición bacteriana.",
        
        "DESCRIPCION_G8": "**Heatmap de Uso de Codones en Salmonella** - Representación visual de la frecuencia de uso de cada codón en Salmonella. Los colores indican intensidad de uso, permitiendo identificar codones preferidos y patrones de uso específicos de la bacteria.",
        
        "DESCRIPCION_G2": "**Distribución del Contenido GC en Salmonella** - Analiza la composición nucleotídica de las secuencias de Salmonella. Revela sesgos genómicos característicos de bacterias y permite comparaciones directas con el contenido GC de Gallus.",
        
        "DESCRIPCION_G7": "**Correlación del Uso de Codones** - Gráfico de dispersión que compara la frecuencia de uso de cada codón entre Salmonella y Gallus. Una correlación alta indica patrones similares, mientras que baja correlación sugiere adaptaciones especie-específicas.",
        
        "DESCRIPCION_G3": "**Comparativa de Distribución GC** - Superposición de las distribuciones de contenido GC de ambas especies. Facilita la identificación visual de diferencias composicionales y patrones evolutivos divergentes.",
        
        "DESCRIPCION_G6": "**Top 15 Codones Más Frecuentes** - Comparación directa de los codones más utilizados por cada especie. Revela preferencias codonales y posibles estrategias de optimización para la expresión génica.",
        
        "DESCRIPCION_G4": "**Distribución Acumulativa de Longitudes** - Muestra la proporción acumulada de genes por debajo de cierta longitud. Útil para comprender la estructura global del tamaño génico en ambas especies.",
        
        "DESCRIPCION_G5": "**Distribución General de Longitudes** - Histograma que muestra la frecuencia de diferentes longitudes de secuencias. Identifica modas y rangos predominantes en el tamaño de genes.",
        
        "DESCRIPCION_G9": "**Relación Longitud vs Contenido GC** - Diagrama de dispersión que explora la correlación entre el tamaño de las secuencias y su composición GC. Revela si genes más largos tienden a tener composiciones específicas."
    }

def init_session_state():
    """Inicialización del estado de la sesión"""
    defaults = {
        'analysis_client': AnalysisClient(),
        'job_id': None,
        'analysis_status': None,
        'analysis_results': None,
        'last_params': None,
        'error_message': None,
        'selected_charts': [],
        'files_validated': False,
        'processing_start_time': None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

@st.cache_data(ttl=300, show_spinner=False)
def validar_archivo_fasta(archivo) -> Tuple[bool, Optional[str]]:
    """Validación rápida de archivos FASTA"""
    if archivo is None:
        return False, "Archivo requerido"
    
    nombre = archivo.name.lower()
    if not (nombre.endswith('.fa') or nombre.endswith('.fasta')):
        return False, "Extensión .fa o .fasta requerida"
    
    if archivo.size == 0:
        return False, "Archivo vacío"
    
    try:
        primeros_bytes = archivo.read(100)
        archivo.seek(0)
        if not primeros_bytes.startswith(b'>'):
            return False, "Formato FASTA inválido - debe comenzar con '>'"
        
        if b'\n>' in primeros_bytes or b'\r>' in primeros_bytes:
            return True, None
        elif b'\n' in primeros_bytes and len(primeros_bytes) > 50:
            return True, None
            
    except Exception as e:
        return False, f"Error de lectura: {str(e)}"
    
    return True, None

def mostrar_seleccion_graficos_ordenada():
    """Selección de gráficos en ORDEN EXACTO"""
    st.markdown('<div class="section-header">Selección de Gráficos para Análisis</div>', unsafe_allow_html=True)
    
    available_charts = get_available_charts()
    
    # Mostrar en el orden exacto definido
    st.markdown("**Selecciona los gráficos que deseas generar:**")
    
    # Organizar por categorías manteniendo el orden
    categorias = {}
    for chart in available_charts:
        if chart["category"] not in categorias:
            categorias[chart["category"]] = []
        categorias[chart["category"]].append(chart)
    
    for categoria, charts in categorias.items():
        st.markdown(f'**{categoria}**')
        
        # Mostrar en columnas para mejor organización visual
        cols = st.columns(2)
        for idx, chart in enumerate(charts):
            with cols[idx % 2]:
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

def ejecutar_analisis(salmonella_file, gallus_file, params: Dict):
    """Ejecuta el análisis manteniendo el orden de gráficos"""
    try:
        st.session_state.processing_start_time = time.time()
        
        # Validación de archivos
        salmonella_valido, msg_sal = validar_archivo_fasta(salmonella_file)
        gallus_valido, msg_gall = validar_archivo_fasta(gallus_file)
        
        if not salmonella_valido or not gallus_valido:
            raise ValueError(f"Salmonella: {msg_sal}, Gallus: {msg_gall}")
        
        # Información del análisis
        tamaño_sal = salmonella_file.size / (1024 * 1024)
        tamaño_gall = gallus_file.size / (1024 * 1024)
        num_charts = len(st.session_state.selected_charts)
        
        with st.status("Procesando análisis...", expanded=True) as status:
            st.write(f"**Información del análisis:**")
            st.write(f"Archivo Salmonella: {salmonella_file.name} ({tamaño_sal:.1f}MB)")
            st.write(f"Archivo Gallus: {gallus_file.name} ({tamaño_gall:.1f}MB)")
            st.write(f"Gráficos seleccionados: {num_charts}")
            
            # Leer archivos
            st.write("Procesando archivos FASTA...")
            salmonella_content = salmonella_file.getvalue()
            gallus_content = gallus_file.getvalue()
            
            # Configurar parámetros con orden específico
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
        
        # Guardar parámetros
        st.session_state.last_params = {
            'salmonella_file': salmonella_file,
            'gallus_file': gallus_file,
            'params': params
        }
        
        processing_time = time.time() - st.session_state.processing_start_time
        st.success(f"Análisis ejecutado exitosamente en {processing_time:.1f} segundos")
        return True
        
    except Exception as e:
        processing_time = time.time() - st.session_state.processing_start_time if st.session_state.processing_start_time else 0
        st.session_state.error_message = f"Error en {processing_time:.1f}s: {str(e)}"
        st.session_state.analysis_status = 'FAILED'
        st.error(f"Error: {str(e)}")
        return False

def mostrar_graficos_ordenados(images: List):
    """Muestra gráficos en el ORDEN EXACTO definido"""
    st.markdown('<div class="section-header">Resultados Gráficos Generados</div>', unsafe_allow_html=True)
    
    if not images:
        st.info("No se generaron gráficos con la configuración actual")
        return
    
    available_charts = get_available_charts()
    chart_descriptions = get_chart_descriptions()
    
    # Crear mapping de ID a información del gráfico
    chart_map = {chart["id"]: chart for chart in available_charts}
    
    # MOSTRAR EN ORDEN EXACTO: GF1, GF8, GF2, GF7, GF3, GF6, GF4, GF5, GF9
    displayed_count = 0
    
    for chart_id in CHART_ORDER:
        if chart_id in st.session_state.selected_charts:
            # Encontrar el índice correcto del gráfico en los resultados
            selected_index = st.session_state.selected_charts.index(chart_id)
            if selected_index < len(images):
                chart_info = chart_map.get(chart_id)
                image_path = images[selected_index]
                
                if chart_info:
                    with st.container():
                        st.markdown(f'<div class="chart-container">', unsafe_allow_html=True)
                        st.markdown(f'<div class="chart-title">{chart_info["name"]}</div>', unsafe_allow_html=True)
                        
                        # Mostrar gráfico
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
                        
                        # Descripción correspondiente
                        descripcion = chart_descriptions.get(chart_info["desc_id"], "Descripción no disponible.")
                        st.markdown(f'<div class="chart-description">{descripcion}</div>', unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        displayed_count += 1
    
    if displayed_count == 0:
        st.warning("Los gráficos seleccionados no están disponibles en los resultados")

def mostrar_resultados(resultados: Dict):
    """Muestra todos los resultados manteniendo el orden correcto"""
    st.markdown('<div class="section-header">Resultados del Análisis</div>', unsafe_allow_html=True)
    
    # Métricas y datos
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
    
    # Gráficos en ORDEN EXACTO
    images = resultados.get('images', [])
    mostrar_graficos_ordenados(images)

def interfaz_carga_archivos():
    """Interfaz para carga de archivos"""
    st.markdown('<div class="section-header">Carga de Archivos FASTA</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="fast-upload">', unsafe_allow_html=True)
        st.subheader("Salmonella")
        salmonella_file = st.file_uploader(
            "Archivo FASTA de Salmonella",
            type=['fa', 'fasta'],
            key="salmonella_file",
            help="Secuencias de Salmonella en formato FASTA"
        )
        if salmonella_file:
            es_valido, mensaje = validar_archivo_fasta(salmonella_file)
            if es_valido:
                tamaño_mb = salmonella_file.size / (1024 * 1024)
                st.markdown(f'<p class="upload-success">✓ Válido: {salmonella_file.name} ({tamaño_mb:.1f}MB)</p>', unsafe_allow_html=True)
            else:
                st.error(f" {mensaje}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="fast-upload">', unsafe_allow_html=True)
        st.subheader("Gallus")
        gallus_file = st.file_uploader(
            "Archivo FASTA de Gallus", 
            type=['fa', 'fasta'],
            key="gallus_file",
            help="Secuencias de Gallus en formato FASTA"
        )
        if gallus_file:
            es_valido, mensaje = validar_archivo_fasta(gallus_file)
            if es_valido:
                tamaño_mb = gallus_file.size / (1024 * 1024)
                st.markdown(f'<p class="upload-success">✓ Válido: {gallus_file.name} ({tamaño_mb:.1f}MB)</p>', unsafe_allow_html=True)
            else:
                st.error(f" {mensaje}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Validar que ambos archivos estén presentes y sean válidos
    archivos_validos = (
        salmonella_file and 
        gallus_file and 
        validar_archivo_fasta(salmonella_file)[0] and 
        validar_archivo_fasta(gallus_file)[0]
    )
    st.session_state.files_validated = archivos_validos
    
    return salmonella_file, gallus_file

def main():
    """Aplicación principal completamente reorganizada"""
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
            st.image(str(logo_path), width=150)
    
    st.markdown('<div class="main-header">SalmoAvianLight</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheader">Análisis Comparativo Salmonella vs Gallus</div>', unsafe_allow_html=True)
    
    # Sección 1: Carga de archivos
    salmonella_file, gallus_file = interfaz_carga_archivos()
    
    # Sección 2: Configuración de análisis
    st.markdown('<div class="section-header">Configuración del Análisis</div>', unsafe_allow_html=True)
    
    mostrar_seleccion_graficos_ordenada()
    
    # Parámetros de análisis
    col1, col2, col3 = st.columns(3)
    with col1:
        min_len = st.number_input("Longitud mínima", value=0, help="Filtrar secuencias muy cortas")
    with col2:
        limpiar_ns = st.checkbox("Limpiar secuencias con Ns", value=True, help="Remover secuencias ambiguas")
    with col3:
        top_codons = st.slider("Top codones a analizar", 5, 30, 15, help="Número de codones principales")
    
    params = {
        'min_len': min_len, 
        'limpiar_ns': limpiar_ns, 
        'top_codons': top_codons
    }
    
    # Sección 3: Ejecución
    st.markdown('<div class="section-header">Ejecución del Análisis</div>', unsafe_allow_html=True)
    
    archivos_listos = st.session_state.files_validated
    ejecutar_btn = st.button(
        "🚀 EJECUTAR ANÁLISIS COMPLETO", 
        type="primary",
        use_container_width=True,
        disabled=not archivos_listos,
        help="Iniciar análisis con la configuración actual" if archivos_listos else "Carga ambos archivos FASTA válidos primero"
    )
    
    if ejecutar_btn and archivos_listos:
        st.session_state.analysis_results = None
        st.session_state.analysis_status = None
        st.session_state.error_message = None
        
        if ejecutar_analisis(salmonella_file, gallus_file, params):
            st.rerun()
    
    # Sección 4: Resultados
    if st.session_state.analysis_status:
        st.markdown('<div class="section-header">Estado del Análisis</div>', unsafe_allow_html=True)
        
        status = st.session_state.analysis_status
        
        if status == 'SUBMITTED':
            st.info("⏳ Análisis en cola de procesamiento...")
            st.progress(0.3)
        elif status == 'RUNNING':
            st.info("🔬 Procesamiento en curso...")
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
                mostrar_resultados(st.session_state.analysis_results)
        
        elif status == 'FAILED':
            st.error("Error en el análisis")
            if st.session_state.error_message:
                st.error(st.session_state.error_message)

if __name__ == "__main__":
    main()
