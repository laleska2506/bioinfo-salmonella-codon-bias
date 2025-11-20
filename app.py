"""
Frontend Web para SalmoAvianLight - Versión Ultra Rápida
Optimizado para procesamiento acelerado de archivos FASTA
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
import asyncio
import concurrent.futures
from functools import lru_cache

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
    /* Optimizaciones de rendimiento */
    .stButton button {
        width: 100%;
    }
    /* Ocultar elementos complejos hasta que sean necesarios */
    .hidden {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

# Cache para resultados frecuentes
@lru_cache(maxsize=128)
def cached_chart_descriptions():
    """Cache de descripciones de gráficos para acceso rápido."""
    return {
        "histograma_longitud": "Este histograma muestra la distribución de longitudes de secuencias...",
        "distribucion_gc": "Este gráfico de densidad muestra la distribución del contenido GC...",
        "frecuencia_codones": "Este gráfico de barras muestra la frecuencia relativa de cada codón...",
        "comparativa_codones": "Este gráfico comparativo muestra las diferencias en uso de codones...",
        "correlacion_codones": "Este gráfico de dispersión explora la correlación en uso de codones...",
        "boxplot_longitud": "Este diagrama de cajas compara distribuciones de longitud...",
        "pca": "Este gráfico de análisis de componentes principales (PCA)...",
        "heatmap": "Este mapa de calor muestra similitudes entre secuencias...",
        "scatter_gc_longitud": "Este gráfico de dispersión explora la relación entre contenido GC..."
    }

# Configuración optimizada
AVAILABLE_CHARTS = [
    {"id": "histograma_longitud", "name": "📊 Histograma", "category": "Básicos", "fast": True},
    {"id": "distribucion_gc", "name": "🧬 Distribución GC", "category": "Básicos", "fast": True},
    {"id": "frecuencia_codones", "name": "📈 Frecuencia Codones", "category": "Básicos", "fast": True},
    {"id": "comparativa_codones", "name": "⚖️ Comparativa", "category": "Comparativos", "fast": True},
    {"id": "correlacion_codones", "name": "🔗 Correlación", "category": "Comparativos", "fast": False},
    {"id": "boxplot_longitud", "name": "📦 Boxplot", "category": "Comparativos", "fast": True},
    {"id": "pca", "name": "🎯 PCA", "category": "Avanzados", "fast": False},
    {"id": "heatmap", "name": "🔥 Heatmap", "category": "Avanzados", "fast": False},
    {"id": "scatter_gc_longitud", "name": "💫 Scatter GC", "category": "Avanzados", "fast": True}
]

# Inicialización optimizada del session state
def init_session_state():
    """Inicializa el session state de manera eficiente."""
    defaults = {
        'analysis_client': AnalysisClient(),
        'job_id': None,
        'analysis_status': None,
        'analysis_results': None,
        'last_params': None,
        'error_message': None,
        'execution_history': [],
        'last_used_params': None,
        'selected_charts': [chart["id"] for chart in AVAILABLE_CHARTS if chart["fast"]],
        'file_cache': {},
        'processing_start_time': None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def fast_file_validation(archivo) -> Tuple[bool, Optional[str]]:
    """
    Validación ultra rápida de archivos FASTA.
    """
    if archivo is None:
        return False, "Archivo requerido"
    
    # Cache de validación
    cache_key = f"{archivo.name}_{archivo.size}"
    if cache_key in st.session_state.file_cache:
        return st.session_state.file_cache[cache_key]
    
    # Validación rápida de extensión
    nombre = archivo.name.lower()
    if not (nombre.endswith('.fa') or nombre.endswith('.fasta')):
        result = (False, "Extensión .fa o .fasta requerida")
        st.session_state.file_cache[cache_key] = result
        return result
    
    # Validación rápida de tamaño
    if archivo.size == 0:
        result = (False, "Archivo vacío")
        st.session_state.file_cache[cache_key] = result
        return result
    
    # Validación rápida de formato (solo primeros bytes)
    try:
        primeros_bytes = archivo.read(100)
        archivo.seek(0)
        if not primeros_bytes.startswith(b'>'):
            result = (False, "Formato FASTA inválido")
            st.session_state.file_cache[cache_key] = result
            return result
    except Exception as e:
        result = (False, f"Error de lectura: {str(e)}")
        st.session_state.file_cache[cache_key] = result
        return result
    
    result = (True, None)
    st.session_state.file_cache[cache_key] = result
    return result

def optimized_file_processing(salmonella_file, gallus_file):
    """
    Procesamiento optimizado de archivos con manejo eficiente de memoria.
    """
    try:
        # Procesamiento en paralelo para archivos grandes
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_sal = executor.submit(process_single_file, salmonella_file)
            future_gall = executor.submit(process_single_file, gallus_file)
            
            salmonella_content = future_sal.result(timeout=30)
            gallus_content = future_gall.result(timeout=30)
        
        return salmonella_content, gallus_content
        
    except concurrent.futures.TimeoutError:
        raise Exception("Timeout en procesamiento de archivos")
    except Exception as e:
        raise Exception(f"Error en procesamiento: {str(e)}")

def process_single_file(file):
    """Procesa un solo archivo de manera eficiente."""
    return file.read()

def mostrar_seleccion_graficos_rapida():
    """Interfaz optimizada para selección de gráficos."""
    st.markdown('<div class="section-header">📊 Selección Rápida de Gráficos</div>', unsafe_allow_html=True)
    
    # Modo rápido por defecto (solo gráficos rápidos)
    modo_rapido = st.checkbox(
        "🚀 Modo Rápido (Solo gráficos esenciales)", 
        value=True,
        help="Selecciona automáticamente los gráficos de procesamiento más rápido"
    )
    
    if modo_rapido:
        st.session_state.selected_charts = [chart["id"] for chart in AVAILABLE_CHARTS if chart["fast"]]
        st.success("✅ Modo rápido activado: Gráficos esenciales seleccionados")
        return
    
    # Selección manual optimizada
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🚀 Gráficos Rápidos")
        for chart in [c for c in AVAILABLE_CHARTS if c["fast"]]:
            selected = st.checkbox(
                chart["name"],
                value=chart["id"] in st.session_state.selected_charts,
                key=f"fast_{chart['id']}",
                help="Procesamiento rápido"
            )
            update_chart_selection(chart["id"], selected)
    
    with col2:
        st.subheader("⚡ Gráficos Intermedios")
        for chart in [c for c in AVAILABLE_CHARTS if not c["fast"] and c["category"] == "Comparativos"]:
            selected = st.checkbox(
                chart["name"],
                value=chart["id"] in st.session_state.selected_charts,
                key=f"med_{chart['id']}",
                help="Procesamiento moderado"
            )
            update_chart_selection(chart["id"], selected)
    
    with col3:
        st.subheader("🔬 Gráficos Avanzados")
        for chart in [c for c in AVAILABLE_CHARTS if not c["fast"] and c["category"] == "Avanzados"]:
            selected = st.checkbox(
                chart["name"],
                value=chart["id"] in st.session_state.selected_charts,
                key=f"adv_{chart['id']}",
                help="Procesamiento más lento"
            )
            update_chart_selection(chart["id"], selected)

def update_chart_selection(chart_id, selected):
    """Actualiza la selección de gráficos de manera eficiente."""
    if selected and chart_id not in st.session_state.selected_charts:
        st.session_state.selected_charts.append(chart_id)
    elif not selected and chart_id in st.session_state.selected_charts:
        st.session_state.selected_charts.remove(chart_id)

def ejecutar_analisis_rapido(salmonella_file, gallus_file, params: Dict):
    """Ejecuta el análisis de manera optimizada."""
    try:
        st.session_state.processing_start_time = time.time()
        
        # Validación ultrarrápida
        salmonella_valido, msg_sal = fast_file_validation(salmonella_file)
        gallus_valido, msg_gall = fast_file_validation(gallus_file)
        
        if not salmonella_valido or not gallus_valido:
            raise ValueError(f"Salmonella: {msg_sal}, Gallus: {msg_gall}")
        
        # Información de procesamiento
        tamaño_sal = salmonella_file.size / (1024 * 1024)
        tamaño_gall = gallus_file.size / (1024 * 1024)
        num_charts = len(st.session_state.selected_charts)
        
        st.write(f"⚡ **Procesamiento optimizado:**")
        st.write(f"- Archivos: {tamaño_sal:.1f}MB + {tamaño_gall:.1f}MB")
        st.write(f"- Gráficos: {num_charts} seleccionados")
        st.write(f"- Estrategia: {'RÁPIDA' if num_charts <= 3 else 'BALANCEADA'}")
        
        # Procesamiento optimizado
        with st.spinner("🚀 Procesamiento acelerado..."):
            salmonella_content, gallus_content = optimized_file_processing(
                salmonella_file, gallus_file
            )
        
        # Parámetros optimizados
        params['selected_charts'] = st.session_state.selected_charts
        params['optimized'] = True
        params['fast_mode'] = len(st.session_state.selected_charts) <= 3
        
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
        
        # Cache de parámetros
        st.session_state.last_params = {
            'salmonella_file': salmonella_file,
            'gallus_file': gallus_file,
            'params': params
        }
        
        st.session_state.last_used_params = params.copy()
        
        # Historial optimizado
        st.session_state.execution_history.append({
            'job_id': st.session_state.job_id or 'LOCAL',
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

def mostrar_resultados_rapidos(resultados: Dict):
    """Muestra resultados de manera optimizada."""
    st.markdown('<div class="section-header">📊 Resultados Rápidos</div>', unsafe_allow_html=True)
    
    # Métricas rápidas
    col1, col2 = st.columns(2)
    
    with col1:
        try:
            if st.session_state.analysis_client.mode == "API":
                import requests
                resumen_csv_url = resultados.get('resumen_csv_url')
                response = requests.get(resumen_csv_url, timeout=10)
                df_metricas = pd.read_csv(io.StringIO(response.text))
            else:
                df_metricas = pd.read_csv(resultados.get('resumen_csv_path'))
            
            st.dataframe(df_metricas.head(20), use_container_width=True)
            
            csv_metricas = df_metricas.to_csv(index=False)
            st.download_button(
                label="📥 Descargar Métricas",
                data=csv_metricas,
                file_name="metricas_rapidas.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"Error métricas: {e}")
    
    with col2:
        try:
            if st.session_state.analysis_client.mode == "API":
                import requests
                codon_csv_url = resultados.get('codon_csv_url')
                response = requests.get(codon_csv_url, timeout=10)
                df_codones = pd.read_csv(io.StringIO(response.text))
            else:
                df_codones = pd.read_csv(resultados.get('codon_csv_path'))
            
            st.dataframe(df_codones.head(20), use_container_width=True)
            
            csv_codones = df_codones.to_csv(index=False)
            st.download_button(
                label="📥 Descargar Codones",
                data=csv_codones,
                file_name="codones_rapidos.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"Error codones: {e}")
    
    # Gráficos optimizados
    mostrar_graficos_rapidos(resultados.get('images', []))

def mostrar_graficos_rapidos(images: List):
    """Muestra gráficos de manera eficiente."""
    st.markdown('<div class="section-header">📈 Visualizaciones Rápidas</div>', unsafe_allow_html=True)
    
    if not images:
        st.info("📊 No se generaron gráficos con la configuración actual")
        return
    
    # Mostrar gráficos en grid responsivo
    charts_per_row = 2
    images_chunks = [images[i:i + charts_per_row] for i in range(0, len(images), charts_per_row)]
    
    for chunk in images_chunks:
        cols = st.columns(charts_per_row)
        for idx, image_path in enumerate(chunk):
            with cols[idx]:
                try:
                    if st.session_state.analysis_client.mode == "API":
                        import requests
                        response = requests.get(image_path, timeout=10)
                        st.image(response.content, use_container_width=True)
                    else:
                        if Path(image_path).exists():
                            st.image(image_path, use_container_width=True)
                    
                    # Descripción rápida
                    chart_id = st.session_state.selected_charts[idx] if idx < len(st.session_state.selected_charts) else "unknown"
                    descripcion = cached_chart_descriptions().get(chart_id, "Visualización generada.")
                    st.markdown(f'<div class="chart-description">{descripcion}</div>', unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Error gráfico {idx}: {e}")

def limpiar_cache():
    """Limpia la cache para liberar memoria."""
    if 'file_cache' in st.session_state:
        st.session_state.file_cache.clear()
    cached_chart_descriptions.cache_clear()

def main():
    """Aplicación principal optimizada para velocidad."""
    init_session_state()
    
    # Header optimizado
    st.markdown('<div class="main-header">🚀 SalmoAvianLight Rápido</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheader">Procesamiento Ultra Acelerado de Secuencias</div>', unsafe_allow_html=True)
    
    # Indicadores de rendimiento
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("⚡ Procesamiento Optimizado")
    with col2:
        st.info("📊 Gráficos Rápidos")
    with col3:
        st.info("💾 Memoria Eficiente")
    
    # Sección 1: Carga ultrarrápida
    st.markdown('<div class="section-header">1️⃣ Carga Express de Archivos</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        salmonella_file = st.file_uploader(
            "Salmonella FASTA",
            type=['fa', 'fasta'],
            key="salmonella_fast",
            help="Archivo FASTA de Salmonella"
        )
        if salmonella_file:
            es_valido, mensaje = fast_file_validation(salmonella_file)
            if es_valido:
                tamaño_mb = salmonella_file.size / (1024 * 1024)
                st.success(f"✅ {salmonella_file.name} ({tamaño_mb:.1f}MB)")
            else:
                st.error(f"❌ {mensaje}")
    
    with col2:
        gallus_file = st.file_uploader(
            "Gallus FASTA", 
            type=['fa', 'fasta'],
            key="gallus_fast",
            help="Archivo FASTA de Gallus"
        )
        if gallus_file:
            es_valido, mensaje = fast_file_validation(gallus_file)
            if es_valido:
                tamaño_mb = gallus_file.size / (1024 * 1024)
                st.success(f"✅ {gallus_file.name} ({tamaño_mb:.1f}MB)")
            else:
                st.error(f"❌ {mensaje}")
    
    # Sección 2: Configuración rápida
    st.markdown('<div class="section-header">2️⃣ Configuración Express</div>', unsafe_allow_html=True)
    
    mostrar_seleccion_graficos_rapida()
    
    # Parámetros optimizados
    col1, col2, col3 = st.columns(3)
    with col1:
        min_len = st.number_input("Longitud mínima", value=0, help="Filtro rápido por longitud")
    with col2:
        limpiar_ns = st.checkbox("Limpiar Ns", value=True, help="Normalización rápida")
    with col3:
        top_codons = st.slider("Top codones", 5, 30, 15, help="Análisis de codones principales")
    
    params = {'min_len': min_len, 'limpiar_ns': limpiar_ns, 'top_codons': top_codons}
    
    # Sección 3: Ejecución acelerada
    st.markdown('<div class="section-header">3️⃣ Análisis Express</div>', unsafe_allow_html=True)
    
    ejecutar_btn = st.button(
        "🚀 EJECUTAR ANÁLISIS RÁPIDO", 
        type="primary",
        use_container_width=True,
        disabled=not (salmonella_file and gallus_file)
    )
    
    if ejecutar_btn:
        # Limpieza previa
        limpiar_cache()
        st.session_state.analysis_results = None
        st.session_state.analysis_status = None
        st.session_state.error_message = None
        
        # Ejecución optimizada
        with st.spinner("⚡ Iniciando procesamiento acelerado..."):
            if ejecutar_analisis_rapido(salmonella_file, gallus_file, params):
                st.success("✅ Análisis iniciado - Procesando en segundo plano...")
                st.rerun()
    
    # Sección 4: Resultados en tiempo real
    if st.session_state.analysis_status:
        st.markdown('<div class="section-header">4️⃣ Progreso en Tiempo Real</div>', unsafe_allow_html=True)
        
        status = st.session_state.analysis_status
        
        if status == 'SUBMITTED':
            st.info("⏳ En cola de procesamiento...")
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
                mostrar_resultados_rapidos(st.session_state.analysis_results)
        
        elif status == 'FAILED':
            st.error("❌ Error en el análisis")
            if st.session_state.error_message:
                st.error(st.session_state.error_message)
            
            if st.button("🔄 Reintentar", key="retry_fast"):
                st.session_state.analysis_status = None
                st.rerun()
    
    # Estadísticas de rendimiento
    if st.session_state.execution_history:
        with st.expander("📊 Estadísticas de Rendimiento"):
            for hist in st.session_state.execution_history[-3:]:  # Solo últimos 3
                st.write(f"{hist['timestamp']} - {hist['status']} - {hist.get('duration', 0):.1f}s")
    
    # Footer optimizado
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; font-size: 0.8rem;">
    🚀 SalmoAvianLight Rápido - v2.0 Optimizado<br>
    Procesamiento acelerado para análisis genético
    </div>
    """, unsafe_allow_html=True)
    
    # Limpieza automática de cache
    if len(st.session_state.file_cache) > 50:
        limpiar_cache()

if __name__ == "__main__":
    main()
