import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.stats import gaussian_kde
import os

def grafico_gc(df, nombre_salida):
    """
    Genera gráfico de distribución de contenido GC para una especie.
    
    Parámetros:
    -----------
    df : pandas.DataFrame
        DataFrame con columna 'porcentaje_GC'
    nombre_salida : str
        Nombre de la especie ('salmonella' o 'gallus')
        
    Genera:
    -------
    results/graficos/{nombre_salida}_gc.png
    """
    plt.figure(figsize=(6,4))
    sns.histplot(df["porcentaje_GC"], kde=True, color="green")
    plt.title(f"Distribución del contenido GC - {nombre_salida.capitalize()}")
    plt.xlabel("%GC")
    plt.ylabel("Frecuencia")
    # Asegura que la carpeta existe
    os.makedirs("results/graficos", exist_ok=True)
    plt.savefig(f"results/graficos/{nombre_salida}_gc.png")
    plt.close()
    print(f" Gráfico GC generado: {nombre_salida}_gc.png")

def distribucion_longitudes(df_metricas):
    """
    Genera histograma de distribución de longitudes de secuencias.
    
    Parámetros:
    -----------
    df_metricas : pandas.DataFrame
        DataFrame cargado desde results/resumen_metricas.csv
        
    Genera:
    -------
    results/graficos/distribucion_longitudes.png
    """
    plt.figure(figsize=(10, 6))
    plt.hist(df_metricas['longitud'], bins=50, alpha=0.7, color='skyblue', edgecolor='black')
    plt.xlabel('Longitud de secuencia (pb)')
    plt.ylabel('Frecuencia')
    plt.title('Distribución de Longitudes de Secuencias')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('results/graficos/distribucion_longitudes.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Gráfico 1: Distribución de longitudes generado")

def distribucion_gc(df_metricas):
    """
    Genera histograma de distribución de contenido GC.
    
    Parámetros:
    -----------
    df_metricas : pandas.DataFrame  
        DataFrame cargado desde results/resumen_metricas.csv
        
    Genera:
    -------
    results/graficos/distribucion_gc.png
    """
    plt.figure(figsize=(10, 6))
    plt.hist(df_metricas['porcentaje_GC'], bins=50, alpha=0.7, color='lightgreen', edgecolor='black')
    plt.xlabel('Contenido de GC (%)')
    plt.ylabel('Frecuencia')
    plt.title('Distribución del Contenido de GC')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('results/graficos/distribucion_gc.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(" Gráfico 2: Distribución de GC generado")

def relacion_longitud_gc(df_metricas):
    """
    Genera gráfico de dispersión entre longitud y contenido GC.
    Usa densidad para colorear puntos y mostrar patrones.
    
    Parámetros:
    -----------
    df_metricas : pandas.DataFrame
        DataFrame cargado desde results/resumen_metricas.csv
        
    Genera:
    -------
    results/graficos/relacion_longitud_gc.png
    """
    plt.figure(figsize=(10, 6))
    x = df_metricas['longitud']
    y = df_metricas['porcentaje_GC']
    xy = np.vstack([x, y])
    z = gaussian_kde(xy)(xy)

    scatter = plt.scatter(x, y, c=z, s=10, alpha=0.6, cmap='viridis')
    plt.colorbar(scatter, label='Densidad')
    plt.xlabel('Longitud (pb)')
    plt.ylabel('Contenido GC (%)')
    plt.title('Relación entre Longitud y Contenido de GC')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('results/graficos/relacion_longitud_gc.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(" Gráfico 3: Relación longitud-GC generado")

def uso_codones_top20(df_codones):
    """
    Genera gráfico de barras comparando los 20 codones más frecuentes entre especies.
    
    Parámetros:
    -----------
    df_codones : pandas.DataFrame
        DataFrame cargado desde results/codon_usage.csv
        
    Genera:
    -------
    results/graficos/uso_codones_top20.png
    """
    # Calcular promedio para seleccionar top 20
    df_codones['promedio'] = (df_codones['frecuencia_salmonella'] + df_codones['frecuencia_gallus']) / 2
    top_codones = df_codones.nlargest(20, 'promedio')

    plt.figure(figsize=(12, 8))
    x = np.arange(len(top_codones))
    width = 0.35

    plt.bar(x - width/2, top_codones['frecuencia_salmonella'], width, label='Salmonella', alpha=0.8)
    plt.bar(x + width/2, top_codones['frecuencia_gallus'], width, label='Gallus', alpha=0.8)

    plt.xlabel('Codones')
    plt.ylabel('Frecuencia de Uso')
    plt.title('Top 20 Codones Más Frecuentes - Comparación entre Especies')
    plt.xticks(x, top_codones['codon'], rotation=45)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('results/graficos/uso_codones_top20.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(" Gráfico 4: Uso de codones top 20 generado")

def correlacion_codones(df_codones):
    """
    Genera gráfico de dispersión de correlación entre uso de codones de ambas especies.
    
    Parámetros:
    -----------
    df_codones : pandas.DataFrame
        DataFrame cargado desde results/codon_usage.csv
        
    Genera:
    -------
    results/graficos/correlacion_codones.png
    """
    plt.figure(figsize=(8, 8))
    plt.scatter(df_codones['frecuencia_salmonella'], 
               df_codones['frecuencia_gallus'], 
               alpha=0.6, s=50)

    max_val = max(df_codones['frecuencia_salmonella'].max(), 
                 df_codones['frecuencia_gallus'].max())
    plt.plot([0, max_val], [0, max_val], 'r--', alpha=0.8, label='Línea de correlación perfecta')

    plt.xlabel('Frecuencia en Salmonella')
    plt.ylabel('Frecuencia en Gallus')
    plt.title('Correlación del Uso de Codones entre Salmonella y Gallus')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('results/graficos/correlacion_codones.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(" Gráfico 5: Correlación de codones generado")

def heatmap_codones(df_codones):
    """
    Genera heatmap del uso de codones organizado por familias.
    
    Parámetros:
    -----------
    df_codones : pandas.DataFrame
        DataFrame cargado desde results/codon_usage.csv
        
    Genera:
    -------
    results/graficos/heatmap_codones.png
    """
    # Reorganizar datos en matriz 16x16 para heatmap
    codon_matrix = df_codones.pivot_table(index=df_codones.index//16, 
                                        columns=df_codones.index%16, 
                                        values='frecuencia_salmonella')

    plt.figure(figsize=(12, 8))
    sns.heatmap(codon_matrix, cmap='YlOrRd', cbar_kws={'label': 'Frecuencia de Uso'})
    plt.title('Heatmap de Uso de Codones en Salmonella\n(Organizado por Familias de Codones)')
    plt.xlabel('Posición en Familia de Codones')
    plt.ylabel('Familia de Codones')
    plt.tight_layout()
    plt.savefig('results/graficos/heatmap_codones.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(" Gráfico 6: Heatmap de codones generado")

def distribucion_acumulativa_longitudes(df_metricas):
    """
    Genera gráfico de distribución acumulativa con percentiles marcados.
    
    Parámetros:
    -----------
    df_metricas : pandas.DataFrame
        DataFrame cargado desde results/resumen_metricas.csv
        
    Genera:
    -------
    results/graficos/distribucion_acumulativa_longitudes.png
    """
    plt.figure(figsize=(10, 6))
    sorted_lengths = np.sort(df_metricas['longitud'])
    y_vals = np.arange(len(sorted_lengths)) / float(len(sorted_lengths))

    plt.plot(sorted_lengths, y_vals, linewidth=2, color='purple')
    plt.xlabel('Longitud de Secuencia (pb)')
    plt.ylabel('Proporción Acumulativa de Genes')
    plt.title('Distribución Acumulativa de Longitudes de Genes')
    plt.grid(True, alpha=0.3)

    # Marcar percentiles importantes
    for percentile in [25, 50, 75, 90]:
        value = np.percentile(df_metricas['longitud'], percentile)
        plt.axvline(x=value, color='red', linestyle='--', alpha=0.7)
        plt.text(value, 0.5, f' {percentile}%: {int(value)} pb', 
                 rotation=90, verticalalignment='center')

    plt.tight_layout()
    plt.savefig('results/graficos/distribucion_acumulativa_longitudes.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(" Gráfico 7: Distribución acumulativa generado")

def generar_todos_los_graficos():
    """
    Función principal que genera los 7 gráficos avanzados de análisis.
    
    Flujo:
    1. Carga datos desde archivos CSV
    2. Genera cada gráfico individualmente
    3. Proporciona feedback del progreso
    
    Dependencias:
    - results/resumen_metricas.csv
    - results/codon_usage.csv
    """
    print("Cargando datos para visualización...")
    
    # Asegurar que la carpeta de gráficos existe
    os.makedirs('results/graficos', exist_ok=True)
    
    # Cargar datos desde archivos CSV
    df_metricas = pd.read_csv('results/resumen_metricas.csv')
    df_codones = pd.read_csv('results/codon_usage.csv')
    
    print("Generando gráficos avanzados...")
    
    # Generar los 7 gráficos avanzados
    distribucion_longitudes(df_metricas)
    distribucion_gc(df_metricas)
    relacion_longitud_gc(df_metricas)
    uso_codones_top20(df_codones)
    correlacion_codones(df_codones)
    heatmap_codones(df_codones)
    distribucion_acumulativa_longitudes(df_metricas)
    
    print("\n¡Todos los gráficos han sido generados exitosamente!")
    print("\n Archivos creados en 'results/graficos/':")
    print("1. distribucion_longitudes.png")
    print("2. distribucion_gc.png")
    print("3. relacion_longitud_gc.png")
    print("4. uso_codones_top20.png")
    print("5. correlacion_codones.png")
    print("6. heatmap_codones.png")
    print("7. distribucion_acumulativa_longitudes.png")
    print("8. gallus_gc.png")
    print("9. salmonella_gc.png")
