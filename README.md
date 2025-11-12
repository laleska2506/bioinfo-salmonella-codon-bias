# 🧬 SalmoAvianLight - Salmonella vs Gallus

Herramienta de bioinformática para analizar y comparar secuencias genéticas entre *Salmonella* (bacteria) y *Gallus* (pollo). Incluye cálculo de métricas, análisis de uso de codones, visualización de datos y una **interfaz web interactiva** para analistas de laboratorio.

## 📋 ¿Qué hace este proyecto?

Este proyecto permite:

- **Analizar secuencias genéticas** desde archivos FASTA
- **Calcular métricas básicas** (longitud, contenido GC, etc.)
- **Analizar el uso de codones** para identificar patrones de codificación
- **Comparar secuencias** entre dos especies (Salmonella vs Gallus)
- **Visualizar resultados** mediante gráficos estadísticos y tablas
- **Interfaz web interactiva** para usar sin programar

## 🚀 Cómo empezar

### Paso 1: Instalar dependencias

```bash
# Crear entorno virtual (recomendado)
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### Paso 2: Usar la aplicación web (Recomendado)

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en `http://localhost:8501`.

**En la interfaz web:**
1. Sube dos archivos FASTA (Salmonella y Gallus)
2. Configura los parámetros de análisis
3. Haz clic en "🚀 Analizar"
4. Revisa y descarga los resultados (tablas CSV, gráficos PNG, ZIP completo)

### Paso 3: Usar desde línea de comandos (Opcional)

```bash
# Coloca tus archivos FASTA en data/
# salmonella_genes.fasta
# gallus_genes.fasta

# Ejecutar análisis
python main.py
```

Los resultados se guardarán en la carpeta `results/`.

## 📦 Requisitos

- Python 3.8 o superior
- Dependencias: streamlit, pandas, biopython, matplotlib, numpy, scipy, seaborn, requests
  (ver `requirements.txt` para versiones específicas)

## 🎯 Características principales

### 🔬 Análisis

- Carga y validación de secuencias FASTA
- Cálculo de métricas básicas (longitud, contenido GC)
- Análisis de frecuencia de uso de codones
- Comparación entre especies
- Filtrado por longitud mínima
- Normalización de caracteres N

### 📊 Visualización

- Distribución de longitudes de secuencias
- Distribución de contenido GC
- Relación longitud-GC
- Gráficos de uso de codones (top N configurable)
- Correlación de codones entre especies
- Heatmap de uso de codones
- Gráficos específicos por especie

### 🌐 Interfaz Web

- **Interfaz intuitiva** para analistas de laboratorio
- **Modo local**: Ejecuta análisis directamente en tu servidor
- **Modo API**: Se conecta a un backend remoto (opcional)
- **Descarga de resultados**: CSV individuales o ZIP completo
- **Manejo de errores**: Mensajes claros y opción de reintento

## 📁 Estructura del proyecto

```
bioinfo_salmonella/
├── app.py              # Aplicación web Streamlit
├── main.py             # Script de línea de comandos
├── src/                # Módulos de análisis
│   ├── procesamiento.py
│   ├── analisis.py
│   └── visualizacion.py
├── services/           # Servicios del frontend
├── utils/              # Utilidades
├── data/               # Archivos FASTA de entrada
├── results/            # Resultados del análisis
└── requirements.txt    # Dependencias
```

## 📊 Resultados

El análisis genera:

- **CSV**: `resumen_metricas.csv`, `codon_usage.csv`
- **Gráficos PNG**: 9 gráficos estadísticos en `results/graficos/`
- **ZIP completo**: Descarga todos los resultados (solo en interfaz web)

## 🔧 Uso avanzado

### Usar como módulo Python

```python
from src import (
    cargar_secuencias,
    calcular_metricas_basicas,
    calcular_uso_codones
)

# Cargar secuencias
salmonella = cargar_secuencias("data/salmonella_genes.fasta")

# Calcular métricas
metricas = calcular_metricas_basicas(salmonella)

# Analizar codones
codones = calcular_uso_codones(salmonella, "salmonella")
```

### Modo API (con backend)

```bash
# Configurar variable de entorno
export BACKEND_BASE_URL="https://tu-backend.com"

# Ejecutar Streamlit
streamlit run app.py
```

## 🐛 Solución de problemas

### Error: "No se pudo encontrar el archivo"
- Verifica que los archivos FASTA estén en `data/` (modo CLI)
- Verifica que los archivos se hayan subido correctamente (modo web)

### Error de importación
- Instala dependencias: `pip install -r requirements.txt`
- Verifica que el entorno virtual esté activado

### Error: "Las secuencias contienen caracteres inválidos"
- Los archivos FASTA solo deben contener: A, T, C, G, N
- Usa la opción "Normalizar/limpiar Ns" en la interfaz web

## 📝 Notas

- Los archivos de resultados en `results/` están ignorados por Git
- En modo web local, los archivos temporales se limpian automáticamente
- Los gráficos se generan en `results/graficos/`

## 📄 Licencia

Este proyecto es de uso educativo y de investigación.

---

**¿Listo para analizar secuencias genéticas?** 🧬

Para más información, consulta el código fuente o los comentarios en los archivos del proyecto.
