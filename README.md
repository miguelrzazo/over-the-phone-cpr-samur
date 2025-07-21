# Through Phone CPR: Análisis de Supervivencia en Parada Cardiorrespiratoria en Madrid 2024

Este repositorio contiene el material de un paper de investigación que explora la tasa de supervivencia en pacientes que han sufrido una parada cardiorrespiratoria en la ciudad de Madrid durante 2024.

## Objetivo del estudio
El foco del estudio es analizar la variación de la supervivencia en función de si los pacientes recibieron RCP transtelefónica o no, considerando además los grupos de edad, sexo y controlando el tiempo de llegada de la unidad actuante.

## Estructura del repositorio
- `data/`: Datos brutos y procesados (proporcionados por SAMUR-PC)
- `notebooks/`: Jupyter Notebooks en Python para análisis y generación de gráficas
- `proyecto/paper/`: Paper científico en LaTeX
- `proyecto/poster/`: Poster científico en LaTeX
- `proyecto/figures/`: Figuras exportadas desde los notebooks para su uso en el paper y el poster
- `src/`: Código fuente adicional
- `tests/`: Pruebas unitarias

## Requisitos
- Python 3.8+
- Paquetes: ver `requirements.txt`
- LaTeX para compilar el paper y el poster

## Instrucciones para reproducibilidad
1. Ejecuta los notebooks en `notebooks/` para generar y actualizar las gráficas en `proyecto/figures/`.
2. Compila el paper o el poster en LaTeX, enlazando las figuras desde la carpeta `figures`.

## Créditos
Datos proporcionados por SAMUR-PC.
