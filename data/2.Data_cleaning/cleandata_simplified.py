"""
RCP Transtelefonica - Script de Limpieza de Datos (Versión Simplificada)
Este script limpia y procesa datos para el estudio de RCP Transtelefónica.
"""

import pandas as pd
import os
import re
from datetime import datetime, timedelta

def read_data(file_path):
    """Lee los datos CSV brutos y renombra las columnas."""
    data = pd.read_csv(file_path, delimiter=';')
    
    # Column renaming dictionary - all in one place for clarity
    rename_cols = {
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
    }
    
    data.rename(columns=rename_cols, inplace=True)
    return data

def process_data(data):
    """Procesa datos con todas las transformaciones necesarias en un enfoque más simplificado"""
    data = data.copy()
    
    # 1. Process boolean columns
    boolean_columns = ['rcp_transtelefonica', 'desa_externo', 'rcp_testigos']
    for col in boolean_columns:
        data[col] = data[col].apply(lambda x: 1 if str(x).lower() in ['verdadero', 'true', '1'] else 0)
    
    # 2. Calculate time columns
    time_cols = ['tiempo_co', 'tiempo_c3', 'tiempo_c2_c3', 'tiempo_c3_c4']
    for col in time_cols:
        data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0).astype(int)
    
    data['tiempo_llegada_unidad'] = data[['tiempo_co', 'tiempo_c3', 'tiempo_c2_c3']].sum(axis=1)
    data['tiempo_rcp'] = data['tiempo_c3_c4']
    
    # 3. Process age
    data['edad'] = pd.to_numeric(data['edad'], errors='coerce')
    
    # 4. Process rhythm
    desfibrilable_ritmos = ['VF', 'TV', 'FV', 'FIBRILACION', 'TAQUICARDIA VENTRICULAR', 'FIBRILACION VENTRICULAR', 'FIBRILACIÓN']
    data['ritmo'] = data['ritmo'].astype(str).apply(
        lambda x: 1 if any(ritmo in x.upper() for ritmo in desfibrilable_ritmos) else 0
    )
    
    # 5. Responder classification
    data['policia'] = data['consulta'].str.contains(
        'policia|municipal|091|092|062', case=False, na=False
    ).astype(int)
    
    data['bombero'] = data['consulta'].str.contains(
        'bombero|080|beta', case=False, na=False
    ).astype(int)
    
    data['sanitario'] = data['consulta'].str.contains(
        'sanitario|medico|enfermero|tes|061|060|summa|samur|svb|hospital|personal sanitario|personal medico', 
        case=False, na=False
    ).astype(int)
    
    data['legos'] = data['consulta'].str.contains(
        'lego|ciudadano|testigo|persona|alertante|demandante|llamante', case=False, na=False
    ).astype(int)
    
    # Important: Be permissive with telephone CPR
    data.loc[data['rcp_transtelefonica'] == 1, 'legos'] = 1
    data.loc[data['rcp_transtelefonica'] == 1, 'rcp_testigos'] = 1

    # 6. Determine ROSC
    data['rosc'] = data['consulta'].str.contains('rosc|recuperada', case=False, na=False).astype(int)
    data.loc[data['tiempo_c3_c4'] > 0, 'rosc'] = 1
    
    # 7. Classify responder type
    def classify_responder(row):
        if row['rcp_testigos'] == 0:
            return ''
        if row['rcp_transtelefonica'] == 1:
            return 'lego'
        if row['sanitario'] == 1:
            return 'sanitario'
        if row['bombero'] == 1:
            return 'bombero'
        if row['policia'] == 1:
            return 'policia'
        if row['legos'] == 1:
            return 'lego'
        return 'lego'  # Default if there's RCP but no clear responder type

    data['respondiente_rcp'] = data.apply(classify_responder, axis=1)
    
    # 8. Calculate RCP time for cases with no ROSC
    data = calculate_rcp_time(data)
    
    # 9. Determine survival and CPC
    data = determine_survival_cpc(data)
    
    return data

def calculate_rcp_time(data):
    """Calculate RCP time more efficiently"""
    data = data.copy()
    
    cols = ['consulta', 'antecedentes', 'tecnicas', 'evolucion', 'hospital', '6 horas', '24 horas', '7 dias']
    
    # Compile regex patterns for better performance
    time_patterns = [
        re.compile(r'rcp.*?(\d+)\s*min'),
        re.compile(r'(\d+)\s*min.*?rcp'),
        re.compile(r'reanimaci[oó]n.*?(\d+)\s*min'),
        re.compile(r'(\d+)\s*min.*?reanimaci[oó]n'),
        re.compile(r'masaje.*?(\d+)\s*min'),
        re.compile(r'(\d+)\s*min.*?masaje'),
        re.compile(r'maniobras.*?(\d+)\s*min'),
        re.compile(r'(\d+)\s*min.*?maniobras')
    ]
    
    date_pattern = re.compile(r'(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}):(\d{2})')
    
    hora_patterns = [
        re.compile(r'exitus.*?(\d{1,2}):(\d{2})'),
        re.compile(r'fallec.*?(\d{1,2}):(\d{2})'),
        re.compile(r'muerte.*?(\d{1,2}):(\d{2})'),
        re.compile(r'(\d{1,2}):(\d{2}).*?exitus'),
        re.compile(r'(\d{1,2}):(\d{2}).*?fallec')
    ]
    
    def extract_rcp_time(row):
        # Skip if we already have valid time for ROSC cases
        if row.get('rosc', 0) == 1 and row.get('tiempo_rcp', 0) > 0:
            return row.get('tiempo_rcp', 0)
        
        # Look for direct RCP time mentions
        for col in cols:
            if col not in row:
                continue
                
            text = str(row.get(col, '')).lower()
            if pd.isna(text) or text == 'nan' or text == '':
                continue
            
            for pattern in time_patterns:
                match = pattern.search(text)
                if match:
                    try:
                        mins = int(match.group(1))
                        if 0 < mins <= 180:  # Max 3 hours is reasonable
                            return mins * 60  # Convert to seconds
                    except (ValueError, IndexError):
                        continue
            
        # Look for exit time and calculate difference
        try:
            fecha_str = str(row.get('fecha', ''))
            if not fecha_str or fecha_str == 'nan':
                return row.get('tiempo_rcp', 0)
                
            fecha_match = date_pattern.search(fecha_str)
            if not fecha_match:
                return row.get('tiempo_rcp', 0)
                
            fecha_inicio = datetime.strptime(fecha_match.group(0), '%d/%m/%Y %H:%M')
            
            # Add arrival time if no witness CPR
            if row.get('rcp_testigos', 0) == 0:
                tiempo_llegada = row.get('tiempo_llegada_unidad', 0)
                fecha_inicio += timedelta(seconds=tiempo_llegada)
            
            for col in cols:
                if col not in row:
                    continue
                    
                text = str(row.get(col, '')).lower()
                if pd.isna(text) or text == 'nan' or text == '':
                    continue
                
                for pattern in hora_patterns:
                    match = pattern.search(text)
                    if match:
                        try:
                            hora_fin = int(match.group(1))
                            min_fin = int(match.group(2))
                            
                            if hora_fin > 23 or min_fin > 59:
                                continue
                            
                            fecha_fin = fecha_inicio.replace(hour=hora_fin, minute=min_fin)
                            
                            if fecha_fin <= fecha_inicio:
                                fecha_fin += timedelta(days=1)
                            
                            diff = (fecha_fin - fecha_inicio).total_seconds()
                            if 0 < diff <= 10800:  # Between 0 and 3 hours
                                return int(diff)
                        except (ValueError, IndexError):
                            continue
        except:
            pass
        
        return row.get('tiempo_rcp', 0)
    
    data.loc[:, 'tiempo_rcp'] = data.apply(extract_rcp_time, axis=1)
    return data

def determine_survival_cpc(data):
    """Determine survival and CPC according to study criteria"""
    data = data.copy()
    
    cols = ['consulta', 'antecedentes', 'tecnicas', 'evolucion', 'hospital', '6 horas', '24 horas', '7 dias']
    followup_cols = ['6 horas', '24 horas', '7 dias']
    
    # First filter traumatic cases
    traumatic_keywords = [
        'trauma', 'traumatico', 'herida', 'heridas', 'herido', 'heridos',
        'caida', 'caidas', 'accidente', 'precipitado', 'ahogamiento', 
        'suicidio', 'golpe', 'golpes', 'agresion', 'agresión',
        'intoxicacion', 'intoxicación', 'sobredosis', 'electrocucion', 'electrocución',
        'lesion', 'lesiones', 'lesión', 'lesiónes', 'incendio', 'atropello'
    ]
    
    # Be permissive with telephone CPR cases
    non_traumatic = ~data[cols].apply(lambda row: any(t in str(cell).lower() for t in traumatic_keywords for cell in row), axis=1)
    data = data[non_traumatic].copy()
    
    # Helper functions for survival and CPC determination
    def has_followup_info(row):
        # Check follow-up columns
        for col in followup_cols:
            if col not in row:
                continue
                
            text = str(row.get(col, '')).strip().lower()
            if text and text != 'nan' and text != '' and len(text) > 2:
                return True
        
        # Check outcome indicators in other columns
        for col in ['evolucion', 'hospital', 'consulta']:
            if col not in row:
                continue
                
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
        
        # If ROSC is explicitly recorded
        if row.get('rosc', 0) == 1:
            return True
            
        # If pathological code indicates outcome
        codigo_patologico = str(row.get('consulta', '')).lower()
        if any(pattern in codigo_patologico for pattern in ['c.0.0', 'w.0.1', 'recuperada', 'exitus']):
            return True
        
        return False
    
    def get_supervivencia(row):
        # Apply specific criteria: if no follow-up info, assume survival = 0
        if not has_followup_info(row):
            return 0
        
        # If no ROSC, survival = 0
        if row.get('rosc', 0) == 0:
            return 0
        
        # Check for death indicators
        muerte_keywords = [
            'exitus', 'fallecido', 'fallece', 'fallecimiento', 'muerte', 'muere', 
            'óbito', 'obito', 'defunción', 'defuncion', 'deceased', 'died',
            'muerte cerebral', 'cese maniobras', 'suspender', 'confirma fallecimiento'
        ]
        
        for col in followup_cols + ['evolucion', 'hospital', 'consulta']:
            if col not in row:
                continue
                
            text = str(row.get(col, '')).lower()
            if any(keyword in text for keyword in muerte_keywords):
                return 0
        
        # Check pathological code
        if 'w.0.1' in str(row.get('consulta', '')).lower() or 'exitus' in str(row.get('consulta', '')).lower():
            return 0
        
        # Check for survival indicators
        supervivencia_keywords = [
            'alta', 'domicilio', 'recupera', 'recuperado', 'recuperada', 
            'vive', 'sobrevive', 'consciente', 'despertar', 'despierta',
            'estable', 'uci', 'planta', 'ingreso', 'hospitaliza',
            'sin incidencias', 'traslado hospital'
        ]
        
        for col in followup_cols + ['evolucion', 'hospital']:
            if col not in row:
                continue
                
            text = str(row.get(col, '')).lower()
            if any(keyword in text for keyword in supervivencia_keywords):
                return 1
        
        # Default: if ROSC but ambiguous follow-up, be conservative
        return 0
    
    def get_cpc(row):
        # If no ROSC, automatically CPC 5
        if row.get('rosc', 0) == 0:
            return 5
            
        # If no follow-up info, assume CPC = 5
        if not has_followup_info(row):
            return 5
        
        # Look for explicit CPC
        cpc_pattern = re.compile(r'cpc\s*(?:de|:)?\s*([1-5])')
        
        for col in cols:
            if col not in row:
                continue
                
            text = str(row.get(col, '')).lower()
            if pd.isna(text) or text == 'nan' or text == '':
                continue
                
            match = cpc_pattern.search(text)
            if match:
                try:
                    cpc_val = int(match.group(1))
                    if 1 <= cpc_val <= 5:
                        return cpc_val
                except (ValueError, IndexError):
                    continue
        
        # If no survival at 7 days, CPC = 5
        if get_supervivencia(row) == 0:
            return 5
        
        # If survival but no explicit CPC, assume CPC 5
        return 5
    
    # Apply functions
    data.loc[:, 'supervivencia_7dias'] = data.apply(get_supervivencia, axis=1)
    data.loc[:, 'cpc'] = data.apply(get_cpc, axis=1)
    
    # Ensure consistency: if CPC = 5, survival = 0
    data.loc[data['cpc'] == 5, 'supervivencia_7dias'] = 0
    
    return data

def merge_svb_sva_data(raw_data):
    """Unir datos SVB con SVA basado en fecha/hora para preservar casos de RCP transtelefónica"""
    # Procesar columnas booleanas para conteos precisos
    data = process_boolean_columns(raw_data.copy())
    
    # Obtener estadísticas antes de la unión
    total_casos = len(data)
    casos_sva = sum(data['tipo_unidad'] == 'SVA')
    casos_svb = sum(data['tipo_unidad'] == 'SVB')
    rcp_trans_sva = sum((data['tipo_unidad'] == 'SVA') & (data['rcp_transtelefonica'] == 1))
    rcp_trans_svb = sum((data['tipo_unidad'] == 'SVB') & (data['rcp_transtelefonica'] == 1))
    
    print(f"\n📊 Antes de la unión: {total_casos} casos totales")
    print(f"   • SVA: {casos_sva} ({rcp_trans_sva} con RCP transtelefónica)")
    print(f"   • SVB: {casos_svb} ({rcp_trans_svb} con RCP transtelefónica)")
    
    # Crear conjunto de datos unidos, empezando con SVA
    sva_data = data[data['tipo_unidad'] == 'SVA'].copy()
    svb_data = data[data['tipo_unidad'] == 'SVB'].copy()
    
    # Encontrar informes coincidentes (para el mismo incidente)
    # Extraer fecha y estandarizar formato para coincidencia
    svb_data['match_date'] = svb_data['fecha'].str.extract(r'(\d{2}/\d{2}/\d{4})').iloc[:, 0]
    sva_data['match_date'] = sva_data['fecha'].str.extract(r'(\d{2}/\d{2}/\d{4})').iloc[:, 0]
    
    # Extraer hora
    svb_data['match_time'] = svb_data['fecha'].str.extract(r'(\d{2}:\d{2})').iloc[:, 0]
    sva_data['match_time'] = sva_data['fecha'].str.extract(r'(\d{2}:\d{2})').iloc[:, 0]
    
    # Registrar todos los casos coincidentes entre SVB y SVA
    matched_svb_indices = []
    matched_sva_updated = []
    
    # Primero, revisar todos los casos SVB y buscar coincidencias en SVA
    for svb_idx, svb_row in svb_data.iterrows():
        # Encontrar casos SVA coincidentes (misma fecha y hora)
        matching_sva = sva_data[
            (sva_data['match_date'] == svb_row['match_date']) & 
            (sva_data['match_time'] == svb_row['match_time'])
        ]
        
        if not matching_sva.empty:
            # Registrar este SVB como coincidente
            matched_svb_indices.append(svb_idx)
            
            # Para cada caso SVA coincidente
            for sva_idx in matching_sva.index:
                # REGLA CRÍTICA: Si cualquiera de los dos tiene RCP transtelefónica=1, el resultado es 1
                if svb_row['rcp_transtelefonica'] == 1:
                    sva_data.loc[sva_idx, 'rcp_transtelefonica'] = 1
                    sva_data.loc[sva_idx, 'rcp_testigos'] = 1
                    matched_sva_updated.append(sva_idx)
    
    # Identificar los casos de SVB con RCP transtelefónica que no tienen coincidencia en SVA
    unmatched_svb_tele = svb_data[
        (svb_data['rcp_transtelefonica'] == 1) & 
        (~svb_data.index.isin(matched_svb_indices))
    ]
    
    # Contar los casos de RCP transtelefónica conservados y perdidos
    preserved_tele_cpr = sum(sva_data['rcp_transtelefonica'] == 1)
    added_from_svb = len(matched_sva_updated)
    lost_svb_tele = len(unmatched_svb_tele)
    
    # Casos perdidos: SVB con RCP transtelefónica sin coincidencia en SVA
    lost_cases_ids = unmatched_svb_tele['n_informe'].tolist() if 'n_informe' in unmatched_svb_tele.columns else []
    
    print(f"   • Después de la unión: {len(sva_data)} casos")
    print(f"   • Casos de RCP transtelefónica: {preserved_tele_cpr} (originales SVA: {rcp_trans_sva}, actualizados desde SVB: {added_from_svb})")
    print(f"   • SVB con RCP transtelefónica sin coincidencia en SVA: {lost_svb_tele} casos")
    
    if lost_cases_ids:
        print(f"   • IDs de casos SVB con RCP transtelefónica perdidos: {', '.join(map(str, lost_cases_ids))}")
    
    # Limpiar columnas temporales
    if 'match_date' in sva_data.columns:
        sva_data.drop(['match_date', 'match_time'], axis=1, inplace=True)
    
    return sva_data

def process_boolean_columns(data):
    """Simple function to process boolean columns"""
    data = data.copy()
    boolean_columns = ['rcp_transtelefonica', 'desa_externo', 'rcp_testigos']
    for col in boolean_columns:
        data[col] = data[col].apply(lambda x: 1 if str(x).lower() in ['verdadero', 'true', '1'] else 0)
    data[boolean_columns] = data[boolean_columns].astype(int)
    return data

def clean_and_reorder(data):
    """Clean and reorder columns for the final dataset"""
    # Define final columns in desired order
    final_columns = [
        'n_informe', 'fecha', 'edad', 'sexo', 'rcp_transtelefonica', 
        'rcp_testigos', 'respondiente_rcp', 'desa_externo', 'ritmo', 
        'tiempo_llegada_unidad', 'tiempo_rcp', 'rosc', 'supervivencia_7dias', 'cpc'
    ]
    
    # Select only columns we need
    cleaned_data = data[final_columns].copy()
    
    # Convert numeric columns properly
    numeric_cols = ['rcp_transtelefonica', 'rcp_testigos', 'desa_externo', 'ritmo', 
                   'tiempo_llegada_unidad', 'tiempo_rcp', 'rosc', 'supervivencia_7dias', 'cpc']
    
    for col in numeric_cols:
        if col in cleaned_data.columns:
            cleaned_data[col] = pd.to_numeric(cleaned_data[col], errors='coerce')
    
    return cleaned_data

def generate_summary_statistics(data):
    """Generar estadísticas resumidas de los datos limpiados"""
    print("\n" + "="*80)
    print("RESUMEN ESTADÍSTICO - ANÁLISIS RCP TRANSTELEFÓNICA")
    print("="*80)
    
    total_casos = len(data)
    print(f"\n📊 TOTAL DE CASOS ANALIZADOS: {total_casos}")
    
    # RCP Transtelefónica
    rcp_trans = data['rcp_transtelefonica'].sum()
    rcp_trans_pct = (rcp_trans / total_casos) * 100
    print(f"\n📞 RCP TRANSTELEFÓNICA:")
    print(f"   • Con RCP transtelefónica: {rcp_trans} ({rcp_trans_pct:.1f}%)")
    print(f"   • Sin RCP transtelefónica: {total_casos - rcp_trans} ({100 - rcp_trans_pct:.1f}%)")
    
    # ROSC por tipo de RCP
    print(f"\n💗 ROSC (Retorno de Circulación Espontánea) por tipo de RCP:")
    
    # Con RCP transtelefónica
    rcp_trans_rosc = data[data['rcp_transtelefonica'] == 1]['rosc'].sum()
    rcp_trans_total = data['rcp_transtelefonica'].sum()
    if rcp_trans_total > 0:
        rcp_trans_rosc_pct = (rcp_trans_rosc / rcp_trans_total) * 100
        print(f"   • ROSC con RCP transtelefónica: {rcp_trans_rosc}/{rcp_trans_total} ({rcp_trans_rosc_pct:.1f}%)")
    
    # Sin RCP transtelefónica
    sin_rcp_trans_rosc = data[data['rcp_transtelefonica'] == 0]['rosc'].sum()
    sin_rcp_trans_total = total_casos - rcp_trans_total
    if sin_rcp_trans_total > 0:
        sin_rcp_trans_rosc_pct = (sin_rcp_trans_rosc / sin_rcp_trans_total) * 100
        print(f"   • ROSC sin RCP transtelefónica: {sin_rcp_trans_rosc}/{sin_rcp_trans_total} ({sin_rcp_trans_rosc_pct:.1f}%)")
    
    # Supervivencia por tipo de RCP
    print(f"\n🏥 Supervivencia por tipo de RCP:")
    
    # Con RCP transtelefónica
    rcp_trans_superv = data[data['rcp_transtelefonica'] == 1]['supervivencia_7dias'].sum()
    if rcp_trans_total > 0:
        rcp_trans_superv_pct = (rcp_trans_superv / rcp_trans_total) * 100
        print(f"   • Supervivencia a 7 días con RCP transtelefónica: {rcp_trans_superv}/{rcp_trans_total} ({rcp_trans_superv_pct:.1f}%)")
    
    # Sin RCP transtelefónica
    sin_rcp_trans_superv = data[data['rcp_transtelefonica'] == 0]['supervivencia_7dias'].sum()
    if sin_rcp_trans_total > 0:
        sin_rcp_trans_superv_pct = (sin_rcp_trans_superv / sin_rcp_trans_total) * 100
        print(f"   • Supervivencia a 7 días sin RCP transtelefónica: {sin_rcp_trans_superv}/{sin_rcp_trans_total} ({sin_rcp_trans_superv_pct:.1f}%)")
    
    print("\n" + "="*80)

def main():
    """Función principal para ejecutar el pipeline de limpieza de datos."""
    # Definir rutas de archivos
    script_dir = os.path.dirname(os.path.abspath(__file__))
    raw_data_path = os.path.join(script_dir, '../1.raw_imported/rawdata_2year.csv')
    output_dir = os.path.join(script_dir, '../3.cleaned_data')
    os.makedirs(output_dir, exist_ok=True)
    
    print("🔍 Leyendo datos brutos...")
    raw_data = read_data(raw_data_path)
    
    print("🔄 Uniendo datos SVB y SVA para preservar casos de RCP transtelefónica...")
    merged_data = merge_svb_sva_data(raw_data)
    
    print("🧹 Procesando y limpiando datos...")
    processed_data = process_data(merged_data)
    
    print("📋 Limpiando y reordenando columnas...")
    final_data = clean_and_reorder(processed_data)
    
    # Guardar los datos limpios
    output_csv = os.path.join(output_dir, 'cleaned_data.csv')
    output_excel = os.path.join(output_dir, 'cleaned_data.xlsx')
    
    final_data.to_csv(output_csv, index=False)
    final_data.to_excel(output_excel, index=False)
    
    print(f"✅ Datos limpios guardados en {output_csv} y {output_excel}")
    
    # Generar estadísticas resumidas
    generate_summary_statistics(final_data)

if __name__ == "__main__":
    main()
