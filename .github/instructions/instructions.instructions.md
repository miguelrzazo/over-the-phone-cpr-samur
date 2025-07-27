---
applyTo: '**'
---

# Instrucciones de Desarrollo para RCP Transtelefónica

## Enfoque y Objetivos del Estudio

### Objetivo Principal
**Evaluar el impacto de la RCP transtelefónica en la supervivencia y estado neurológico (CPC) de pacientes con paro cardiorrespiratorio extrahospitalario.**

### Grupos de Comparación
1. **RCP Transtelefónica** - Pacientes que recibieron instrucciones de RCP por teléfono
2. **RCP de Testigos** - Pacientes que recibieron RCP presencial de testigos sin guía telefónica
3. **Sin RCP Previa** - Pacientes sin RCP hasta llegada de servicios de emergencia

### Variables de Resultado Principales
- **Supervivencia al alta hospitalaria**
- **CPC (Cerebral Performance Category) favorable** (CPC 1-2)
- **ROSC (Return of Spontaneous Circulation)**
- **Supervivencia a 24 horas**

### Estratificaciones Analíticas Obligatorias

#### 1. **Estratificación por Edad**
- **Menores de 65 años** vs **65 años o más**
- Justificación: Diferente pronóstico y respuesta a RCP por edad

#### 2. **Estratificación por Tiempo de Llegada**
- **Menor a la mediana** vs **Mayor a la mediana** del tiempo de llegada de la unidad
- Justificación: El tiempo es factor crítico en outcomes de RCP

#### 3. **Análisis Combinado**
- **Edad × Tipo de RCP** (6 grupos: 2 edades × 3 tipos RCP)
- **Tiempo × Tipo de RCP** (6 grupos: 2 tiempos × 3 tipos RCP)
- **Edad × Tiempo × Tipo de RCP** (análisis multivariado)

### Hipótesis de Investigación
- **H1**: La RCP transtelefónica mejora la supervivencia comparada con sin RCP previa
- **H2**: La RCP transtelefónica mejora el CPC favorable comparada con sin RCP previa  
- **H3**: El beneficio es mayor en pacientes <65 años
- **H4**: El beneficio relativo es mayor cuando el tiempo de llegada es mayor a la mediana

## Estructura de Datos del Proyecto

### Directorios Principales
```
RCP Transtelefonica/
├── data/
│   ├── 1.raw_imported/          # Datos originales sin procesar
│   ├── 2.Data_cleaning/         # Scripts y reportes de limpieza
│   └── 3.cleaned_data/          # Datos finales limpios
├── documentation/               # Documentación del proyecto
├── final_noteboooks/           # Notebooks finales de análisis
├── latex/                      # Archivos LaTeX del paper final
│   ├── figures/                # Gráficos para el paper
│   ├── tables/                 # Tablas para el paper
│   └── paper/                  # Documento principal LaTeX
└── proyecto/                   # Trabajo en progreso
```

## Ubicación del Draft Paper

**IMPORTANTE**: El draft paper final debe guardarse en:
```
latex/paper/
```

Este directorio contendrá:
- `rcp_transtelefonica_paper.tex` - Documento principal
- `rcp_transtelefonica_paper.pdf` - PDF compilado
- Archivos auxiliares generados por LaTeX

### Gráficos y Tablas Finales
- **Gráficos**: `latex/figures/` - Todos los gráficos finales en formato PNG/PDF
- **Tablas**: `latex/tables/` - Archivos CSV y datos tabulares para LaTeX

## Rutas Relativas - OBLIGATORIO

**NUNCA usar rutas absolutas** como `/Users/miguelrosa/Desktop/`. 

**SIEMPRE usar rutas relativas** desde el workspace:
```python
# ❌ INCORRECTO
ruta = "/Users/miguelrosa/Desktop/RCP Transtelefonica/data/..."

# ✅ CORRECTO
import os
workspace_root = os.getcwd()  # o definir explícitamente
ruta = "./data/3.cleaned_data/cleaned_data.csv"
ruta = "latex/figures/figura_1.png"
```

### Ejemplos de Rutas Correctas
```python
# Para leer datos
data_path = "./data/3.cleaned_data/cleaned_data.csv"

# Para guardar figuras
fig_path = "./latex/figures/distribucion_scores.png"

# Para guardar tablas
table_path = "./latex/tables/tabla_caracteristicas.csv"
```

## Lenguaje de Diseño Visual

### Notebook de Referencia
Usar siempre las especificaciones del notebook:
```
final_noteboooks/1. design_language.ipynb
```

### Configuración Tipográfica Obligatoria
```python
import matplotlib.pyplot as plt
```



### Guardado de Figuras

# Configuración estándar para todas las figuras
```python
plt.tight_layout()
plt.savefig('./latex/figures/nombre_figura.png', 
           dpi=300, bbox_inches='tight', 
           facecolor='white', edgecolor='none')
plt.show()
```

## Flujo de Trabajo

1. **Análisis** → `final_noteboooks/`
2. **Aplicar diseño** → Usar especificaciones de `1. design_language.ipynb`
3. **Exportar resultados** → `latex/figures/` y `latex/tables/`
4. **Integrar en paper** → `latex/paper/rcp_transtelefonica_paper.tex`
5. **Compilar** → Usar las tareas de VS Code disponibles

## Documentación del Proyecto

### Ubicación de Documentación
Toda la documentación debe guardarse en:
```
documentation/
```

### Archivos de Documentación Requeridos

#### `documentation/1.workflow.md`
**Propósito**: Explicar el flujo de trabajo completo del proyecto
**Contenido**:
- Proceso paso a paso del análisis
- Dependencias entre etapas
- Criterios de validación para cada fase
- Puntos de control de calidad

#### `documentation/2.data_cleaning.md`
**Propósito**: Documentar todo el proceso de limpieza de datos
**Contenido**:
- Criterios de exclusión aplicados y por qué
- Transformaciones realizadas
- Validaciones implementadas
- Reporte de datos excluidos con justificación

#### `documentation/3.data_analysis.md`
**Propósito**: Documentar la metodología de análisis
**Contenido**:
- Tests estadísticos utilizados para comparar RCP transtelefónica vs testigos vs sin RCP
- Análisis estratificado por edad (<65 vs ≥65 años)
- Análisis estratificado por tiempo de llegada (menor vs mayor que la mediana)
- Análisis multivariado combinando edad, tiempo y tipo de RCP
- Justificación de métodos elegidos
- Interpretación de resultados para supervivencia y CPC
- Limitaciones del análisis

#### `documentation/4.presentation.md`
**Propósito**: Guía para presentación de resultados
**Contenido**:
- Estructura de presentación enfocada en efectividad de RCP transtelefónica
- Resultados principales: supervivencia y CPC favorable por grupos
- Análisis estratificado por edad y tiempo de llegada
- Puntos clave a destacar sobre beneficios de RCP telefónica
- Audiencia objetivo: comunidad médica de emergencias
- Tiempo estimado por sección
- Explicacion para no programadores de como usar latex, al bajarselo un medico o sanitario sin experiencia en programación debe poder reproducir nuestro trabajo

## Reglas de Guardado de Archivos

### ⚠️ RESTRICCIONES IMPORTANTES



#### Para Notebooks Finales (`final_noteboooks/`)
- **SOLO** `4.draft_paper.ipynb` pueden guardar en `latex/figures/` y `latex/tables/`
- El resto solo generar outputs temporales, a no ser que se especifique lo contrario explicitamente.
- Estos son los únicos autorizados para generar outputs definitivos
- Siempre verificar que se usa el lenguaje de diseño correcto al escribir las graficas.

#### Guardado Explícito
- Solo guardar archivos cuando se solicite explícitamente
- Siempre preguntar ubicación si hay dudas
- Respetar la estructura de directorios establecida

## Estándares Científicos del Paper

### Nivel Académico Requerido
- **Nivel**: Doctorado/PhD
- **Lenguaje**: Científico riguroso y preciso
- **Audiencia**: Comunidad médica especializada en emergencias y RCP

### Estructura del Paper Científico

#### 1. **Abstract/Resumen**
- Máximo 350 palabras
- Introduccion, Objetivos, métodos, resultados principales, conclusiones

    
- Keywords/Palabras clave (5-8 términos MeSH) Van aparte, no cuentan a las 350 palabras del resumen

#### 2. **Introducción**
- Contexto epidemiológico del paro cardiorrespiratorio
- Estado del arte en RCP telefónica vs presencial
- Gap de conocimiento identificado
- **Objetivo primario** y objetivos secundarios claramente definidos
- Hipótesis de investigación

#### 3. **Métodos**
- Diseño del estudio (observacional retrospectivo)
- Población y muestra
- **Variables principales**:
  - Variables dependientes: supervivencia al alta hospitalaria, CPC favorable (1-2), ROSC, supervivencia a 24h
  - Variables independientes: tipo de RCP (transtelefónica vs testigos vs sin RCP), edad (<65 vs ≥65), tiempo de llegada (menor vs mayor que mediana)
- **Variables de confusión**: edad, comorbilidades, causa del paro, ritmo inicial, localización
- **Estratificaciones obligatorias**: 
  - Por edad: <65 años vs ≥65 años
  - Por tiempo de llegada: menor vs mayor que la mediana
  - Análisis combinado: edad × tipo RCP × tiempo llegada
- Criterios de inclusión/exclusión
- Análisis estadístico con justificación de tests utilizados
- Consideraciones éticas

#### 4. **Resultados**
- Características basales de la población estratificada por tipo de RCP
- **Resultados principales**:
  - Supervivencia al alta: RCP transtelefónica vs testigos vs sin RCP
  - CPC favorable: RCP transtelefónica vs testigos vs sin RCP
- **Análisis estratificado por edad**: 
  - Efectividad de RCP transtelefónica en <65 años vs ≥65 años
- **Análisis estratificado por tiempo de llegada**:
  - Efectividad según tiempo menor vs mayor que mediana
- **Intervalos de confianza al 95%** para todas las estimaciones
- p-valores con corrección por múltiples comparaciones
- Análisis de supervivencia (Kaplan-Meier, Cox) estratificado

#### 5. **Discusión**
- **Interpretación de hallazgos principales**:
  - Efectividad de RCP transtelefónica en supervivencia y CPC favorable
  - Diferencias entre grupos de edad (<65 vs ≥65 años)
  - Impacto del tiempo de llegada en la efectividad
- **Comparación con literatura existente** sobre RCP telefónica
- **Limitaciones del estudio** específicas para análisis estratificado
- **Implicaciones clínicas**: protocolos de RCP telefónica, formación operadores
- **Implicaciones de política sanitaria**: implementación de sistemas de RCP telefónica
- Direcciones futuras de investigación

### Estándares Gráficos Científicos

#### Gráficos Obligatorios con Intervalos de Confianza
```python
# Configuración para gráficos científicos
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats

# Configuración científica
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.family'] = ['sans-serif']
plt.rcParams['font.serif'] = ['Times New Roman']

# Para intervalos de confianza en barplots
def plot_with_ci(data, x, y, ci=95):
    """
    Crear gráfico con intervalos de confianza
    """
    sns.barplot(data=data, x=x, y=y, ci=ci, capsize=0.05)
    plt.ylabel(f'{y} (IC {ci}%)')
    
# Para forest plots de odds ratios
def forest_plot_or(or_values, ci_lower, ci_upper, labels):
    """
    Forest plot para odds ratios con IC 95%
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    y_pos = np.arange(len(labels))
    
    # Plot points and error bars
    ax.errorbar(or_values, y_pos, xerr=[or_values-ci_lower, ci_upper-or_values], 
                fmt='o', capsize=5, capthick=2)
    
    # Reference line at OR=1
    ax.axvline(x=1, color='red', linestyle='--', alpha=0.7)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.set_xlabel('Odds Ratio (IC 95%)')
    ax.set_title('Forest Plot - Odds Ratios')
```

#### Tipos de Gráficos Requeridos
1. **Tabla 1**: Características basales con tests estadísticos
2. **Gráficos de supervivencia**: Kaplan-Meier con log-rank test
3. **Forest plots**: Odds ratios con IC 95%
4. **Box plots**: Variables continuas con medianas e IQR
5. **Histogramas**: Distribuciones con tests de normalidad

#### Elementos Obligatorios en Gráficos
- **Intervalos de confianza al 95%** en todas las estimaciones
- **P-valores** claramente indicados
- **Tamaños muestrales (n)** en cada grupo
- **Ejes claramente etiquetados** con unidades
- **Leyendas explicativas** completas
- **Títulos informativos** que resuman el hallazgo principal

### Reportes Estadísticos Obligatorios
- **Medidas de tendencia central**: Media ± DE o Mediana (IQR)
- **Tests de hipótesis**: Chi-cuadrado, t-Student, Mann-Whitney
- **Análisis multivariado**: Regresión logística con OR ajustados
- **Análisis de supervivencia**: Hazard ratios con IC 95%
- **Corrección por múltiples comparaciones**: Bonferroni o FDR

## Compilación LaTeX

Usar las tareas predefinidas en VS Code:
- "Build LaTeX Paper" (XeLaTeX)
- "Build LaTeX Paper (pdfLaTeX fallback)"
