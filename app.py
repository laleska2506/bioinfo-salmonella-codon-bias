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
from typing import Optional, Dict, Tuple
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

# Estilos CSS personalizados
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


def validar_archivo_fasta(archivo) -> Tuple[bool, Optional[str]]:
    """
    Valida que el archivo subido sea un FASTA válido.
    
    Retorna:
    --------
    (bool, str): (es_válido, mensaje_error)
    """
    if archivo is None:
        return False, "Por favor, sube un archivo FASTA"
    
    # Validar extensión
    nombre_archivo = archivo.name.lower()
    if not (nombre_archivo.endswith('.fa') or nombre_archivo.endswith('.fasta')):
        return False, "El archivo debe tener extensión .fa o .fasta"
    
    # Validar que no esté vacío
    if archivo.size == 0:
        return False, "El archivo está vacío"
    
    # Validar tamaño máximo (si está configurado)
    max_upload_mb = os.environ.get("MAX_UPLOAD_MB")
    if max_upload_mb:
        max_size = int(max_upload_mb) * 1024 * 1024
        if archivo.size > max_size:
            return False, f"El archivo es demasiado grande. Máximo: {max_upload_mb} MB"
    
    # Validar formato básico (debe empezar con >)
    contenido = archivo.read()
    archivo.seek(0)  # Resetear puntero
    if not contenido.startswith(b'>'):
        return False, "El archivo no parece ser un FASTA válido (debe empezar con '>')"
    
    return True, None


def ejecutar_analisis(salmonella_file, gallus_file, params: Dict):
    """Ejecuta el análisis genético."""
    try:
        # Debug: mostrar parámetros recibidos
        st.write(f"🔍 **Parámetros del análisis:**")
        st.write(f"- Longitud mínima: {params.get('min_len', 0)}")
        st.write(f"- Limpiar Ns: {params.get('limpiar_ns', True)}")
        st.write(f"- Top codones: {params.get('top_codons', 20)}")
        
        # Leer archivos
        salmonella_content = salmonella_file.read()
        gallus_content = gallus_file.read()
        
        # Resetear punteros
        salmonella_file.seek(0)
        gallus_file.seek(0)
        
        # Ejecutar análisis
        if st.session_state.analysis_client.mode == "API":
            # Modo API: iniciar trabajo
            resultado = st.session_state.analysis_client.start_analysis(
                salmonella_content,
                gallus_content,
                params
            )
            st.session_state.job_id = resultado.get('jobId')
            st.session_state.analysis_status = 'SUBMITTED'
        else:
            # Modo LOCAL: ejecutar directamente
            resultado = st.session_state.analysis_client.start_analysis(
                salmonella_content,
                gallus_content,
                params
            )
            st.session_state.analysis_status = resultado.get('status')
            st.session_state.analysis_results = resultado.get('results')
        
        # Guardar parámetros para reintentos
        st.session_state.last_params = {
            'salmonella_file': salmonella_file,
            'gallus_file': gallus_file,
            'params': params
        }
        
        # Guardar parámetros usados para detectar cambios
        st.session_state.last_used_params = params.copy()
        
        # Agregar a historial
        st.session_state.execution_history.append({
            'job_id': st.session_state.job_id or 'LOCAL',
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'status': st.session_state.analysis_status
        })
        
        return True
        
    except Exception as e:
        st.session_state.error_message = str(e)
        st.session_state.analysis_status = 'FAILED'
        return False


def mostrar_resultados(resultados: Dict):
    """Muestra los resultados del análisis."""
    st.markdown('<div class="section-header">📊 Resultados del Análisis</div>', 
                unsafe_allow_html=True)
    
    # Verificar si estamos en modo API o LOCAL
    if st.session_state.analysis_client.mode == "API":
        # En modo API, los resultados vienen con URLs
        resumen_csv_url = resultados.get('resumen_csv_url')
        codon_csv_url = resultados.get('codon_csv_url')
        images = resultados.get('images', [])
        zip_url = resultados.get('zip_url')
    else:
        # En modo LOCAL, los resultados vienen con paths
        resumen_csv_path = resultados.get('resumen_csv_path')
        codon_csv_path = resultados.get('codon_csv_path')
        images = resultados.get('images', [])
    
    # Mostrar tablas CSV
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Resumen de Métricas")
        try:
            if st.session_state.analysis_client.mode == "API":
                # Descargar desde URL
                import requests
                response = requests.get(resumen_csv_url)
                df_metricas = pd.read_csv(io.StringIO(response.text))
            else:
                df_metricas = pd.read_csv(resumen_csv_path)
            
            st.dataframe(df_metricas.head(50), use_container_width=True)
            
            # Botón de descarga
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
                response = requests.get(codon_csv_url)
                df_codones = pd.read_csv(io.StringIO(response.text))
            else:
                df_codones = pd.read_csv(codon_csv_path)
            
            st.dataframe(df_codones.head(50), use_container_width=True)
            
            # Botón de descarga
            csv_codones = df_codones.to_csv(index=False)
            st.download_button(
                label="📥 Descargar codon_usage.csv",
                data=csv_codones,
                file_name="codon_usage.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"Error al cargar codones: {e}")
    
    # Mostrar gráficos
    st.subheader("📈 Gráficos Generados")
    
    if images:
        # Organizar gráficos en columnas
        num_cols = 3
        cols = st.columns(num_cols)
        
        for idx, img_path in enumerate(images):
            col_idx = idx % num_cols
            with cols[col_idx]:
                try:
                    if st.session_state.analysis_client.mode == "API":
                        # Cargar imagen desde URL
                        import requests
                        response = requests.get(img_path)
                        st.image(response.content, caption=Path(img_path).name, use_container_width=True)
                    else:
                        # Cargar imagen desde path local
                        if Path(img_path).exists():
                            st.image(img_path, caption=Path(img_path).name, use_container_width=True)
                except Exception as e:
                    st.error(f"Error al cargar imagen {img_path}: {e}")
    else:
        st.info("No se generaron gráficos")
    
    # Botón de descarga ZIP
    st.subheader("📦 Descargar Reporte Completo")
    
    try:
        if st.session_state.analysis_client.mode == "API":
            if zip_url:
                st.markdown(f"**[Descargar ZIP completo]({zip_url})**")
            else:
                st.warning("El backend no proporcionó un archivo ZIP")
        else:
            # Crear ZIP local desde los paths de resultados
            if resumen_csv_path and codon_csv_path:
                # Obtener directorio de resultados
                resultados_dir = Path(resumen_csv_path).parent
                
                # Crear ZIP
                zip_path = crear_zip_resultados(str(resultados_dir))
                
                if Path(zip_path).exists():
                    with open(zip_path, 'rb') as f:
                        st.download_button(
                            label="📥 Descargar reporte ZIP completo",
                            data=f.read(),
                            file_name="resultados_analisis.zip",
                            mime="application/zip"
                        )
                else:
                    st.warning("No se pudo crear el archivo ZIP")
            else:
                st.warning("No hay resultados disponibles para comprimir")
    except Exception as e:
        st.error(f"Error al crear ZIP: {e}")


def main():
    """Función principal de la aplicación."""
    
    # Logo centrado en la parte superior
    logo_path = Path(__file__).parent / "assets" / "logo.png"
    
    # Contenedor centrado para el logo
    if logo_path.exists():
        # Leer la imagen y convertir a base64 para incluirla en HTML
        import base64
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
            es_valido, mensaje = validar_archivo_fasta(salmonella_file)
            if not es_valido:
                st.error(mensaje)
            else:
                st.success(f"✅ Archivo válido: {salmonella_file.name} ({salmonella_file.size / 1024:.2f} KB)")
    
    with col2:
        st.subheader("Gallus")
        gallus_file = st.file_uploader(
            "Selecciona el archivo FASTA de Gallus",
            type=['fa', 'fasta'],
            key="gallus_uploader",
            help="Archivo FASTA con secuencias de Gallus"
        )
        if gallus_file:
            es_valido, mensaje = validar_archivo_fasta(gallus_file)
            if not es_valido:
                st.error(mensaje)
            else:
                st.success(f"✅ Archivo válido: {gallus_file.name} ({gallus_file.size / 1024:.2f} KB)")
    
    # Sección 2: Parámetros
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
    
    # Verificar si los parámetros han cambiado desde el último análisis
    params_changed = False
    if st.session_state.last_used_params is not None:
        params_changed = st.session_state.last_used_params != params
    
    # Si los parámetros cambiaron y hay resultados anteriores, mostrar advertencia
    if params_changed and st.session_state.analysis_status == 'COMPLETED':
        st.warning(
            "⚠️ **Parámetros modificados**: Los resultados mostrados fueron generados con parámetros diferentes. "
            "Ejecuta un nuevo análisis para ver los resultados con los parámetros actuales."
        )
    
    # Sección 3: Ejecutar análisis
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
    
    # Ejecutar análisis cuando se presiona el botón
    if ejecutar_btn:
        if salmonella_file and gallus_file:
            # Validar archivos
            salmonella_valido, msg_sal = validar_archivo_fasta(salmonella_file)
            gallus_valido, msg_gall = validar_archivo_fasta(gallus_file)
            
            if not salmonella_valido:
                st.error(f"Error en archivo Salmonella: {msg_sal}")
            elif not gallus_valido:
                st.error(f"Error en archivo Gallus: {msg_gall}")
            else:
                # Limpiar resultados anteriores antes de ejecutar nuevo análisis
                st.session_state.analysis_results = None
                st.session_state.analysis_status = None
                st.session_state.error_message = None
                
                # Limpiar directorio temporal anterior si existe
                if st.session_state.analysis_client.temp_dir:
                    try:
                        import shutil
                        if os.path.exists(st.session_state.analysis_client.temp_dir):
                            shutil.rmtree(st.session_state.analysis_client.temp_dir, ignore_errors=True)
                    except Exception:
                        pass
                
                # Ejecutar análisis
                with st.spinner("Ejecutando análisis..."):
                    if ejecutar_analisis(salmonella_file, gallus_file, params):
                        st.success("✅ Análisis iniciado correctamente")
                        st.rerun()  # Recargar para mostrar nuevos resultados
                    else:
                        st.error(f"❌ Error al ejecutar análisis: {st.session_state.error_message}")
    
    # Sección 4: Estado y progreso
    if st.session_state.analysis_status:
        st.markdown('<div class="section-header">4️⃣ Estado del Análisis</div>', 
                    unsafe_allow_html=True)
        
        # Mostrar estado
        status = st.session_state.analysis_status
        
        if status == 'SUBMITTED':
            st.info("⏳ Análisis enviado. Esperando procesamiento...")
            # En modo API, hacer polling automático
            if st.session_state.analysis_client.mode == "API" and st.session_state.job_id:
                # Botón para actualizar estado manualmente (evita loops infinitos)
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
            
            # Polling en modo API
            if st.session_state.analysis_client.mode == "API" and st.session_state.job_id:
                if st.button("🔄 Actualizar estado", key="refresh_running"):
                    status_response = st.session_state.analysis_client.get_status(st.session_state.job_id)
                    nuevo_status = status_response.get('status')
                    st.session_state.analysis_status = nuevo_status
                    if status_response.get('message'):
                        st.write(status_response.get('message'))
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
                st.warning("Los resultados no están disponibles aún. Por favor, intenta actualizar el estado.")
        
        elif status == 'FAILED':
            st.error("❌ El análisis falló")
            if st.session_state.error_message:
                st.error(f"Error: {st.session_state.error_message}")
            
            # Botón de reintento
            if st.session_state.last_params:
                if st.button("🔄 Reintentar análisis"):
                    st.session_state.analysis_status = None
                    st.session_state.error_message = None
                    st.rerun()
    
    # Sección 5: Historial de ejecuciones
    if st.session_state.execution_history:
        with st.expander("📜 Historial de Ejecuciones"):
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

