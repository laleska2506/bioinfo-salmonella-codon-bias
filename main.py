# Importaciones simplificadas gracias al __init__.py
from src import (
    cargar_secuencias, 
    calcular_metricas_basicas, 
    calcular_uso_codones,
    grafico_gc, 
    generar_todos_los_graficos
)
import pandas as pd
import os

def main():
    
    print("Iniciando analisis de secuencias de Salmonella y Gallus")
    print("=" * 60)
    
    # Crear carpetas necesarias si no existen
    os.makedirs('results/graficos', exist_ok=True)
    
    try:
        # === 1. CARGA DE SECUENCIAS ===
        print("Paso 1: Cargando secuencias desde archivos FASTA...")
        salmonella = cargar_secuencias("data/salmonella_genes.fasta")
        gallus = cargar_secuencias("data/gallus_genes.fasta")
        print("Secuencias cargadas: {} de Salmonella, {} de Gallus".format(
            len(salmonella), len(gallus)))
        
        # === 2. CALCULO DE METRICAS BASICAS ===
        print("\nPaso 2: Calculando metricas basicas...")
        df_salmonella = calcular_metricas_basicas(salmonella)
        df_gallus = calcular_metricas_basicas(gallus)
        
        # Combinar resultados de ambas especies
        df_metricas = pd.concat([df_salmonella, df_gallus], ignore_index=True)
        df_metricas.to_csv("results/resumen_metricas.csv", index=False)
        print("Metricas guardadas en: results/resumen_metricas.csv")
        
        # === 3. ANALISIS DE USO DE CODONES ===
        print("\nPaso 3: Analizando uso de codones...")
        df_codones_salmonella = calcular_uso_codones(salmonella, "salmonella")
        df_codones_gallus = calcular_uso_codones(gallus, "gallus")
        
        # Combinar datos de uso de codones
        df_codones = (pd.merge(df_codones_salmonella, df_codones_gallus, on="codon", how="outer")
                      .fillna(0)
                      .sort_values("codon")
                      .reset_index(drop=True)
        )
        df_codones.to_csv("results/codon_usage.csv", index=False)
        print("Uso de codones guardado en: results/codon_usage.csv")
        
        # === 4. GENERACION DE GRAFICOS BASICOS ===
        print("\nPaso 4: Generando graficos basicos de GC...")
        grafico_gc(df_salmonella, "salmonella")
        grafico_gc(df_gallus, "gallus")
        
        # === 5. GENERACION DE GRAFICOS AVANZADOS ===
        print("\nPaso 5: Generando graficos avanzados de analisis...")
        print("-" * 50)
        generar_todos_los_graficos()
        
        # Mensaje de finalización
        print("\nAnalisis completado exitosamente")
        print("Resultados guardados en la carpeta: results/")
        print("Graficos guardados en: results/graficos/")
        
    except FileNotFoundError as e:
        print("Error: No se pudo encontrar el archivo: {}".format(e.filename))
        print("Asegurese de que los archivos FASTA esten en la carpeta data/")
        
    except Exception as e:
        print("Error inesperado durante el analisis: {}".format(e))
        import traceback
        traceback.print_exc()
        print("Por favor, verifique la estructura del proyecto y los archivos de datos")

if __name__ == "__main__":
    main()