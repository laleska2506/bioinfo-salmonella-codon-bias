"""
Frontend Web para SalmoAvianLight - Salmonella vs Gallus
Aplicación Streamlit mejorada con selección de gráficos y descripciones
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

# Estilos CSS personalizados mejorados
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
    /* Contenedor de gráficos con bordes */
    .chart-container {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
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
        padding: 10px;
        background-color: #f8f9fa;
        border-left: 3px solid #3498db;
        border-radius: 5px;
    }
    /* Estilos para la selección de gráficos */
    .likert-option {
        padding: 8px 12px;
        margin: 5px 0;
        border-radius: 5px;
        background-color: #f0f2f6;
        border: 1px solid #ddd;
    }
    .likert-option.selected {
        background-color: #e3f2fd;
        border-color: #2196f3;
    }
    /* Asegurar que el logo esté centrado incluso con el padding de Streamlit */
    div[data-testid="stMarkdownContainer"]:has(.logo-wrapper) {
        text-align: center;
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
if 'selected_charts' not in st.session_state:
    st.session_state.selected_charts = []

# Diccionario de descripciones para cada tipo de gráfico
CHART_DESCRIPTIONS = {
    "histograma_longitud": """
    Este histograma muestra la distribución de longitudes de secuencias. El eje horizontal representa los rangos de longitud 
    y el vertical la frecuencia. Permite identificar la longitud más común, la variabilidad y la presencia de valores atípicos. 
    Una distribución normal sugiere homogeneidad, mientras que múltiples picos indican subpoblaciones con características distintas.
    """,
    
    "distribucion_gc": """
    Este gráfico de densidad muestra la distribución del contenido GC. La curva representa la frecuencia de secuencias 
    con determinado porcentaje GC. Picos pronunciados indican concentración en valores específicos, mientras distribuciones 
    planas sugieren diversidad composicional. Modas múltiples pueden reflejar diferentes grupos genómicos.
    """,
    
    "frecuencia_codones": """
    Este gráfico de barras muestra la frecuencia relativa de cada codón. La altura de cada barra indica cuán común es 
    ese codón. Permite identificar codones preferidos y raros. Patrones similares entre especies sugieren conservación 
    evolutiva, mientras diferencias indican adaptaciones específicas.
    """,
    
    "comparativa_codones": """
    Este gráfico comparativo muestra las diferencias en uso de codones entre especies. Barras adyacentes para cada codón 
    permiten visualizar preferencias específicas. Diferencias marcadas sugieren presiones evolutivas divergentes, 
    mientras similitudes indican restricciones funcionales compartidas.
    """,
    
    "correlacion_codones": """
    Este gráfico de dispersión explora la correlación en uso de codones entre especies. Cada punto representa un codón. 
    Una nube de puntos a lo largo de la diagonal indica correlación positiva fuerte. Dispersión aleatoria sugiere 
    independencia, mientras patrones no lineales revelan relaciones complejas.
    """,
    
    "boxplot_longitud": """
    Este diagrama de cajas compara distribuciones de longitud entre especies. Cada caja muestra la mediana, cuartiles 
    y valores extremos. Cajas superpuestas indican similitud, mientras separación sugiere diferencias significativas. 
    Bigotes largos revelan alta variabilidad, puntos atípicos muestran secuencias excepcionales.
    """,
    
    "pca": """
    Este gráfico de análisis de componentes principales (PCA) reduce la dimensionalidad de datos de uso de codones. 
    Agrupamientos de puntos indican similitudes en patrones de uso. La proximidad sugiere relación evolutiva o funcional, 
    mientras la dispersión refleja diversidad. Ejes representan direcciones de máxima varianza.
    """,
    
    "heatmap": """
    Este mapa de calor muestra similitudes entre secuencias mediante gradientes de color. Tonos cálidos indican alta 
    similitud, fríos baja similitud. Patrones de bloques a lo largo de la diagonal sugieren agrupamientos naturales. 
    Permite identificar clusters y relaciones a simple vista.
    """,
    
    "scatter_gc_longitud": """
    Este gráfico de dispersión explora la relación entre contenido GC y longitud. Cada punto es una secuencia. 
    Tendencia creciente sugiere correlación positiva, decreciente negativa. Nubes sin patrón indican independencia. 
    Agrupamientos revelan subpoblaciones con características composicionales similares.
    """
}

# Configuración de gráficos disponibles
AVAILABLE_CHARTS = [
    {
        "id": "histograma_longitud",
        "name": "📊 Histograma de Longitudes",
        "category": "Básicos",
        "description": "Distribución de longitudes de secuencias"
    },
    {
        "id": "distribucion_gc", 
        "name": "🧬 Distribución GC",
        "category": "Básicos",
        "description": "Distribución del contenido de GC"
    },
    {
        "id": "frecuencia_codones",
        "name": "📈 Frecuencia de Codones", 
        "category": "Básicos",
        "description": "Frecuencia de uso de codones"
    },
    {
        "id": "comparativa_codones",
        "name": "⚖️ Comparativa de Codones",
        "category": "Comparativos", 
        "description": "Comparación de uso de codones entre especies"
    },
    {
        "id": "correlacion_codones",
        "name": "🔗 Correlación de Codones",
        "category": "Comparativos",
        "description": "Correlación en uso de codones"
    },
    {
        "id": "boxplot_longitud", 
        "name": "📦 Boxplot por Especie",
        "category": "Comparativos",
        "description": "Distribución de longitudes por especie"
    },
    {
        "id": "pca",
        "name": "🎯 Análisis PCA",
        "category": "Avanzados",
        "description": "Análisis de componentes principales"
    },
    {
        "id": "heatmap",
        "name": "🔥 Heatmap de Similitud", 
        "category": "Avanzados",
        "description": "Mapa de calor de similitudes"
    },
    {
        "id": "scatter_gc_longitud",
        "name": "💫 Scatter GC vs Longitud",
        "category": "Avanzados", 
        "description": "Relación entre GC y longitud"
    }
]


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
    
    try:
        primeros_bytes = archivo.read(100)
        archivo.seek(0)
        if not primeros_bytes.startswith(b'>'):
            return False, "El archivo no parece ser un FASTA válido (debe empezar con '>')"
    except Exception as e:
        return False, f"Error al leer el archivo: {str(e)}"
    
    return True, None


def mostrar_seleccion_graficos():
    """Muestra la interfaz de selección de gráficos tipo Likert."""
    st.markdown('<div class="section-header">📊 Selección de Gráficos</div>', unsafe_allow_html=True)
    st.markdown("Selecciona los gráficos que deseas generar:")
    
    # Inicializar selección si es necesario
    if not st.session_state.selected_charts:
        st.session_state.selected_charts = [chart["id"] for chart in AVAILABLE_CHARTS]
    
    # Organizar por categorías
    categorias = {}
    for chart in AVAILABLE_CHARTS:
        if chart["category"] not in categorias:
            categorias[chart["category"]] = []
        categorias[chart["category"]].append(chart)
    
    # Mostrar en columnas
    cols = st.columns(len(categorias))
    
    for idx, (categoria, charts) in enumerate(categorias.items()):
        with cols[idx]:
            st.subheader(f"{categoria}")
            for chart in charts:
                # Crear un key único para cada checkbox
                key = f"chart_{chart['id']}"
                selected = st.checkbox(
                    f"**{chart['name']}**",
                    value=chart["id"] in st.session_state.selected_charts,
                    key=key,
                    help=chart["description"]
                )
                
                # Actualizar la lista de selección
                if selected and chart["id"] not in st.session_state.selected_charts:
                    st.session_state.selected_charts.append(chart["id"])
                elif not selected and chart["id"] in st.session_state.selected_charts:
                    st.session_state.selected_charts.remove(chart["id"])


def ejecutar_analisis(salmonella_file, gallus_file, params: Dict):
    """Ejecuta el análisis genético."""
    try:
        if salmonella_file is None or gallus_file is None:
            raise ValueError("Ambos archivos FASTA son requeridos")
        
        # Mostrar información
        tamaño_sal = salmonella_file.size / (1024 * 1024)
        tamaño_gall = gallus_file.size / (1024 * 1024)
        
        st.write(f"🔍 **Información del análisis:**")
        st.write(f"- Archivo Salmonella: {salmonella_file.name} ({tamaño_sal:.2f} MB)")
        st.write(f"- Archivo Gallus: {gallus_file.name} ({tamaño_gall:.2f} MB)")
        st.write(f"- Gráficos seleccionados: {len(st.session_state.selected_charts)}")
        
        # Leer archivos
        with st.spinner("Leyendo archivos FASTA..."):
            salmonella_content = salmonella_file.read()
            gallus_content = gallus_file.read()
        
        # Resetear punteros
        salmonella_file.seek(0)
        gallus_file.seek(0)
        
        # Agregar gráficos seleccionados a los parámetros
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
        
        # Guardar parámetros
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
        
    except MemoryError as e:
        st.session_state.error_message = "Error de memoria: Archivo demasiado grande."
        st.session_state.analysis_status = 'FAILED'
        st.error("❌ **Error de Memoria**: Archivo demasiado grande.")
        return False
    except Exception as e:
        error_msg = str(e)
        st.session_state.error_message = error_msg
        st.session_state.analysis_status = 'FAILED'
        st.error(f"❌ **Error**: {error_msg}")
        return False


def mostrar_graficos_con_descripciones(images: List, chart_mapping: Dict):
    """Muestra los gráficos con sus descripciones en contenedores organizados."""
    st.markdown('<div class="section-header">📈 Gráficos Generados</div>', unsafe_allow_html=True)
    
    # Organizar gráficos por categoría
    categorias = {}
    for chart_id in st.session_state.selected_charts:
        chart_info = next((c for c in AVAILABLE_CHARTS if c["id"] == chart_id), None)
        if chart_info:
            categoria = chart_info["category"]
            if categoria not in categorias:
                categorias[categoria] = []
            categorias[categoria].append(chart_info)
    
    # Mostrar por categorías
    for categoria, charts in categorias.items():
        st.subheader(f"📁 {categoria}")
        
        for chart_info in charts:
            chart_id = chart_info["id"]
            
            if chart_id not in chart_mapping:
                st.warning(f"⚠️ Gráfico no generado: {chart_info['name']}")
                continue
            
            image_path = chart_mapping[chart_id]
            
            # Contenedor para gráfico y descripción
            with st.container():
                st.markdown(f'<div class="chart-container">', unsafe_allow_html=True)
                st.markdown(f'<div class="chart-title">{chart_info["name"]}</div>', unsafe_allow_html=True)
                
                # Dos columnas: gráfico y descripción
                col_grafico, col_desc = st.columns([1, 1])
                
                with col_grafico:
                    try:
                        if st.session_state.analysis_client.mode == "API":
                            import requests
                            response = requests.get(image_path)
                            st.image(response.content, use_container_width=True)
                        else:
                            if Path(image_path).exists():
                                st.image(image_path, use_container_width=True)
                    except Exception as e:
                        st.error(f"Error al cargar imagen: {e}")
                
                with col_desc:
                    descripcion = CHART_DESCRIPTIONS.get(chart_id, "Descripción no disponible.")
                    st.markdown(f'<div class="chart-description">{descripcion}</div>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)


def mostrar_resultados(resultados: Dict):
    """Muestra los resultados del análisis con gráficos organizados."""
    st.markdown('<div class="section-header">📊 Resultados del Análisis</div>', unsafe_allow_html=True)
    
    # Mostrar tablas CSV
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Resumen de Métricas")
        try:
            if st.session_state.analysis_client.mode == "API":
                import requests
                resumen_csv_url = resultados.get('resumen_csv_url')
                response = requests.get(resumen_csv_url)
                df_metricas = pd.read_csv(io.StringIO(response.text))
            else:
                df_metricas = pd.read_csv(resultados.get('resumen_csv_path'))
            
            st.dataframe(df_metricas.head(50), use_container_width=True)
            
            csv_metricas = df_metricas.to_csv(index=False)
            st.download_button(
                label="📥 Descargar resumen_metricas.csv",
                data=csv_metricas,
                file_name="resumen_metricas.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"Error al cargar métricas: {e}")
    
    with col2:
        st.subheader("🧬 Uso de Codones")
        try:
            if st.session_state.analysis_client.mode == "API":
                import requests
                codon_csv_url = resultados.get('codon_csv_url')
                response = requests.get(codon_csv_url)
                df_codones = pd.read_csv(io.StringIO(response.text))
            else:
                df_codones = pd.read_csv(resultados.get('codon_csv_path'))
            
            st.dataframe(df_codones.head(50), use_container_width=True)
            
            csv_codones = df_codones.to_csv(index=False)
            st.download_button(
                label="📥 Descargar codon_usage.csv",
                data=csv_codones,
                file_name="codon_usage.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"Error al cargar codones: {e}")
    
    # Mostrar gráficos organizados
    images = resultados.get('images', [])
    
    # Crear mapeo de gráficos (asumiendo que el backend devuelve en orden)
    chart_mapping = {}
    for idx, chart_id in enumerate(st.session_state.selected_charts):
        if idx < len(images):
            chart_mapping[chart_id] = images[idx]
    
    mostrar_graficos_con_descripciones(images, chart_mapping)
    
    # Botón de descarga ZIP
    st.subheader("📦 Descargar Reporte Completo")
    
    try:
        if st.session_state.analysis_client.mode == "API":
            zip_url = resultados.get('zip_url')
            if zip_url:
                st.markdown(f"**[Descargar ZIP completo]({zip_url})**")
            else:
                st.warning("El backend no proporcionó un archivo ZIP")
        else:
            resumen_csv_path = resultados.get('resumen_csv_path')
            if resumen_csv_path:
                resultados_dir = Path(resumen_csv_path).parent
                zip_path = crear_zip_resultados(str(resultados_dir))
                
                if Path(zip_path).exists():
                    with open(zip_path, 'rb') as f:
                        st.download_button(
                            label="📥 Descargar reporte ZIP completo",
                            data=f.read(),
                            file_name="resultados_analisis.zip",
                            mime="application/zip"
                        )
    except Exception as e:
        st.error(f"Error al crear ZIP: {e}")


def main():
    """Función principal de la aplicación mejorada."""
    
    # Logo centrado
    logo_path = Path(__file__).parent / "assets" / "logo.png"
    
    if logo_path.exists():
        import base64
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
        except Exception as e:
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                st.image(str(logo_path), width=150)
    else:
        st.markdown(
            "<div style='text-align: center; font-size: 3rem; margin-bottom: 1rem;'>🧬</div>", 
            unsafe_allow_html=True
        )
    
    # Título
    st.markdown('<div class="main-header">SalmoAvianLight</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheader">Comparación de Secuencias: Salmonella vs Gallus</div>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; color: #888; margin-bottom: 2rem;">
    Herramienta profesional para análisis genético comparativo.<br>
    Selecciona los gráficos que necesitas y obtén resultados detallados con explicaciones.
    </div>
    """, unsafe_allow_html=True)
    
    # Indicador de modo
    modo = st.session_state.analysis_client.mode
    if modo == "API":
        st.info(f"🌐 Modo API: Conectado a {st.session_state.analysis_client.base_url}")
    else:
        st.info("💻 Modo Local: Ejecutando análisis en este servidor")
    
    # Sección 1: Carga de archivos
    st.markdown('<div class="section-header">1️⃣ Carga de Archivos FASTA</div>', 
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
            es_valido, mensaje = validar_archivo_fasta(salmonella_file)
            if not es_valido:
                st.error(f"❌ {mensaje}")
            else:
                st.success(f"✅ Archivo válido: {salmonella_file.name} ({tamaño_mb:.2f} MB)")
    
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
                st.error(f"❌ {mensaje}")
            else:
                st.success(f"✅ Archivo válido: {gallus_file.name} ({tamaño_mb:.2f} MB)")
    
    # Sección 2: Selección de gráficos
    mostrar_seleccion_graficos()
    
    # Sección 3: Parámetros
    st.markdown('<div class="section-header">2️⃣ Parámetros de Análisis</div>', 
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
    
    # Verificar cambios en parámetros
    params_changed = False
    if st.session_state.last_used_params is not None:
        params_changed = st.session_state.last_used_params != params
    
    if params_changed and st.session_state.analysis_status == 'COMPLETED':
        st.warning("⚠️ **Parámetros modificados**: Ejecuta un nuevo análisis para ver resultados actualizados.")
    
    # Sección 4: Ejecutar análisis
    st.markdown('<div class="section-header">3️⃣ Ejecutar Análisis</div>', 
                unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        ejecutar_btn = st.button(
            "🚀 Analizar",
            type="primary",
            use_container_width=True,
            disabled=(salmonella_file is None or gallus_file is None)
        )
    
    if ejecutar_btn:
        if salmonella_file and gallus_file:
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
                
                # Limpiar directorio temporal
                if st.session_state.analysis_client.temp_dir:
                    try:
                        if os.path.exists(st.session_state.analysis_client.temp_dir):
                            shutil.rmtree(st.session_state.analysis_client.temp_dir, ignore_errors=True)
                    except Exception:
                        pass
                
                # Ejecutar análisis
                with st.spinner("Ejecutando análisis..."):
                    if ejecutar_analisis(salmonella_file, gallus_file, params):
                        st.success("✅ Análisis iniciado correctamente")
                        st.rerun()
                    else:
                        st.error(f"❌ Error al ejecutar análisis: {st.session_state.error_message}")
    
    # Sección 5: Estado y resultados
    if st.session_state.analysis_status:
        st.markdown('<div class="section-header">4️⃣ Estado del Análisis</div>', 
                    unsafe_allow_html=True)
        
        status = st.session_state.analysis_status
        
        if status == 'SUBMITTED':
            st.info("⏳ Análisis enviado. Esperando procesamiento...")
            if st.session_state.analysis_client.mode == "API" and st.session_state.job_id:
                if st.button("🔄 Actualizar estado", key="refresh_status"):
                    status_response = st.session_state.analysis_client.get_status(st.session_state.job_id)
                    nuevo_status = status_response.get('status')
                    st.session_state.analysis_status = nuevo_status
                    if status_response.get('message'):
                        st.write(status_response.get('message'))
                    st.rerun()
        
        elif status == 'RUNNING':
            st.info("🔄 Análisis en progreso...")
            progress_bar = st.progress(0.5)
            st.write("Procesando secuencias y generando gráficos...")
            
            if st.session_state.analysis_client.mode == "API" and st.session_state.job_id:
                if st.button("🔄 Actualizar estado", key="refresh_running"):
                    status_response = st.session_state.analysis_client.get_status(st.session_state.job_id)
                    nuevo_status = status_response.get('status')
                    st.session_state.analysis_status = nuevo_status
                    st.rerun()
        
        elif status == 'COMPLETED':
            st.success("✅ Análisis completado exitosamente")
            
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
                mostrar_resultados(st.session_state.analysis_results)
            else:
                st.warning("Los resultados no están disponibles aún.")
        
        elif status == 'FAILED':
            st.error("❌ El análisis falló")
            if st.session_state.error_message:
                st.error(f"Error: {st.session_state.error_message}")
            
            if st.session_state.last_params:
                if st.button("🔄 Reintentar análisis"):
                    st.session_state.analysis_status = None
                    st.session_state.error_message = None
                    st.rerun()
    
    # Historial
    if st.session_state.execution_history:
        with st.expander("📜 Historial de Ejecuciones"):
            hist_df = pd.DataFrame(st.session_state.execution_history)
            st.dataframe(hist_df, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; font-size: 0.9rem;">
    Herramienta de Análisis Genético - Salmonella vs Gallus<br>
    Para analistas de laboratorio - Versión Mejorada
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
