# Análisis de Secuencias Genéticas: Salmonella y Gallus

Proyecto de bioinformática para el análisis comparativo de secuencias genéticas entre *Salmonella* (bacteria) y *Gallus* (pollo). El proyecto incluye cálculo de métricas básicas, análisis de uso de codones y generación de visualizaciones estadísticas.

## 📋 Descripción

Este proyecto realiza un análisis bioinformático completo de secuencias genéticas, incluyendo:

- **Carga y procesamiento** de secuencias desde archivos FASTA
- **Cálculo de métricas básicas** (longitud, contenido GC, etc.)
- **Análisis de uso de codones** para identificar patrones de codificación
- **Visualización de datos** mediante gráficos estadísticos y comparativos
- **Comparación entre especies** (Salmonella vs Gallus)

## ✨ Características

### Procesamiento de Secuencias
- Carga de secuencias desde archivos FASTA
- Validación de secuencias
- Cálculo de métricas básicas (longitud, contenido GC)

### Análisis de Codones
- Cálculo de frecuencia de uso de codones
- Análisis de bias de codones
- Comparación de uso de codones entre especies
- Generación de tablas de codones y aminoácidos

### Visualización
- Distribución de longitudes de secuencias
- Distribución de contenido GC
- Relación entre longitud y contenido GC
- Análisis de uso de codones (top 20)
- Correlación de codones entre especies
- Heatmap de uso de codones
- Distribución acumulativa de longitudes

## 🔧 Requisitos

- Python 3.8 o superior
- Las siguientes librerías (ver `requeriments.txt`):
  - biopython >= 1.83
  - pandas >= 2.0
  - matplotlib >= 3.8
  - seaborn >= 0.13
  - numpy >= 1.26
  - scipy >= 1.11

## 📦 Instalación

1. **Clonar el repositorio** (o descargar el proyecto):
```bash
git clone <url-del-repositorio>
cd bioinfo_salmonella
```

2. **Crear un entorno virtual** (recomendado):
```bash
python -m venv venv
```

3. **Activar el entorno virtual**:
   - En Windows:
   ```bash
   venv\Scripts\activate
   ```
   - En Linux/Mac:
   ```bash
   source venv/bin/activate
   ```

4. **Instalar las dependencias**:
```bash
pip install -r requeriments.txt
```

## 🚀 Uso

### Ejecución del análisis completo

Para ejecutar el análisis completo de secuencias:

```bash
python main.py
```

Este script realizará:
1. Carga de secuencias desde `data/salmonella_genes.fasta` y `data/gallus_genes.fasta`
2. Cálculo de métricas básicas
3. Análisis de uso de codones
4. Generación de gráficos básicos y avanzados
5. Guardado de resultados en formato CSV

### Uso como módulo

También puedes importar las funciones del módulo `src` para usar en tus propios scripts:

```python
from src import (
    cargar_secuencias,
    calcular_metricas_basicas,
    calcular_uso_codones,
    generar_todos_los_graficos
)

# Cargar secuencias
salmonella = cargar_secuencias("data/salmonella_genes.fasta")

# Calcular métricas
metricas = calcular_metricas_basicas(salmonella)

# Analizar uso de codones
codones = calcular_uso_codones(salmonella, "salmonella")
```

## 📁 Estructura del Proyecto

```
bioinfo_salmonella/
│
├── data/                          # Archivos de datos FASTA
│   ├── salmonella_genes.fasta     # Secuencias de Salmonella
│   └── gallus_genes.fasta         # Secuencias de Gallus
│
├── src/                           # Módulos del proyecto
│   ├── __init__.py               # Inicialización del paquete
│   ├── procesamiento.py          # Funciones de carga y procesamiento
│   ├── analisis.py               # Funciones de análisis de codones
│   └── visualizacion.py          # Funciones de visualización
│
├── results/                       # Resultados del análisis
│   ├── graficos/                 # Gráficos generados
│   │   ├── distribucion_longitudes.png
│   │   ├── distribucion_gc.png
│   │   ├── relacion_longitud_gc.png
│   │   ├── uso_codones_top20.png
│   │   ├── correlacion_codones.png
│   │   ├── heatmap_codones.png
│   │   ├── distribucion_acumulativa_longitudes.png
│   │   ├── salmonella_gc.png
│   │   └── gallus_gc.png
│   ├── resumen_metricas.csv      # Métricas básicas
│   └── codon_usage.csv           # Uso de codones
│
├── main.py                        # Script principal
├── requeriments.txt               # Dependencias del proyecto
├── README.md                      # Este archivo
└── .gitignore                     # Archivos ignorados por Git
```

## 📊 Resultados

El análisis genera los siguientes archivos de resultados:

### Archivos CSV
- **`results/resumen_metricas.csv`**: Contiene las métricas básicas calculadas para todas las secuencias (longitud, contenido GC, especie, etc.)
- **`results/codon_usage.csv`**: Contiene la frecuencia de uso de cada codón para ambas especies

### Gráficos Generados
1. **distribucion_longitudes.png**: Distribución de longitudes de secuencias por especie
2. **distribucion_gc.png**: Distribución del contenido GC por especie
3. **relacion_longitud_gc.png**: Relación entre longitud y contenido GC
4. **uso_codones_top20.png**: Top 20 codones más utilizados
5. **correlacion_codones.png**: Correlación de uso de codones entre especies
6. **heatmap_codones.png**: Heatmap del uso de codones
7. **distribucion_acumulativa_longitudes.png**: Distribución acumulativa de longitudes
8. **salmonella_gc.png**: Gráfico específico de contenido GC para Salmonella
9. **gallus_gc.png**: Gráfico específico de contenido GC para Gallus

## 🔬 Funcionalidades del Módulo

### Módulo `procesamiento`
- `cargar_secuencias(ruta_archivo)`: Carga secuencias desde un archivo FASTA
- `calcular_metricas_basicas(secuencias)`: Calcula métricas básicas de las secuencias
- `validar_secuencias(secuencias)`: Valida las secuencias cargadas

### Módulo `analisis`
- `calcular_uso_codones(secuencias, etiqueta)`: Calcula la frecuencia de uso de codones
- `analizar_bias_codones(df_codones, especie)`: Analiza el bias en el uso de codones
- `comparar_uso_codones_especies(df_codones)`: Compara el uso de codones entre especies
- `generar_tabla_codones_aminoacidos()`: Genera una tabla de codones y aminoácidos

### Módulo `visualizacion`
- `grafico_gc(df_metricas, especie)`: Genera gráfico de contenido GC
- `distribucion_longitudes(df_metricas)`: Genera gráfico de distribución de longitudes
- `distribucion_gc(df_metricas)`: Genera gráfico de distribución de GC
- `relacion_longitud_gc(df_metricas)`: Genera gráfico de relación longitud-GC
- `uso_codones_top20(df_codones)`: Genera gráfico de top 20 codones
- `correlacion_codones(df_codones)`: Genera gráfico de correlación de codones
- `heatmap_codones(df_codones)`: Genera heatmap de uso de codones
- `distribucion_acumulativa_longitudes(df_metricas)`: Genera gráfico acumulativo
- `generar_todos_los_graficos()`: Genera todos los gráficos avanzados

## ⚠️ Notas Importantes

- Asegúrate de que los archivos FASTA estén en la carpeta `data/` antes de ejecutar el análisis
- Los archivos de resultados se guardan automáticamente en la carpeta `results/`
- La carpeta `results/graficos/` se crea automáticamente si no existe
- Los archivos CSV y PNG en `results/` están ignorados por Git (ver `.gitignore`)

## 🐛 Solución de Problemas

### Error: "No se pudo encontrar el archivo"
- Verifica que los archivos `salmonella_genes.fasta` y `gallus_genes.fasta` estén en la carpeta `data/`
- Verifica que las rutas de los archivos sean correctas

### Error de importación
- Asegúrate de haber instalado todas las dependencias: `pip install -r requeriments.txt`
- Verifica que estés usando el entorno virtual correcto

### Error al generar gráficos
- Verifica que la carpeta `results/` exista y tenga permisos de escritura
- Asegúrate de que los archivos CSV necesarios estén presentes en `results/`

## 📝 Versión

Versión actual: **1.0.0**

## 👤 Autor

Analista de Secuencias

## 📄 Licencia

Este proyecto es de uso educativo y de investigación.

---

**¡Disfruta analizando secuencias genéticas!** 🧬

