# Notebooks de Análisis - Estudio RCP Transtelefónica

Este directorio contiene los notebooks principales para el análisis estadístico del estudio sobre la efectividad de la RCP transtelefónica.

## Estructura de los Notebooks

### 1. Design Language (`1. design_language.ipynb`)
- **Propósito**: Establece el lenguaje de diseño visual consistente
- **Contenido**: Paleta de colores, configuraciones de matplotlib, especificaciones gráficas
- **Uso**: Referencia para todos los otros notebooks

### 2. Estadística Descriptiva (`2.descriptive_statistics.ipynb`) ✨ NUEVO
- **Propósito**: Análisis descriptivo completo de la muestra
- **Contenido**: 
  - Características basales por grupo de RCP
  - Distribuciones de edad, sexo, tiempos de respuesta
  - Outcomes principales (ROSC, supervivencia, CPC)
  - Análisis estratificado por edad
- **Outputs**: `outputs_descriptivos/` (tablas CSV, figuras PNG, reportes)

### 3. Análisis Inferencial (`3.exploratory_analysis.ipynb`) ✨ NUEVO
- **Propósito**: Inferencia estadística y machine learning
- **Contenido**:
  - Tests estadísticos bivariados (χ², Fisher exacto)
  - Regresión logística con validación cruzada
  - Modelos ML con regularización
  - Curvas ROC y métricas de rendimiento
  - Análisis de importancia de variables
- **Outputs**: `outputs_inferencia/` (tablas CSV, figuras PNG, modelos, reportes)

### 4. Draft Paper (`4. draft_paper.ipynb`)
- **Propósito**: Esquema del paper científico
- **Contenido**: Integra resultados de notebooks 2 y 3 para LaTeX
- **Outputs**: Directamente a `latex/figures/` y `latex/tables/`

## Flujo de Trabajo Recomendado

1. **Revisar diseño**: Ejecutar notebook 1 para familiarizarse con el lenguaje visual
2. **Análisis descriptivo**: Ejecutar notebook 2 para entender la muestra
3. **Análisis inferencial**: Ejecutar notebook 3 para probar hipótesis
4. **Paper final**: Usar notebook 4 para generar outputs finales para LaTeX

## Requisitos Técnicos

### Bibliotecas Python Requeridas
```bash
pip install pandas numpy matplotlib seaborn scikit-learn scipy jupyter
```

### Opcional (para análisis avanzado)
```bash
pip install statsmodels
```

## Datos

Los notebooks están diseñados para trabajar con:
- **Datos reales**: `../data/3.cleaned_data/datos_con_cpc_valido.csv`
- **Datos simulados**: Se generan automáticamente si no hay datos reales disponibles

## Características de los Nuevos Notebooks

### Notebook 2: Estadística Descriptiva
- ✅ **Tabla 1 científica**: Características basales con tests estadísticos
- ✅ **Visualizaciones profesionales**: Box plots, histogramas, gráficos de barras
- ✅ **Análisis estratificado**: Por edad (<65 vs ≥65 años)
- ✅ **Reportes automáticos**: Resumen ejecutivo en texto
- ✅ **Exportación organizada**: Outputs a `outputs_descriptivos/`

### Notebook 3: Análisis Inferencial + ML
- ✅ **Tests estadísticos clásicos**: Chi-cuadrado, Fisher exacto
- ✅ **Regresión logística avanzada**: Con validación cruzada estratificada
- ✅ **Machine Learning**: Regularización L2, pesos balanceados, StandardScaler
- ✅ **Métricas robustas**: AUC-ROC, precision, recall, F1-score
- ✅ **Curvas ROC**: Visualizaciones de rendimiento predictivo
- ✅ **Análisis de importancia**: Variables más influyentes en cada outcome
- ✅ **Hipótesis científicas**: Evaluación sistemática de H1-H4

## Principios de Machine Learning Aplicados

1. **Validación cruzada**: StratifiedKFold con 5 particiones
2. **Regularización**: Modelos L2 (Ridge) para prevenir overfitting
3. **Normalización**: StandardScaler para variables continuas
4. **Balance de clases**: Pesos automáticos para outcomes desbalanceados
5. **Métricas apropiadas**: AUC-ROC para problemas binarios médicos
6. **Reproducibilidad**: Semillas fijas (random_state=42)

## Outputs Generados

### Tablas CSV
- `tabla1_caracteristicas_basales.csv`: Tabla 1 para el paper
- `tabla_tests_bivariados.csv`: Resultados de tests estadísticos
- `resultados_modelos_ml.csv`: Rendimiento de modelos ML
- `analisis_estratificado_edad.csv`: Resultados por grupos de edad

### Figuras PNG (300 DPI)
- `figura1_distribucion_edad.png`: Distribuciones por edad
- `figura2_outcomes_principales.png`: Outcomes por grupo de RCP
- `curvas_roc_modelos_ml.png`: Curvas ROC de todos los modelos
- `importancia_variables_ml.png`: Importancia de variables predictoras

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