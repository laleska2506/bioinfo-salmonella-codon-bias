"""
Utilidad para comprimir resultados de análisis en un archivo ZIP.
"""
import os
import zipfile
from pathlib import Path
from typing import List, Optional


def crear_zip_resultados(
    directorio_resultados: str,
    archivo_salida: Optional[str] = None,
    incluir_csv: bool = True,
    incluir_graficos: bool = True
) -> str:
    """
    Crea un archivo ZIP con los resultados del análisis.
    
    Parámetros:
    -----------
    directorio_resultados : str
        Ruta al directorio de resultados (debe contener resumen_metricas.csv, 
        codon_usage.csv y graficos/)
    archivo_salida : str, optional
        Ruta del archivo ZIP de salida. Si no se proporciona, se usa 
        'resultados_analisis.zip' en el directorio de resultados.
    incluir_csv : bool
        Si True, incluye los archivos CSV
    incluir_graficos : bool
        Si True, incluye los gráficos PNG
    
    Retorna:
    --------
    str
        Ruta del archivo ZIP creado
    """
    resultados_path = Path(directorio_resultados)
    
    if not resultados_path.exists():
        raise ValueError(f"El directorio de resultados no existe: {directorio_resultados}")
    
    # Determinar nombre del archivo ZIP
    if archivo_salida is None:
        archivo_salida = str(resultados_path / "resultados_analisis.zip")
    else:
        archivo_salida = str(Path(archivo_salida))
    
    # Crear archivo ZIP
    with zipfile.ZipFile(archivo_salida, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Agregar archivos CSV
        if incluir_csv:
            csv_files = [
                resultados_path / "resumen_metricas.csv",
                resultados_path / "codon_usage.csv",
            ]
            for csv_file in csv_files:
                if csv_file.exists():
                    zipf.write(csv_file, csv_file.name)
        
        # Agregar gráficos
        if incluir_graficos:
            graficos_dir = resultados_path / "graficos"
            if graficos_dir.exists():
                for png_file in graficos_dir.glob("*.png"):
                    # Guardar en subdirectorio graficos/ dentro del ZIP
                    zipf.write(png_file, f"graficos/{png_file.name}")
    
    return archivo_salida


def crear_zip_desde_paths(
    archivos: List[str],
    archivo_salida: str
) -> str:
    """
    Crea un archivo ZIP desde una lista de paths de archivos.
    
    Parámetros:
    -----------
    archivos : List[str]
        Lista de rutas de archivos a incluir en el ZIP
    archivo_salida : str
        Ruta del archivo ZIP de salida
    
    Retorna:
    --------
    str
        Ruta del archivo ZIP creado
    """
    with zipfile.ZipFile(archivo_salida, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for archivo in archivos:
            archivo_path = Path(archivo)
            if archivo_path.exists():
                # Mantener estructura de directorios relativa
                if archivo_path.is_file():
                    zipf.write(archivo_path, archivo_path.name)
                else:
                    # Si es un directorio, agregar todos los archivos recursivamente
                    for file_path in archivo_path.rglob("*"):
                        if file_path.is_file():
                            # Mantener estructura relativa
                            arcname = file_path.relative_to(archivo_path.parent)
                            zipf.write(file_path, arcname)
    
    return archivo_salida

