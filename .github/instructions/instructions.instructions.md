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

3. **Exportar resultados**:
   - Cuaderno 2 (`2.descriptive_statistics.ipynb`): exporta tablas y figuras descriptivas a `final_noteboooks/outputs_descriptivos/`.
   - Cuaderno 3 (`3.exploratory_analysis.ipynb`): exporta tablas y figuras inferenciales a `final_noteboooks/outputs_inferencia/`.
   - Solo el cuaderno 4 (`4.draft_paper.ipynb`) puede exportar directamente a `latex/figures/` y `latex/tables/`.
4. **Integrar en paper** → `latex/paper/rcp_transtelefonica_paper.tex`
5. **Compilar** → Usar las tareas de VS Code disponibles

## Especificación de Cuadernos de Análisis

### Cuaderno 2: Estadística Descriptiva (`2.descriptive_statistics.ipynb`)
- Dedicado exclusivamente a la estadística descriptiva de la muestra.
- Genera tablas y gráficos descriptivos (distribución de variables, frecuencias, medidas de tendencia central, etc.).
- Todos los outputs descriptivos se exportan a `final_noteboooks/outputs_descriptivos/` para su posterior uso en LaTeX.

### Cuaderno 3: Inferencia Estadística (`3.exploratory_analysis.ipynb`)

Este cuaderno documenta y ejecuta toda la inferencia estadística que se reportará en el paper, generando las tablas y figuras necesarias para LaTeX.

**Grupos de estudio:**
1. Sin RCP previa
2. RCP por testigos legos
3. RCP por primeros respondientes: sanitario, policía, bomberos. (Añadir nota que sanitarios incluye SVB SAMUR, personal hospitalario, SUMMA, etc.)
4. RCP transtelefónica

**Estratificaciones:**
- Por edad: ≤65 años vs >65 años
- Por tiempo de llegada: menor vs mayor que la media
- Por tiempo de RCP (excluyendo valores 0): menor vs mayor que la media

**Hipótesis principales:**
1. La RCP transtelefónica mejora los outcomes comparado con RCP por legos.
2. El beneficio es mayor cuanto más tarda la unidad en llegar.
3. El beneficio es mayor cuanto mayor es el tiempo de RCP.

**Hipótesis alternativa/nula:**
La RCP transtelefónica no mejora los outcomes comparado con RCP por legos.
El tiempo de llegada no afecta a la efectividad de la RCP transtelefónica.
El tiempo de RCP no afecta a la efectividad de la RCP transtelefónica.

**Variables outcome a evaluar:**
- ROSC (retorno circulación espontánea)
- Supervivencia
- CPC favorable (CPC 1-2)

**Pruebas estadísticas:**
a) Supervivencia (dicotómica):
   - Test χ² (Chi-cuadrado) para comparar proporciones entre grupos.
   - Si alguna celda tiene <5 observaciones, usar test exacto de Fisher.
b) CPC (ordinal/categórica):
   - Comparar "Buen CPC" (1-2) vs "Malo" (3-5) con χ².
   - Para comparar medianas/distribuciones completas, usar Mann-Whitney U.
c) ROSC: igual que supervivencia.
d) Regresión logística:
   - Estimar asociación entre tipo de RCP y outcomes (supervivencia, CPC), ajustando por edad, sexo, etc.
   - Aplicar scikit-learn para modelos multivariados y machine learning si procede.

**Outputs requeridos:**
- Tablas resumen de resultados de cada análisis (proporciones, OR, IC95%, p-valores).
- Gráficos inferenciales: forest plots, gráficos de barras con IC, etc.
- Apartado resumen de resultados estadísticamente significativos para discusión.
- Todos los outputs se exportan a `final_noteboooks/outputs_inferencia/` para su posterior uso en LaTeX.

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

- **SOLO** `4.draft_paper.ipynb` puede guardar outputs definitivos en `latex/figures/` y `latex/tables/`.
- `2.descriptive_statistics.ipynb` y `3.exploratory_analysis.ipynb` deben guardar sus outputs definitivos en carpetas propias al mismo nivel que el notebook (`final_noteboooks/outputs_descriptivos/` y `final_noteboooks/outputs_inferencia/` respectivamente), y no directamente en `latex/figures/` o `latex/tables/`.
- Siempre verificar que se usa el lenguaje de diseño correcto al escribir las gráficas.

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
* Todas las abreviaciones deben ser definidas en su primera aparición. Despues de la primera vez, se pueden usar las abreviaciones sin definirlas de nuevo.
* El paper debe seguir la estructura IMRaD (Introducción, Métodos, Resultados y Discusión) con secciones adicionales según sea necesario.
* Las secciones deben ser claras y concisas, con un enfoque en la reproducibilidad y transparencia del análisis.
* Las tablas y figuras deben ser autoexplicativas y acompañadas de leyendas detalladas.
* 
* Se citara en IEEE

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

### Reportes Estadísticos
- **Medidas de tendencia central**: Media ± DE o Mediana (IQR)
- **Tests de hipótesis**: Chi-cuadrado, t-Student, Mann-Whitney, Fisher
- **Análisis multivariado**: Regresión logística con OR ajustados
- **Análisis de supervivencia**: Hazard ratios con IC 95%
- **Corrección por múltiples comparaciones**: Bonferroni o FDR

