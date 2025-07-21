# Instrucciones para GitHub Copilot en este proyecto

Este repositorio es un paper de investigación sobre la supervivencia en parada cardiorrespiratoria en Madrid (2024), con foco en el impacto de la RCP transtelefónica, edad, sexo y tiempo de llegada de la unidad actuante. Los datos provienen de SAMUR-PC.

## Buenas prácticas para Copilot

- Usa notebooks en Python para análisis y generación de gráficas. Guarda las figuras en `proyecto/figures/` usando rutas relativas.
- El paper y el poster están en LaTeX (`proyecto/paper/` y `proyecto/poster/`). Incluye las figuras con rutas relativas (`../figures/figura.png`).
- Si generas nuevas figuras en el notebook, usa siempre `plt.savefig('../proyecto/figures/nombre_figura.png', dpi=300, bbox_inches='tight')` para que se actualicen automáticamente en el paper/poster.
- Mantén el código limpio y documentado. Usa funciones para análisis repetitivos.
- Si necesitas agregar nuevos análisis, crea nuevas celdas en el notebook y guarda las figuras con nombres descriptivos.
- No subas datos sensibles ni personales.

## Ejemplo de guardado de figura en notebook
```python
plt.figure(figsize=(8,6))
sns.histplot(df['EDAD'])
plt.title('Distribución de Edad')
plt.savefig('../proyecto/figures/edad_hist.png', dpi=300, bbox_inches='tight')
plt.close()
```

## Ejemplo de inclusión de figura en LaTeX
```latex
\begin{figure}[ht]
    \centering
    \includegraphics[width=0.7\textwidth]{../figures/edad_hist.png}
    \caption{Distribución de edad de los pacientes}
\end{figure}
```
