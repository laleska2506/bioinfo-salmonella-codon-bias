"""
Cliente de análisis que soporta dos modos:
1. Local-Import Mode: ejecuta análisis localmente usando módulos Python
2. API Mode: usa un backend HTTP para ejecutar análisis remotos
"""
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import requests
import pandas as pd

# Detectar modo de operación
BACKEND_BASE_URL = os.environ.get("BACKEND_BASE_URL")

# Si estamos en modo local, importar módulos
if not BACKEND_BASE_URL:
    # Agregar el directorio raíz al path para importar src
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    try:
        from src import (
            cargar_secuencias,
            calcular_metricas_basicas,
            validar_secuencias,
            calcular_uso_codones,
            generar_todos_los_graficos,
            grafico_gc,
        )
        from src.visualizacion import (
            distribucion_longitudes,
            distribucion_gc,
            relacion_longitud_gc,
            uso_codones_top20,
            correlacion_codones,
            heatmap_codones,
            distribucion_acumulativa_longitudes,
        )
        LOCAL_MODE = True
    except ImportError as e:
        print(f"Error al importar módulos locales: {e}")
        LOCAL_MODE = False
else:
    LOCAL_MODE = False


class AnalysisClient:
    """Cliente para ejecutar análisis genéticos en modo local o API."""
    
    def __init__(self):
        self.mode = "LOCAL" if LOCAL_MODE else "API"
        self.base_url = BACKEND_BASE_URL.rstrip('/') if BACKEND_BASE_URL else None
        self.temp_dir = None
    
    def start_analysis(
        self,
        salmonella_fasta: bytes,
        gallus_fasta: bytes,
        params: Dict
    ) -> Dict:
        """
        Inicia un análisis genético.
        
        Parámetros:
        -----------
        salmonella_fasta : bytes
            Contenido del archivo FASTA de Salmonella
        gallus_fasta : bytes
            Contenido del archivo FASTA de Gallus
        params : dict
            Parámetros del análisis:
            - min_len: int (longitud mínima de secuencias)
            - limpiar_ns: bool (normalizar/limpiar Ns)
            - top_codons: int (número de codones para gráfico comparativo)
        
        Retorna:
        --------
        dict
            {'jobId': str} en modo API
            {'status': 'COMPLETED', 'results': {...}} en modo LOCAL
        """
        if self.mode == "API":
            return self._start_analysis_api(salmonella_fasta, gallus_fasta, params)
        else:
            return self._start_analysis_local(salmonella_fasta, gallus_fasta, params)
    
    def _start_analysis_api(
        self,
        salmonella_fasta: bytes,
        gallus_fasta: bytes,
        params: Dict
    ) -> Dict:
        """Inicia análisis en modo API."""
        url = f"{self.base_url}/start-analysis"
        
        files = {
            'salmonella_fasta': ('salmonella.fasta', salmonella_fasta, 'text/plain'),
            'gallus_fasta': ('gallus.fasta', gallus_fasta, 'text/plain'),
        }
        
        data = {
            'min_len': params.get('min_len', 0),
            'limpiar_ns': params.get('limpiar_ns', True),
            'top_codons': params.get('top_codons', 20),
        }
        
        try:
            response = requests.post(url, files=files, data=data, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            raise Exception("❌ Tiempo de espera agotado al comunicarse con el servidor. El archivo puede ser demasiado grande o el servidor está ocupado.")
        except requests.exceptions.HTTPError as e:
            # Intentar obtener mensaje de error del servidor si está disponible
            try:
                error_data = response.json()
                error_msg = error_data.get('error', error_data.get('message', str(e)))
                raise Exception(f"❌ Error del servidor: {error_msg}")
            except:
                raise Exception(f"❌ Error al comunicarse con el backend (HTTP {response.status_code}): {str(e)}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"❌ Error de conexión con el backend: {str(e)}. Verifique que el servidor esté disponible.")
    
    def _start_analysis_local(
        self,
        salmonella_fasta: bytes,
        gallus_fasta: bytes,
        params: Dict
    ) -> Dict:
        """Ejecuta análisis localmente."""
        import shutil
        
        # Limpiar directorio temporal anterior si existe
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            except Exception:
                pass
        
        # Crear directorio temporal nuevo para archivos
        self.temp_dir = tempfile.mkdtemp(prefix="bioinfo_analysis_")
        results_dir = Path(self.temp_dir) / "results"
        graficos_dir = results_dir / "graficos"
        graficos_dir.mkdir(parents=True, exist_ok=True)
        
        # Guardar archivos FASTA temporales
        salmonella_path = Path(self.temp_dir) / "salmonella.fasta"
        gallus_path = Path(self.temp_dir) / "gallus.fasta"
        
        # Escribir archivos con manejo de errores de memoria y codificación
        try:
            # Si los archivos vienen como bytes, escribirlos directamente
            # Si vienen como string, convertirlos a bytes con UTF-8
            if isinstance(salmonella_fasta, bytes):
                salmonella_path.write_bytes(salmonella_fasta)
            else:
                salmonella_path.write_text(str(salmonella_fasta), encoding='utf-8')
            
            if isinstance(gallus_fasta, bytes):
                gallus_path.write_bytes(gallus_fasta)
            else:
                gallus_path.write_text(str(gallus_fasta), encoding='utf-8')
        except MemoryError:
            raise MemoryError("No hay suficiente memoria para guardar los archivos. Los archivos son demasiado grandes.")
        except UnicodeEncodeError as e:
            raise ValueError(
                "Error de codificación al guardar el archivo. El archivo contiene caracteres que no se pueden procesar. "
                "Por favor, asegúrese de que el archivo esté guardado en formato UTF-8 o ASCII."
            )
        
        try:
            # 1. Cargar secuencias usando paths absolutos
            # Mostrar progreso para archivos grandes
            import sys
            sys.stdout.write("[DEBUG] Cargando secuencias de Salmonella...\n")
            sys.stdout.flush()
            try:
                salmonella = cargar_secuencias(str(salmonella_path.absolute()))
                sys.stdout.write(f"[DEBUG] Cargadas {len(salmonella)} secuencias de Salmonella\n")
                sys.stdout.flush()
            except (ValueError, FileNotFoundError) as e:
                raise ValueError(f"Error al cargar el archivo FASTA de Salmonella: {str(e)}")
            
            sys.stdout.write("[DEBUG] Cargando secuencias de Gallus...\n")
            sys.stdout.flush()
            try:
                gallus = cargar_secuencias(str(gallus_path.absolute()))
                sys.stdout.write(f"[DEBUG] Cargadas {len(gallus)} secuencias de Gallus\n")
                sys.stdout.flush()
            except (ValueError, FileNotFoundError) as e:
                raise ValueError(f"Error al cargar el archivo FASTA de Gallus: {str(e)}")
            
            # 2. Validar secuencias
            if not validar_secuencias(salmonella):
                raise ValueError("Las secuencias de Salmonella contienen caracteres inválidos. Solo se permiten A, T, C, G y N.")
            if not validar_secuencias(gallus):
                raise ValueError("Las secuencias de Gallus contienen caracteres inválidos. Solo se permiten A, T, C, G y N.")
            
            # 3. Filtrar por longitud mínima
            min_len = params.get('min_len', 0)
            print(f"[DEBUG] Parámetros recibidos: min_len={min_len}, limpiar_ns={params.get('limpiar_ns')}, top_codons={params.get('top_codons')}")
            print(f"[DEBUG] Secuencias antes del filtro: Salmonella={len(salmonella)}, Gallus={len(gallus)}")
            
            if min_len > 0:
                salmonella = [(id_seq, seq) for id_seq, seq in salmonella if len(seq) >= min_len]
                gallus = [(id_seq, seq) for id_seq, seq in gallus if len(seq) >= min_len]
                print(f"[DEBUG] Secuencias después del filtro (min_len={min_len}): Salmonella={len(salmonella)}, Gallus={len(gallus)}")
            
            # 4. Limpiar Ns si está habilitado
            limpiar_ns = params.get('limpiar_ns', True)
            if limpiar_ns:
                print(f"[DEBUG] Limpiando caracteres N de las secuencias")
                salmonella = self._limpiar_ns(salmonella)
                gallus = self._limpiar_ns(gallus)
            
            # 5. Calcular métricas básicas
            df_salmonella = calcular_metricas_basicas(salmonella)
            df_gallus = calcular_metricas_basicas(gallus)
            
            # Combinar métricas
            df_metricas = pd.concat([df_salmonella, df_gallus], ignore_index=True)
            metricas_path = results_dir / "resumen_metricas.csv"
            df_metricas.to_csv(str(metricas_path.absolute()), index=False)
            
            # 6. Calcular uso de codones
            df_codones_salmonella = calcular_uso_codones(salmonella, "salmonella")
            df_codones_gallus = calcular_uso_codones(gallus, "gallus")
            
            # Combinar datos de codones
            df_codones = pd.merge(
                df_codones_salmonella,
                df_codones_gallus,
                on="codon",
                how="outer"
            ).fillna(0).sort_values("codon").reset_index(drop=True)
            
            codon_path = results_dir / "codon_usage.csv"
            df_codones.to_csv(str(codon_path.absolute()), index=False)
            
            # 7. Generar gráficos básicos de GC (necesitan que results/graficos exista)
            # Guardar el directorio de trabajo original y cambiar temporalmente
            original_cwd = os.getcwd()
            try:
                # Cambiar al directorio temporal solo para los gráficos
                os.chdir(self.temp_dir)
                grafico_gc(df_salmonella, "salmonella")
                grafico_gc(df_gallus, "gallus")
                
                # 8. Generar gráficos avanzados (adaptando uso_codones_top20 para top_codons)
                top_codons_param = params.get('top_codons', 20)
                print(f"[DEBUG] Llamando a _generar_graficos_avanzados con top_codons={top_codons_param}")
                self._generar_graficos_avanzados(df_metricas, df_codones, top_codons_param)
            finally:
                # Siempre restaurar el directorio original
                os.chdir(original_cwd)
            
            # Preparar resultados con paths absolutos
            images = list(graficos_dir.glob("*.png"))
            images_paths = [str(img.absolute()) for img in images]
            
            return {
                'status': 'COMPLETED',
                'results': {
                    'resumen_csv_path': str(metricas_path.absolute()),
                    'codon_csv_path': str(codon_path.absolute()),
                    'images': images_paths,
                }
            }
            
        except ValueError as e:
            # Re-lanzar ValueError con el mensaje original (ya es descriptivo)
            raise
        except MemoryError as e:
            # Re-lanzar MemoryError con el mensaje original
            raise
        except Exception as e:
            # Para otros errores, proporcionar contexto adicional
            error_msg = str(e)
            if "FASTA" in error_msg or "corrupto" in error_msg.lower():
                raise ValueError(f"Error al procesar archivos FASTA: {error_msg}")
            else:
                raise Exception(f"Error durante el análisis local: {error_msg}")
    
    def _limpiar_ns(self, secuencias: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        """Elimina o reemplaza caracteres N en secuencias."""
        cleaned = []
        for id_seq, seq in secuencias:
            # Reemplazar Ns con la base más común en la secuencia (o simplemente eliminarlas)
            # Por simplicidad, reemplazamos N con A
            cleaned_seq = seq.replace('N', 'A')
            cleaned.append((id_seq, cleaned_seq))
        return cleaned
    
    def _generar_graficos_avanzados(
        self,
        df_metricas: pd.DataFrame,
        df_codones: pd.DataFrame,
        top_codons: int = 20
    ):
        """Genera todos los gráficos avanzados, adaptando top_codons."""
        import matplotlib.pyplot as plt
        import numpy as np
        
        print(f"[DEBUG] _generar_graficos_avanzados: top_codons recibido = {top_codons}")
        
        # Cargar funciones de visualización (asumen que estamos en el directorio correcto)
        distribucion_longitudes(df_metricas)
        distribucion_gc(df_metricas)
        relacion_longitud_gc(df_metricas)
        correlacion_codones(df_codones)
        heatmap_codones(df_codones)
        distribucion_acumulativa_longitudes(df_metricas)
        
        # Gráfico de uso de codones con top_codons configurable
        df_codones_copy = df_codones.copy()
        df_codones_copy['promedio'] = (
            df_codones_copy['frecuencia_salmonella'] + 
            df_codones_copy['frecuencia_gallus']
        ) / 2
        top_codones_df = df_codones_copy.nlargest(top_codons, 'promedio')
        
        print(f"[DEBUG] Generando gráfico con {len(top_codones_df)} codones (solicitados: {top_codons})")
        
        plt.figure(figsize=(12, 8))
        x = np.arange(len(top_codones_df))
        width = 0.35
        
        plt.bar(x - width/2, top_codones_df['frecuencia_salmonella'], width, 
                label='Salmonella', alpha=0.8)
        plt.bar(x + width/2, top_codones_df['frecuencia_gallus'], width, 
                label='Gallus', alpha=0.8)
        
        plt.xlabel('Codones')
        plt.ylabel('Frecuencia de Uso')
        plt.title(f'Top {top_codons} Codones Más Frecuentes - Comparación entre Especies')
        plt.xticks(x, top_codones_df['codon'], rotation=45)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        # Usar path relativo porque ya estamos en el directorio temporal
        plt.savefig('results/graficos/uso_codones_top20.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"[DEBUG] Gráfico de top {top_codons} codones guardado correctamente")
    
    def get_status(self, job_id: str) -> Dict:
        """
        Obtiene el estado de un trabajo en modo API.
        
        Parámetros:
        -----------
        job_id : str
            ID del trabajo
        
        Retorna:
        --------
        dict
            {'status': str, 'message': str}
        """
        if self.mode == "LOCAL":
            return {'status': 'COMPLETED', 'message': 'Análisis completado'}
        
        url = f"{self.base_url}/status/{job_id}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'status': 'FAILED', 'message': f"Error al obtener estado: {e}"}
    
    def get_results(self, job_id: Optional[str] = None) -> Dict:
        """
        Obtiene los resultados de un análisis.
        
        Parámetros:
        -----------
        job_id : str, optional
            ID del trabajo (solo en modo API)
        
        Retorna:
        --------
        dict
            Resultados del análisis con paths o URLs
        """
        if self.mode == "API":
            url = f"{self.base_url}/results/{job_id}"
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                raise Exception(f"Error al obtener resultados: {e}")
        else:
            # En modo local, los resultados ya están en el último análisis
            # Esta función se usa después de start_analysis
            pass
    
    def cleanup(self):
        """Limpia archivos temporales."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            self.temp_dir = None

