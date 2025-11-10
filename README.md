# Efectividad de la RCP Transtelefónica en Paradas Cardíacas Extrahospitalarias

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Status: Complete](https://img.shields.io/badge/status-complete-success.svg)]()

Este repositorio contiene todo el código, datos procesados, análisis estadístico y documentación del estudio sobre la efectividad de la Reanimación Cardiopulmonar (RCP) guiada telefónicamente por el servicio de emergencias SAMUR-PC de Madrid.

## 📊 Resumen del Estudio

### Contexto Clínico
La parada cardiaca extrahospitalaria (PCEH) es una de las principales causas de mortalidad a nivel mundial. La RCP transtelefónica, donde los operadores de emergencias guían a los testigos mediante instrucciones telefónicas, representa una estrategia clave para mejorar los resultados en pacientes con PCEH antes de la llegada de los servicios médicos.

### Objetivos
Evaluar el impacto de la RCP transtelefónica en:
- **Retorno de circulación espontánea (ROSC)**
- **Supervivencia a 7 días**
- **Estado neurológico favorable** (CPC 1-2: Cerebral Performance Category)

### Diseño del Estudio
- **Tipo:** Estudio observacional retrospectivo
- **Población:** 500 casos de PCEH no traumática
- **Período:** Julio 2023 - Junio 2025 (24 meses)
- **Servicio:** SAMUR-PC Madrid
- **Ejecutores:** Técnicos de Emergencias Sanitarias (TES) voluntarios de SAMUR-PC

### 🎯 Resultados Principales

#### Outcomes por Tipo de RCP

| Grupo de RCP | N | ROSC | Supervivencia 7d | CPC Favorable (1-2) |
|--------------|---|------|------------------|---------------------|
| **Sanitarios** | 93 | 67.7% | 40.9% | **38.7%** |
| **RCP por testigos legos** | 172 | 65.7% | 29.7% | 25.6% |
| **Sin RCP previa** | 169 | 53.3% | 17.2% | 13.0% |
| **Policía** | 64 | 50.0% | 17.2% | 14.1% |

*Nota: Los datos de RCP transtelefónica están incluidos en el grupo de testigos legos con guía telefónica.*

#### Hallazgos Clave
✅ **La RCP por personal sanitario** mostró los mejores outcomes en todos los indicadores  
✅ **La RCP por testigos legos** (incluida guía telefónica) mejoró significativamente el ROSC comparado con sin RCP previa (65.7% vs 53.3%)  
✅ **La supervivencia a 7 días** fue 72% mayor con RCP por testigos comparado con sin RCP (29.7% vs 17.2%)  
✅ **El CPC favorable** duplicó con RCP por testigos comparado con sin RCP (25.6% vs 13.0%)

### Características de la Muestra
- **Edad media:** 66.1 ± 16.3 años
- **Sexo masculino:** 79.2%
- **Estratificación por edad:**
  - <65 años: 44.4% (mejor pronóstico)
  - ≥65 años: 55.6%

### Transparencia y Reproducibilidad
Todos los métodos analíticos, procedimientos estadísticos y técnicas de visualización están documentados y disponibles para revisión por pares y replicación. Los datos originales no están disponibles públicamente por protección de datos personales, pero todos los scripts de procesamiento y análisis están incluidos.

---

## 📁 Estructura del Repositorio

```
RCP-Transtelefonica/
│
├── 📄 README.md                      # Este archivo
├── 📄 LICENSE                        # Licencia MIT
├── 📄 CITATION.cff                   # Información de citación
│
├── 📂 data/                          # Pipeline de procesamiento de datos
│   ├── 1.raw_imported/              # Datos originales (no públicos)
│   ├── 2.Data_cleaning/             # Scripts de limpieza y validación
│   │   ├── cleaning.py
│   │   ├── process_data.py
│   │   ├── informe_anomalias.md
│   │   └── Reglas_exclusion.md
│   └── 3.cleaned_data/              # Datos finales limpios
│       ├── datos_con_cpc_valido.csv # 500 casos para análisis
│       ├── datos_excluidos.csv      # 566 casos excluidos
│       └── RESUMEN_PROCESAMIENTO.md # Resumen completo
│
├── 📂 final_noteboooks/             # Análisis estadístico completo
│   ├── 1. design_language.ipynb    # Especificaciones de diseño visual
│   ├── 2. descriptive_statistics.ipynb  # Estadística descriptiva
│   ├── 3. exploratory_analysis.ipynb    # Análisis inferencial
│   ├── 4. draft_paper.ipynb        # Integración para paper
│   ├── outputs_descriptivos/       # Tablas y figuras descriptivas
│   └── outputs_inferencia/         # Resultados inferenciales y ML
│
├── 📂 latex/                        # Materiales de publicación
│   ├── paper/                      # Manuscrito científico
│   │   └── rcp_transtelefonica_paper.tex
│   ├── figures/                    # Figuras finales alta resolución
│   └── tables/                     # Tablas en formato LaTeX
│
├── 📂 Poster/                       # Poster del congreso
│   └── Poster_final.pdf            # Versión presentada
│
└── 📂 documentation/                # Documentación técnica
    ├── 1. Workflow.md              # Flujo de trabajo del estudio
    ├── 2. data_cleaning.md         # Proceso de limpieza
    ├── 3. data_analysis.md         # Metodología estadística
    ├── 4. Presentation.md          # Guía de presentación
    └── requirements.txt            # Dependencias Python
```

---

## 🚀 Cómo Usar Este Repositorio

### Para Profesionales Médicos e Investigadores

**1. Comprender la Metodología**
- Comienza con [`documentation/1. Workflow.md`](documentation/1.%20Workflow.md) para una guía completa del enfoque metodológico
- Revisa [`data/3.cleaned_data/RESUMEN_PROCESAMIENTO.md`](data/3.cleaned_data/RESUMEN_PROCESAMIENTO.md) para entender los criterios de inclusión/exclusión

**2. Explorar los Resultados**
- **Poster del congreso:** [`Poster/Poster_final.pdf`](Poster/Poster_final.pdf) - Resumen visual de hallazgos
- **Manuscrito completo:** `latex/paper/rcp_transtelefonica_paper.pdf` (una vez compilado)
- **Figuras de alta resolución:** `latex/figures/`

**3. Revisar los Análisis**
- **Estadística descriptiva:** [`final_noteboooks/2. descriptive_statistics.ipynb`](final_noteboooks/2.%20descriptive_statistics.ipynb)
- **Análisis inferencial:** [`final_noteboooks/3. exploratory_analysis.ipynb`](final_noteboooks/3.%20exploratory_analysis.ipynb)
- No se requiere experiencia en programación para leer los notebooks - incluyen explicaciones detalladas

**4. Entender el Procesamiento de Datos**
- [`documentation/2. data_cleaning.md`](documentation/2.%20data_cleaning.md) - Criterios de exclusión y transformaciones
- [`data/2.Data_cleaning/Reglas_exclusion.md`](data/2.Data_cleaning/Reglas_exclusion.md) - Reglas específicas aplicadas

### Para Usuarios Técnicos

**Requisitos:**
```bash
# Python 3.10 o superior
python --version

# Instalar dependencias
pip install -r documentation/requirements.txt
```

**Ejecutar Análisis:**
```bash
# 1. Navegar al directorio de notebooks
cd final_noteboooks/

# 2. Iniciar Jupyter
jupyter notebook

# 3. Abrir y ejecutar notebooks en orden:
#    - 1. design_language.ipynb
#    - 2. descriptive_statistics.ipynb
#    - 3. exploratory_analysis.ipynb
#    - 4. draft_paper.ipynb
```

**Compilar Paper LaTeX:**
```bash
cd latex/paper/
xelatex rcp_transtelefonica_paper.tex
# o usar pdflatex si xelatex no está disponible
```

---

## 📊 Métodos Estadísticos Empleados

### Análisis Descriptivo
- Estadísticas de tendencia central y dispersión
- Tablas de características basales (Tabla 1)
- Análisis estratificado por edad y otros factores

### Análisis Inferencial
- **Tests bivariados:** Chi-cuadrado (χ²), Fisher exacto, Mann-Whitney U
- **Regresión logística:** Modelos ajustados por edad, sexo, ritmo inicial
- **Análisis de supervivencia:** Curvas de Kaplan-Meier, modelo de Cox
- **Machine Learning:** Modelos con regularización L2, validación cruzada estratificada
- **Métricas:** Odds Ratios (OR), Intervalos de Confianza 95%, AUC-ROC, p-valores

### Control de Calidad
- Corrección por múltiples comparaciones
- Validación cruzada estratificada (5-fold)
- Bootstrap para intervalos de confianza robustos
- Semillas fijas para reproducibilidad (random_state=42)

---

## 📖 Citación

Si utilizas este código, metodología o hallazgos en tu investigación, por favor cita apropiadamente:

```bibtex
@misc{munoz2025rcp_transtelefonica,
  author = {Muñoz Condés, María del Rosario and Rosa Zazo, Miguel and Córcoba Fernández, Óscar and others},
  title = {Efectividad de la RCP Transtelefónica en Paradas Cardíacas Extrahospitalarias: Análisis SAMUR-PC 2023-2025},
  year = {2025},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/miguelrzazo/over-the-phone-cpr-samur}}
}
```

---

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

**Política de Datos:**
- Los datos originales no están disponibles públicamente por protección de datos personales
- Los scripts de procesamiento y análisis están completamente disponibles
- Los resultados agregados y anonimizados se comparten para transparencia científica

---

## 👥 Equipo de Investigación

**Institución:** SAMUR-PC, Servicio de Asistencia Municipal de Urgencias y Rescate, Madrid, España

**Coordinadores del estudio:**
- María del Rosario Muñoz Condés, TES
- Miguel Rosa Zazo, TES
- Óscar Córcoba Fernández, TES

**Voluntarios TES de SAMUR-PC** que contribuyeron a la recolección de datos y revisión del estudio.

---

## 🔬 Ética y Cumplimiento

Este estudio fue conducido de acuerdo con:
- Directrices éticas de investigación aplicables
- Regulaciones de protección de datos (GDPR)
- Estándares STROBE para estudios observacionales
- Protocolos de SAMUR-PC Madrid

---

## 📞 Contacto

Para consultas sobre el estudio, metodología o colaboraciones:
- **Email:** [contacto pendiente]
- **Institución:** SAMUR-PC Madrid

---

## 🙏 Agradecimientos

Agradecemos a:
- Todo el personal de SAMUR-PC Madrid por su dedicación
- Los técnicos de emergencias sanitarias voluntarios que recopilaron los datos
- Los coordinadores médicos que facilitaron el estudio
- Las familias y pacientes que indirectamente contribuyen a mejorar la atención de emergencias

---

**Última actualización:** Noviembre 2025  
**Estado del proyecto:** ✅ Completo - Poster presentado en congreso
