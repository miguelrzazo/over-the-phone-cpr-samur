import pandas as pd
import numpy as np

# Cargar datos
df = pd.read_csv('raw_data_cpr.csv', encoding='utf-8', sep=';')

# Seleccionar columnas relevantes (ajustar si es necesario)
cols = ['EDAD', 'SEXO', 'RCP_TRANSTELEFONICA', 'C0_C1', 'C1_C2', 'C2_C3']
df = df[cols].copy()

# Limpiar y codificar variables
df['EDAD'] = pd.to_numeric(df['EDAD'], errors='coerce')
df['SEXO'] = df['SEXO'].str.strip().str.capitalize()
df['RCP_TRANSTELEFONICA'] = df['RCP_TRANSTELEFONICA'].str.strip().str.lower()

# Calcular tiempo de llegada (suma de C0_C1, C1_C2 y C2_C3)
for col in ['C0_C1', 'C1_C2', 'C2_C3']:
    df[col] = pd.to_numeric(df[col], errors='coerce')
df['TIEMPO_LLEGADA_UNIDAD'] = df['C0_C1'].fillna(0) + df['C1_C2'].fillna(0) + df['C2_C3'].fillna(0)

# Eliminar columnas originales de tiempos parciales
df = df.drop(['C0_C1', 'C1_C2', 'C2_C3'], axis=1)

# Guardar todos los datos (incluyendo filas con datos faltantes)
df.to_csv('cleaned_data_with_missing.csv', index=False)

# Guardar solo filas completas (sin datos faltantes)
df_clean = df.dropna()
df_clean.to_csv('cleaned_data.csv', index=False)