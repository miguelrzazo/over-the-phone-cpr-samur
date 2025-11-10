# Datos del Estudio RCP Transtelefónica

## ⚠️ Aviso Importante sobre Privacidad

**Los datos originales de pacientes NO están disponibles públicamente por protección de datos personales (GDPR).**

Este directorio contiene:
- ✅ Scripts de procesamiento y limpieza (código abierto)
- ✅ Documentación del proceso (transparencia metodológica)
- ❌ Datos brutos de pacientes (confidenciales)
- ❌ Datos individuales identificables (protegidos)

---

## 📁 Estructura del Directorio

```
data/
├── 1.raw_imported/           # Datos originales (NO PÚBLICOS)
│   └── *.csv, *.xlsx        # Archivos confidenciales ignorados por git
│
├── 2.Data_cleaning/          # Pipeline de limpieza
│   ├── cleaning.py          # Script principal de limpieza
│   ├── process_data.py      # Procesamiento y separación
│   ├── Reglas_exclusion.md  # Criterios de exclusión documentados
│   ├── informe_anomalias.md # Reporte de anomalías detectadas
│   └── [PDFs generados]     # Reportes visuales del procesamiento
│
└── 3.cleaned_data/          # Datos finales procesados (NO PÚBLICOS)
    ├── datos_con_cpc_valido.csv      # 500 casos válidos para análisis
    ├── datos_excluidos.csv           # 566 casos excluidos
    ├── tabla_resumen_caracteristicas.csv  # Estadísticas agregadas
    └── RESUMEN_PROCESAMIENTO.md      # Documentación completa
```

---

## 🔄 Pipeline de Procesamiento

### Fase 1: Importación (`1.raw_imported/`)

**Fuente:** Formularios electrónicos de SAMUR-PC Madrid
**Período:** Julio 2023 - Junio 2025 (24 meses)
**Formato original:** Excel (.xlsx) y CSV

**Datos originales:**
- 1,066 registros iniciales
- Variables: demográficas, clínicas, tiempos, outcomes
- Cumplimentados por: Unidades SVA, SVB y teleoperadores

### Fase 2: Limpieza y Validación (`2.Data_cleaning/`)

**Scripts principales:**

#### `cleaning.py`
- Detección de duplicados
- Validación de tipos de datos
- Identificación de valores atípicos
- Merge de registros SVA/SVB de mismo evento

#### `process_data.py`
- Aplicación de criterios de exclusión
- Separación de datos válidos vs excluidos
- Generación de reportes visuales (PDF)
- Creación de tablas resumen

**Criterios de exclusión aplicados:**
1. **SVB (n=325, 30.5%):** No correspondían a PCR
2. **TRAUMA (n=143, 13.4%):** Paradas traumáticas excluidas
3. **CADÁVER (n=45, 4.2%):** Fallecidos antes de llegada
4. **NO CPC (n=35, 3.3%):** Sin CPC asignado
5. **OTROS (n=18, 1.7%):** Diversas razones

**Total excluidos:** 566 casos (53.1%)  
**Total válidos:** 500 casos (46.9%)

### Fase 3: Datos Finales (`3.cleaned_data/`)

#### `datos_con_cpc_valido.csv` (500 registros)

**Estructura:**
```csv
NUM_INFORME, FECHA_LLAMADA, EDAD, SEXO, 
RCP_TRANSTELEFONICA, DESA_EXTERNO, RCP_TESTIGOS,
Tiempo_llegada, Tiempo_Rcp, Desfibrilable_inicial,
ROSC, Supervivencia_7dias, CPC
```

**Características:**
- **Edad:** Media 66.1 ± 16.3 años (rango: 18-98)
- **Sexo:** 79.2% masculino
- **Grupos de RCP:**
  - Sin RCP previa: 169 (33.8%)
  - Testigos legos: 172 (34.4%)
  - Sanitarios: 93 (18.6%)
  - Policía: 64 (12.8%)
  - Bomberos: 2 (0.4%)

**Outcomes:**
- ROSC: 300 casos (60.0%)
- Supervivencia 7d: 129 casos (25.8%)
- CPC favorable (1-2): 111 casos (22.2%)

#### `datos_excluidos.csv` (566 registros)

Contiene todos los casos excluidos con:
- Motivo de exclusión en columna `Excluido`
- Misma estructura que archivo principal
- Útil para auditoría y análisis de sesgos de selección

#### `RESUMEN_PROCESAMIENTO.md`

Documentación exhaustiva del proceso:
- Estadísticas detalladas por grupo
- Justificación de cada exclusión
- Análisis de calidad de datos
- Validaciones implementadas

---

## 📊 Estadísticas de la Muestra Final

### Demografía
- **N total:** 500 casos válidos
- **Edad media:** 66.1 ± 16.3 años
- **Distribución edad:**
  - <65 años: 222 casos (44.4%)
  - ≥65 años: 278 casos (55.6%)
- **Sexo:** 396 hombres (79.2%), 104 mujeres (20.8%)

### Tiempos de Respuesta
- **Tiempo llegada:** Media 8.4 min (rango: 0.1 - 70.8 min)
- **Tiempo RCP:** Media 29.8 min (rango: 0.02 - 76.7 min)

### Outcomes Principales

**Por grupo de RCP:**

| Grupo | n | ROSC | Supervivencia | CPC Favorable |
|-------|---|------|---------------|---------------|
| Sanitarios | 93 | 67.7% | 40.9% | 38.7% |
| Testigos legos | 172 | 65.7% | 29.7% | 25.6% |
| Sin RCP previa | 169 | 53.3% | 17.2% | 13.0% |
| Policía | 64 | 50.0% | 17.2% | 14.1% |
| Bomberos | 2 | 100% | 0% | 0% |

**Estratificación por edad:**

| Grupo Edad | n | ROSC | Supervivencia | CPC Favorable |
|------------|---|------|---------------|---------------|
| <65 años | 222 | 69.7% | 34.4% | 31.5% |
| ≥65 años | 278 | 52.9% | 19.1% | 14.7% |

---

## 🔍 Validaciones Implementadas

### 1. Validación de Tipos de Datos
```python
# Ejecutado por fix_data_types.py
- Conversión a enteros cuando apropiado
- Preservación de NaN para valores faltantes
- Verificación de rangos válidos (edad: 0-120, CPC: 1-5)
```

### 2. Detección de Duplicados
- Merge de SVA/SVB del mismo evento (por fecha/hora)
- Priorización de datos SVA sobre SVB
- Documentación de casos fusionados

### 3. Consistencia Lógica
- ROSC=1 → Supervivencia puede ser 0 o 1
- Supervivencia=1 → ROSC debe ser 1
- CPC 1-2 → Supervivencia debe ser 1
- Edad vs CPC: consistencia verificada

### 4. Valores Atípicos
- Tiempos negativos: corregidos o excluidos
- Tiempos extremos (>120 min): revisados manualmente
- CPC fuera de rango 1-5: excluidos

---

## 📖 Cómo Reproducir el Procesamiento

### Requisitos
```bash
pip install pandas numpy openpyxl
```

### Ejecución (SI TIENES ACCESO A DATOS BRUTOS)

```bash
# 1. Colocar archivos originales en data/1.raw_imported/

# 2. Ejecutar limpieza
cd data/2.Data_cleaning/
python cleaning.py

# 3. Procesar y separar datos
python process_data.py

# 4. Verificar outputs en data/3.cleaned_data/
ls -la ../3.cleaned_data/
```

### Para Investigadores Externos

Si eres un investigador y deseas:
- **Replicar la metodología:** Usa los scripts en `2.Data_cleaning/` con tus propios datos
- **Verificar el análisis:** Los notebooks en `final_noteboooks/` funcionan con datos simulados
- **Solicitar colaboración:** Contacta a los autores (ver README principal)

---

## 🛡️ Consideraciones Éticas y Legales

### Protección de Datos
- Cumplimiento **GDPR** (Reglamento General de Protección de Datos)
- Datos anonimizados para análisis
- Sin identificadores personales en archivos de análisis

### Aprobación Ética
- Estudio retrospectivo observacional
- Datos recopilados como parte de la asistencia estándar
- Sin intervenciones experimentales

### Uso Permitido
✅ Scripts de procesamiento (código abierto)  
✅ Metodología de limpieza (documentada)  
✅ Resultados agregados (anonimizados)  
❌ Datos individuales de pacientes (protegidos)

---

## 📝 Documentación Relacionada

- **Procesamiento completo:** `3.cleaned_data/RESUMEN_PROCESAMIENTO.md`
- **Reglas de exclusión:** `2.Data_cleaning/Reglas_exclusion.md`
- **Análisis estadístico:** `../documentation/3.data_analysis.md`
- **Workflow general:** `../documentation/1. Workflow.md`

---

## 🔧 Scripts Disponibles

### `cleaning.py`
**Función:** Limpieza inicial y detección de anomalías  
**Input:** `1.raw_imported/*.csv`  
**Output:** Reportes de validación

### `process_data.py`
**Función:** Procesamiento final y separación de datos  
**Input:** Datos limpios  
**Output:** 
- `datos_con_cpc_valido.csv`
- `datos_excluidos.csv`
- PDF de reportes visuales

### `fix_data_types.py`
**Función:** Corrección de tipos de datos  
**Input:** Datos procesados  
**Output:** Datos con tipos correctos

---

## 📊 Calidad de los Datos

### Completitud
- **CPC:** 100% (criterio de inclusión)
- **Edad:** 98.2% (9 valores faltantes)
- **Sexo:** 100%
- **ROSC:** 100%
- **Supervivencia:** 100%
- **Tiempos:** 95.4% completo

### Consistencia
- ✅ Sin duplicados en muestra final
- ✅ Rangos de valores validados
- ✅ Relaciones lógicas verificadas
- ✅ Tipos de datos correctos

### Trazabilidad
- 📄 Todos los cambios documentados
- 📄 Criterios de exclusión justificados
- 📄 Transformaciones registradas
- 📄 Versiones de scripts versionadas

---

## 📞 Contacto

Para consultas sobre:
- **Acceso a datos:** No disponible por protección de datos
- **Colaboraciones:** Contactar a los autores (ver README principal)
- **Metodología:** Revisar documentación en `documentation/`

---

**Última actualización:** Noviembre 2025  
**Versión de datos:** 1.0 (Final)  
**Responsable:** Equipo SAMUR-PC Madrid
