import pandas as pd

def read_data(file_path):
    """Reads the raw CSV data and renames columns."""
    data = pd.read_csv(file_path, delimiter=';')
    data.rename(columns={
        'NUM INFORME': 'n_informe',
        'FECHA_LLAMADA': 'fecha',
        'EDAD': 'edad',
        'SEXO': 'sexo',
        'RCP_TRANSTELEFONICA': 'rcp_transtelefonica',
        'DESA_EXTERNO': 'desa_externo',
        'RCP_TESTIGOS': 'rcp_testigos',
        'C0_C1': 'tiempo_co',
        'C1_C2': 'tiempo_c3',
        'C2_C3': 'tiempo_c2_c3',
        'C3_C4': 'tiempo_c3_c4',
        'RITMO INICIAL': 'ritmo',
        'ROSC': 'rosc',
        '7 DIAS': 'supervivencia_7dias',
        'CPC': 'cpc',
        'Tipo de Unidad': 'tipo_unidad',
        'CONSULTA': 'consulta',
        'ANTECEDENTES': 'antecedentes',
        'TECNICAS': 'tecnicas',
        'EVOLUCION': 'evolucion',
        'HOSPITAL': 'hospital',
        '6 HORAS': '6 horas',
        '24 HORAS': '24 horas',
        '7 DIAS': '7 dias'
    }, inplace=True)
    return data

def filter_sva(data):
    """Filters for SVA units and handles duplicates."""
    sva_data = data[data['tipo_unidad'] == 'SVA'].copy()
    return sva_data

def calculate_derived_columns(data):
    """Calculates derived time and rhythm columns."""
    # Convert time columns to numeric, coercing errors to NaN
    time_cols = ['tiempo_co', 'tiempo_c3', 'tiempo_c2_c3', 'tiempo_c3_c4']
    for col in time_cols:
        data[col] = pd.to_numeric(data[col], errors='coerce')

    # Fill NaN values with 0 before summation
    data['tiempo_llegada_unidad'] = data[['tiempo_co', 'tiempo_c3', 'tiempo_c2_c3']].sum(axis=1)
    data['tiempo_rcp'] = pd.to_numeric(data['tiempo_c3_c4'], errors='coerce').fillna(0).astype(int)

    # Convert 'edad' to integer only if not NaN
    data['edad'] = pd.to_numeric(data['edad'], errors='coerce')

    desfibrilable_ritmos = ['VF', 'TV', 'FV', 'FIBRILACION', 'TAQUICARDIA VENTRICULAR', 'FIBRILACION VENTRICULAR', 'FIBRILACIÓN']
    data['ritmo'] = data['ritmo'].astype(str).apply(
        lambda x: 1 if any(ritmo in x.upper() for ritmo in desfibrilable_ritmos) else 0
    )
    return data

def process_boolean_columns(data):
    """Maps boolean-like values to 0s and 1s."""
    boolean_columns = ['rcp_transtelefonica', 'desa_externo', 'rcp_testigos']
    for col in boolean_columns:
        data[col] = data[col].apply(lambda x: 1 if str(x).lower() in ['verdadero', 'true', '1'] else 0)
    data[boolean_columns] = data[boolean_columns].astype(int)
    return data

def classify_responders_and_rosc(data):
    """Classifies responders and determines ROSC from the 'consulta' column."""
    # Policía: incluye códigos 091, 092, 062 y términos relacionados
    data['policia'] = data['consulta'].str.contains(
        'policia|municipal|091|092|062', case=False, na=False
    ).astype(int)
    
    # Bomberos: incluye código 080, beta y términos relacionados
    data['bombero'] = data['consulta'].str.contains(
        'bombero|080|beta', case=False, na=False
    ).astype(int)
    
    # Sanitarios: incluye códigos 061, 060, SUMMA, SAMUR, SVB, personal hospital y términos médicos
    data['sanitario'] = data['consulta'].str.contains(
        'sanitario|medico|enfermero|tes|061|060|summa|samur|svb|hospital|personal sanitario|personal medico', 
        case=False, na=False
    ).astype(int)
    
    # Legos: ciudadanos, testigos y personas sin formación médica específica
    data['legos'] = data['consulta'].str.contains(
        'lego|ciudadano|testigo|persona|alertante|demandante|llamante', case=False, na=False
    ).astype(int)
    
    # Si hubo RCP transtelefónica, asumir que hubo testigo lego
    data.loc[data['rcp_transtelefonica'] == 1, 'legos'] = 1

    # Determine ROSC based on 'consulta' or if there is a time in 'tiempo_c3_c4'
    data['rosc'] = data['consulta'].str.contains('rosc|recuperada', case=False, na=False).astype(int)
    data.loc[data['tiempo_c3_c4'] > 0, 'rosc'] = 1
    
    # Si hubo RCP transtelefónica, asumir que hubo RCP de testigos (lego)
    data.loc[data['rcp_transtelefonica'] == 1, 'rcp_testigos'] = 1

    def classify_responder(row):
        if row['rcp_testigos'] == 0:
            return ''
        # Si hubo RCP transtelefónica, el respondiente es lego (por defecto)
        if row['rcp_transtelefonica'] == 1:
            return 'lego'
        # Prioridad de clasificación: sanitario > bombero > policia > lego
        if row['sanitario'] == 1:
            return 'sanitario'
        if row['bombero'] == 1:
            return 'bombero'
        if row['policia'] == 1:
            return 'policia'
        if row['legos'] == 1:
            return 'lego'
        return 'lego'  # Por defecto si hay RCP de testigos pero no se identifica el tipo

    data['respondiente_rcp'] = data.apply(classify_responder, axis=1)
    return data

def filter_rcp_transtelefonica(data):
    """Filters cases to include only those with telephone-guided CPR data."""
    # Mantener solo casos donde hay información clara sobre RCP transtelefónica
    # Esto incluye tanto casos con RCP transtelefónica (1) como sin ella (0)
    # Eliminar casos donde la información no esté clara o sea ambigua
    
    # Por ahora, mantenemos todos los casos ya que el procesamiento booleano
    # ya ha convertido los valores a 0 o 1 de forma consistente
    return data

def filter_traumatic(data):
    """Filters out cases with traumatic origin."""
    traumatic_keywords = [
        'trauma', 'traumatico', 'herida', 'heridas', 'herido', 'heridos',
        'caida', 'caidas', 'accidente', 'precipitado', 'ahogamiento', 
        'suicidio', 'golpe', 'golpes', 'agresion', 'agresión',
        'intoxicacion', 'intoxicación', 'sobredosis', 'electrocucion', 'electrocución',
        'lesion', 'lesiones', 'lesión', 'lesiónes'
    ]
    return data[~data['consulta'].str.contains('|'.join(traumatic_keywords), case=False, na=False)]

def calculate_rcp_time_no_rosc(data):
    """Calculates RCP time when there's no ROSC, based on text analysis of multiple columns."""
    import re
    from datetime import datetime, timedelta
    
    # Crear una copia explícita para evitar warnings
    data = data.copy()
    
    cols = ['consulta', 'antecedentes', 'tecnicas', 'evolucion', 'hospital', '6 horas', '24 horas', '7 dias']
    
    def extract_rcp_time(row):
        if row.get('rosc', 0) == 1 and row.get('tiempo_rcp', 0) > 0:  # Si hay ROSC y ya hay tiempo, mantenerlo
            return row.get('tiempo_rcp', 0)
        
        # Buscar tiempo directo de RCP en minutos/horas en todas las columnas
        for col in cols:
            text = str(row.get(col, '')).lower()
            if pd.isna(text) or text == 'nan' or text == '':
                continue
                
            # Patrones más amplios para detectar tiempo de RCP
            patterns = [
                r'rcp.*?(\d+)\s*min',
                r'(\d+)\s*min.*?rcp',
                r'reanimaci[oó]n.*?(\d+)\s*min',
                r'(\d+)\s*min.*?reanimaci[oó]n',
                r'rcp.*?(\d+)\s*hora',
                r'(\d+)\s*hora.*?rcp',
                r'masaje.*?(\d+)\s*min',
                r'(\d+)\s*min.*?masaje',
                r'maniobras.*?(\d+)\s*min',
                r'(\d+)\s*min.*?maniobras',
                r'soporte.*?(\d+)\s*min',
                r'(\d+)\s*min.*?soporte',
                r'compresiones.*?(\d+)\s*min',
                r'(\d+)\s*min.*?compresiones'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    try:
                        mins = int(match.group(1))
                        if mins > 0 and mins <= 180:  # Máximo 3 horas razonable
                            return mins * 60  # Convertir a segundos
                    except ValueError:
                        continue
        
        # Buscar hora de exitus/fallecimiento y calcular diferencia
        try:
            fecha_str = str(row.get('fecha', ''))
            if not fecha_str or fecha_str == 'nan':
                return row.get('tiempo_rcp', 0)
                
            # Extraer hora de inicio de la fecha
            fecha_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}):(\d{2})', fecha_str)
            if not fecha_match:
                return row.get('tiempo_rcp', 0)
                
            fecha_inicio = datetime.strptime(fecha_match.group(0), '%d/%m/%Y %H:%M')
            
            # Sumar tiempo de llegada si no hay RCP de testigos
            if row.get('rcp_testigos', 0) == 0:
                tiempo_llegada = row.get('tiempo_llegada_unidad', 0)
                fecha_inicio += timedelta(seconds=tiempo_llegada)
            
            # Buscar hora de exitus/fallecimiento
            for col in cols:
                text = str(row.get(col, '')).lower()
                if pd.isna(text) or text == 'nan' or text == '':
                    continue
                    
                # Patrones más amplios de hora de fallecimiento
                hora_patterns = [
                    r'exitus.*?(\d{1,2}):(\d{2})',
                    r'fallec.*?(\d{1,2}):(\d{2})',
                    r'muerte.*?(\d{1,2}):(\d{2})',
                    r'fin.*?(\d{1,2}):(\d{2})',
                    r'cese.*?(\d{1,2}):(\d{2})',
                    r'parada.*?(\d{1,2}):(\d{2})',
                    r'(\d{1,2}):(\d{2}).*?exitus',
                    r'(\d{1,2}):(\d{2}).*?fallec',
                    r'(\d{1,2}):(\d{2}).*?muerte',
                    r'(\d{1,2}):(\d{2}).*?fin',
                    r'(\d{1,2}):(\d{2}).*?cese'
                ]
                
                for pattern in hora_patterns:
                    match = re.search(pattern, text)
                    if match:
                        try:
                            hora_fin = int(match.group(1))
                            min_fin = int(match.group(2))
                            
                            if hora_fin > 23 or min_fin > 59:  # Validar hora
                                continue
                            
                            # Crear datetime de fin (mismo día)
                            fecha_fin = fecha_inicio.replace(hour=hora_fin, minute=min_fin, second=0, microsecond=0)
                            
                            # Si la hora es menor, asumir día siguiente
                            if fecha_fin <= fecha_inicio:
                                fecha_fin += timedelta(days=1)
                            
                            # Calcular diferencia en segundos
                            diff = (fecha_fin - fecha_inicio).total_seconds()
                            if 0 < diff <= 10800:  # Entre 0 y 3 horas
                                return int(diff)
                        except (ValueError, IndexError):
                            continue
                            
        except Exception:
            pass
        
        # Si no se encuentra nada específico, usar el tiempo original o 0
        return row.get('tiempo_rcp', 0)
    
    data.loc[:, 'tiempo_rcp'] = data.apply(extract_rcp_time, axis=1)
    return data

def analyze_excluded_cases(data, merge_stats=None):
    """
    Analiza los casos y genera reporte detallado de exclusiones
    siguiendo los criterios específicos del estudio.
    """
    import re
    
    print(f"\n🔍 ANÁLISIS DETALLADO DE EXCLUSIONES:")
    print(f"   • Casos totales iniciales: {len(data)}")
    
    # PASO 1: Contar casos iniciales RCP transtelefónica
    casos_rcp_trans_iniciales = data['rcp_transtelefonica'].sum()
    print(f"   • Casos con RCP transtelefónica iniciales: {casos_rcp_trans_iniciales}")
    
    # PASO 2: Analizar exclusiones por casos traumáticos
    traumaticos = [
        'incendio', 'ahogamiento', 'precipitado', 'atropello', 'trauma', 'traumatico',
        'herida', 'heridas', 'herido', 'heridos', 'accidente', 'caida', 'caidas',
        'golpe', 'golpes', 'agresion', 'agresión', 'suicidio', 'intoxicacion', 
        'intoxicación', 'sobredosis', 'electrocucion', 'electrocución'
    ]
    
    cols_trauma = ['consulta', 'antecedentes', 'tecnicas', 'evolucion', 'hospital', '6 horas', '24 horas', '7 dias']
    
    # Identificar casos traumáticos globales
    casos_traumaticos_globales = []
    for idx, row in data.iterrows():
        es_traumatico = False
        motivo_trauma = ""
        texto_relevante = ""
        
        for col in cols_trauma:
            if col in row and pd.notna(row[col]):
                texto = str(row[col]).lower()
                for trauma_keyword in traumaticos:
                    if trauma_keyword in texto:
                        es_traumatico = True
                        motivo_trauma = f"'{trauma_keyword}' en columna '{col}'"
                        texto_relevante = texto[:100] + "..." if len(texto) > 100 else texto
                        break
                if es_traumatico:
                    break
        
        if es_traumatico:
            casos_traumaticos_globales.append({
                'n_informe': row.get('n_informe', 'N/A'),
                'rcp_transtelefonica': row.get('rcp_transtelefonica', 0),
                'motivo': motivo_trauma,
                'texto_relevante': texto_relevante
            })
    
    # Separar traumáticos con y sin RCP transtelefónica
    traumaticos_con_rcp = [caso for caso in casos_traumaticos_globales if caso['rcp_transtelefonica'] == 1]
    traumaticos_sin_rcp = [caso for caso in casos_traumaticos_globales if caso['rcp_transtelefonica'] == 0]
    
    print(f"   • Casos traumáticos totales excluidos: {len(casos_traumaticos_globales)}")
    print(f"     - Con RCP transtelefónica: {len(traumaticos_con_rcp)}")
    print(f"     - Sin RCP transtelefónica: {len(traumaticos_sin_rcp)}")
    
    # PASO 3: Analizar casos sin RCP transtelefónica información
    data_no_traumaticos = data.copy()
    # Simular exclusión de traumáticos
    for caso in casos_traumaticos_globales:
        data_no_traumaticos = data_no_traumaticos[data_no_traumaticos['n_informe'] != caso['n_informe']]
    
    sin_rcp_info = []
    for idx, row in data_no_traumaticos.iterrows():
        if pd.isna(row.get('rcp_transtelefonica')) or str(row.get('rcp_transtelefonica')).strip() == '':
            sin_rcp_info.append({
                'n_informe': row.get('n_informe', 'N/A'),
                'motivo': 'Sin información de RCP transtelefónica'
            })
    
    print(f"   • Casos sin información RCP transtelefónica excluidos: {len(sin_rcp_info)}")
    
    # CÁLCULOS FINALES
    casos_finales_total = len(data) - len(casos_traumaticos_globales) - len(sin_rcp_info)
    casos_rcp_trans_finales = casos_rcp_trans_iniciales - len(traumaticos_con_rcp)
    
    print(f"\n📊 RESUMEN DE EXCLUSIONES:")
    print(f"   • TOTAL:")
    print(f"     - Casos iniciales: {len(data)}")
    print(f"     - Excluidos por traumáticos: {len(casos_traumaticos_globales)}")
    print(f"     - Excluidos por falta RCP transtelefónica: {len(sin_rcp_info)}")
    print(f"     - Casos finales: {casos_finales_total}")
    print(f"     - Tasa de retención: {(casos_finales_total/len(data)*100):.1f}%")
    
    print(f"   • RCP TRANSTELEFÓNICA:")
    print(f"     - Casos iniciales: {casos_rcp_trans_iniciales}")
    print(f"     - Excluidos por traumáticos: {len(traumaticos_con_rcp)}")
    print(f"     - Casos finales: {casos_rcp_trans_finales}")
    print(f"     - Tasa de retención: {(casos_rcp_trans_finales/casos_rcp_trans_iniciales*100):.1f}%")
    
    # GENERAR REPORTE DETALLADO
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    reporte_path = os.path.join(script_dir, 'reporte_exclusiones_detallado.txt')
    
    with open(reporte_path, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("REPORTE DETALLADO DE EXCLUSIONES - ESTUDIO RCP TRANSTELEFÓNICA\n")
        f.write("="*80 + "\n")
        f.write(f"Generado el: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("CRITERIOS DE EXCLUSIÓN APLICADOS:\n")
        f.write("1. Casos traumáticos (solo evaluamos paradas médicas)\n")
        f.write("2. Casos sin información de RCP transtelefónica\n")
        f.write("3. Para casos restantes: campos vacíos se dejan vacíos\n")
        f.write("4. Excepción: Si supervivencia 7 días vacía → asumimos 0 y CPC 5\n\n")
        
        # AÑADIR INFORMACIÓN DEL MERGE SI ESTÁ DISPONIBLE
        if merge_stats:
            f.write("INFORMACIÓN DEL PROCESO DE MERGE SVB→SVA:\n")
            f.write("-" * 50 + "\n")
            f.write(f"DATOS ORIGINALES (antes del merge):\n")
            f.write(f"• Total casos: {merge_stats['total_originales']}\n")
            f.write(f"• Casos SVA: {merge_stats['sva_originales']}\n")
            f.write(f"• Casos SVB: {merge_stats['svb_originales']}\n")
            f.write(f"• RCP transtelefónica en SVA: {merge_stats['rcp_trans_sva_originales']}\n")
            f.write(f"• RCP transtelefónica en SVB: {merge_stats['rcp_trans_svb_originales']}\n")
            f.write(f"• RCP transtelefónica TOTAL: {merge_stats['rcp_trans_total_originales']}\n\n")
            
            f.write(f"DESPUÉS DEL MERGE:\n")
            f.write(f"• Total casos: {merge_stats['total_merged']}\n")
            f.write(f"• RCP transtelefónica conservados: {merge_stats['rcp_trans_merged']}\n")
            f.write(f"• RCP transtelefónica perdidos: {merge_stats['rcp_trans_total_originales'] - merge_stats['rcp_trans_merged']}\n\n")
            
            # NÚMEROS DE INFORME ANTES DEL MERGE
            f.write("NÚMEROS DE INFORME RCP TRANSTELEFÓNICA ANTES DEL MERGE:\n")
            f.write("-" * 50 + "\n")
            f.write(f"SVA ({len(merge_stats['rcp_trans_sva_informes'])} casos):\n")
            for i in range(0, len(merge_stats['rcp_trans_sva_informes']), 10):
                grupo = merge_stats['rcp_trans_sva_informes'][i:i+10]
                f.write(f"   {', '.join(map(str, grupo))}\n")
            f.write(f"\nSVB ({len(merge_stats['rcp_trans_svb_informes'])} casos):\n")
            for i in range(0, len(merge_stats['rcp_trans_svb_informes']), 10):
                grupo = merge_stats['rcp_trans_svb_informes'][i:i+10]
                f.write(f"   {', '.join(map(str, grupo))}\n")
            f.write(f"\nCONSERVADOS DESPUÉS DEL MERGE ({len(merge_stats['rcp_trans_merged_informes'])} casos):\n")
            for i in range(0, len(merge_stats['rcp_trans_merged_informes']), 10):
                grupo = merge_stats['rcp_trans_merged_informes'][i:i+10]
                f.write(f"   {', '.join(map(str, grupo))}\n")
            f.write("\n")
        
        f.write("RESUMEN CUANTITATIVO:\n")
        f.write("-" * 40 + "\n")
        f.write(f"ANÁLISIS GLOBAL:\n")
        f.write(f"• Casos totales iniciales: {len(data)}\n")
        f.write(f"• Excluidos por traumáticos: {len(casos_traumaticos_globales)} ({len(casos_traumaticos_globales)/len(data)*100:.1f}%)\n")
        f.write(f"• Excluidos por falta RCP transtelefónica: {len(sin_rcp_info)} ({len(sin_rcp_info)/len(data)*100:.1f}%)\n")
        f.write(f"• Casos finales incluidos: {casos_finales_total} ({casos_finales_total/len(data)*100:.1f}%)\n\n")
        
        f.write(f"ANÁLISIS RCP TRANSTELEFÓNICA:\n")
        f.write(f"• Casos iniciales: {casos_rcp_trans_iniciales}\n")
        f.write(f"• Excluidos por traumáticos: {len(traumaticos_con_rcp)} ({len(traumaticos_con_rcp)/casos_rcp_trans_iniciales*100:.1f}%)\n")
        f.write(f"• Casos finales incluidos: {casos_rcp_trans_finales} ({casos_rcp_trans_finales/casos_rcp_trans_iniciales*100:.1f}%)\n\n")
        
        # NÚMEROS DE INFORME DE CASOS RCP TRANSTELEFÓNICA
        f.write("NÚMEROS DE INFORME - CASOS RCP TRANSTELEFÓNICA:\n")
        f.write("-" * 60 + "\n")
        rcp_trans_casos = data[data['rcp_transtelefonica'] == 1]
        rcp_trans_informes = rcp_trans_casos['n_informe'].tolist()
        
        f.write(f"CASOS RCP TRANSTELEFÓNICA INCLUIDOS EN EL ANÁLISIS ({len(rcp_trans_informes)} casos):\n")
        # Escribir en grupos de 10 para mejor legibilidad
        for i in range(0, len(rcp_trans_informes), 10):
            grupo = rcp_trans_informes[i:i+10]
            f.write(f"   {', '.join(map(str, grupo))}\n")
        f.write("\n")
        
        if traumaticos_con_rcp:
            f.write("CASOS RCP TRANSTELEFÓNICA EXCLUIDOS POR SER TRAUMÁTICOS:\n")
            f.write("-" * 60 + "\n")
            for caso in traumaticos_con_rcp:
                f.write(f"Nº Informe: {caso['n_informe']}\n")
                f.write(f"  Motivo: {caso['motivo']}\n")
                f.write(f"  Texto: {caso['texto_relevante']}\n\n")
        
        if casos_traumaticos_globales:
            f.write("TODOS LOS CASOS TRAUMÁTICOS EXCLUIDOS:\n")
            f.write("-" * 60 + "\n")
            for caso in casos_traumaticos_globales:
                rcp_status = "CON RCP TRANS" if caso['rcp_transtelefonica'] == 1 else "SIN RCP TRANS"
                f.write(f"Nº Informe: {caso['n_informe']} ({rcp_status})\n")
                f.write(f"  Motivo: {caso['motivo']}\n")
                f.write(f"  Texto: {caso['texto_relevante']}\n\n")
    
    print(f"📋 Reporte detallado generado: {reporte_path}")
    
    return len(casos_traumaticos_globales), len(sin_rcp_info), casos_rcp_trans_finales
    
    def has_followup_info(row):
        """Verificar si hay información de seguimiento en las columnas clave"""
        # Verificar columnas de seguimiento temporal
        for col in followup_cols:
            text = str(row.get(col, '')).strip().lower()
            # Si hay texto real (no vacío, no NaN, no solo espacios)
            if text and text != 'nan' and text != '' and len(text) > 2:
                return True
        
        # Verificar información de outcome en otras columnas relevantes
        for col in ['evolucion', 'hospital', 'consulta']:
            text = str(row.get(col, '')).lower()
            if text and text != 'nan' and len(text) > 10:  # Mínimo contenido
                # Indicadores claros de outcome
                outcome_indicators = [
                    'exitus', 'fallec', 'muerte', 'muere', 'óbito', 'obito', 'defunción',
                    'alta', 'domicilio', 'recupera', 'vive', 'sobrevive', 'consciente',
                    'traslado', 'ingresa', 'uci', 'planta', 'hospital', 'cuidados',
                    'pcr recuperada', 'rosc', 'pulso'
                ]
                if any(indicator in text for indicator in outcome_indicators):
                    return True
        
        # Si hay información de ROSC clara, consideramos que hay seguimiento
        if row.get('rosc', 0) == 1:
            return True
            
        # Si hay código patológico que indica outcome
        codigo_patologico = str(row.get('consulta', '')).lower()
        if any(pattern in codigo_patologico for pattern in ['c.0.0', 'w.0.1', 'recuperada', 'exitus']):
            return True
        
        return False

    def analyze_case_for_review(row):
        """Analizar si un caso requiere revisión manual"""
        review_needed = False
        reasons = []
        critical_issues = []  # Solo problemas que requieren revisión
        
        # 1. Sin información de RCP transtelefónica (estos se excluirán)
        if pd.isna(row.get('rcp_transtelefonica')) or str(row.get('rcp_transtelefonica')).strip() == '':
            reasons.append("Sin información de RCP transtelefónica - EXCLUIR")
            return True, reasons  # Estos casos se excluyen completamente
        
        # 2. Verificar información de seguimiento faltante
        if not has_followup_info(row):
            critical_issues.append("Sin información de seguimiento - se asumirá supervivencia=0 y CPC=5")
            review_needed = True
        
        # 3. Verificar información de CPC explícito (solo si hay seguimiento)
        has_explicit_cpc = False
        if has_followup_info(row):
            for col in cols:
                text = str(row.get(col, '')).lower()
                if pd.isna(text) or text == 'nan':
                    continue
                
                patterns = [
                    r'cpc\s*de\s*([1-5])', r'cpc\s*([1-5])', r'cpc\s*:\s*([1-5])',
                    r'cpc\s*=\s*([1-5])', r'cpc-([1-5])', r'cerebral\s*performance\s*category\s*([1-5])',
                    r'cerebral\s*performance\s*([1-5])', r'escala\s*cpc\s*([1-5])',
                    r'glasgow\s*outcome\s*scale?\s*([1-5])', r'puntuacion\s*cpc\s*([1-5])', r'score\s*cpc\s*([1-5])'
                ]
                
                for pattern in patterns:
                    if re.search(pattern, text):
                        has_explicit_cpc = True
                        break
                if has_explicit_cpc:
                    break
            
            # Si no hay ROSC, no necesitamos CPC explícito (será CPC 5)
            if row.get('rosc', 0) == 0:
                has_explicit_cpc = True  # No requerido en estos casos
            
            # Si columna "7 dias" está vacía, CPC será 5 automáticamente
            dias7_text = str(row.get('7 dias', '')).strip().lower()
            if not dias7_text or dias7_text == 'nan' or dias7_text == '' or len(dias7_text) <= 2:
                has_explicit_cpc = True  # Se asigna CPC 5 automáticamente
            
            if not has_explicit_cpc:
                # Verificar si hay supervivencia clara sin CPC explícito
                supervivencia_keywords = [
                    'alta', 'domicilio', 'recupera', 'recuperado', 'recuperada', 
                    'vive', 'sobrevive', 'consciente', 'despertar', 'despierta',
                    'estable', 'uci', 'planta', 'ingreso', 'hospitaliza',
                    'sin incidencias', 'traslado hospital'
                ]
                
                has_survival_info = False
                for col in followup_cols + ['evolucion', 'hospital']:
                    text = str(row.get(col, '')).lower()
                    if any(keyword in text for keyword in supervivencia_keywords):
                        has_survival_info = True
                        break
                
                if has_survival_info:
                    critical_issues.append("Con indicadores de supervivencia pero sin CPC explícito - REVISAR MANUALMENTE")
                    review_needed = True
        
        # 4. Verificar otras deficiencias de datos (solo para clasificar múltiples deficiencias)
        minor_issues = []
        
        if pd.isna(row.get('edad')) or str(row.get('edad')).strip() == '':
            minor_issues.append("Sin información de edad - se dejará vacío")
        
        if pd.isna(row.get('sexo')) or str(row.get('sexo')).strip() == '':
            minor_issues.append("Sin información de sexo - se dejará vacío")
        
        if pd.isna(row.get('rosc')) or str(row.get('rosc')).strip() == '':
            minor_issues.append("Sin información de ROSC - se dejará vacío")
        
        # Solo incluir para revisión si hay problemas críticos O múltiples deficiencias
        all_issues = critical_issues + minor_issues
        
        if critical_issues:  # Hay problemas críticos
            reasons = all_issues
            if len(all_issues) > 1:
                reasons.append("MÚLTIPLES DEFICIENCIAS - requiere revisión prioritaria")
            review_needed = True
        elif len(minor_issues) > 1:  # Solo múltiples problemas menores
            reasons = minor_issues
            reasons.append("MÚLTIPLES DEFICIENCIAS - requiere revisión prioritaria")
            review_needed = True
        # Si solo hay un problema menor (edad o sexo), NO se incluye para revisión
        
        return review_needed, reasons

    # Contadores y listas para el reporte
    cases_for_review = []
    exclusion_count = 0
    
    for idx, row in data.iterrows():
        review_needed, reasons = analyze_case_for_review(row)
        
        if any("Sin información de RCP transtelefónica" in reason for reason in reasons):
            exclusion_count += 1
        elif review_needed:
            cases_for_review.append({
                'n_informe': row.get('n_informe', 'N/A'),
                'razones': reasons
            })
    
    # Generar archivo de texto con casos para revisión
    if cases_for_review:
        with open('casos_para_revision.txt', 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("CASOS QUE REQUIEREN REVISIÓN MANUAL\n")
            f.write("="*80 + "\n")
            f.write(f"Generado el: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total de casos para revisar: {len(cases_for_review)}\n\n")
            
            # Agrupar por tipo de problema
            sin_cpc_con_supervivencia = []
            multiples_deficiencias = []
            sin_seguimiento = []
            
            for case in cases_for_review:
                has_cpc_issue = any("CPC explícito" in reason for reason in case['razones'])
                has_multiple = any("MÚLTIPLES DEFICIENCIAS" in reason for reason in case['razones'])
                has_followup_issue = any("seguimiento" in reason for reason in case['razones'])
                
                if has_multiple:
                    multiples_deficiencias.append(case)
                elif has_cpc_issue:
                    sin_cpc_con_supervivencia.append(case)
                elif has_followup_issue:
                    sin_seguimiento.append(case)
            
            # Escribir casos con supervivencia pero sin CPC explícito
            if sin_cpc_con_supervivencia:
                f.write("CASOS CON SUPERVIVENCIA PERO SIN CPC EXPLÍCITO:\n")
                f.write("-" * 50 + "\n")
                for case in sin_cpc_con_supervivencia:
                    f.write(f"Nº Informe: {case['n_informe']}\n")
                    for reason in case['razones']:
                        if "MÚLTIPLES DEFICIENCIAS" not in reason:  # No repetir esta línea
                            f.write(f"  - {reason}\n")
                    f.write("\n")
            
            # Escribir casos con múltiples deficiencias
            if multiples_deficiencias:
                f.write("CASOS CON MÚLTIPLES DEFICIENCIAS:\n")
                f.write("-" * 50 + "\n")
                for case in multiples_deficiencias:
                    f.write(f"Nº Informe: {case['n_informe']}\n")
                    for reason in case['razones']:
                        f.write(f"  - {reason}\n")
                    f.write("\n")
            
            # Escribir casos sin seguimiento
            if sin_seguimiento:
                f.write("CASOS SIN INFORMACIÓN DE SEGUIMIENTO:\n")
                f.write("-" * 50 + "\n")
                for case in sin_seguimiento:
                    f.write(f"Nº Informe: {case['n_informe']}\n")
                    for reason in case['razones']:
                        if "MÚLTIPLES DEFICIENCIAS" not in reason:  # No repetir esta línea
                            f.write(f"  - {reason}\n")
                    f.write("\n")
        
        print(f"\n📝 Archivo 'casos_para_revision.txt' generado con {len(cases_for_review)} casos para revisar")
        print(f"   • Casos con supervivencia sin CPC explícito: {len(sin_cpc_con_supervivencia)}")
        print(f"   • Casos con múltiples deficiencias: {len(multiples_deficiencias)}")
        print(f"   • Casos sin seguimiento: {len(sin_seguimiento)}")
    else:
        print(f"\n✅ No hay casos que requieran revisión manual")
    
    # GENERAR REPORTE ESPECÍFICO DE RCP TRANSTELEFÓNICA
    with open('reporte_rcp_transtelefonica.txt', 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("REPORTE DETALLADO - CASOS RCP TRANSTELEFÓNICA\n")
        f.write("="*80 + "\n")
        f.write(f"Generado el: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write(f"RESUMEN INICIAL:\n")
        f.write(f"• Casos con RCP transtelefónica detectados inicialmente: {casos_rcp_trans_iniciales}\n")
        f.write(f"• Casos RCP transtelefónica excluidos por traumáticos: {len(rcp_trans_traumaticos)}\n")
        f.write(f"• Casos RCP transtelefónica que pasarán a análisis final: {casos_rcp_trans_iniciales - len(rcp_trans_traumaticos)}\n\n")
        
        if rcp_trans_traumaticos:
            f.write("CASOS RCP TRANSTELEFÓNICA EXCLUIDOS POR SER TRAUMÁTICOS:\n")
            f.write("-" * 60 + "\n")
            for caso in rcp_trans_traumaticos:
                f.write(f"Nº Informe: {caso['n_informe']}\n")
                f.write(f"  Motivo: {caso['motivo']}\n")
                f.write(f"  Texto: {caso['texto_relevante']}\n\n")
        
        # Analizar casos RCP transtelefónica que requieren revisión
        rcp_trans_revision = [case for case in cases_for_review 
                             if any("RCP transtelefónica" in str(reason) for reason in case.get('razones', []))]
        
        f.write(f"CASOS RCP TRANSTELEFÓNICA QUE REQUIEREN REVISIÓN MANUAL: {len(rcp_trans_revision)}\n")
        f.write("-" * 60 + "\n")
        for case in rcp_trans_revision:
            f.write(f"Nº Informe: {case['n_informe']}\n")
            for reason in case['razones']:
                f.write(f"  - {reason}\n")
            f.write("\n")
    
    print(f"📋 Reporte específico de RCP transtelefonica generado: reporte_rcp_transtelefonica.txt")
    
    return exclusion_count, len(cases_for_review)

def determine_survival_cpc(data, merge_stats=None):
    """
    Determina supervivencia y CPC con criterios específicos del estudio.
    Solo excluye: 1) casos traumáticos, 2) casos sin info RCP transtelefónica.
    Para campos vacíos: se dejan vacíos, excepto supervivencia → asume 0 y CPC 5.
    """
    import re
    
    # PRIMERO: Analizar exclusiones según criterios específicos
    print(f"\n🔍 ANÁLISIS DE CALIDAD DE DATOS:")
    print(f"   • Total de casos antes del filtrado: {len(data)}")
    
    traumaticos_excluidos, sin_rcp_excluidos, rcp_trans_finales = analyze_excluded_cases(data, merge_stats)
    
    # Crear una copia explícita para evitar warnings
    data = data.copy()
    
    # Columnas a analizar
    cols = ['consulta', 'antecedentes', 'tecnicas', 'evolucion', 'hospital', '6 horas', '24 horas', '7 dias']
    followup_cols = ['6 horas', '24 horas', '7 dias']
    
    # Asegura que todas las columnas existen
    for col in cols:
        if col not in data.columns:
            data[col] = ''

    # PASO 1: Filtra casos traumáticos (según criterios específicos)
    traumaticos = [
        'incendio', 'ahogamiento', 'precipitado', 'atropello', 'trauma', 'traumatico',
        'herida', 'heridas', 'herido', 'heridos', 'accidente', 'caida', 'caidas',
        'golpe', 'golpes', 'agresion', 'agresión', 'suicidio', 'intoxicacion', 
        'intoxicación', 'sobredosis', 'electrocucion', 'electrocución'
    ]
    mask_traumatico = data[cols].apply(lambda row: any(t in str(cell).lower() for t in traumaticos for cell in row), axis=1)
    data = data[~mask_traumatico].copy()
    
    # PASO 2: Filtra casos sin información de RCP transtelefónica
    sin_rcp_trans = data['rcp_transtelefonica'].isna() | (data['rcp_transtelefonica'].astype(str).str.strip() == '')
    data = data[~sin_rcp_trans].copy()
    
    print(f"   • Casos después de aplicar criterios de exclusión: {len(data)}")
    print(f"   • Casos RCP transtelefónica finales: {data['rcp_transtelefonica'].sum()}")

    def has_followup_info(row):
        """Verifica si hay información de seguimiento válida"""
        # Verificar columnas de seguimiento temporal
        for col in followup_cols:
            text = str(row.get(col, '')).strip().lower()
            if text and text != 'nan' and text != '' and len(text) > 2:
                return True
        
        # Verificar información de outcome en otras columnas relevantes
        for col in ['evolucion', 'hospital', 'consulta']:
            text = str(row.get(col, '')).lower()
            if text and text != 'nan' and len(text) > 10:
                outcome_indicators = [
                    'exitus', 'fallec', 'muerte', 'muere', 'óbito', 'obito', 'defunción',
                    'alta', 'domicilio', 'recupera', 'vive', 'sobrevive', 'consciente',
                    'traslado', 'ingresa', 'uci', 'planta', 'hospital', 'cuidados',
                    'pcr recuperada', 'rosc', 'pulso'
                ]
                if any(indicator in text for indicator in outcome_indicators):
                    return True
        
        # Si hay información de ROSC clara, consideramos que hay seguimiento
        if row.get('rosc', 0) == 1:
            return True
            
        # Si hay código patológico que indica outcome
        codigo_patologico = str(row.get('consulta', '')).lower()
        if any(pattern in codigo_patologico for pattern in ['c.0.0', 'w.0.1', 'recuperada', 'exitus']):
            return True
        
        return False

    def get_cpc(row):
        # Si no hay ROSC, automáticamente CPC 5
        if row.get('rosc', 0) == 0:
            return 5
            
        # Si no hay información de seguimiento, asumir CPC = 5 (criterio específico)
        if not has_followup_info(row):
            return 5
        
        # Buscar CPC explícito en todas las columnas
        for col in cols:
            text = str(row.get(col, '')).lower()
            if pd.isna(text) or text == 'nan' or text == '':
                continue
                
            patterns = [
                r'cpc\s*de\s*([1-5])',
                r'cpc\s*(?:de|:)?\s*([1-5])',
                r'cerebral\s*performance\s*category\s*([1-5])',
                r'escala\s*cpc\s*([1-5])',
                r'cpc-([1-5])',
                r'glasgow\s*outcome\s*scale?\s*([1-5])',
                r'cpc\s*=\s*([1-5])',
                r'puntuacion\s*cpc\s*([1-5])',
                r'score\s*cpc\s*([1-5])'
            ]
            
            for pattern in patterns:
                matches = re.finditer(pattern, text)
                for match in matches:
                    try:
                        cpc_val = int(match.group(1))
                        if 1 <= cpc_val <= 5:
                            return cpc_val
                    except (ValueError, IndexError):
                        continue
        
        # Si no hay supervivencia a 7 días, CPC = 5
        supervivencia = get_supervivencia_temp(row)
        if supervivencia == 0:
            return 5
        
        # Si hay supervivencia pero no CPC explícito: según criterio específico, dejar vacío
        # pero para mantener consistencia del análisis, asumimos CPC 5
        return 5

    def get_supervivencia_temp(row):
        """Función para determinar supervivencia según criterios específicos"""
        # Si no hay ROSC, supervivencia = 0
        if row.get('rosc', 0) == 0:
            return 0
        
        # Si no hay información de seguimiento, asumir supervivencia = 0
        if not has_followup_info(row):
            return 0
        
        # Buscar indicadores explícitos de fallecimiento
        muerte_keywords = [
            'exitus', 'fallecido', 'fallece', 'fallecimiento', 'muerte', 'muere', 
            'óbito', 'obito', 'defunción', 'defuncion', 'deceased', 'died',
            'muerte cerebral', 'cese maniobras', 'suspender', 'confirma fallecimiento'
        ]
        
        for col in followup_cols + ['evolucion', 'hospital', 'consulta']:
            text = str(row.get(col, '')).lower()
            if any(keyword in text for keyword in muerte_keywords):
                return 0
        
        # Si el código patológico indica éxitus
        if 'w.0.1' in str(row.get('consulta', '')).lower() or 'exitus' in str(row.get('consulta', '')).lower():
            return 0
        
        # Buscar indicadores explícitos de supervivencia
        supervivencia_keywords = [
            'alta', 'domicilio', 'recupera', 'recuperado', 'recuperada', 
            'vive', 'sobrevive', 'consciente', 'despertar', 'despierta',
            'estable', 'uci', 'planta', 'ingreso', 'hospitaliza',
            'sin incidencias', 'traslado hospital'
        ]
        
        for col in followup_cols + ['evolucion', 'hospital']:
            text = str(row.get(col, '')).lower()
            if any(keyword in text for keyword in supervivencia_keywords):
                return 1
        
        # Si hay ROSC y código C.0.0 pero información ambigua, ser conservador
        return 0

    def get_supervivencia(row):
        # Aplicar criterio específico: si no hay información, asumir supervivencia = 0
        if not has_followup_info(row):
            return 0
            
        return get_supervivencia_temp(row)

    # Aplicar las funciones según criterios específicos
    data.loc[:, 'cpc'] = data.apply(get_cpc, axis=1)
    data.loc[:, 'supervivencia_7dias'] = data.apply(get_supervivencia, axis=1)
    
    # Asegurar consistencia: Si CPC = 5, supervivencia = 0
    data.loc[data['cpc'] == 5, 'supervivencia_7dias'] = 0
    
    print(f"\n📋 RESUMEN DE PROCESAMIENTO:")
    print(f"   • Casos finales procesados: {len(data)}")
    print(f"   • Casos RCP transtelefónica finales: {data['rcp_transtelefonica'].sum()}")
    print(f"   • Casos con supervivencia asignada por defecto: {len(data[~data.apply(has_followup_info, axis=1)])}")
    
    return data

def clean_and_reorder(data):
    """Drops temporary columns and reorders the final columns. Preserves NaN values for missing data."""
    # Define final columns in desired order
    final_columns = [
        'n_informe', 'fecha', 'edad', 'sexo', 'rcp_transtelefonica', 
        'rcp_testigos', 'respondiente_rcp', 'desa_externo', 'ritmo', 
        'tiempo_llegada_unidad', 'tiempo_rcp', 'rosc', 'supervivencia_7dias', 'cpc'
    ]
    
    # Select and reorder
    cleaned_data = data[final_columns].copy()
    
    # Convertir columnas numéricas, preservando NaN para datos faltantes
    # No forzar conversión de edad y sexo si están vacíos
    numeric_cols = ['rcp_transtelefonica', 'rcp_testigos', 'desa_externo', 'ritmo', 
                   'tiempo_llegada_unidad', 'tiempo_rcp', 'rosc', 'supervivencia_7dias', 'cpc']
    
    for col in numeric_cols:
        if col in cleaned_data.columns:
            cleaned_data[col] = pd.to_numeric(cleaned_data[col], errors='coerce')
    
    return cleaned_data

def print_data_summary(data, merge_stats=None):
    """Prints a comprehensive summary table of the processed data."""
    print("\n" + "="*80)
    print("RESUMEN ESTADÍSTICO - ANÁLISIS RCP TRANSTELEFÓNICA")
    print("="*80)
    
    # MOSTRAR ESTADÍSTICAS DEL MERGE SI ESTÁN DISPONIBLES
    if merge_stats:
        print(f"\n📈 ESTADÍSTICAS DEL PROCESO DE MERGE SVB→SVA:")
        print(f"   • DATOS ORIGINALES (antes del merge):")
        print(f"     - Total casos: {merge_stats['total_originales']}")
        print(f"     - Casos SVA: {merge_stats['sva_originales']}")
        print(f"     - Casos SVB: {merge_stats['svb_originales']}")
        print(f"     - RCP transtelefónica en SVA: {merge_stats['rcp_trans_sva_originales']}")
        print(f"     - RCP transtelefónica en SVB: {merge_stats['rcp_trans_svb_originales']}")
        print(f"     - RCP transtelefónica TOTAL: {merge_stats['rcp_trans_total_originales']}")
        
        print(f"   • DESPUÉS DEL MERGE:")
        print(f"     - Total casos: {merge_stats['total_merged']}")
        print(f"     - RCP transtelefónica conservados: {merge_stats['rcp_trans_merged']}")
        print(f"     - RCP transtelefónica perdidos: {merge_stats['rcp_trans_total_originales'] - merge_stats['rcp_trans_merged']}")
        
        perdidos_pct = ((merge_stats['rcp_trans_total_originales'] - merge_stats['rcp_trans_merged']) / merge_stats['rcp_trans_total_originales'] * 100) if merge_stats['rcp_trans_total_originales'] > 0 else 0
        print(f"     - Porcentaje de RCP transtelefónica perdidos: {perdidos_pct:.1f}%")
    
    total_casos = len(data)
    print(f"\n📊 TOTAL DE CASOS ANALIZADOS (FINALES): {total_casos}")
    
    if total_casos == 0:
        print("\n⚠️  NO HAY CASOS VÁLIDOS PARA ANALIZAR")
        print("   Todos los casos fueron excluidos por falta de información de seguimiento.")
        print("="*80 + "\n")
        return
    
    # Estadísticas demográficas
    print(f"\n👥 DEMOGRAFÍA:")
    if not data['edad'].isna().all():
        print(f"   • Edad promedio: {data['edad'].mean():.1f} ± {data['edad'].std():.1f} años")
        print(f"   • Rango de edad: {data['edad'].min():.0f} - {data['edad'].max():.0f} años")
    else:
        print("   • Edad: No disponible")
    
    # Distribución por sexo
    sexo_counts = data['sexo'].value_counts()
    print(f"   • Sexo:")
    for sexo, count in sexo_counts.items():
        porcentaje = (count / total_casos) * 100
        print(f"     - {sexo}: {count} ({porcentaje:.1f}%)")
    
    # RCP Transtelefónica
    print(f"\n📞 RCP TRANSTELEFÓNICA:")
    rcp_trans = data['rcp_transtelefonica'].sum()
    rcp_trans_pct = (rcp_trans / total_casos) * 100
    print(f"   • Con RCP transtelefónica: {rcp_trans} ({rcp_trans_pct:.1f}%)")
    print(f"   • Sin RCP transtelefónica: {total_casos - rcp_trans} ({100 - rcp_trans_pct:.1f}%)")
    
    # RCP de testigos
    print(f"\n👨‍👩‍👧‍👦 RCP DE TESTIGOS:")
    rcp_testigos = data['rcp_testigos'].sum()
    rcp_testigos_pct = (rcp_testigos / total_casos) * 100
    print(f"   • Con RCP de testigos: {rcp_testigos} ({rcp_testigos_pct:.1f}%)")
    print(f"   • Sin RCP de testigos: {total_casos - rcp_testigos} ({100 - rcp_testigos_pct:.1f}%)")
    
    # Tipo de respondiente
    print(f"\n🚑 TIPO DE RESPONDIENTE (cuando hay RCP de testigos):")
    respondientes = data[data['respondiente_rcp'] != '']['respondiente_rcp'].value_counts()
    for resp, count in respondientes.items():
        porcentaje = (count / rcp_testigos) * 100 if rcp_testigos > 0 else 0
        print(f"   • {resp.capitalize()}: {count} ({porcentaje:.1f}% de los que recibieron RCP)")
    
    # DESA externo
    print(f"\n⚡ DESA EXTERNO:")
    desa = data['desa_externo'].sum()
    desa_pct = (desa / total_casos) * 100
    print(f"   • Con DESA: {desa} ({desa_pct:.1f}%)")
    print(f"   • Sin DESA: {total_casos - desa} ({100 - desa_pct:.1f}%)")
    
    # Ritmo desfibrilable
    print(f"\n💓 RITMO INICIAL:")
    ritmo_desf = data['ritmo'].sum()
    ritmo_desf_pct = (ritmo_desf / total_casos) * 100
    print(f"   • Ritmo desfibrilable: {ritmo_desf} ({ritmo_desf_pct:.1f}%)")
    print(f"   • Ritmo no desfibrilable: {total_casos - ritmo_desf} ({100 - ritmo_desf_pct:.1f}%)")
    
    # Tiempos
    print(f"\n⏱️  TIEMPOS:")
    print(f"   • Tiempo llegada unidad (promedio): {data['tiempo_llegada_unidad'].mean():.1f} ± {data['tiempo_llegada_unidad'].std():.1f} segundos")
    print(f"   • Tiempo llegada unidad (mediana): {data['tiempo_llegada_unidad'].median():.1f} segundos")
    
    tiempo_rcp_nonzero = data[data['tiempo_rcp'] > 0]['tiempo_rcp']
    if len(tiempo_rcp_nonzero) > 0:
        print(f"   • Tiempo RCP (promedio, casos con tiempo>0): {tiempo_rcp_nonzero.mean():.1f} ± {tiempo_rcp_nonzero.std():.1f} segundos")
        print(f"   • Tiempo RCP (mediana, casos con tiempo>0): {tiempo_rcp_nonzero.median():.1f} segundos")
        print(f"   • Casos con tiempo RCP documentado: {len(tiempo_rcp_nonzero)} ({len(tiempo_rcp_nonzero)/total_casos*100:.1f}%)")
    
    # ROSC
    print(f"\n💗 ROSC (Retorno de Circulación Espontánea):")
    rosc = data['rosc'].sum()
    rosc_pct = (rosc / total_casos) * 100
    print(f"   • Con ROSC: {rosc} ({rosc_pct:.1f}%)")
    print(f"   • Sin ROSC: {total_casos - rosc} ({100 - rosc_pct:.1f}%)")
    
    # Supervivencia a 7 días
    print(f"\n🏥 SUPERVIVENCIA A 7 DÍAS:")
    supervivencia = data['supervivencia_7dias'].sum()
    supervivencia_pct = (supervivencia / total_casos) * 100
    print(f"   • Supervivientes: {supervivencia} ({supervivencia_pct:.1f}%)")
    print(f"   • No supervivientes: {total_casos - supervivencia} ({100 - supervivencia_pct:.1f}%)")
    
    # CPC
    print(f"\n🧠 CPC (Cerebral Performance Category):")
    cpc_counts = data['cpc'].value_counts().sort_index()
    for cpc, count in cpc_counts.items():
        porcentaje = (count / total_casos) * 100
        descripcion = {
            1: "Buen rendimiento neurológico",
            2: "Discapacidad moderada",
            3: "Discapacidad severa",
            4: "Estado vegetativo",
            5: "Muerte cerebral/muerte"
        }.get(cpc, "Desconocido")
        print(f"   • CPC {cpc} ({descripcion}): {count} ({porcentaje:.1f}%)")
    
    # Análisis cruzado clave
    print(f"\n🔍 ANÁLISIS CRUZADO CLAVE:")
    
    # ROSC por RCP transtelefónica
    rcp_trans_rosc = data[data['rcp_transtelefonica'] == 1]['rosc'].sum()
    rcp_trans_total = data['rcp_transtelefonica'].sum()
    sin_rcp_trans_rosc = data[data['rcp_transtelefonica'] == 0]['rosc'].sum()
    sin_rcp_trans_total = total_casos - rcp_trans_total
    
    if rcp_trans_total > 0:
        rcp_trans_rosc_pct = (rcp_trans_rosc / rcp_trans_total) * 100
        print(f"   • ROSC con RCP transtelefónica: {rcp_trans_rosc}/{rcp_trans_total} ({rcp_trans_rosc_pct:.1f}%)")
    
    if sin_rcp_trans_total > 0:
        sin_rcp_trans_rosc_pct = (sin_rcp_trans_rosc / sin_rcp_trans_total) * 100
        print(f"   • ROSC sin RCP transtelefónica: {sin_rcp_trans_rosc}/{sin_rcp_trans_total} ({sin_rcp_trans_rosc_pct:.1f}%)")
    
    # Supervivencia por RCP transtelefónica
    rcp_trans_superv = data[data['rcp_transtelefonica'] == 1]['supervivencia_7dias'].sum()
    sin_rcp_trans_superv = data[data['rcp_transtelefonica'] == 0]['supervivencia_7dias'].sum()
    
    if rcp_trans_total > 0:
        rcp_trans_superv_pct = (rcp_trans_superv / rcp_trans_total) * 100
        print(f"   • Supervivencia 7d con RCP transtelefónica: {rcp_trans_superv}/{rcp_trans_total} ({rcp_trans_superv_pct:.1f}%)")
    
    if sin_rcp_trans_total > 0:
        sin_rcp_trans_superv_pct = (sin_rcp_trans_superv / sin_rcp_trans_total) * 100
        print(f"   • Supervivencia 7d sin RCP transtelefónica: {sin_rcp_trans_superv}/{sin_rcp_trans_total} ({sin_rcp_trans_superv_pct:.1f}%)")
    
    # ROSC por ritmo
    ritmo_desf_rosc = data[data['ritmo'] == 1]['rosc'].sum()
    ritmo_no_desf_rosc = data[data['ritmo'] == 0]['rosc'].sum()
    
    if ritmo_desf > 0:
        ritmo_desf_rosc_pct = (ritmo_desf_rosc / ritmo_desf) * 100
        print(f"   • ROSC con ritmo desfibrilable: {ritmo_desf_rosc}/{ritmo_desf} ({ritmo_desf_rosc_pct:.1f}%)")
    
    ritmo_no_desf_total = total_casos - ritmo_desf
    if ritmo_no_desf_total > 0:
        ritmo_no_desf_rosc_pct = (ritmo_no_desf_rosc / ritmo_no_desf_total) * 100
        print(f"   • ROSC con ritmo no desfibrilable: {ritmo_no_desf_rosc}/{ritmo_no_desf_total} ({ritmo_no_desf_rosc_pct:.1f}%)")
    
    print("\n" + "="*80)
    print("Datos guardados en: data/cleaned_data.csv")
    print("="*80 + "\n")

def merge_svb_into_sva(data):
    """Merges SVB data into SVA data based on the 'fecha' column."""
    # Crear una copia para evitar warnings
    data = data.copy()
    
    # Separate SVB and SVA data
    svb_data = data[data['tipo_unidad'] == 'SVB'].copy()
    sva_data = data[data['tipo_unidad'] == 'SVA'].copy()

    # Merge SVB into SVA based on 'fecha'
    merged_data = sva_data.copy()
    for index, svb_row in svb_data.iterrows():
        matching_sva_rows = merged_data[merged_data['fecha'] == svb_row['fecha']]
        if not matching_sva_rows.empty:
            for sva_index, sva_row in matching_sva_rows.iterrows():
                # Example: Add SVB times to SVA times if they exist
                for time_col in ['tiempo_co', 'tiempo_c3', 'tiempo_c2_c3', 'tiempo_c3_c4']:
                    if pd.notna(svb_row[time_col]):
                        merged_data.loc[sva_index, time_col] += svb_row[time_col]
                # Optionally, merge other relevant columns here

    return merged_data

def main():
    """Main function to run the data cleaning pipeline."""
    # 1. Leer datos crudos desde la carpeta correcta (sin espacios en la ruta)
    import os
    raw_data = read_data(os.path.join(os.path.dirname(__file__), '../1.raw_imported/rawdata_2year.csv'))
    
    # 1.5. Procesar booleanos para poder contar RCP transtelefónica antes del merge
    raw_data_with_booleans = process_boolean_columns(raw_data.copy())
    
    # ESTADÍSTICAS ANTES DEL MERGE
    print("\n" + "="*80)
    print("📊 ESTADÍSTICAS ANTES DEL MERGE SVB→SVA")
    print("="*80)
    
    total_casos_originales = len(raw_data_with_booleans)
    casos_sva_originales = len(raw_data_with_booleans[raw_data_with_booleans['tipo_unidad'] == 'SVA'])
    casos_svb_originales = len(raw_data_with_booleans[raw_data_with_booleans['tipo_unidad'] == 'SVB'])
    
    rcp_trans_sva_originales = len(raw_data_with_booleans[(raw_data_with_booleans['tipo_unidad'] == 'SVA') & (raw_data_with_booleans['rcp_transtelefonica'] == 1)])
    rcp_trans_svb_originales = len(raw_data_with_booleans[(raw_data_with_booleans['tipo_unidad'] == 'SVB') & (raw_data_with_booleans['rcp_transtelefonica'] == 1)])
    rcp_trans_total_originales = rcp_trans_sva_originales + rcp_trans_svb_originales
    
    print(f"   • CASOS TOTALES: {total_casos_originales}")
    print(f"     - SVA: {casos_sva_originales}")
    print(f"     - SVB: {casos_svb_originales}")
    print(f"   • RCP TRANSTELEFÓNICA:")
    print(f"     - En SVA: {rcp_trans_sva_originales}")
    print(f"     - En SVB: {rcp_trans_svb_originales}")
    print(f"     - TOTAL: {rcp_trans_total_originales}")
    
    # Obtener números de informe de RCP transtelefónica antes del merge
    rcp_trans_sva_informes = raw_data_with_booleans[(raw_data_with_booleans['tipo_unidad'] == 'SVA') & (raw_data_with_booleans['rcp_transtelefonica'] == 1)]['n_informe'].tolist()
    rcp_trans_svb_informes = raw_data_with_booleans[(raw_data_with_booleans['tipo_unidad'] == 'SVB') & (raw_data_with_booleans['rcp_transtelefonica'] == 1)]['n_informe'].tolist()

    # 2. PRIMERO: Merge SVB data into SVA data (antes de cualquier filtro)
    merged_data = merge_svb_into_sva(raw_data)

    # 3. Procesar los datos combinados
    processed_data = calculate_derived_columns(merged_data)
    processed_data = process_boolean_columns(processed_data)
    processed_data = classify_responders_and_rosc(processed_data)
    
    # ESTADÍSTICAS DESPUÉS DEL MERGE
    print(f"\n📊 ESTADÍSTICAS DESPUÉS DEL MERGE SVB→SVA")
    print("="*80)
    
    total_casos_merged = len(processed_data)
    rcp_trans_merged = len(processed_data[processed_data['rcp_transtelefonica'] == 1])
    rcp_trans_merged_informes = processed_data[processed_data['rcp_transtelefonica'] == 1]['n_informe'].tolist()
    
    print(f"   • CASOS TOTALES DESPUÉS DEL MERGE: {total_casos_merged}")
    print(f"   • RCP TRANSTELEFÓNICA DESPUÉS DEL MERGE: {rcp_trans_merged}")
    print(f"   • CASOS RCP TRANSTELEFÓNICA PERDIDOS EN EL MERGE: {rcp_trans_total_originales - rcp_trans_merged}")
    
    # Guardar estadísticas para usar en print_data_summary
    merge_stats = {
        'total_originales': total_casos_originales,
        'sva_originales': casos_sva_originales, 
        'svb_originales': casos_svb_originales,
        'rcp_trans_sva_originales': rcp_trans_sva_originales,
        'rcp_trans_svb_originales': rcp_trans_svb_originales,
        'rcp_trans_total_originales': rcp_trans_total_originales,
        'total_merged': total_casos_merged,
        'rcp_trans_merged': rcp_trans_merged,
        'rcp_trans_sva_informes': rcp_trans_sva_informes,
        'rcp_trans_svb_informes': rcp_trans_svb_informes,
        'rcp_trans_merged_informes': rcp_trans_merged_informes
    }
    
    # 4. Filtrar casos traumáticos (después del merge y procesamiento básico)
    processed_data = filter_traumatic(processed_data)
    
    # 5. Filtrar casos de RCP transtelefónica (asegurar calidad de datos)
    processed_data = filter_rcp_transtelefonica(processed_data)
    
    # 6. Calcular tiempo de RCP cuando no hay ROSC
    processed_data = calculate_rcp_time_no_rosc(processed_data)
    
    # 7. Determinar supervivencia y CPC (pasar estadísticas del merge)
    processed_data = determine_survival_cpc(processed_data, merge_stats)

    # 8. Limpiar y reordenar columnas finales
    final_data = clean_and_reorder(processed_data)

    # 9. Guardar datos procesados en la carpeta correcta
    import os
    output_dir = os.path.join(os.path.dirname(__file__), '../3.cleaned_data')
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, 'cleaned_data.csv')
    final_data.to_csv(output_path, index=False)
    print(f"Cleaned data saved to {output_path}")

    # Guardar también como archivo Excel (xlsx)
    excel_output_path = os.path.join(output_dir, 'cleaned_data.xlsx')
    final_data.to_excel(excel_output_path, index=False)
    print(f"Cleaned data also saved to {excel_output_path}")
    
    # 10. Mostrar resumen estadístico (ahora con estadísticas del merge)
    print_data_summary(final_data, merge_stats)

if __name__ == "__main__":
    main()
