---
applyTo: '**'
---
## Contexto del Proyecto
Este repositorio contiene el análisis científico de datos de RCP (reanimación cardiopulmonar) transtelefónica, con el objetivo de evaluar rigurosamente si la RCP guiada por teléfono mejora la recuperación del pulso (ROSC) y la supervivencia a 7 días tras una parada cardiaca extrahospitalaria.

### Variables principales del dataset (`cleaned_data.csv`):
- `EDAD`: Edad del paciente.
- `SEXO`: Sexo del paciente.
- `RCP_TRANSTELEFONICA`: Si recibió RCP guiada por teléfono (verdadero/falso).
- `TIEMPO_LLEGADA_UNIDAD`: Tiempo (en segundos) hasta la llegada de la unidad de emergencia.
- `SOBREVIVE_7DIAS`: Supervivencia a los 7 días (booleano).
- `ROSC`: Retorno de circulación espontánea (booleano, verdadero si el código patológico es C.0.0 o C.0.2 ECMO).

## Enfoque y metodología
El análisis se realizará en un notebook Jupyter, donde:
- Se explorarán y describirán los datos.
- Se generarán visualizaciones (todas las figuras se guardarán en la carpeta `proyecto/figures`).
- Se aplicarán análisis estadísticos rigurosos, incluyendo el estudio de factores asociados mediante:
  - Regresión logística multivariante para ajustar por variables de confusión (edad, sexo, tiempo de llegada) y analizar predictores de ROSC y supervivencia.
  - Pruebas de chi cuadrado para comparar proporciones (por ejemplo, ROSC vs. no ROSC según RCP transtelefónica o sexo).
  - Pruebas t de Student para comparar medias (edad, tiempo de llegada, según ROSC).
  - Tablas de contingencia y análisis de regresión logística incluyendo ROSC como predictor.
  - Cálculo de valores p, intervalos de confianza y análisis de sensibilidad.
  - Se reportarán los resultados siguiendo estándares de inferencia estadística.

## Flujo de trabajo
1. Análisis exploratorio y visualización en Jupyter Notebook.
2. Guardado de todas las figuras en `proyecto/figures` para su uso posterior.
3. Redacción del paper científico en LaTeX (carpeta `proyecto/paper`).
4. Preparación de un póster científico (`proyecto/poster`).

## Directrices para la generación de código y análisis
- El código debe ser claro, reproducible y documentado.
- Las visualizaciones deben ser exportadas a la carpeta de figuras.
- Los análisis deben incluir medidas de incertidumbre (intervalos de confianza) y pruebas de hipótesis (valor p).
- Se debe justificar y explicar cada paso del análisis en el notebook.