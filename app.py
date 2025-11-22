"""
Frontend Web para SalmoAvianLight 
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

# MAESTRO DE GRÁFICOS - COINCIDENCIA EXACTA CON visualizacion.py 
CHART_MASTER = {
    "distribucion_longitudes": {
        "id": "GF5",
        "name": "Distribución de Longitudes de Secuencias",
        "category": "Distribuciones Básicas",
        "description": "Histograma de distribución de longitudes de secuencias",
        "filename": "distribucion_longitudes.png",
        "desc_id": "DESC_GF5"
    },
    "distribucion_gc": {
        "id": "GF3", 
        "name": "Distribución del Contenido de GC",
        "category": "Distribuciones Básicas",
        "description": "Distribución general del contenido GC",
        "filename": "distribucion_gc.png",
        "desc_id": "DESC_GF3"
    },
    "relacion_longitud_gc": {
        "id": "GF9",
        "name": "Relación entre Longitud y Contenido de GC", 
        "category": "Análisis de Relaciones",
        "description": "Gráfico de dispersión entre longitud y contenido GC",
        "filename": "relacion_longitud_gc.png",
        "desc_id": "DESC_GF9"
    },
    "uso_codones_top20": {
        "id": "GF6",
        "name": "Top 20 Codones Más Frecuentes",
        "category": "Análisis de Codones",
        "description": "Comparación de los 20 codones más frecuentes entre especies",
        "filename": "uso_codones_top20.png", 
        "desc_id": "DESC_GF6"
    },
    "correlacion_codones": {
        "id": "GF7",
        "name": "Correlación del Uso de Codones",
        "category": "Análisis de Codones",
        "description": "Correlación entre uso de codones de Salmonella y Gallus",
        "filename": "correlacion_codones.png",
        "desc_id": "DESC_GF7"
    },
    "heatmap_codones": {
        "id": "GF8",
        "name": "Heatmap de Uso de Codones en Salmonella", 
        "category": "Análisis de Codones",
        "description": "Heatmap organizado por familias de codones",
        "filename": "heatmap_codones.png",
        "desc_id": "DESC_GF8"
    },
    "distribucion_acumulativa_longitudes": {
        "id": "GF4",
        "name": "Distribución Acumulativa de Longitudes de Genes",
        "category": "Distribuciones Avanzadas", 
        "description": "Distribución acumulativa con percentiles marcados",
        "filename": "distribucion_acumulativa_longitudes.png",
        "desc_id": "DESC_GF4"
    },
    "gallus_gc": {
        "id": "GF1",
        "name": "Distribución del Contenido GC (Gallus)",
        "category": "Distribuciones por Especie", 
        "description": "Distribución específica de contenido GC en Gallus",
        "filename": "gallus_gc.png",
        "desc_id": "DESC_GF1"
    },
    "salmonella_gc": {
        "id": "GF2",
        "name": "Distribución del Contenido GC (Salmonella)",
        "category": "Distribuciones por Especie",
        "description": "Distribución específica de contenido GC en Salmonella", 
        "filename": "salmonella_gc.png",
        "desc_id": "DESC_GF2"
    }
}

@st.cache_data(ttl=3600, show_spinner=False)
def get_available_charts():
    """Gráficos disponibles que COINCIDEN EXACTAMENTE con visualizacion.py"""
    return list(CHART_MASTER.values())

@st.cache_data(ttl=3600, show_spinner=False)
def get_chart_descriptions():
    """Descripciones que coinciden con los gráficos reales generados"""
    return {
        "DESC_GF1": "Distribución del Contenido GC en Gallus - Muestra la frecuencia de los valores de contenido GC específicamente en las secuencias de Gallus. Permite identificar patrones composicionales característicos de la especie aviar, mostrando si existe un rango preferido de contenido GC y la variabilidad composicional del genoma.",
        
        "DESC_GF2": "Distribución del Contenido GC en Salmonella - Analiza la composición nucleotídica específica de las secuencias de Salmonella. Revela sesgos genómicos característicos de bacterias y permite identificar la distribución particular del contenido GC en este organismo, mostrando posibles adaptaciones evolutivas en su composición genética.",
        
        "DESC_GF3": "Distribución General del Contenido GC - Histograma que muestra la distribución global del contenido GC combinando ambas especies. Proporciona una visión general de la composición nucleotídica del conjunto de datos completo, identificando modas y rangos predominantes de contenido GC sin distinción de especie.",
        
        "DESC_GF4": "Distribución Acumulativa de Longitudes de Genes - Gráfico de distribución acumulativa que muestra la proporción de genes por debajo de cierta longitud. Incluye marcadores de percentiles (25%, 50%, 75%, 90%) que permiten identificar valores de referencia para el tamaño génico en el conjunto de datos analizado.",
        
        "DESC_GF5": "Distribución de Longitudes de Secuencias - Histograma detallado de la distribución de longitudes de todas las secuencias analizadas. Muestra la frecuencia de diferentes tamaños de genes, permitiendo identificar si existen picos específicos, distribución normal o sesgos en el tamaño de las secuencias génicas.",
        
        "DESC_GF6": "Top 20 Codones Más Frecuentes - Gráfico de barras comparativo que muestra los 20 codones con mayor frecuencia de uso en ambas especies. Permite identificar visualmente las preferencias codonales de cada organismo y comparar directamente cuáles codones son más utilizados en Salmonella versus Gallus.",
        
        "DESC_GF7": "Correlación del Uso de Codones - Gráfico de dispersión que compara la frecuencia de uso de cada codón entre Salmonella y Gallus. La línea diagonal representa la correlación perfecta. Permite evaluar si existen patrones de uso similares o divergentes entre las especies a nivel de cada codón específico.",
        
        "DESC_GF8": "Heatmap de Uso de Codones en Salmonella - Representación matricial del uso de codones organizado por familias. El mapa de calor utiliza colores para indicar la intensidad de uso de cada codón, permitiendo identificar patrones grupales y preferencias en la utilización del código genético en Salmonella.",
        
        "DESC_GF9": "Relación entre Longitud y Contenido GC - Diagrama de dispersión que explora la posible correlación entre el tamaño de las secuencias y su composición GC. Utiliza densidad de color para mostrar concentraciones de puntos, revelando si genes más largos tienden a tener composiciones GC específicas o si no existe relación aparente."
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
    """
    Validación mejorada de archivos FASTA.
    
    Verifica:
    - Que el archivo no sea None
    - Que tenga extensión .fa o .fasta
    - Que no esté vacío
    - Que tenga el formato FASTA básico (comience con '>')
    - Que tenga al menos una secuencia válida
    """
    if archivo is None:
        return False, "❌ Archivo requerido"
    
    nombre = archivo.name.lower()
    if not (nombre.endswith('.fa') or nombre.endswith('.fasta')):
        return False, "❌ El archivo debe tener extensión .fa o .fasta"
    
    if archivo.size == 0:
        return False, "❌ El archivo está vacío"
    
    try:
        # Leer los primeros bytes para validar formato básico
        archivo.seek(0)
        primeros_bytes = archivo.read(1000)  # Leer más bytes para mejor validación
        archivo.seek(0)
        
        # Verificar que comience con '>'
        if not primeros_bytes.startswith(b'>'):
            return False, "❌ Formato FASTA inválido: el archivo debe comenzar con '>' (cabecera de secuencia)"
        
        # Verificar que tenga al menos una secuencia completa
        # Buscar patrón: '>' seguido de texto y luego nueva línea con secuencia
        contenido_str = primeros_bytes.decode('utf-8', errors='ignore')
        
        # Verificar que haya al menos un salto de línea después de la primera cabecera
        if b'\n' not in primeros_bytes and b'\r\n' not in primeros_bytes:
            if len(primeros_bytes) < 50:
                return False, "❌ El archivo parece estar incompleto o corrupto. Verifique que tenga el formato FASTA correcto."
        
        # Verificar que haya al menos una secuencia (buscar múltiples '>')
        num_cabeceras = primeros_bytes.count(b'>')
        if num_cabeceras == 0:
            return False, "❌ No se encontraron secuencias FASTA válidas en el archivo"
        
        # Verificar que no sea solo texto sin secuencias
        # Un FASTA válido debe tener: '>ID\n' seguido de caracteres de secuencia
        lineas = contenido_str.split('\n', 3)
        if len(lineas) < 2:
            return False, "❌ El archivo FASTA parece estar incompleto. Debe tener al menos una cabecera y una secuencia."
        
        # Verificar que la segunda línea (secuencia) tenga caracteres válidos
        if len(lineas) >= 2 and len(lineas[1].strip()) == 0:
            return False, "❌ El archivo FASTA tiene una cabecera pero la secuencia está vacía"
            
    except UnicodeDecodeError:
        return False, "❌ Error: el archivo contiene caracteres no válidos. Verifique que sea un archivo de texto FASTA."
    except Exception as e:
        return False, f"❌ Error al leer el archivo: {str(e)}. El archivo puede estar corrupto."
    
    return True, None

def mostrar_seleccion_graficos():
    """Selección de gráficos sin prefijos GF"""
    st.markdown('<div class="section-header">Selección de Gráficos para Análisis</div>', unsafe_allow_html=True)
    
    available_charts = get_available_charts()
    
    # Organizar por categorías
    categorias = {}
    for chart in available_charts:
        if chart["category"] not in categorias:
            categorias[chart["category"]] = []
        categorias[chart["category"]].append(chart)
    
    # Mostrar por categorías
    for categoria, charts in categorias.items():
        st.markdown(f'**{categoria}**')
        
        for chart in charts:
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
    """Ejecuta el análisis y genera gráficos que COINCIDEN con visualizacion.py"""
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
            st.write(f"Información del análisis:")
            st.write(f"Archivo Salmonella: {salmonella_file.name} ({tamaño_sal:.1f}MB)")
            st.write(f"Archivo Gallus: {gallus_file.name} ({tamaño_gall:.1f}MB)")
            st.write(f"Gráficos seleccionados: {num_charts}")
            
            # Leer archivos
            st.write("Procesando archivos FASTA...")
            salmonella_content = salmonella_file.getvalue()
            gallus_content = gallus_file.getvalue()
            
            # Configurar parámetros
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
        
    except ValueError as e:
        # Errores de validación de archivos (formato, corrupto, etc.)
        processing_time = time.time() - st.session_state.processing_start_time if st.session_state.processing_start_time else 0
        error_msg = str(e)
        
        # Mensajes más descriptivos según el tipo de error
        if "FASTA" in error_msg or "corrupto" in error_msg.lower() or "formato" in error_msg.lower():
            mensaje_usuario = f"❌ Error en el archivo FASTA: {error_msg}"
        elif "caracteres inválidos" in error_msg.lower():
            mensaje_usuario = f"❌ El archivo contiene caracteres inválidos: {error_msg}"
        elif "vacío" in error_msg.lower() or "empty" in error_msg.lower():
            mensaje_usuario = f"❌ El archivo está vacío o no contiene secuencias: {error_msg}"
        else:
            mensaje_usuario = f"❌ Error de validación: {error_msg}"
        
        st.session_state.error_message = f"Error en {processing_time:.1f}s: {mensaje_usuario}"
        st.session_state.analysis_status = 'FAILED'
        st.error(mensaje_usuario)
        return False
    except FileNotFoundError as e:
        processing_time = time.time() - st.session_state.processing_start_time if st.session_state.processing_start_time else 0
        mensaje_usuario = f"❌ Archivo no encontrado: {str(e)}"
        st.session_state.error_message = f"Error en {processing_time:.1f}s: {mensaje_usuario}"
        st.session_state.analysis_status = 'FAILED'
        st.error(mensaje_usuario)
        return False
    except MemoryError as e:
        processing_time = time.time() - st.session_state.processing_start_time if st.session_state.processing_start_time else 0
        mensaje_usuario = f"❌ Error de memoria: Los archivos son demasiado grandes para procesar. {str(e)}"
        st.session_state.error_message = f"Error en {processing_time:.1f}s: {mensaje_usuario}"
        st.session_state.analysis_status = 'FAILED'
        st.error(mensaje_usuario)
        return False
    except Exception as e:
        processing_time = time.time() - st.session_state.processing_start_time if st.session_state.processing_start_time else 0
        error_msg = str(e)
        
        # Detectar errores comunes y proporcionar mensajes más claros
        if "FASTA" in error_msg or "parse" in error_msg.lower() or "corrupto" in error_msg.lower():
            mensaje_usuario = f"❌ Error al procesar el archivo FASTA (archivo posiblemente corrupto): {error_msg}"
        elif "comunicarse con el backend" in error_msg.lower():
            mensaje_usuario = f"❌ Error de conexión con el servidor: {error_msg}"
        else:
            mensaje_usuario = f"❌ Error durante el análisis: {error_msg}"
        
        st.session_state.error_message = f"Error en {processing_time:.1f}s: {mensaje_usuario}"
        st.session_state.analysis_status = 'FAILED'
        st.error(mensaje_usuario)
        return False

def mostrar_graficos_correspondientes(resultados: Dict):
    """Muestra gráficos sin prefijos GF en los títulos"""
    st.markdown('<div class="section-header">Resultados Gráficos Generados</div>', unsafe_allow_html=True)
    
    available_charts = get_available_charts()
    chart_descriptions = get_chart_descriptions()
    
    # Crear mapping de ID a información del gráfico
    chart_map = {chart["id"]: chart for chart in available_charts}
    
    # Para cada gráfico seleccionado, mostrar la imagen correspondiente
    for chart_id in st.session_state.selected_charts:
        chart_info = chart_map.get(chart_id)
        if not chart_info:
            continue
            
        # Encontrar el nombre del archivo correspondiente
        filename = chart_info["filename"]
        
        with st.container():
            st.markdown(f'<div class="chart-container">', unsafe_allow_html=True)
            st.markdown(f'<div class="chart-title">{chart_info["name"]}</div>', unsafe_allow_html=True)  # Sin prefijo GF
            
            # Mostrar gráfico - buscar la imagen en los resultados
            try:
                image_found = False
                
                if st.session_state.analysis_client.mode == "API":
                    # En modo API, buscar en las URLs de resultados
                    images = resultados.get('images', [])
                    for img_url in images:
                        if filename in img_url:
                            import requests
                            response = requests.get(img_url, timeout=10)
                            if response.status_code == 200:
                                st.image(response.content, use_container_width=True)
                                image_found = True
                                break
                else:
                    # En modo local, buscar en el sistema de archivos
                    image_path = Path("results/graficos") / filename
                    if image_path.exists():
                        st.image(str(image_path), use_container_width=True)
                        image_found = True
                
                if not image_found:
                    st.warning(f"Gráfico no generado: {filename}")
                    
            except Exception as e:
                st.error(f"Error cargando gráfico {chart_info['name']}: {e}")
            
            # Descripción correspondiente
            descripcion = chart_descriptions.get(chart_info["desc_id"], "Descripción no disponible.")
            st.markdown(f'<div class="chart-description">{descripcion}</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

def mostrar_resultados(resultados: Dict):
    """Muestra todos los resultados con gráficos sin prefijos GF"""
    st.markdown('<div class="section-header">Resultados del Análisis</div>', unsafe_allow_html=True)
    
    # Métricas y datos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Resumen de Métricas")
        try:
            if st.session_state.analysis_client.mode == "API":
                import requests
                resumen_csv_url = resultados.get('resumen_csv_url')
                if resumen_csv_url:
                    response = requests.get(resumen_csv_url, timeout=10)
                    df_metricas = pd.read_csv(io.StringIO(response.text))
                else:
                    st.error("URL de métricas no disponible")
                    return
            else:
                df_metricas = pd.read_csv(resultados.get('resumen_csv_path', 'results/resumen_metricas.csv'))
            
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
                if codon_csv_url:
                    response = requests.get(codon_csv_url, timeout=10)
                    df_codones = pd.read_csv(io.StringIO(response.text))
                else:
                    st.error("URL de codones no disponible")
                    return
            else:
                df_codones = pd.read_csv(resultados.get('codon_csv_path', 'results/codon_usage.csv'))
            
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
    
    # Gráficos sin prefijos GF
    mostrar_graficos_correspondientes(resultados)

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
                st.markdown(f'<p class="upload-success"> Válido: {salmonella_file.name} ({tamaño_mb:.1f}MB)</p>', unsafe_allow_html=True)
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
                st.markdown(f'<p class="upload-success"> Válido: {gallus_file.name} ({tamaño_mb:.1f}MB)</p>', unsafe_allow_html=True)
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
    """Aplicación principal sin prefijos GF en la interfaz"""
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
    
    mostrar_seleccion_graficos()
    
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
        " EJECUTAR ANÁLISIS COMPLETO", 
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
            st.info(" Análisis en cola de procesamiento...")
            st.progress(0.3)
        elif status == 'RUNNING':
            st.info(" Procesamiento en curso...")
            st.progress(0.7)
        elif status == 'COMPLETED':
            st.success(" Análisis completado exitosamente!")
            
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
            st.error(" Error en el análisis del archivo, se han encontrado caracteres inválidos en las secuencias.")
            if st.session_state.error_message:
                st.error(st.session_state.error_message)

if __name__ == "__main__":
    main()
