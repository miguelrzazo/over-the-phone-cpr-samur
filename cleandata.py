import pandas as pd
import numpy as np

import os
# Cargar datos
DATA_DIR = 'data'
df = pd.read_csv(os.path.join(DATA_DIR, 'raw_data_cpr.csv'), encoding='utf-8', sep=';')

# Seleccionar columnas relevantes (ajustar si es necesario)
cols = ['EDAD', 'SEXO', 'RCP_TRANSTELEFONICA', 'C0_C1', 'C1_C2', 'C2_C3',
        'CODIGO PATOLOGICO', 'Evolución', '6 HORAS', '24 horas', '7 días']
df = df[cols].copy()

# Limpiar y codificar variables
df['EDAD'] = pd.to_numeric(df['EDAD'], errors='coerce')
df['SEXO'] = df['SEXO'].str.strip().str.capitalize()
df['RCP_TRANSTELEFONICA'] = df['RCP_TRANSTELEFONICA'].astype(str).str.strip().str.lower()

# Calcular tiempo de llegada (suma de C0_C1, C1_C2 y C2_C3)
for col in ['C0_C1', 'C1_C2', 'C2_C3']:
    df[col] = pd.to_numeric(df[col], errors='coerce')
df['TIEMPO_LLEGADA_UNIDAD'] = df['C0_C1'].fillna(0) + df['C1_C2'].fillna(0) + df['C2_C3'].fillna(0)

# Determinar supervivencia a 7 días
def determina_superviviente(row):
    fallecimiento_keywords = [
        'éxitus', 'fallece', 'fallecido', 'fallecimiento', 'defunción', 'muere', 'muerte', 'exit', 'exitus', 'deceso',
        '3.1 - parada no recuperada',
        'parada no recuperada', 'parada no recup', 'parada irrecuperable', 'parada exitus', 'parada fallecido',
        'o.0.1', 'w.0.1'
    ]
    textos = [
        str(row.get('CODIGO PATOLOGICO', '')),
        str(row.get('Evolución', '')),
        str(row.get('6 HORAS', '')),
        str(row.get('24 horas', '')),
        str(row.get('7 días', ''))
    ]
    texto_completo = ' '.join(textos).lower()
    return not any(palabra in texto_completo for palabra in fallecimiento_keywords)

df['SOBREVIVE_7DIAS'] = df.apply(determina_superviviente, axis=1)

# Eliminar columnas originales de tiempos parciales y textos auxiliares
df = df.drop(['C0_C1', 'C1_C2', 'C2_C3', 'CODIGO PATOLOGICO', 'Evolución', '6 HORAS', '24 horas', '7 días'], axis=1)

# Guardar todos los datos (incluyendo filas con datos faltantes)
df.to_csv(os.path.join(DATA_DIR, 'cleaned_data_with_missing.csv'), index=False)

# Guardar solo filas completas (sin datos faltantes)
df_clean = df.dropna(how='any')
# Filtrar filas donde RCP_TRANSTELEFONICA es nan, vacío o la cadena 'nan'
df_clean = df_clean[df_clean['RCP_TRANSTELEFONICA'].notna() & (df_clean['RCP_TRANSTELEFONICA'] != '') & (df_clean['RCP_TRANSTELEFONICA'].str.lower() != 'nan')]
# Eliminar filas con NaN en columnas booleanas antes de guardar
bool_cols = df_clean.select_dtypes(include=['bool']).columns
if len(bool_cols) > 0:
    df_clean = df_clean.dropna(subset=bool_cols, how='any')
# Convertir EDAD y TIEMPO_LLEGADA_UNIDAD a enteros
for col in ['EDAD', 'TIEMPO_LLEGADA_UNIDAD']:
    if col in df_clean.columns:
        df_clean[col] = df_clean[col].astype(int)
df_clean.to_csv(os.path.join(DATA_DIR, 'cleaned_data.csv'), index=False)