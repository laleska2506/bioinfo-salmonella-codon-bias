import pandas as pd
from collections import Counter

def calcular_uso_codones(secuencias, etiqueta):
    """
    Calcula la frecuencia de uso de codones para una lista de secuencias.
    
    Parámetros:
    -----------
    secuencias : list
        Lista de tuplas (id_secuencia, secuencia) cargada desde FASTA
    etiqueta : str
        Etiqueta para identificar el conjunto de secuencias ('salmonella' o 'gallus')
        
    Retorna:
    --------
    pandas.DataFrame
        DataFrame con las columnas:
        - codon: el codon (en mayúsculas)
        - frecuencia_{etiqueta}: frecuencia relativa del codon
        
    Genera:
    -------
    results/codon_usage.csv (cuando se combina con los datos de la otra especie)
    """
    # Contador para todos los codones
    contador_codones = Counter()
    total_codones = 0
    
    for _, sec in secuencias:
        # Dividir la secuencia en codones (triplets)
        # Asumimos que la secuencia está en frame correcto
        codones = [sec[i:i+3] for i in range(0, len(sec) - 2, 3)]
        
        # Filtrar solo codones completos (de 3 bases)
        codones_completos = [c for c in codones if len(c) == 3]
        
        # Actualizar contadores
        contador_codones.update(codones_completos)
        total_codones += len(codones_completos)
    
    # Calcular frecuencias relativas
    frecuencias = {}
    for codon, count in contador_codones.items():
        frecuencias[codon] = count / total_codones if total_codones > 0 else 0
    
    # Crear DataFrame ordenado
    df = pd.DataFrame(list(frecuencias.items()), columns=['codon', f'frecuencia_{etiqueta}'])
    df = df.sort_values('codon').reset_index(drop=True)
    
    print(f" Calculado uso de codones para {etiqueta}: {total_codones} codones analizados")
    
    return df

def analizar_bias_codones(df_codones, especie):
    """
    Analiza el bias de uso de codones para una especie usando codon_usage.csv.
    
    Parámetros:
    -----------
    df_codones : pandas.DataFrame
        DataFrame cargado desde results/codon_usage.csv
    especie : str
        Nombre de la especie a analizar ('salmonella' o 'gallus')
        
    Retorna:
    --------
    dict
        Diccionario con métricas de bias
    """
    columna_frecuencia = f'frecuencia_{especie}'
    
    # Codones más y menos usados
    codones_mas_usados = df_codones.nlargest(10, columna_frecuencia)[['codon', columna_frecuencia]]
    codones_menos_usados = df_codones.nsmallest(10, columna_frecuencia)[['codon', columna_frecuencia]]
    
    # Calcular entropía (medida de diversidad)
    frecuencias = df_codones[columna_frecuencia].values
    entropia = -sum(f * np.log2(f) for f in frecuencias if f > 0)
    
    resultado = {
        'codones_mas_usados': codones_mas_usados,
        'codones_menos_usados': codones_menos_usados,
        'entropia': entropia,
        'total_codones_diferentes': len(df_codones)
    }
    
    print(f" Análisis de bias de codones completado para {especie}")
    print(f"  Entropía: {entropia:.4f}")
    print(f"  Codones diferentes: {len(df_codones)}")
    
    return resultado

def comparar_uso_codones_especies(df_codones_salmonella, df_codones_gallus):
    """
    Compara el uso de codones entre dos especies y genera codon_usage.csv.
    
    Parámetros:
    -----------
    df_codones_salmonella : pandas.DataFrame
        DataFrame con frecuencias de Salmonella
    df_codones_gallus : pandas.DataFrame
        DataFrame con frecuencias de Gallus
        
    Retorna:
    --------
    pandas.DataFrame
        DataFrame combinado que se guarda como results/codon_usage.csv
    """
    # Combinar DataFrames
    df_combinado = pd.merge(
        df_codones_salmonella, 
        df_codones_gallus, 
        on='codon', 
        how='outer'
    ).fillna(0)
    
    # Calcular diferencia absoluta
    df_combinado['diferencia_absoluta'] = abs(
        df_combinado['frecuencia_salmonella'] - df_combinado['frecuencia_gallus']
    )
    
    # Ordenar por diferencia (mayor a menor)
    df_combinado = df_combinado.sort_values('diferencia_absoluta', ascending=False)
    
    print(" Comparación de uso de codones entre especies completada")
    print(f"  Diferencia promedio: {df_combinado['diferencia_absoluta'].mean():.6f}")
    print(f"  Codones con mayor diferencia: {', '.join(df_combinado.head(3)['codon'].tolist())}")
    
    return df_combinado

def generar_tabla_codones_aminoacidos():
    """
    Genera un mapeo de codones a aminoácidos usando el código genético estándar.
    
    Retorna:
    --------
    dict
        Diccionario que mapea cada codon a su aminoácido correspondiente
    """
    codigo_genetico = {
        'ATA':'I', 'ATC':'I', 'ATT':'I', 'ATG':'M',
        'ACA':'T', 'ACC':'T', 'ACG':'T', 'ACT':'T',
        'AAC':'N', 'AAT':'N', 'AAA':'K', 'AAG':'K',
        'AGC':'S', 'AGT':'S', 'AGA':'R', 'AGG':'R',
        'CTA':'L', 'CTC':'L', 'CTG':'L', 'CTT':'L',
        'CCA':'P', 'CCC':'P', 'CCG':'P', 'CCT':'P',
        'CAC':'H', 'CAT':'H', 'CAA':'Q', 'CAG':'Q',
        'CGA':'R', 'CGC':'R', 'CGG':'R', 'CGT':'R',
        'GTA':'V', 'GTC':'V', 'GTG':'V', 'GTT':'V',
        'GCA':'A', 'GCC':'A', 'GCG':'A', 'GCT':'A',
        'GAC':'D', 'GAT':'D', 'GAA':'E', 'GAG':'E',
        'GGA':'G', 'GGC':'G', 'GGG':'G', 'GGT':'G',
        'TCA':'S', 'TCC':'S', 'TCG':'S', 'TCT':'S',
        'TTC':'F', 'TTT':'F', 'TTA':'L', 'TTG':'L',
        'TAC':'Y', 'TAT':'Y', 'TAA':'*', 'TAG':'*',
        'TGC':'C', 'TGT':'C', 'TGA':'*', 'TGG':'W'
    }
    
    return codigo_genetico