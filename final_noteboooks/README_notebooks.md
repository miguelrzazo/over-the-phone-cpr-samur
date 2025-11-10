# Notebooks de Análisis - Estudio RCP Transtelefónica SAMUR-PC

## 📋 Descripción General

Este directorio contiene los **notebooks de Jupyter** que implementan todo el análisis estadístico del estudio sobre la efectividad de la RCP transtelefónica en paradas cardíacas extrahospitalarias.

**Período de estudio:** Julio 2023 - Junio 2025 (24 meses)  
**Muestra final:** 500 casos de PCEH no traumática  
**Institución:** SAMUR-PC Madrid

---

## 📚 Estructura de Notebooks

Los notebooks están diseñados para ejecutarse **secuencialmente** y cada uno tiene un propósito específico:

### 1️⃣ Design Language (`1. design_language.ipynb`)

**🎯 Propósito:** Establecer especificaciones visuales consistentes

**📦 Contenido:**
- Paleta de colores institucional
- Configuración de matplotlib/seaborn
- Plantillas de gráficos (barras, forest plots, box plots)
- Especificaciones de tipografía y tamaños
- Ejemplos de visualizaciones estándar

**📤 Outputs:** Ninguno (es un notebook de referencia)

**⏱️ Tiempo de ejecución:** < 1 minuto

---

### 2️⃣ Estadística Descriptiva (`2. descriptive_statistics.ipynb`)

**🎯 Propósito:** Análisis descriptivo completo de la muestra

**📦 Contenido:**
- **Características demográficas:**
  - Edad: media 66.1 ± 16.3 años
  - Sexo: 79.2% masculino
  - Estratificación por edad (<65 vs ≥65 años)
  
- **Distribución de grupos de RCP:**
  - Sin RCP previa: 169 casos (33.8%)
  - Testigos legos: 172 casos (34.4%)
  - Sanitarios: 93 casos (18.6%)
  - Policía: 64 casos (12.8%)
  - Bomberos: 2 casos (0.4%)
  
- **Outcomes principales:**
  - ROSC (Retorno Circulación Espontánea)
  - Supervivencia a 7 días
  - CPC favorable (1-2)
  
- **Tiempos de respuesta:**
  - Tiempo de llegada medio: 8.4 minutos
  - Tiempo de RCP medio: 29.8 minutos

**📤 Outputs:** `outputs_descriptivos/`
- `figures/` - Histogramas, box plots, gráficos de barras (PNG, 300 DPI)
- `tables/` - Tablas CSV con estadísticas descriptivas
- `reports/` - Resúmenes de texto

**⏱️ Tiempo de ejecución:** 2-3 minutos

**📊 Figuras generadas:**
- Distribución de edad por grupo
- Distribución de sexo
- Tiempos de respuesta
- Outcomes por grupo (barras)

---

### 3️⃣ Análisis Inferencial (`3. exploratory_analysis.ipynb`)

**🎯 Propósito:** Inferencia estadística y machine learning

**📦 Contenido:**

#### A. Tests Estadísticos Bivariados
- **Chi-cuadrado (χ²):** Comparación de proporciones entre grupos
- **Fisher exacto:** Para grupos pequeños (n < 5)
- **Mann-Whitney U:** Comparación de medianas entre dos grupos
- **Kruskal-Wallis:** Comparación entre múltiples grupos

#### B. Análisis Multivariado
- **Regresión logística:**
  - Variables dependientes: ROSC, Supervivencia, CPC favorable
  - Variables independientes: Tipo RCP, edad, sexo, tiempo llegada, ritmo inicial
  - Ajuste por factores de confusión
  - Odds Ratios (OR) con IC 95%

#### C. Machine Learning
- Regresión logística con regularización L2
- Validación cruzada estratificada (5-fold)
- StandardScaler para normalización
- Pesos balanceados para clases desbalanceadas
- Métricas: AUC-ROC, precision, recall, F1-score

#### D. Análisis Estratificado
- **Por edad:** <65 vs ≥65 años
- **Por tiempo de llegada:** Menor vs mayor que mediana
- **Por ritmo inicial:** Desfibrilable vs no desfibrilable

**📤 Outputs:** `outputs_inferencia/`
- `figures/` - Forest plots, curvas ROC, barplots con IC (PNG, 300 DPI)
- `tables/` - Resultados de tests, OR, p-valores (CSV)
- `models/` - Modelos ML serializados (JSON)
- `reports/` - Reportes estadísticos detallados

**⏱️ Tiempo de ejecución:** 5-10 minutos (incluye validación cruzada)

**📊 Figuras generadas:**
- Forest plots de Odds Ratios
- Curvas ROC de modelos ML
- Gráficos de importancia de variables
- Comparaciones estratificadas

**📈 Resultados principales:**
| Grupo | ROSC | Supervivencia 7d | CPC Favorable |
|-------|------|------------------|---------------|
| Sanitarios | 67.7% | 40.9% | 38.7% |
| Testigos legos | 65.7% | 29.7% | 25.6% |
| Sin RCP previa | 53.3% | 17.2% | 13.0% |
| Policía | 50.0% | 17.2% | 14.1% |

---

### 4️⃣ Draft Paper (`4. draft_paper.ipynb`)

**🎯 Propósito:** Integrar resultados para el manuscrito científico en LaTeX

**📦 Contenido:**
- Selección de figuras más relevantes
- Generación de tablas en formato LaTeX
- Redacción de leyendas
- Resumen de hallazgos principales para el paper

**📤 Outputs:** 
- **`latex/figures/`** - Figuras finales de alta resolución
- **`latex/tables/`** - Tablas en formato .tex y .csv

**⚠️ IMPORTANTE:** 
Solo este notebook tiene permiso para exportar directamente a `latex/`. Los notebooks 2 y 3 exportan a sus propias carpetas de outputs.

**⏱️ Tiempo de ejecución:** 3-5 minutos

---

## 🚀 Cómo Ejecutar los Notebooks

### Requisitos Previos

#### 1. Python 3.10 o superior
```bash
python --version  # Debe mostrar Python 3.10.x o superior
```

#### 2. Instalar dependencias
```bash
# Desde el directorio raíz del proyecto
pip install -r documentation/requirements.txt
```

**Librerías principales:**
- `pandas` - Manipulación de datos
- `numpy` - Operaciones numéricas
- `matplotlib` - Visualización
- `seaborn` - Gráficos estadísticos
- `scipy` - Tests estadísticos
- `scikit-learn` - Machine learning
- `jupyter` - Entorno de notebooks

### Ejecución Paso a Paso

#### Opción A: Desde Terminal

```bash
# 1. Navegar al directorio de notebooks
cd final_noteboooks/

# 2. Iniciar Jupyter Notebook
jupyter notebook

# 3. Se abrirá tu navegador con la lista de notebooks
# 4. Abrir y ejecutar en orden:
#    - 1. design_language.ipynb
#    - 2. descriptive_statistics.ipynb
#    - 3. exploratory_analysis.ipynb
#    - 4. draft_paper.ipynb

# 5. En cada notebook, ejecutar celda por celda con Shift + Enter
#    O ejecutar todo: Cell → Run All
```

#### Opción B: Desde VS Code

1. Instalar extensión "Jupyter" de Microsoft
2. Abrir cualquier notebook (.ipynb)
3. Seleccionar kernel de Python 3.10+
4. Ejecutar celdas con Shift + Enter

#### Opción C: Desde Anaconda Navigator

1. Abrir Anaconda Navigator
2. Lanzar Jupyter Notebook
3. Navegar a `final_noteboooks/`
4. Abrir y ejecutar notebooks

---

## 📂 Estructura de Outputs

```
final_noteboooks/
├── 1. design_language.ipynb
├── 2. descriptive_statistics.ipynb
├── 3. exploratory_analysis.ipynb
├── 4. draft_paper.ipynb
│
├── outputs_descriptivos/          # Outputs del notebook 2
│   ├── figures/
│   │   ├── distribucion_edades.png
│   │   ├── distribucion_sexo.png
│   │   └── ...
│   ├── tables/
│   │   ├── tabla_caracteristicas_basales.csv
│   │   └── ...
│   └── reports/
│       └── resumen_descriptivo.txt
│
└── outputs_inferencia/            # Outputs del notebook 3
    ├── figures/
    │   ├── forestplot_or_outcomes_grupo_rcp.png
    │   ├── roc_curves_ml_models.png
    │   └── ...
    ├── tables/
    │   ├── tabla_comparacion_outcomes.csv
    │   ├── resultados_hipotesis.json
    │   └── ...
    ├── models/
    │   └── modelos_ml.json
    └── reports/
        └── resumen_inferencial.txt
```

---

## 🔍 Datos Utilizados

### Datos Principales

**Archivo:** `../data/3.cleaned_data/datos_con_cpc_valido.csv`

**Características:**
- 500 registros (casos válidos para análisis)
- Excluidos: 566 casos (trauma, SVB no-PCR, cadáveres, sin CPC)
- Variables principales:
  - NUM_INFORME, FECHA_LLAMADA
  - EDAD, SEXO
  - RCP_TRANSTELEFONICA, RCP_TESTIGOS, RCP_SANITARIOS
  - Tiempo_llegada, Tiempo_Rcp
  - Desfibrilable_inicial
  - ROSC, Supervivencia_7dias, CPC

### Datos Excluidos

**Archivo:** `../data/3.cleaned_data/datos_excluidos.csv`
- 566 registros excluidos con motivo de exclusión

### Procesamiento

Ver `../data/3.cleaned_data/RESUMEN_PROCESAMIENTO.md` para detalles completos del pipeline de limpieza.

---

## 🧪 Metodología Estadística Resumida

### Tests Utilizados

#### Variables Categóricas (Outcomes Binarios)
- **Chi-cuadrado (χ²):** Comparación de proporciones
- **Fisher exacto:** Cuando n < 5 en alguna celda
- **Significancia:** α = 0.05

#### Variables Continuas
- **Mann-Whitney U:** Comparación de dos grupos
- **Kruskal-Wallis:** Comparación de múltiples grupos

#### Análisis Multivariado
- **Regresión logística:** OR ajustados con IC 95%
- **Validación cruzada:** 5-fold estratificada
- **Regularización:** L2 (Ridge) para prevenir overfitting

### Métricas Reportadas

- **Odds Ratios (OR)** con IC 95%
- **p-valores** (con corrección por múltiples comparaciones si aplica)
- **AUC-ROC** para modelos predictivos
- **Sensibilidad, Especificidad, F1-score**

---

## ⚙️ Configuración y Reproducibilidad

### Semillas Aleatorias
Todos los análisis usan `random_state=42` para reproducibilidad exacta.

### Versiones de Software
```python
import sys
print(f"Python: {sys.version}")

import pandas as pd
import numpy as np
import sklearn
print(f"Pandas: {pd.__version__}")
print(f"NumPy: {np.__version__}")
print(f"Scikit-learn: {sklearn.__version__}")
```

Ver `documentation/requirements.txt` para versiones exactas.

---

## 🐛 Resolución de Problemas

### Error: "ModuleNotFoundError"
```bash
# Instalar dependencias faltantes
pip install -r ../documentation/requirements.txt
```

### Error: "FileNotFoundError" (datos no encontrados)
- Verificar que exista `../data/3.cleaned_data/datos_con_cpc_valido.csv`
- Si no existe, ejecutar script de limpieza: `../data/2.Data_cleaning/process_data.py`

### Kernel Crashes o Out of Memory
- Reiniciar el kernel: Kernel → Restart
- Cerrar otros notebooks
- Ejecutar notebooks uno a la vez

### Gráficos No Se Muestran
```python
# Asegurarse de tener:
%matplotlib inline
import matplotlib.pyplot as plt
plt.show()
```

---

## 📖 Lectura de Notebooks (sin ejecutar)

Si solo quieres **leer** los análisis sin ejecutar código:

1. **GitHub/GitLab:** Los notebooks se renderizan automáticamente
2. **nbviewer:** [https://nbviewer.org/](https://nbviewer.org/) - pega la URL del notebook
3. **VS Code:** Abre el .ipynb y navega con las flechas
4. **Jupyter:** Abre el notebook pero no ejecutes celdas

---

## 📊 Principales Hallazgos (Resumen)

### Outcomes por Grupo de RCP

**ROSC (Retorno de Circulación Espontánea):**
- ✅ Sanitarios: **67.7%** (mejor)
- ✅ Testigos legos: **65.7%**
- ⚠️ Sin RCP previa: **53.3%**
- ⚠️ Policía: **50.0%**

**Supervivencia a 7 días:**
- ✅ Sanitarios: **40.9%** (mejor)
- ✅ Testigos legos: **29.7%**
- ⚠️ Sin RCP previa: **17.2%**
- ⚠️ Policía: **17.2%**

**CPC Favorable (1-2):**
- ✅ Sanitarios: **38.7%** (mejor)
- ✅ Testigos legos: **25.6%**
- ⚠️ Policía: **14.1%**
- ⚠️ Sin RCP previa: **13.0%**

### Impacto de la Edad

**<65 años (mejor pronóstico):**
- ROSC: 69.7%
- Supervivencia: 34.4%
- CPC favorable: 31.5%

**≥65 años:**
- ROSC: 52.9%
- Supervivencia: 19.1%
- CPC favorable: 14.7%

### RCP Transtelefónica

- **113 de 172 casos** de testigos legos (65.7%) recibieron guía telefónica
- Outcomes comparables al resto de RCP por testigos
- **Papel clave:** Aumentar tasa de inicio de RCP

---

## 📞 Contacto y Soporte

**Dudas técnicas (Python, Jupyter):**
- Revisar comentarios inline en notebooks
- Consultar documentación de librerías
- Stack Overflow para errores comunes

**Dudas metodológicas (estadística):**
- Ver `../documentation/3.data_analysis.md`
- Consultar notebooks con explicaciones detalladas

**Sobre el estudio:**
- Contactar a los autores (ver README principal)

---

## ✅ Checklist de Ejecución

Antes de considerar el análisis completo, verificar:

- [ ] Notebook 1 ejecutado sin errores
- [ ] Notebook 2 ejecutado - outputs en `outputs_descriptivos/`
- [ ] Notebook 3 ejecutado - outputs en `outputs_inferencia/`
- [ ] Notebook 4 ejecutado - figuras en `../latex/figures/`
- [ ] Todas las figuras generadas correctamente (300 DPI)
- [ ] Tablas exportadas en formato correcto
- [ ] Modelos ML guardados en JSON
- [ ] Reportes de texto generados

---

**Última actualización:** Noviembre 2025  
**Versión:** 1.0 (Final)  
**Estado:** ✅ Análisis completo - Resultados validados


### Reportes de Texto
- `reporte_estadistica_descriptiva.txt`: Resumen ejecutivo descriptivo
- `resumen_analisis_inferencial.txt`: Conclusiones inferenciales

## Uso Rápido

Para ejecutar los análisis principales:

```bash
cd final_noteboooks/

# Opción 1: Jupyter Lab
jupyter lab

# Opción 2: Jupyter Notebook clásico  
jupyter notebook

# Ejecutar en orden: notebook 2 → notebook 3 → notebook 4
```

## Compatibilidad

- ✅ **Python 3.8+**
- ✅ **Jupyter Lab / Notebook**
- ✅ **VS Code con extensión Python**
- ✅ **Google Colab** (con adaptaciones menores de rutas)

## Troubleshooting

### Error: "ModuleNotFoundError"
```bash
pip install -r requirements.txt  # Si existe
# O instalar manualmente: pandas numpy matplotlib seaborn scikit-learn scipy
```

### Error: "Datos no encontrados"
- Los notebooks generan datos simulados automáticamente
- Para usar datos reales, colocar en `../data/3.cleaned_data/datos_con_cpc_valido.csv`

### Error: "Figuras no se muestran"
```python
%matplotlib inline  # Añadir al inicio del notebook
```

## Contribución

Estos notebooks siguen las especificaciones del proyecto RCP Transtelefónica:
- Lenguaje de diseño consistente
- Estructura de outputs organizada
- Principios de machine learning
- Estándares científicos de publicación

Para modificaciones, consultar `documentation/` y mantener la consistencia con el proyecto.