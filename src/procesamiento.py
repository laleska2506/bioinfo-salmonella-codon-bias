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
        # Intentar detectar y manejar la codificación del archivo
        # Primero intentamos con UTF-8, luego con otras codificaciones comunes
        codificaciones = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        archivo_parseado = False
        
        for encoding in codificaciones:
            try:
                # Abrir el archivo con la codificación especificada y parsearlo
                with open(ruta_archivo, 'r', encoding=encoding) as f:
                    registros = list(SeqIO.parse(f, "fasta"))
                    archivo_parseado = True
                    break
            except UnicodeDecodeError:
                # Intentar con la siguiente codificación
                continue
            except Exception:
                # Si es otro tipo de error, intentar con la siguiente codificación
                continue
        
        # Si no se pudo parsear con ninguna codificación, intentar con el método por defecto
        if not archivo_parseado:
            try:
                registros = list(SeqIO.parse(ruta_archivo, "fasta"))
            except UnicodeDecodeError as e:
                # Error de codificación - proporcionar mensaje claro
                raise ValueError(
                    "El archivo contiene caracteres especiales (como acentos, ñ, etc.) que no se pueden leer correctamente. "
                    "Por favor, guarde el archivo en formato UTF-8 o ASCII antes de subirlo. "
                    "Puede hacer esto abriendo el archivo en un editor de texto y guardándolo como 'UTF-8' o 'ASCII'."
                )
        
        # Verificar que se encontraron secuencias
        if len(registros) == 0:
            raise ValueError(f"El archivo FASTA no contiene secuencias válidas: {ruta_archivo}. Verifique que el archivo tenga el formato correcto.")
        
        for registro in registros:
            # Verificar que el registro tenga un ID válido
            if not registro.id or len(registro.id.strip()) == 0:
                raise ValueError(f"El archivo FASTA contiene secuencias sin identificador válido. Verifique el formato del archivo.")
            
            # Guardar ID y secuencia (sin normalizar aún)
            secuencias.append((registro.id, str(registro.seq)))
        
        print(f" Cargadas {len(secuencias)} secuencias desde {ruta_archivo}")
        
        # Limpiar y normalizar las secuencias
        secuencias = limpiar_y_normalizar_secuencias(secuencias)
        
    except ValueError as e:
        # Re-lanzar ValueError con mensaje descriptivo (ya incluye mensajes claros)
        raise
    except UnicodeDecodeError as e:
        # Error de codificación - proporcionar mensaje claro y útil
        raise ValueError(
            "El archivo contiene caracteres especiales (como acentos, ñ, etc.) que no se pueden leer correctamente. "
            "Por favor, guarde el archivo en formato UTF-8 o ASCII antes de subirlo. "
            "Puede hacer esto abriendo el archivo en un editor de texto y guardándolo como 'UTF-8' o 'ASCII'."
        )
    except Exception as e:
        # Capturar otros errores de parsing (archivo corrupto, formato inválido, etc.)
        error_msg = str(e).lower()
        
        # Detectar específicamente errores de codificación
        if "codec" in error_msg or "decode" in error_msg or "ascii" in error_msg or "utf" in error_msg:
            raise ValueError(
                "El archivo contiene caracteres especiales (como acentos, ñ, etc.) que no se pueden leer correctamente. "
                "Por favor, guarde el archivo en formato UTF-8 o ASCII antes de subirlo. "
                "Puede hacer esto abriendo el archivo en un editor de texto y guardándolo como 'UTF-8' o 'ASCII'."
            )
        elif "empty" in error_msg or "no sequences" in error_msg:
            raise ValueError(f"El archivo FASTA está vacío o no contiene secuencias válidas: {ruta_archivo}")
        elif "format" in error_msg or "parse" in error_msg:
            raise ValueError(f"El archivo FASTA está corrupto o tiene un formato inválido: {ruta_archivo}. Verifique que el archivo tenga el formato FASTA correcto.")
        else:
            raise ValueError(f"Error al cargar el archivo FASTA (archivo posiblemente corrupto): {ruta_archivo}. Error: {str(e)}")
    
    return secuencias

def limpiar_y_normalizar_secuencias(secuencias):
    """
    Limpia y normaliza las secuencias FASTA.
    
    Esta función:
    - Convierte todas las secuencias a mayúsculas
    - Elimina espacios, saltos de línea, tabs y otros caracteres de formato
    - Valida que solo contenga caracteres válidos (A, T, C, G, N)
    - Si encuentra caracteres inválidos, lanza un error descriptivo
    
    Parámetros:
    -----------
    secuencias : list
        Lista de tuplas (id_secuencia, secuencia) donde:
        - id_secuencia: es el ID de la secuencia
        - secuencia: es la secuencia de ADN (puede contener espacios, minúsculas, etc.)
        
    Retorna:
    --------
    list
        Lista de tuplas (id_secuencia, secuencia_limpia) con secuencias normalizadas
        
    Lanza:
    ------
    ValueError: Si se encuentran caracteres inválidos en las secuencias (no A, T, C, G, N)
    """
    nucleotidos_validos = {'A', 'T', 'C', 'G', 'N'}
    secuencias_limpias = []
    caracteres_invalidos_encontrados = set()
    secuencias_con_error = []
    
    for id_sec, sec in secuencias:
        # Normalizar: convertir a mayúsculas y eliminar espacios, saltos de línea, tabs, etc.
        sec_limpia = sec.upper().replace(' ', '').replace('\n', '').replace('\r', '').replace('\t', '')
        
        # Eliminar cualquier otro carácter que no sea un nucleótido válido
        # Solo mantener A, T, C, G, N
        sec_limpia = ''.join(c for c in sec_limpia if c in nucleotidos_validos)
        
        # Validar caracteres - solo permitir A, T, C, G, N
        caracteres_unicos = set(sec_limpia)
        caracteres_invalidos = caracteres_unicos - nucleotidos_validos
        
        if caracteres_invalidos:
            # Agregar los caracteres inválidos encontrados al conjunto global
            caracteres_invalidos_encontrados.update(caracteres_invalidos)
            secuencias_con_error.append(id_sec)
            print(f" Advertencia: Secuencia {id_sec} contiene caracteres inválidos: {sorted(caracteres_invalidos)}")
        
        secuencias_limpias.append((id_sec, sec_limpia))
    
    # Si se encontraron caracteres inválidos, lanzar error descriptivo
    if caracteres_invalidos_encontrados:
        caracteres_lista = sorted(caracteres_invalidos_encontrados)
        caracteres_str = ', '.join([f"'{c}'" for c in caracteres_lista])
        
        # Mostrar algunas secuencias con error como ejemplo
        ejemplos = secuencias_con_error[:5]  # Primeras 5 secuencias con error
        ejemplos_str = ', '.join(ejemplos)
        if len(secuencias_con_error) > 5:
            ejemplos_str += f" y {len(secuencias_con_error) - 5} más"
        
        raise ValueError(
            f"El archivo está corrupto porque se han identificado caracteres inválidos en las secuencias: {caracteres_str}. "
            f"Las secuencias FASTA solo pueden contener las letras A, T, C, G y N (para bases ambiguas). "
            f"Se encontraron caracteres inválidos en {len(secuencias_con_error)} secuencia(s), por ejemplo: {ejemplos_str}. "
            f"Por favor, verifique que el archivo contenga solo secuencias de ADN válidas."
        )
    
    print(f" Secuencias normalizadas: {len(secuencias_limpias)} secuencias procesadas correctamente")
    return secuencias_limpias

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