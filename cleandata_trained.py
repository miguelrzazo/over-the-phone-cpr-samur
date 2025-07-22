import pandas as pd
import numpy as np
import re
import os

# Cargar datos
DATA_DIR = 'data'
df = pd.read_csv(os.path.join(DATA_DIR, 'raw_data_cpr.csv'), encoding='utf-8', sep=';')

# Seleccionar columnas relevantes
cols = ['EDAD', 'SEXO', 'RCP_TRANSTELEFONICA', 'C0_C1', 'C1_C2', 'C2_C3',
        'CODIGO PATOLOGICO', 'Evolución', '6 HORAS', '24 horas', '7 días', 'Consulta']
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

def determina_rosc(row):
    cod = str(row.get('CODIGO PATOLOGICO', '')).strip().upper()
    return cod.startswith('C.0.0') or cod.startswith('C.0.2')

# Actualizar la lógica de determina_rcp_en_llegada para eliminar la clase 'entrenado'
def determina_rcp_en_llegada(row):
    consulta = str(row.get('Consulta', '')).lower()
    
    # Palabras clave que indican RCP en curso por testigos
    rcp_keywords = [
        'rcp', 'masaje', 'compresiones', 'reanimacion', 'reanimación', 
        'maniobras', 'svb'
    ]
    
    # Primero, verificar si hay alguna mención de RCP
    if not any(re.search(r'\b' + keyword + r'\b', consulta) for keyword in rcp_keywords):
        return False  # No hay RCP por testigos

    # Si hay RCP, clasificar quién la realiza
    trained_keywords = {
        'policia': 'policia',
        'bombero': 'bombero',
        'sanitario': 'sanitario'
    }
    for keyword, value in trained_keywords.items():
        if re.search(keyword, consulta):
            return value
            
    return 'no entrenado'  # Lego o no entrenado si se mencionó RCP pero no un profesional

# Aplicar funciones
df['SOBREVIVE_7DIAS'] = df.apply(determina_superviviente, axis=1)
df['ROSC'] = df.apply(determina_rosc, axis=1)
df['RCP_EN_LLEGADA'] = df.apply(determina_rcp_en_llegada, axis=1)

# Convertir RCP_TRANSTELEFONICA de "verdadero"/"falso" a True/False
df['RCP_TRANSTELEFONICA'] = df['RCP_TRANSTELEFONICA'].map({'verdadero': True, 'falso': False})

# Eliminar columnas originales innecesarias
df = df.drop(['C0_C1', 'C1_C2', 'C2_C3', 'CODIGO PATOLOGICO', 'Evolución', '6 HORAS', '24 horas', '7 días', 'Consulta'], axis=1)

# Reordenar columnas
cols_order = ['EDAD', 'SEXO', 'RCP_TRANSTELEFONICA', 'TIEMPO_LLEGADA_UNIDAD', 'RCP_EN_LLEGADA', 'ROSC', 'SOBREVIVE_7DIAS']
df = df[cols_order]

# Eliminar filas con datos faltantes
df = df.dropna()

# Guardar datos limpios
df.to_csv(os.path.join(DATA_DIR, 'cleaned_data_trained.csv'), index=False)
