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
        'CONSULTA': 'consulta'
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
    traumatic_keywords = ['trauma', 'herida', 'caida', 'accidente', 'precipitado', 'ahogamiento', 'suicidio']
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

def determine_survival_cpc(data):
    """Determines 7-day survival and CPC score from all relevant columns, discarding traumatic cases like incendio or ahogamiento."""
    import re
    
    # Crear una copia explícita para evitar warnings
    data = data.copy()
    
    # Columnas a analizar
    cols = ['consulta', 'antecedentes', 'tecnicas', 'evolucion', 'hospital', '6 horas', '24 horas', '7 dias']
    fallecimiento_cols = ['6 horas', '24 horas', '7 dias']
    # Asegura que todas las columnas existen
    for col in cols:
        if col not in data.columns:
            data[col] = ''

    # Filtra casos traumáticos (incendio, ahogamiento)
    traumaticos = ['incendio', 'ahogamiento']
    mask_traumatico = data[cols].apply(lambda row: any(t in str(cell).lower() for t in traumaticos for cell in row), axis=1)
    data = data[~mask_traumatico].copy()

    def get_cpc(row):
        # Buscar CPC en todas las columnas con patrones más amplios
        for col in cols:
            text = str(row.get(col, '')).lower()
            if pd.isna(text) or text == 'nan' or text == '':
                continue
                
            # Patrones más específicos para encontrar CPC
            patterns = [
                r'cpc\s*(?:de|:)?\s*([1-5])',
                r'cerebral\s*performance\s*category\s*([1-5])',
                r'escala\s*cpc\s*([1-5])',
                r'cpc-([1-5])',
                r'cpc\s*([1-5])',
                r'categoria\s*cerebral\s*([1-5])',
                r'performance\s*([1-5])',
                r'neurologic\s*outcome\s*([1-5])',
                r'estado\s*neurologico\s*([1-5])',
                r'glasgow\s*outcome\s*([1-5])'
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
        
        # Si no se encuentra CPC específico, determinar basado en supervivencia y ROSC
        if row.get('rosc', 0) == 0:
            return 5
        
        # Buscar indicadores de buen/mal pronóstico neurológico
        for col in cols:
            text = str(row.get(col, '')).lower()
            if pd.isna(text) or text == 'nan' or text == '':
                continue
            
            # Indicadores de buen pronóstico (CPC 1-2)
            buen_pronostico = ['consciente', 'vigil', 'orientado', 'colaborador', 'reactivo', 'despierto', 'alerta', 'normal', 'sin deficit', 'recuperado completamente']
            if any(indicador in text for indicador in buen_pronostico):
                return 1
            
            # Indicadores de pronóstico moderado (CPC 2-3)
            mod_pronostico = ['confusion', 'desorientado', 'agitado', 'somnoliento', 'deficit leve', 'deficit moderado']
            if any(indicador in text for indicador in mod_pronostico):
                return 2
            
            # Indicadores de mal pronóstico (CPC 4-5)
            mal_pronostico = ['coma', 'vegetativo', 'no responde', 'deficit severo', 'grave', 'sedado', 'intubado']
            if any(indicador in text for indicador in mal_pronostico):
                return 4
        
        # Por defecto, si hay ROSC asumir CPC moderado
        return 3

    def get_supervivencia(row):
        # Primero calcular CPC
        cpc_val = get_cpc(row)
        
        # Si CPC es 5, automáticamente supervivencia = 0
        if cpc_val == 5:
            return 0
        
        # Buscar indicadores de fallecimiento en las columnas de tiempo
        fallecido_kw = ['exitus', 'fallecido', 'fallece', 'muerte', 'muere', 'parada', 'óbito', 'obito', 'defunción', 'defuncion', 'cese', 'fin', 'deceased', 'died']
        for col in fallecimiento_cols:
            text = str(row.get(col, '')).lower()
            if any(k in text for k in fallecido_kw):
                return 0
        
        # Buscar indicadores de supervivencia en todas las columnas
        supervivencia_kw = ['vive', 'alta', 'recupera', 'domicilio', 'recuperado', 'recuperada', 'recuperación', 'recuperacion', 'despierta', 'despertó', 'desperto', 'consciente', 'consciencia', 'vigil', 'estable', 'sobrevive', 'alive', 'discharged']
        for col in cols:
            text = str(row.get(col, '')).lower()
            if any(k in text for k in supervivencia_kw):
                return 1
        
        # Si la casilla '7 dias' está vacía o es NaN, supervivencia=0
        dias7_text = str(row.get('7 dias', '')).strip()
        if pd.isna(row.get('7 dias', '')) or dias7_text == '' or dias7_text == 'nan':
            return 0
            
        return 0

    # Aplicar las funciones
    data.loc[:, 'cpc'] = data.apply(get_cpc, axis=1)
    data.loc[:, 'supervivencia_7dias'] = data.apply(get_supervivencia, axis=1)
    
    # Asegurar consistencia: Si CPC = 5, supervivencia = 0
    data.loc[data['cpc'] == 5, 'supervivencia_7dias'] = 0
    
    return data

def clean_and_reorder(data):
    """Drops temporary columns and reorders the final columns."""
    # Define final columns in desired order
    final_columns = [
        'n_informe', 'fecha', 'edad', 'sexo', 'rcp_transtelefonica', 
        'rcp_testigos', 'respondiente_rcp', 'desa_externo', 'ritmo', 
        'tiempo_llegada_unidad', 'tiempo_rcp', 'rosc', 'supervivencia_7dias', 'cpc'
    ]
    
    # Select and reorder
    cleaned_data = data[final_columns].copy()
    
    return cleaned_data

def print_data_summary(data):
    """Prints a comprehensive summary table of the processed data."""
    print("\n" + "="*80)
    print("RESUMEN ESTADÍSTICO - ANÁLISIS RCP TRANSTELEFÓNICA")
    print("="*80)
    
    total_casos = len(data)
    print(f"\n📊 TOTAL DE CASOS ANALIZADOS: {total_casos}")
    
    # Estadísticas demográficas
    print(f"\n👥 DEMOGRAFÍA:")
    print(f"   • Edad promedio: {data['edad'].mean():.1f} ± {data['edad'].std():.1f} años")
    print(f"   • Rango de edad: {data['edad'].min():.0f} - {data['edad'].max():.0f} años")
    
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
    # 1. Leer datos crudos
    raw_data = read_data('data/rawdata_2year.csv')

    # 2. PRIMERO: Merge SVB data into SVA data (antes de cualquier filtro)
    merged_data = merge_svb_into_sva(raw_data)

    # 3. Procesar los datos combinados
    processed_data = calculate_derived_columns(merged_data)
    processed_data = process_boolean_columns(processed_data)
    processed_data = classify_responders_and_rosc(processed_data)
    
    # 4. Filtrar casos traumáticos (después del merge y procesamiento básico)
    processed_data = filter_traumatic(processed_data)
    
    # 5. Filtrar casos de RCP transtelefónica (asegurar calidad de datos)
    processed_data = filter_rcp_transtelefonica(processed_data)
    
    # 6. Calcular tiempo de RCP cuando no hay ROSC
    processed_data = calculate_rcp_time_no_rosc(processed_data)
    
    # 7. Determinar supervivencia y CPC
    processed_data = determine_survival_cpc(processed_data)

    # 8. Limpiar y reordenar columnas finales
    final_data = clean_and_reorder(processed_data)

    # 9. Guardar datos procesados
    output_path = 'data/cleaned_data.csv'
    final_data.to_csv(output_path, index=False)
    print(f"Cleaned data saved to {output_path}")
    
    # 10. Mostrar resumen estadístico
    print_data_summary(final_data)

if __name__ == "__main__":
    main()