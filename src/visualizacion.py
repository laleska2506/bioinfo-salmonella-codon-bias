import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.stats import gaussian_kde
import os

def grafico_gc_gallus():
    """GF1: Distribución del contenido GC - Gallus"""
    try:
        df = pd.read_csv('results/resumen_metricas_gallus.csv')
        plt.figure(figsize=(6,4))
        sns.histplot(df["porcentaje_GC"], kde=True, color="green")
        plt.title(f"Distribución del contenido GC - Gallus")
        plt.xlabel("%GC")
        plt.ylabel("Frecuencia")
        os.makedirs("results/graficos", exist_ok=True)
        plt.savefig(f"results/graficos/gallus_gc.png")
        plt.close()
        print("✓ Gráfico GF1: Distribución GC Gallus generado")
    except Exception as e:
        print(f"Error en GF1: {e}")

def grafico_gc_salmonella():
    """GF2: Distribución del contenido GC - Salmonella"""
    try:
        df = pd.read_csv('results/resumen_metricas_salmonella.csv')
        plt.figure(figsize=(6,4))
        sns.histplot(df["porcentaje_GC"], kde=True, color="blue")
        plt.title(f"Distribución del contenido GC - Salmonella")
        plt.xlabel("%GC")
        plt.ylabel("Frecuencia")
        os.makedirs("results/graficos", exist_ok=True)
        plt.savefig(f"results/graficos/salmonella_gc.png")
        plt.close()
        print("✓ Gráfico GF2: Distribución GC Salmonella generado")
    except Exception as e:
        print(f"Error en GF2: {e}")

def grafico_gc_comparativa():
    """GF3: Distribución del contenido GC - Comparativa"""
    try:
        df_sal = pd.read_csv('results/resumen_metricas_salmonella.csv')
        df_gal = pd.read_csv('results/resumen_metricas_gallus.csv')
        
        plt.figure(figsize=(8,5))
        sns.histplot(df_sal["porcentaje_GC"], kde=True, color="blue", alpha=0.6, label="Salmonella")
        sns.histplot(df_gal["porcentaje_GC"], kde=True, color="green", alpha=0.6, label="Gallus")
        plt.title("Comparativa de Distribución de GC entre Especies")
        plt.xlabel("%GC")
        plt.ylabel("Frecuencia")
        plt.legend()
        os.makedirs("results/graficos", exist_ok=True)
        plt.savefig(f"results/graficos/comparativa_gc.png")
        plt.close()
        print("✓ Gráfico GF3: Comparativa GC generado")
    except Exception as e:
        print(f"Error en GF3: {e}")

def distribucion_acumulativa_longitudes():
    """GF4: Distribución Acumulativa de Longitudes de Genes"""
    try:
        df_metricas = pd.read_csv('results/resumen_metricas.csv')
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
        print("✓ Gráfico GF4: Distribución acumulativa generado")
    except Exception as e:
        print(f"Error en GF4: {e}")

def distribucion_longitudes():
    """GF5: Distribución de Longitudes de Secuencias"""
    try:
        df_metricas = pd.read_csv('results/resumen_metricas.csv')
        plt.figure(figsize=(10, 6))
        plt.hist(df_metricas['longitud'], bins=50, alpha=0.7, color='skyblue', edgecolor='black')
        plt.xlabel('Longitud de secuencia (pb)')
        plt.ylabel('Frecuencia')
        plt.title('Distribución de Longitudes de Secuencias')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('results/graficos/distribucion_longitudes.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Gráfico GF5: Distribución de longitudes generado")
    except Exception as e:
        print(f"Error en GF5: {e}")

def uso_codones_top15():
    """GF6: Top 15 Codones Más Frecuentes"""
    try:
        df_codones = pd.read_csv('results/codon_usage.csv')
        # Calcular promedio para seleccionar top 15
        df_codones['promedio'] = (df_codones['frecuencia_salmonella'] + df_codones['frecuencia_gallus']) / 2
        top_codones = df_codones.nlargest(15, 'promedio')

        plt.figure(figsize=(12, 8))
        x = np.arange(len(top_codones))
        width = 0.35

        plt.bar(x - width/2, top_codones['frecuencia_salmonella'], width, label='Salmonella', alpha=0.8)
        plt.bar(x + width/2, top_codones['frecuencia_gallus'], width, label='Gallus', alpha=0.8)

        plt.xlabel('Codones')
        plt.ylabel('Frecuencia de Uso')
        plt.title('Top 15 Codones Más Frecuentes - Comparación entre Especies')
        plt.xticks(x, top_codones['codon'], rotation=45)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('results/graficos/uso_codones_top15.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Gráfico GF6: Uso de codones top 15 generado")
    except Exception as e:
        print(f"Error en GF6: {e}")

def correlacion_codones():
    """GF7: Correlación del Uso de Codones entre Salmonella y Gallus"""
    try:
        df_codones = pd.read_csv('results/codon_usage.csv')
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
        print("✓ Gráfico GF7: Correlación de codones generado")
    except Exception as e:
        print(f"Error en GF7: {e}")

def heatmap_codones():
    """GF8: Heatmap de Uso de Codones en Salmonella"""
    try:
        df_codones = pd.read_csv('results/codon_usage.csv')
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
        print("✓ Gráfico GF8: Heatmap de codones generado")
    except Exception as e:
        print(f"Error en GF8: {e}")

def relacion_longitud_gc():
    """GF9: Relación entre Longitud y Contenido GC"""
    try:
        df_metricas = pd.read_csv('results/resumen_metricas.csv')
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
        print("✓ Gráfico GF9: Relación longitud-GC generado")
    except Exception as e:
        print(f"Error en GF9: {e}")

def generar_todos_los_graficos():
    """
    Función principal que genera los 9 gráficos exactos
    """
    print("Iniciando generación de 9 gráficos específicos...")
    
    # Asegurar que la carpeta de gráficos existe
    os.makedirs('results/graficos', exist_ok=True)
    
    # Generar los 9 gráficos en orden
    grafico_gc_gallus()        # GF1
    grafico_gc_salmonella()    # GF2  
    grafico_gc_comparativa()   # GF3
    distribucion_acumulativa_longitudes()  # GF4
    distribucion_longitudes()              # GF5
    uso_codones_top15()                    # GF6
    correlacion_codones()                  # GF7
    heatmap_codones()                      # GF8
    relacion_longitud_gc()                 # GF9
    
    print("\n¡Todos los 9 gráficos han sido generados exitosamente!")
    print("\n Archivos creados en 'results/graficos/':")
    archivos = [
        "1. gallus_gc.png (GF1)",
        "2. salmonella_gc.png (GF2)", 
        "3. comparativa_gc.png (GF3)",
        "4. distribucion_acumulativa_longitudes.png (GF4)",
        "5. distribucion_longitudes.png (GF5)",
        "6. uso_codones_top15.png (GF6)",
        "7. correlacion_codones.png (GF7)", 
        "8. heatmap_codones.png (GF8)",
        "9. relacion_longitud_gc.png (GF9)"
    ]
    for archivo in archivos:
        print(f"   {archivo}")
