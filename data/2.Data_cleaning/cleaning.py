"""
Script de limpieza y procesamiento de datos para el estudio de RCP Transtelefónica.
Este script implementa las reglas de exclusión definidas en Reglas_exclusion.md
y genera un conjunto de datos limpio para análisis posterior.
"""

import pandas as pd
import numpy as np
import os
import re
import datetime
from datetime import datetime

def read_raw_data(filepath):
    """Lee los datos crudos desde el archivo CSV"""
    print(f"📂 Leyendo datos desde: {filepath}")
    data = pd.read_csv(filepath, delimiter=';')
    
    # Renombrar columnas para facilitar el procesamiento
    column_mapping = {
        'NUM INFORME': 'n_informe',
        'FECHA_LLAMADA': 'fecha',
        'EDAD': 'edad',
        'SEXO': 'sexo',
        'RCP_TRANSTELEFONICA': 'rcp_transtelefonica',
        'DESA_EXTERNO': 'desa_externo',
        'RCP_TESTIGOS': 'rcp_testigos',
        'C0_C1': 'tiempo_c0_c1',
        'C1_C2': 'tiempo_c1_c2',
        'C2_C3': 'tiempo_c2_c3',
        'C3_C4': 'tiempo_rcp',
        'RITMO INICIAL': 'ritmo_inicial',
        'ROSC': 'rosc',
        '7 DIAS': 'supervivencia_7dias',
        'CPC': 'cpc',
        'Tipo de Unidad': 'tipo_unidad',
        'CONSULTA': 'consulta',
        'ANTECEDENTES': 'antecedentes',
        'TECNICAS': 'tecnicas',
        'EVOLUCION': 'evolucion',
        'HOSPITAL': 'hospital',
        '6 HORAS': '6_horas',
        '24 HORAS': '24_horas',
        '7 DIAS': '7_dias'
    }
    
    data = data.rename(columns=column_mapping)
    
    # Convertir columnas de texto a minúsculas para facilitar búsquedas
    text_columns = ['consulta', 'antecedentes', 'tecnicas', 'evolucion', 'hospital', '6_horas', '24_horas', '7_dias']
    for col in text_columns:
        if col in data.columns:
            data[col] = data[col].astype(str).str.lower()
    
    print(f"✅ Datos cargados: {len(data)} registros iniciales")
    return data

def process_boolean_columns(data):
    """Procesa columnas booleanas para estandarizarlas a 1/0"""
    boolean_columns = ['rcp_transtelefonica', 'desa_externo', 'rcp_testigos', 'rosc']
    
    for col in boolean_columns:
        if col in data.columns:
            # Primero reemplazamos valores de texto conocidos
            data[col] = data[col].apply(
                lambda x: 1 if (pd.notna(x) and str(x).lower() in ['verdadero', 'true', '1', '1.0']) else 0
            )
            # Aseguramos que son enteros
            data[col] = data[col].astype(int)
    
    return data

def is_traumatic(row):
    """Determina si un caso es de origen traumático"""
    traumatic_keywords = [
        'ahogamiento', 'herida', 'precipitad', 'arma', 'trauma', 'accident', 
        'colision', 'choque', 'atropell', 'caida', 'casual', 'autolisis', 
        'autolit', 'suicid', 'defenestr', 'ahorcad', 'sumersion', 'quemad', 
        'incendio', 'moto', 'motocicle', 'trafico'
    ]
    
    # Buscar palabras clave en consulta
    consulta = str(row.get('consulta', '')).lower()
    
    for keyword in traumatic_keywords:
        if keyword in consulta:
            return True
    
    return False

def identify_responder_type(row):
    """Identifica el tipo de respondiente de RCP"""
    if row['rcp_testigos'] == 0:
        return ''
    
    consulta = str(row.get('consulta', '')).lower()
    antecedentes = str(row.get('antecedentes', '')).lower()
    text_to_search = consulta + " " + antecedentes
    
    # Si hay RCP transtelefónica, el respondiente es lego
    if row['rcp_transtelefonica'] == 1:
        return 'lego'
    
    # Palabras clave para identificar tipo de respondiente
    bombero_keywords = ['bombero', '080', 'beta']
    policia_keywords = ['092', '091', '062', 'agente', 'municipal', 'nacional', 'policia']
    sanitario_keywords = ['tes', 'svb', 'basica', 'upr', 'basico', 'sanitario', 'personal hospital', 
                         'socorrista', 'enfermera', 'medico', 'doctor', 'enfermero', 'facultativo']
    
    # Comprobar por tipo de respondiente
    for keyword in bombero_keywords:
        if keyword in text_to_search:
            return 'bombero'
    
    for keyword in policia_keywords:
        if keyword in text_to_search:
            return 'policia'
    
    for keyword in sanitario_keywords:
        if keyword in text_to_search:
            return 'sanitario'
    
    # Si hay RCP por testigos pero no se identifica el tipo, asumimos lego
    return 'lego'

def classify_initial_rhythm(rhythm_str):
    """Clasifica el ritmo inicial como desfibrilable (1) o no desfibrilable (0)"""
    if pd.isna(rhythm_str) or rhythm_str == '' or rhythm_str.lower() == 'nan':
        return np.nan
    
    rhythm_str = str(rhythm_str).lower()
    desfibrilable = [
        'fv', 'tv', 'fibrilacion ventricular', 'taquicardia ventricular',
        'fibrilación', 'fibrila', 'tv sin pulso', 'ventricular'
    ]
    
    for rhythm in desfibrilable:
        if rhythm in rhythm_str:
            return 1
    
    return 0

def determine_rosc_and_rcp_time(row):
    """
    Determina ROSC y tiempo de RCP según las nuevas reglas:
    - Si hay hospital entonces el ROSC es 1
    - Si hay texto que menciona ROSC en técnicas o evolución, ROSC es 1
    - Si hay mención a exitus, fallecimiento o éxitus, ROSC es 0
    - Si el ROSC es 0 entonces el tiempo de RCP se estima desde la casilla técnicas
    - Si hay hora de fallecimiento y hay RCP testigos, se calcula con la hora de inicio y fin
    - Si no hay RCP testigos, se resta el tiempo de llegada
    """
    rosc = 0
    tiempo_rcp = row.get('tiempo_rcp', np.nan)
    
    # Si hay mención a hospital, entonces ROSC es 1
    hospital_text = str(row.get('hospital', '')).lower()
    if hospital_text and hospital_text != 'nan' and hospital_text != 'none':
        rosc = 1
    
    # Buscar menciones explícitas de ROSC en las casillas de texto
    tecnicas_text = str(row.get('tecnicas', '')).lower()
    evolucion_text = str(row.get('evolucion', '')).lower()
    consulta_text = str(row.get('consulta', '')).lower()
    
    combined_text = tecnicas_text + " " + evolucion_text
    
    # Palabras clave que indican ROSC
    rosc_keywords = ['rosc', 'recupera', 'recuperación', 'circulación espontánea', 'pulso', 'ritmo']
    exitus_keywords = ['exitus', 'fallec', 'éxitus', 'exito', 'muerte', 'muerto', 'fallido']
    
    # Buscar si hay palabras clave que indiquen ROSC
    for keyword in rosc_keywords:
        if keyword in combined_text:
            # Asegurarse que no está negado (ej: "no recupera", "sin pulso")
            if not any(neg + " " + keyword in combined_text for neg in ['no', 'sin', 'nunca', 'ningún', 'ausencia de']):
                rosc = 1
                break
    
    # Buscar si hay palabras clave que indiquen exitus (esto anularía el ROSC)
    for keyword in exitus_keywords:
        if keyword in combined_text:
            rosc = 0
            break
    
    # Si ROSC es 0, intentar estimar tiempo de RCP
    if rosc == 0:
        # Buscar patrón de tiempo de RCP en la casilla técnicas
        rcp_time_pattern = r'tras\s+(\d+)\s+min(?:utos)?\s+(?:de)?\s+rcp'
        match = re.search(rcp_time_pattern, tecnicas_text)
        
        if match:
            # Convertir minutos a segundos
            tiempo_rcp = int(match.group(1)) * 60
        else:
            # Buscar hora de fallecimiento
            death_time_pattern = r'fallec(?:e|ido|imiento).*?(\d{1,2})[:.h](\d{1,2})'
            death_match = re.search(death_time_pattern, tecnicas_text + " " + consulta_text)
            
            if death_match and row.get('rcp_testigos', 0) == 1:
                # Extraer hora y minuto de fallecimiento
                hora_fallecimiento = int(death_match.group(1))
                minuto_fallecimiento = int(death_match.group(2))
                
                # Extraer hora de inicio de la fecha
                fecha_hora = pd.to_datetime(row.get('fecha'), errors='coerce')
                if pd.notna(fecha_hora):
                    hora_inicio = fecha_hora.hour
                    minuto_inicio = fecha_hora.minute
                    
                    # Calcular tiempo total en segundos
                    tiempo_total_minutos = (hora_fallecimiento - hora_inicio) * 60 + (minuto_fallecimiento - minuto_inicio)
                    
                    # Si el tiempo es negativo (ej. cruce de medianoche), ajustamos
                    if tiempo_total_minutos < 0:
                        tiempo_total_minutos += 24 * 60
                        
                    tiempo_rcp = int(tiempo_total_minutos * 60)
            elif row.get('rcp_testigos', 0) == 0 and pd.notna(row.get('tiempo_llegada', np.nan)):
                # Si no hay RCP testigos, usar el tiempo de llegada
                tiempo_rcp = int(row.get('tiempo_llegada')) if not pd.isna(row.get('tiempo_llegada')) else np.nan
    
    return rosc, tiempo_rcp

def determine_survival_and_cpc(row):
    """Determina supervivencia y CPC basado en los campos disponibles"""
    supervivencia = 0
    cpc = 5
    
    # Leer casilla 6 para determinar si ha fallecido
    casilla_6 = str(row.get('6', '')).lower()
    if casilla_6 and any(word in casilla_6 for word in ['exitus', 'fallec', 'muerte', 'muerto', 'óbito', 'cadaver']):
        supervivencia = 0
        cpc = 5
        return supervivencia, cpc
    
    # Comprobar supervivencia a 7 días
    if '7_dias' in row and not pd.isna(row['7_dias']) and row['7_dias'] != 'nan':
        supervivencia_text = str(row['7_dias']).lower()
        if any(word in supervivencia_text for word in ['bien', 'alta', 'vivo', 'estable', 'buen']):
            supervivencia = 1
        elif any(word in supervivencia_text for word in ['exitus', 'fallec', 'muerte', 'muerto', 'óbito']):
            supervivencia = 0
            cpc = 5
            return supervivencia, cpc
        elif supervivencia_text.strip():  # Si hay texto pero no se identificó estado
            supervivencia = 1
            # CPC se dejará en blanco si no se encuentra explícitamente
            cpc = np.nan
    
    # Intentar extraer CPC
    if supervivencia == 1:
        cpc_pattern = r'cpc\s*(?:de|es|:)?\s*([1-5])'
        for field in ['7_dias', 'evolucion', 'hospital']:
            if field in row and not pd.isna(row[field]) and row[field] != 'nan':
                match = re.search(cpc_pattern, str(row[field]).lower())
                if match:
                    cpc = int(match.group(1))
                    break
        
        # Si CPC es 5 pero el paciente sobrevivió, ajustamos a valores entre 1-4
        if cpc == 5:
            cpc = np.nan
    
    return supervivencia, cpc

def calculate_arrival_time(row):
    """Calcula el tiempo total de llegada sumando los tiempos parciales"""
    time_cols = ['tiempo_c0_c1', 'tiempo_c1_c2', 'tiempo_c2_c3']
    
    # Convertir posibles valores no numéricos a NaN
    times = []
    for col in time_cols:
        if col in row:
            try:
                val = float(row[col]) if not pd.isna(row[col]) else 0
                times.append(val)
            except (ValueError, TypeError):
                times.append(0)
    
    return sum(times)

def merge_svb_sva(data):
    """Fusiona registros SVB y SVA basados en fecha/hora"""
    print("\n🔄 FUSIÓN DE REGISTROS SVB Y SVA")
    
    # Convertir fecha a datetime
    data['fecha'] = pd.to_datetime(data['fecha'], errors='coerce')
    
    # Separar registros por tipo de unidad
    sva_records = data[data['tipo_unidad'] == 'SVA'].copy()
    svb_records = data[data['tipo_unidad'] == 'SVB'].copy()
    otros_records = data[(data['tipo_unidad'] != 'SVA') & (data['tipo_unidad'] != 'SVB')].copy()
    
    # Registrar estadísticas de unidades
    estadisticas_unidades = {
        'total_sva': len(sva_records),
        'total_svb': len(svb_records),
        'total_otros': len(otros_records),
        'svb_emparejados': 0,
        'svb_no_emparejados': 0
    }
    
    print(f"   • Registros SVA: {len(sva_records)}")
    print(f"   • Registros SVB: {len(svb_records)}")
    print(f"   • Otros tipos: {len(otros_records)}")
    
    # Crear ventanas de tiempo para matching (2 horas antes y después)
    time_window = pd.Timedelta(hours=2)
    
    # Resultados de la fusión
    merged_records = []
    matched_svb_ids = set()
    
    # Para cada registro SVA, buscar coincidencias en SVB
    for _, sva_row in sva_records.iterrows():
        sva_time = sva_row['fecha']
        
        if pd.isna(sva_time):
            merged_records.append(sva_row.to_dict())
            continue
        
        # Buscar coincidencias en SVB dentro de la ventana de tiempo
        potential_matches = svb_records[
            (svb_records['fecha'] >= sva_time - time_window) &
            (svb_records['fecha'] <= sva_time + time_window)
        ]
        
        if len(potential_matches) == 0:
            # No hay coincidencias, usar registro SVA tal cual
            merged_records.append(sva_row.to_dict())
        else:
            # Encontrar la coincidencia más cercana
            potential_matches['time_diff'] = (potential_matches['fecha'] - sva_time).abs()
            best_match = potential_matches.loc[potential_matches['time_diff'].idxmin()]
            
            # Si la diferencia es menor a 2 horas, considerar como match
            if best_match['time_diff'] <= time_window:
                merged_row = sva_row.copy()
                svb_id = best_match['n_informe']
                
                # Fusionar datos dando preferencia a SVA, excepto rcp_transtelefonica
                if best_match['rcp_transtelefonica'] == 1:
                    merged_row['rcp_transtelefonica'] = 1
                
                # Para campos vacíos en SVA, usar datos de SVB
                for col in merged_row.index:
                    if pd.isna(merged_row[col]) and not pd.isna(best_match[col]):
                        merged_row[col] = best_match[col]
                
                # Asegurar que valores booleanos son enteros
                boolean_columns = ['rcp_transtelefonica', 'desa_externo', 'rcp_testigos', 'rosc']
                for col in boolean_columns:
                    if col in merged_row and pd.notna(merged_row[col]):
                        if isinstance(merged_row[col], str):
                            # Convertir string a booleano y luego a entero
                            merged_row[col] = 1 if merged_row[col].lower() in ['verdadero', 'true', '1', '1.0'] else 0
                        else:
                            # Si no es string, convertir directamente a entero
                            merged_row[col] = int(float(merged_row[col]))
                
                merged_records.append(merged_row.to_dict())
                matched_svb_ids.add(svb_id)
            else:
                # No hay match cercano, usar registro SVA tal cual
                merged_records.append(sva_row.to_dict())
    
    # Ahora NO añadimos los registros SVB que no fueron emparejados
    # Se excluyen deliberadamente del conjunto final
    
    # Convertir a DataFrame
    merged_df = pd.DataFrame(merged_records)
    
    # Calcular estadísticas de fusión
    svb_emparejados = len(matched_svb_ids)
    svb_no_emparejados = len(svb_records) - svb_emparejados
    
    # Actualizar estadísticas
    estadisticas_unidades['svb_emparejados'] = svb_emparejados
    estadisticas_unidades['svb_no_emparejados'] = svb_no_emparejados
    
    print(f"   • SVB emparejados con SVA: {svb_emparejados} ({(svb_emparejados/len(svb_records))*100:.1f}% de SVB)")
    print(f"   • SVB no emparejados (excluidos): {svb_no_emparejados} ({(svb_no_emparejados/len(svb_records))*100:.1f}% de SVB)")
    print(f"✅ Fusión completada: {len(merged_df)} registros totales tras fusión")
    
    # Guardar estadísticas en el DataFrame
    merged_df.attrs['estadisticas_unidades'] = estadisticas_unidades
    
    return merged_df

def process_data(data):
    """Proceso principal de limpieza y transformación de datos"""
    # Registrar conteos iniciales
    total_inicial = len(data)
    print(f"\n📊 ESTADÍSTICAS DE EXCLUSIÓN DE CASOS:")
    print(f"   • Total de registros iniciales: {total_inicial}")
    
    # Diccionario para guardar estadísticas de exclusión
    estadisticas_exclusion = {
        'total_inicial': total_inicial,
        'excluidos_rcp_trans': 0,
        'excluidos_traumaticos': 0
    }
    
    # 1. Procesar columnas booleanas
    data = process_boolean_columns(data)
    
    # 2. Filtrar casos que no tienen información de RCP transtelefónica
    missing_rcp_trans = data['rcp_transtelefonica'].isna()
    excluidos_rcp_trans = sum(missing_rcp_trans)
    estadisticas_exclusion['excluidos_rcp_trans'] = excluidos_rcp_trans
    data = data[~missing_rcp_trans]
    print(f"   • Excluidos por RCP transtelefónica desconocida: {excluidos_rcp_trans} ({(excluidos_rcp_trans/total_inicial)*100:.1f}%)")
    print(f"   • Registros después de filtrar por RCP transtelefónica: {len(data)}")
    
    # 3. Filtrar casos traumáticos
    traumatic_cases = data.apply(is_traumatic, axis=1)
    excluidos_traumaticos = sum(traumatic_cases)
    estadisticas_exclusion['excluidos_traumaticos'] = excluidos_traumaticos
    non_traumatic_data = data[~traumatic_cases]
    print(f"   • Excluidos por origen traumático: {excluidos_traumaticos} ({(excluidos_traumaticos/len(data))*100:.1f}%)")
    print(f"   • Registros después de filtrar casos traumáticos: {len(non_traumatic_data)}")
    
    # Guardar las estadísticas en el dataframe para uso posterior
    non_traumatic_data.attrs['estadisticas_exclusion'] = estadisticas_exclusion
    
    # 4. Identificar tipo de respondiente de RCP
    non_traumatic_data['tipo_respondiente'] = non_traumatic_data.apply(identify_responder_type, axis=1)
    
    # 5. Clasificar ritmo inicial
    non_traumatic_data['ritmo_desfibrilable'] = non_traumatic_data['ritmo_inicial'].apply(classify_initial_rhythm)
    
    # 6. Calcular tiempo de llegada
    non_traumatic_data['tiempo_llegada'] = non_traumatic_data.apply(calculate_arrival_time, axis=1)
    
    # 7. Determinar ROSC y tiempo de RCP
    rosc_rcp_time = non_traumatic_data.apply(determine_rosc_and_rcp_time, axis=1, result_type='expand')
    non_traumatic_data['rosc'] = rosc_rcp_time[0].astype(int)  # Asegurar que ROSC sea entero
    
    # Actualizar tiempo de RCP si se calculó en la función
    non_traumatic_data['tiempo_rcp'] = rosc_rcp_time[1]
    # Asegurar que tiempo_rcp sea entero donde hay valores
    non_traumatic_data['tiempo_rcp'] = non_traumatic_data['tiempo_rcp'].apply(
        lambda x: int(x) if not pd.isna(x) else np.nan)
    
    # 8. Determinar supervivencia y CPC
    survival_cpc = non_traumatic_data.apply(determine_survival_and_cpc, axis=1, result_type='expand')
    non_traumatic_data['supervivencia_7dias'] = survival_cpc[0].astype(int)  # Asegurar que sea entero
    non_traumatic_data['cpc'] = survival_cpc[1].apply(lambda x: int(x) if not pd.isna(x) else x)
    
    # 9. Convertir edad a numérico entero
    non_traumatic_data['edad'] = pd.to_numeric(non_traumatic_data['edad'], errors='coerce')
    # Convertir a entero, manteniendo NaN donde corresponda
    non_traumatic_data['edad'] = non_traumatic_data['edad'].apply(lambda x: int(x) if not pd.isna(x) else x)
    
    # 10. Procesar tiempo de RCP y convertir a entero
    non_traumatic_data['tiempo_rcp'] = pd.to_numeric(non_traumatic_data['tiempo_rcp'], errors='coerce')
    non_traumatic_data['tiempo_rcp'] = non_traumatic_data['tiempo_rcp'].apply(lambda x: int(x) if not pd.isna(x) else x)
    
    # 11. Convertir tiempo_llegada a entero
    non_traumatic_data['tiempo_llegada'] = pd.to_numeric(non_traumatic_data['tiempo_llegada'], errors='coerce')
    non_traumatic_data['tiempo_llegada'] = non_traumatic_data['tiempo_llegada'].apply(lambda x: int(x) if not pd.isna(x) else x)
    
    # 12. Asegurar que ritmo_desfibrilable sea entero
    non_traumatic_data['ritmo_desfibrilable'] = pd.to_numeric(non_traumatic_data['ritmo_desfibrilable'], errors='coerce')
    non_traumatic_data['ritmo_desfibrilable'] = non_traumatic_data['ritmo_desfibrilable'].apply(lambda x: int(x) if not pd.isna(x) else x)
    
    # 13. Asegurar que todas las columnas booleanas sean de tipo entero (0 o 1)
    boolean_columns = ['rcp_transtelefonica', 'desa_externo', 'rcp_testigos', 'rosc', 'supervivencia_7dias']
    for col in boolean_columns:
        if col in non_traumatic_data.columns:
            non_traumatic_data[col] = non_traumatic_data[col].fillna(0).astype(int)  # Valores NaN como 0
    
    return non_traumatic_data

def select_final_columns(data):
    """Selecciona y ordena las columnas finales para el dataset procesado"""
    columns = [
        'n_informe', 'fecha', 'edad', 'sexo', 'rcp_transtelefonica', 'tipo_respondiente',
        'tiempo_llegada', 'desa_externo', 'ritmo_desfibrilable', 'tiempo_rcp',
        'rosc', 'supervivencia_7dias', 'cpc'
    ]
    
    # Asegurar que solo se seleccionan columnas disponibles
    available_columns = [col for col in columns if col in data.columns]
    return data[available_columns]

def generate_summary_statistics(data):
    """Genera estadísticas descriptivas del dataset procesado"""
    print("\n" + "="*80)
    print("📊 RESUMEN ESTADÍSTICO - ANÁLISIS RCP TRANSTELEFÓNICA")
    print("="*80)
    
    # Tamaño del conjunto de datos
    total_casos = len(data)
    print(f"\n📋 TOTAL DE CASOS ANALIZADOS: {total_casos}")
    
    # Distribución por tipo de RCP
    rcp_trans_count = data['rcp_transtelefonica'].sum()
    rcp_trans_pct = (rcp_trans_count / total_casos) * 100 if total_casos > 0 else 0
    
    print("\n📞 DISTRIBUCIÓN POR TIPO DE RCP:")
    print(f"   • Con RCP transtelefónica: {rcp_trans_count} ({rcp_trans_pct:.1f}%)")
    print(f"   • Sin RCP transtelefónica: {total_casos - rcp_trans_count} ({100 - rcp_trans_pct:.1f}%)")
    
    # Distribución por tipo de respondiente
    if 'tipo_respondiente' in data.columns:
        print("\n👥 DISTRIBUCIÓN POR TIPO DE RESPONDIENTE:")
        respondent_counts = data['tipo_respondiente'].value_counts()
        for respondent, count in respondent_counts.items():
            if respondent:  # No mostrar valores vacíos
                pct = (count / total_casos) * 100
                print(f"   • {respondent.capitalize()}: {count} ({pct:.1f}%)")
    
    # Estadísticas por ritmo inicial
    if 'ritmo_desfibrilable' in data.columns:
        desfib_count = data['ritmo_desfibrilable'].sum()
        desfib_pct = (desfib_count / data['ritmo_desfibrilable'].count()) * 100
        
        print("\n💓 DISTRIBUCIÓN POR RITMO INICIAL:")
        print(f"   • Ritmo desfibrilable: {desfib_count} ({desfib_pct:.1f}%)")
        print(f"   • Ritmo no desfibrilable: {data['ritmo_desfibrilable'].count() - desfib_count} ({100 - desfib_pct:.1f}%)")
    
    # Estadísticas de supervivencia
    if 'supervivencia_7dias' in data.columns:
        surv_count = data['supervivencia_7dias'].sum()
        surv_pct = (surv_count / total_casos) * 100 if total_casos > 0 else 0
        
        print("\n🏥 SUPERVIVENCIA A 7 DÍAS:")
        print(f"   • Supervivientes: {surv_count} ({surv_pct:.1f}%)")
        print(f"   • No supervivientes: {total_casos - surv_count} ({100 - surv_pct:.1f}%)")
        
        # Supervivencia por tipo de RCP
        rcp_trans_data = data[data['rcp_transtelefonica'] == 1]
        rcp_trans_surv = rcp_trans_data['supervivencia_7dias'].sum()
        rcp_trans_total = len(rcp_trans_data)
        
        no_rcp_trans_data = data[data['rcp_transtelefonica'] == 0]
        no_rcp_trans_surv = no_rcp_trans_data['supervivencia_7dias'].sum()
        no_rcp_trans_total = len(no_rcp_trans_data)
        
        print("\n📊 SUPERVIVENCIA POR TIPO DE RCP:")
        if rcp_trans_total > 0:
            rcp_trans_surv_pct = (rcp_trans_surv / rcp_trans_total) * 100
            print(f"   • Con RCP transtelefónica: {rcp_trans_surv}/{rcp_trans_total} ({rcp_trans_surv_pct:.1f}%)")
        
        if no_rcp_trans_total > 0:
            no_rcp_trans_surv_pct = (no_rcp_trans_surv / no_rcp_trans_total) * 100
            print(f"   • Sin RCP transtelefónica: {no_rcp_trans_surv}/{no_rcp_trans_total} ({no_rcp_trans_surv_pct:.1f}%)")
    
    # Estadísticas de ROSC por tipo de RCP
    if 'rosc' in data.columns:
        rosc_count = data['rosc'].sum()
        rosc_pct = (rosc_count / total_casos) * 100 if total_casos > 0 else 0
        
        print("\n💓 RETORNO DE CIRCULACIÓN ESPONTÁNEA (ROSC):")
        print(f"   • Total casos con ROSC: {rosc_count} ({rosc_pct:.1f}%)")
        print(f"   • Total casos sin ROSC: {total_casos - rosc_count} ({100 - rosc_pct:.1f}%)")
        
        # ROSC por tipo de RCP
        rcp_trans_rosc = rcp_trans_data['rosc'].sum() if 'rosc' in rcp_trans_data.columns else 0
        no_rcp_trans_rosc = no_rcp_trans_data['rosc'].sum() if 'rosc' in no_rcp_trans_data.columns else 0
        
        print("\n📊 ROSC POR TIPO DE RCP:")
        if rcp_trans_total > 0:
            rcp_trans_rosc_pct = (rcp_trans_rosc / rcp_trans_total) * 100
            print(f"   • Con RCP transtelefónica: {rcp_trans_rosc}/{rcp_trans_total} ({rcp_trans_rosc_pct:.1f}%)")
        
        if no_rcp_trans_total > 0:
            no_rcp_trans_rosc_pct = (no_rcp_trans_rosc / no_rcp_trans_total) * 100
            print(f"   • Sin RCP transtelefónica: {no_rcp_trans_rosc}/{no_rcp_trans_total} ({no_rcp_trans_rosc_pct:.1f}%)")
    
    # Estadísticas de CPC
    if 'cpc' in data.columns and 'supervivencia_7dias' in data.columns:
        surv_data = data[data['supervivencia_7dias'] == 1]
        
        if len(surv_data) > 0:
            print("\n🧠 DISTRIBUCIÓN DE CPC EN SUPERVIVIENTES:")
            cpc_counts = surv_data['cpc'].value_counts().sort_index()
            
            for cpc, count in cpc_counts.items():
                if not pd.isna(cpc):  # No mostrar valores NaN
                    pct = (count / len(surv_data)) * 100
                    print(f"   • CPC {int(cpc)}: {count} ({pct:.1f}%)")
            
            favorable_cpc = surv_data[surv_data['cpc'].isin([1, 2])]
            favorable_pct = (len(favorable_cpc) / len(surv_data)) * 100 if len(surv_data) > 0 else 0
            
            print(f"\n   • CPC favorable (1-2): {len(favorable_cpc)} ({favorable_pct:.1f}% de supervivientes)")
    
    # Estadísticas de edad
    if 'edad' in data.columns:
        edad_media = data['edad'].mean()
        edad_mediana = data['edad'].median()
        edad_min = data['edad'].min()
        edad_max = data['edad'].max()
        
        print("\n👴 DISTRIBUCIÓN POR EDAD:")
        print(f"   • Media: {edad_media:.1f} años")
        print(f"   • Mediana: {edad_mediana:.1f} años")
        print(f"   • Rango: {edad_min:.0f}-{edad_max:.0f} años")
        
        # Calcular estadísticas de grupos de edad sin crear columnas permanentes
        edad_menor_65 = len(data[data['edad'] < 65])
        edad_mayor_igual_65 = len(data[(data['edad'] >= 65) & (~data['edad'].isna())])
        total_con_edad = edad_menor_65 + edad_mayor_igual_65
        
        print("\n   Estratificación por edad:")
        if total_con_edad > 0:
            pct_menor = (edad_menor_65 / total_con_edad) * 100
            pct_mayor = (edad_mayor_igual_65 / total_con_edad) * 100
            print(f"   • <65 años: {edad_menor_65} ({pct_menor:.1f}%)")
            print(f"   • ≥65 años: {edad_mayor_igual_65} ({pct_mayor:.1f}%)")
    
    # Estadísticas de tiempo de llegada
    if 'tiempo_llegada' in data.columns:
        tiempo_medio = data['tiempo_llegada'].mean()
        tiempo_mediana = data['tiempo_llegada'].median()
        
        print("\n⏱️ TIEMPO DE LLEGADA:")
        print(f"   • Media: {tiempo_medio:.1f} segundos")
        print(f"   • Mediana: {tiempo_mediana:.1f} segundos")
        
        # Calcular estadísticas por tiempo sin crear columnas permanentes
        tiempo_menor_mediana = len(data[data['tiempo_llegada'] < tiempo_mediana])
        tiempo_mayor_igual_mediana = len(data[(data['tiempo_llegada'] >= tiempo_mediana) & (~data['tiempo_llegada'].isna())])
        total_con_tiempo = tiempo_menor_mediana + tiempo_mayor_igual_mediana
        
        print("\n   Estratificación por tiempo de llegada:")
        if total_con_tiempo > 0:
            pct_menor = (tiempo_menor_mediana / total_con_tiempo) * 100
            pct_mayor = (tiempo_mayor_igual_mediana / total_con_tiempo) * 100
            print(f"   • <mediana: {tiempo_menor_mediana} ({pct_menor:.1f}%)")
            print(f"   • ≥mediana: {tiempo_mayor_igual_mediana} ({pct_mayor:.1f}%)")
    
    print("\n" + "="*80)

def save_output(data, output_dir):
    """Guarda los datos procesados en formatos CSV y Excel"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Eliminar columnas de estratificación que son para análisis, no para datos brutos
    if 'grupo_edad' in data.columns:
        data = data.drop(columns=['grupo_edad'])
    if 'grupo_tiempo' in data.columns:
        data = data.drop(columns=['grupo_tiempo'])
        
    csv_path = os.path.join(output_dir, 'cleaned_data.csv')
    excel_path = os.path.join(output_dir, 'cleaned_data.xlsx')
    
    # Convertir todas las columnas numéricas a enteros naturales (sin decimales)
    for col in data.columns:
        if pd.api.types.is_numeric_dtype(data[col]):
            # Solo convertir si no hay NaN, si hay NaN, mantener como int donde se pueda
            if data[col].isnull().any():
                data[col] = data[col].apply(lambda x: int(x) if not pd.isna(x) else x)
            else:
                data[col] = data[col].astype(int)
    # Guardar sin floats
    data.to_csv(csv_path, index=False)
    data.to_excel(excel_path, index=False)
    
    print(f"\n💾 Datos procesados guardados en:")
    print(f"   • CSV: {csv_path}")
    print(f"   • Excel: {excel_path}")

def generar_resumen_exclusion(datos_iniciales, datos_finales, estadisticas_unidades={}, estadisticas_exclusion={}):
    """Genera un resumen del proceso de exclusión de datos"""
    print("\n" + "="*80)
    print("📋 RESUMEN DEL PROCESO DE LIMPIEZA Y EXCLUSIÓN")
    print("="*80)
    
    total_inicial = len(datos_iniciales)
    total_final = len(datos_finales)
    excluidos = total_inicial - total_final
    
    print(f"• Total de registros iniciales: {total_inicial}")
    print(f"• Total de registros finales: {total_final}")
    print(f"• Total de registros excluidos: {excluidos} ({(excluidos/total_inicial)*100:.1f}%)")
    
    # Desglose de exclusiones por motivo
    print("\n📊 DESGLOSE DE EXCLUSIONES POR MOTIVO:")
    
    # Exclusiones por RCP transtelefónica desconocida
    excluidos_rcp_trans = estadisticas_exclusion.get('excluidos_rcp_trans', 0)
    if excluidos_rcp_trans > 0:
        pct_rcp_trans = (excluidos_rcp_trans / total_inicial) * 100
        print(f"   • Por RCP transtelefónica desconocida: {excluidos_rcp_trans} ({pct_rcp_trans:.1f}%)")
    
    # Exclusiones por origen traumático
    excluidos_traumaticos = estadisticas_exclusion.get('excluidos_traumaticos', 0)
    if excluidos_traumaticos > 0:
        pct_trauma = (excluidos_traumaticos / (total_inicial - excluidos_rcp_trans)) * 100
        print(f"   • Por origen traumático: {excluidos_traumaticos} ({pct_trauma:.1f}%)")
    
    # Información sobre registros SVA y SVB
    if estadisticas_unidades:
        print("\n📋 ESTADÍSTICAS DE UNIDADES:")
        total_sva = estadisticas_unidades.get('total_sva', 0)
        total_svb = estadisticas_unidades.get('total_svb', 0)
        total_otros = estadisticas_unidades.get('total_otros', 0)
        svb_emparejados = estadisticas_unidades.get('svb_emparejados', 0)
        svb_no_emparejados = estadisticas_unidades.get('svb_no_emparejados', 0)
        
        print(f"   • Total registros SVA: {total_sva}")
        print(f"   • Total registros SVB: {total_svb}")
        if total_otros > 0:
            print(f"   • Otros tipos de registros: {total_otros}")
        
        if total_svb > 0:
            pct_emparejados = (svb_emparejados / total_svb) * 100
            pct_no_emparejados = (svb_no_emparejados / total_svb) * 100
            print(f"   • SVB emparejados con SVA: {svb_emparejados} ({pct_emparejados:.1f}%)")
            print(f"   • SVB no emparejados (excluidos): {svb_no_emparejados} ({pct_no_emparejados:.1f}%)")
    
    # Análisis de campos faltantes en datos finales
    campos_faltantes = {}
    for columna in datos_finales.columns:
        nulos = datos_finales[columna].isna().sum()
        if nulos > 0:
            campos_faltantes[columna] = nulos
    
    if campos_faltantes:
        print("\n📉 CAMPOS CON DATOS FALTANTES EN REGISTROS FINALES:")
        for campo, nulos in sorted(campos_faltantes.items(), key=lambda x: x[1], reverse=True):
            porcentaje = (nulos / len(datos_finales)) * 100
            print(f"   • {campo}: {nulos} valores nulos ({porcentaje:.1f}%)")
    
    print("="*80)

def main():
    """Función principal que coordina todo el proceso de limpieza y procesamiento"""
    print("\n" + "="*80)
    print("🧹 PROCESAMIENTO DE DATOS - ESTUDIO RCP TRANSTELEFÓNICA")
    print("="*80)
    print(f"📅 Fecha de ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Definir rutas
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(os.path.dirname(script_dir))  # Subir dos niveles
    
    raw_data_path = os.path.join(project_dir, 'data', '1.raw_imported', 'rawdata_2year.csv')
    output_dir = os.path.join(project_dir, 'data', '3.cleaned_data')
    
    # 1. Leer datos crudos
    raw_data = read_raw_data(raw_data_path)
    
    # 2. Fusionar datos SVA y SVB
    merged_data = merge_svb_sva(raw_data)
    
    # 3. Procesar datos
    processed_data = process_data(merged_data)
    
    # Recopilar estadísticas de exclusión
    estadisticas_unidades = merged_data.attrs.get('estadisticas_unidades', {})
    estadisticas_exclusion = processed_data.attrs.get('estadisticas_exclusion', {})
    
    # 4. Seleccionar columnas finales
    final_data = select_final_columns(processed_data)
    
    # 5. Generar estadísticas resumidas
    generate_summary_statistics(final_data)
    
    # 6. Generar resumen de exclusión detallado
    generar_resumen_exclusion(raw_data, final_data, estadisticas_unidades, estadisticas_exclusion)
    
    # 7. Guardar resultados
    save_output(final_data, output_dir)

    # 8. Generar informe de anomalías para comprobación manual
    generate_manual_check_report(final_data, output_dir)

    print("\n✅ Procesamiento completado con éxito")
    print("="*80)

def generate_manual_check_report(data, output_dir):
    """Genera un informe markdown con anomalías para comprobación manual"""
    report_lines = []
    report_lines.append("# Informe de comprobación manual de anomalías\n")
    report_lines.append(f"Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report_lines.append("\n## 1. Supervivientes sin CPC\n")
    # Filas con supervivencia pero sin CPC
    mask_surv_no_cpc = (data['supervivencia_7dias'] == 1) & (data['cpc'].isna() | (data['cpc'] == ''))
    rows_surv_no_cpc = data[mask_surv_no_cpc]
    if not rows_surv_no_cpc.empty:
        report_lines.append("N_informe de casos con supervivencia pero CPC vacío:")
        for idx, row in rows_surv_no_cpc.iterrows():
            report_lines.append(f"- {row.get('n_informe','')} (fecha: {row.get('fecha','')})")
    else:
        report_lines.append("No se encontraron casos.\n")

    report_lines.append("\n## 2. Filas con 4 o más campos vacíos\n")
    # Contar nulos por fila (solo en columnas principales)
    main_cols = ['n_informe', 'fecha', 'edad', 'sexo', 'rcp_transtelefonica', 'tipo_respondiente',
                 'tiempo_llegada', 'desa_externo', 'ritmo_desfibrilable', 'tiempo_rcp',
                 'rosc', 'supervivencia_7dias', 'cpc']
    data_main = data[main_cols]
    null_counts = data_main.isnull() | (data_main == '')
    mask_4plus_nulls = null_counts.sum(axis=1) >= 4
    rows_4plus_nulls = data[mask_4plus_nulls]
    if not rows_4plus_nulls.empty:
        report_lines.append("N_informe de casos con 4 o más campos principales vacíos:")
        for idx, row in rows_4plus_nulls.iterrows():
            report_lines.append(f"- {row.get('n_informe','')} (fecha: {row.get('fecha','')})")
    else:
        report_lines.append("No se encontraron casos.\n")

    # Guardar el informe en la carpeta de limpieza
    report_path = os.path.join(output_dir, '../2.Data_cleaning/informe_anomalias.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    print(f"\n📝 Informe de anomalías guardado en: {report_path}")

if __name__ == "__main__":
    main()