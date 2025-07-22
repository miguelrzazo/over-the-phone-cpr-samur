import pandas as pd
import numpy as np
import re

import os
# Cargar datos
DATA_DIR = 'data'
df = pd.read_csv(os.path.join(DATA_DIR, 'raw_data_cpr.csv'), encoding='utf-8', sep=';')

# Seleccionar columnas relevantes (ajustar si es necesario)
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

# Nueva columna: ROSC (Retorno de circulación espontánea)

# ROSC: True si CODIGO PATOLOGICO es C.0.0 o C.0.2 (ECMO)
def determina_rosc(row):
    cod = str(row.get('CODIGO PATOLOGICO', '')).strip().upper()
    return cod.startswith('C.0.0') or cod.startswith('C.0.2')

# Nueva columna: RCP_EN_LLEGADA
# Determina si se estaba realizando RCP a la llegada de la unidad basándose en comentarios
def determina_rcp_en_llegada(row):
    # Si hay RCP transtelefónica, siempre será verdadero
    rcp_transtel = str(row.get('RCP_TRANSTELEFONICA', '')).strip().lower()
    if rcp_transtel == 'verdadero':
        return True
    
    # Buscar en el campo 'Consulta' indicios de RCP en curso
    consulta = str(row.get('Consulta', '')).lower()
    
    # Palabras clave que indican RCP en curso a la llegada
    rcp_en_curso_keywords = [
        'masaje', 'compresiones', 'rcp', 'reanimacion', 'reanimación',
        'masaje cardiaco', 'compresiones toracicas', 'compresiones torácicas',
        'maniobras', 'svb', 'rcp basica', 'rcp básica', 'rcp avanzada',
        'realizando rcp', 'realizando maniobras', 'masaje de mala calidad',
        'inicio compresiones', 'empezamos a realizar', 'continuando',
        'apoyo.*rcp', 'colaboramos.*rcp', 'rcp.*llegada'
    ]
    
    # Palabras que indican que la RCP la está haciendo el SAMUR/equipo médico (no testigos)
    palabras_exclusion = [
        'iniciamos', 'empezamos', 'solicitamos', 'aplicamos', 'se realiza',
        'tras.*llegada.*iniciamos', 'a nuestra llegada.*iniciamos'
    ]
    
    # Buscar patrones que indican RCP en curso a la llegada
    for keyword in rcp_en_curso_keywords:
        if re.search(keyword, consulta):
            # Verificar que no sea una exclusión (RCP iniciada por el equipo médico)
            es_exclusion = False
            for exclusion in palabras_exclusion:
                if re.search(exclusion, consulta):
                    es_exclusion = True
                    break
            
            if not es_exclusion:
                # Buscar patrones específicos que confirmen RCP previa a la llegada
                patrones_confirmacion = [
                    r'a.*llegada.*masaje',
                    r'a.*llegada.*compresiones',
                    r'a.*llegada.*rcp',
                    r'llegada.*realizando',
                    r'llegada.*maniobras',
                    r'masaje.*mala.*calidad',
                    r'\d+.*minutos.*rcp',
                    r'continuando.*masaje',
                    r'policia.*compresiones',
                    r'testigo.*rcp',
                    r'familiar.*rcp',
                    r'socorista.*rcp',
                    r'bombero.*rcp',
                    r'bomberos.*rcp',
                    r'091.*rcp',
                    r'092.*rcp',
                    r'060.*rcp',
                    r'061.*rcp',
                    r'062.*rcp',
                    r'guardia civil.*rcp',
                    r'policia nacional.*rcp',
                    r'policia municipal.*rcp',
                    r'samur social.*rcp',
                    r'samur.*rcp'
                ]
                
                for patron in patrones_confirmacion:
                    if re.search(patron, consulta):
                        return True
    
    return False

df['SOBREVIVE_7DIAS'] = df.apply(determina_superviviente, axis=1)
df['ROSC'] = df.apply(determina_rosc, axis=1)
df['RCP_EN_LLEGADA'] = df.apply(determina_rcp_en_llegada, axis=1)

# Convertir RCP_TRANSTELEFONICA de "verdadero"/"falso" a True/False
df['RCP_TRANSTELEFONICA'] = df['RCP_TRANSTELEFONICA'].map({'verdadero': True, 'falso': False})

# Eliminar columnas originales de tiempos parciales, textos auxiliares y CODIGO PATOLOGICO
df = df.drop(['C0_C1', 'C1_C2', 'C2_C3', 'CODIGO PATOLOGICO', 'Evolución', '6 HORAS', '24 horas', '7 días', 'Consulta'], axis=1)

# Reordenar columnas: RCP_EN_LLEGADA, ROSC, SOBREVIVE_7DIAS al final
cols_order = ['EDAD', 'SEXO', 'RCP_TRANSTELEFONICA', 'TIEMPO_LLEGADA_UNIDAD', 'RCP_EN_LLEGADA', 'ROSC', 'SOBREVIVE_7DIAS']
df = df[cols_order]

# Guardar todos los datos (incluyendo filas con datos faltantes)
df.to_csv(os.path.join(DATA_DIR, 'cleaned_data_with_missing.csv'), index=False)

# Guardar solo filas completas (sin datos faltantes)
df_clean = df.dropna(how='any')
# Filtrar filas donde RCP_TRANSTELEFONICA es nan, vacío o la cadena 'nan'
df_clean = df_clean[df_clean['RCP_TRANSTELEFONICA'].notna()]
# Eliminar filas con NaN en columnas booleanas antes de guardar
bool_cols = df_clean.select_dtypes(include=['bool']).columns
if len(bool_cols) > 0:
    df_clean = df_clean.dropna(subset=bool_cols, how='any')
# Convertir EDAD y TIEMPO_LLEGADA_UNIDAD a enteros
for col in ['EDAD', 'TIEMPO_LLEGADA_UNIDAD']:
    if col in df_clean.columns:
        df_clean[col] = df_clean[col].astype(int)
df_clean.to_csv(os.path.join(DATA_DIR, 'cleaned_data.csv'), index=False)