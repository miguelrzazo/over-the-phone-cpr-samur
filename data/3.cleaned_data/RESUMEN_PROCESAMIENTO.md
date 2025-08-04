# Resumen de Procesamiento de Datos RCP Transtelefónica (ACTUALIZADO)

## Fecha de Procesamiento
**4 de Agosto de 2025**

## Archivos Generados

### 1. Archivos de Datos FINALES
- **`datos_con_cpc_valido.csv`**: 500 registros con CPC válido (valores 1-5) y sin casilla Excluido rellenada
- **`datos_excluidos.csv`**: 566 registros excluidos del análisis
- **`tabla_resumen_caracteristicas.csv`**: Tabla resumen con estadísticas descriptivas

### 2. Scripts de Procesamiento
- **`process_data.py`**: Script principal que separa los datos y genera el reporte PDF
- **`detailed_analysis.py`**: Script de análisis detallado con estadísticas por grupos
- **`fix_data_types.py`**: Script para corregir tipos de datos a enteros

### 3. Reportes
- **`reporte_datos_rcp_transtelefonica.pdf`**: Reporte visual con gráficos (ubicado en data/2.Data_cleaning/)

## ✅ CAMBIOS IMPLEMENTADOS

### Exclusiones Más Estrictas
- **REGLA PRINCIPAL**: Si la casilla `Excluido` está rellenada, el registro NO puede estar en el archivo de CPC válido
- **Resultado**: 8 registros que tenían CPC válido pero casilla Excluido rellenada fueron movidos SOLO a exclusiones

### Limpieza de Columnas
- **ELIMINADAS** de archivos finales: `Excluido`, `CPC_valido`, `Es_excluido`
- **CONSERVADA** en archivo exclusiones: columna `Excluido` para ver motivo

### Tipos de Datos
- **Números convertidos a enteros** cuando es posible
- **NaN preservados** para valores faltantes
- **Formato limpio** sin decimales innecesarios

## Resumen Ejecutivo ACTUALIZADO

### Datos Originales
- **Total registros originales**: 1,066
- **Registros procesados**: 1,066 (100%)

### Exclusiones (566 casos, 53.1%)
- **SVB**: 325 casos (30.5%) - No fueron casos de parada cardiorrespiratoria
- **TRAUMA**: 143 casos (13.4%) - Casos de trauma excluidos del estudio
- **CADÁVER**: 45 casos (4.2%) - Pacientes fallecidos antes de la llegada
- **NO CPC**: 35 casos (3.3%) - Sin CPC asignado pero casos válidos
- **Otros motivos**: 18 casos (1.7%) - Otras razones de exclusión

### Datos Válidos para Análisis (500 casos, 46.9%)

#### Características de la Población
- **Edad media**: 66.1 ± 16.3 años
- **Sexo masculino**: 396 casos (79.2%)
- **Estratificación por edad**:
  - <65 años: 222 casos (44.4%)
  - ≥65 años: 278 casos (55.6%)

#### Grupos de RCP
1. **Sin RCP previa**: 166 casos (33.2%)
2. **RCP por primeros respondientes**: 144 casos (28.8%)
   - Incluye: sanitarios, policía, bomberos
3. **RCP Transtelefónica**: 113 casos (22.6%)
4. **RCP por testigos legos**: 77 casos (15.4%)

#### Outcomes Principales
- **ROSC**: 300 casos (60.0%)
- **Supervivencia a 7 días**: 129 casos (25.8%)
- **CPC favorable (1-2)**: 111 casos (22.2%)
  - CPC 1 (función normal): 101 casos (20.2%)
  - CPC 2 (discapacidad leve): 10 casos (2.0%)

#### Distribución de CPC
- **CPC 1**: 101 casos (20.2%)
- **CPC 2**: 10 casos (2.0%)
- **CPC 3**: 6 casos (1.2%)
- **CPC 4**: 3 casos (0.6%)
- **CPC 5**: 380 casos (76.0%)

#### Tiempos de Respuesta
- **Tiempo de llegada medio**: 8.4 minutos (rango: 0.1 - 70.8 min)
- **Tiempo de RCP medio**: 29.8 minutos (rango: 0.02 - 76.7 min)

## Análisis por Grupos de RCP

### ROSC por Grupo
- **RCP por testigos legos**: 68.8%
- **RCP por primeros respondientes**: 63.2%
- **RCP Transtelefónica**: 60.4%
- **Sin RCP previa**: 53.9%

### Supervivencia a 7 días por Grupo
- **RCP por primeros respondientes**: 31.9%
- **RCP Transtelefónica**: 29.2%
- **RCP por testigos legos**: 28.6%
- **Sin RCP previa**: 17.0%

### CPC Favorable por Grupo
- **RCP por primeros respondientes**: 29.9%
- **RCP por testigos legos**: 26.0%
- **RCP Transtelefónica**: 23.0%
- **Sin RCP previa**: 13.3%

## Análisis Estratificado por Edad

### Outcomes en <65 años
- **ROSC**: 69.7%
- **Supervivencia**: 34.4%
- **CPC favorable**: 31.5%

### Outcomes en ≥65 años
- **ROSC**: 52.9%
- **Supervivencia**: 19.1%
- **CPC favorable**: 14.7%

## Estructura de Archivos Finales

### `datos_con_cpc_valido.csv` (500 registros)
**Columnas incluidas:**
- NUM INFORME (entero)
- FECHA_LLAMADA (texto)
- EDAD (entero, permite NaN)
- SEXO (texto)
- RCP_TRANSTELEFONICA (entero: 0 o 1)
- DESA_EXTERNO (entero: 0 o 1)
- RCP_TESTIGOS (texto)
- Tiempo_llegada (entero, segundos)
- Tiempo_Rcp (entero, segundos)
- Desfibrilable_inicial (entero: 0 o 1)
- ROSC (entero: 0 o 1)
- Supervivencia_7dias (entero: 0 o 1)
- CPC (entero: 1, 2, 3, 4, o 5)

**✅ NO incluye:** columnas auxiliares (`Excluido`, `CPC_valido`, `Es_excluido`)

### `datos_excluidos.csv` (566 registros)
**Estructura:** Mismas columnas + columna `Excluido` con motivo de exclusión

## Reglas de Exclusión Aplicadas

1. **Si `Excluido` tiene cualquier valor** → Va a archivo de exclusiones
2. **Si `CPC` no es 1, 2, 3, 4, o 5** → No va a archivo CPC válido  
3. **Si ambas condiciones se cumplen** → Va SOLO a exclusiones (no duplicado)

## Archivos Listos para Análisis

Los siguientes archivos están listos para ser utilizados en los notebooks de análisis:

- `./data/3.cleaned_data/datos_con_cpc_valido.csv` - Para análisis principal
- `./data/3.cleaned_data/datos_excluidos.csv` - Para análisis de exclusiones
- `./data/3.cleaned_data/tabla_resumen_caracteristicas.csv` - Para tabla descriptiva en LaTeX

## Diferencias con Versión Anterior

1. **8 registros menos** en datos válidos (500 vs 508) - tenían CPC válido pero casilla Excluido rellenada
2. **Columnas auxiliares eliminadas** de archivos finales
3. **Tipos de datos más limpios** (enteros cuando es posible)
4. **Reglas de exclusión más estrictas** aplicadas
