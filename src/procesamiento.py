from Bio import SeqIO
import pandas as pd
import os

def cargar_secuencias(ruta_archivo):
    """
    Carga secuencias desde un archivo FASTA.
    
    Parámetros:
    -----------
    ruta_archivo : str
        Ruta al archivo FASTA (ej: "data/salmonella_genes.fasta")
        
    Retorna:
    --------
    list
        Lista de tuplas (id_secuencia, secuencia) para cada secuencia en el archivo
        
    Conectado con:
    --------------
    - data/salmonella_genes.fasta
    - data/gallus_genes.fasta
    
    Lanza:
    ------
    FileNotFoundError: Si el archivo no existe
    ValueError: Si el archivo está corrupto o no es un FASTA válido
    """
    # Verificar que el archivo existe
    if not os.path.exists(ruta_archivo):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_archivo}")
    
    # Verificar que el archivo no esté vacío
    if os.path.getsize(ruta_archivo) == 0:
        raise ValueError(f"El archivo FASTA está vacío: {ruta_archivo}")
    
    secuencias = []
    try:
        # Intentar parsear el archivo FASTA
        registros = list(SeqIO.parse(ruta_archivo, "fasta"))
        
        # Verificar que se encontraron secuencias
        if len(registros) == 0:
            raise ValueError(f"El archivo FASTA no contiene secuencias válidas: {ruta_archivo}. Verifique que el archivo tenga el formato correcto.")
        
        for registro in registros:
            # Verificar que el registro tenga un ID válido
            if not registro.id or len(registro.id.strip()) == 0:
                raise ValueError(f"El archivo FASTA contiene secuencias sin identificador válido. Verifique el formato del archivo.")
            
            # Guardar ID y secuencia en mayúsculas
            secuencias.append((registro.id, str(registro.seq).upper()))
        
        print(f" Cargadas {len(secuencias)} secuencias desde {ruta_archivo}")
        
    except ValueError as e:
        # Re-lanzar ValueError con mensaje descriptivo
        raise ValueError(f"Error al procesar el archivo FASTA: {str(e)}")
    except Exception as e:
        # Capturar otros errores de parsing (archivo corrupto, formato inválido, etc.)
        error_msg = str(e).lower()
        if "empty" in error_msg or "no sequences" in error_msg:
            raise ValueError(f"El archivo FASTA está vacío o no contiene secuencias válidas: {ruta_archivo}")
        elif "format" in error_msg or "parse" in error_msg:
            raise ValueError(f"El archivo FASTA está corrupto o tiene un formato inválido: {ruta_archivo}. Error: {str(e)}")
        else:
            raise ValueError(f"Error al cargar el archivo FASTA (archivo posiblemente corrupto): {ruta_archivo}. Error: {str(e)}")
    
    return secuencias

def calcular_metricas_basicas(secuencias):
    """
    Calcula métricas básicas para una lista de secuencias.
    
    Parámetros:
    -----------
    secuencias : list
        Lista de tuplas (id_secuencia, secuencia) cargada desde FASTA
        
    Retorna:
    --------
    pandas.DataFrame
        DataFrame con las columnas:
        - id: identificador de la secuencia
        - longitud: longitud de la secuencia
        - porcentaje_GC: porcentaje de bases G y C en la secuencia
        
    Genera:
    -------
    results/resumen_metricas.csv (cuando se combina con los datos de Gallus)
    """
    datos = []
    
    for id_sec, sec in secuencias:
        # Calcular longitud
        longitud = len(sec)
        
        # Calcular contenido GC
        count_g = sec.count('G')
        count_c = sec.count('C')
        porcentaje_gc = (count_g + count_c) / longitud * 100 if longitud > 0 else 0
        
        # Almacenar resultados
        datos.append({
            'id': id_sec,
            'longitud': longitud,
            'porcentaje_GC': round(porcentaje_gc, 2)
        })
    
    # Crear DataFrame
    df = pd.DataFrame(datos)
    print(f" Calculadas métricas para {len(datos)} secuencias")
    
    return df

def validar_secuencias(secuencias):
    """
    Valida que las secuencias contengan solo caracteres de nucleótidos válidos.
    
    Parámetros:
    -----------
    secuencias : list
        Lista de tuplas (id_secuencia, secuencia) cargada desde FASTA
        
    Retorna:
    --------
    bool
        True si todas las secuencias son válidas, False en caso contrario
    """
    nucleotidos_validos = {'A', 'T', 'C', 'G', 'N'}
    
    for id_sec, sec in secuencias:
        sec_set = set(sec.upper())
        if not sec_set.issubset(nucleotidos_validos):
            print(f" Secuencia {id_sec} contiene caracteres inválidos: {sec_set - nucleotidos_validos}")
            return False
    
    print(" Todas las secuencias contienen solo nucleótidos válidos")
    return True