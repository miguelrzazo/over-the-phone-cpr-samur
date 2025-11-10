#!/usr/bin/env python3
"""
Script complementario para análisis detallado de datos RCP Transtelefónica
Genera estadísticas descriptivas completas y análisis por grupos
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

def load_processed_data():
    """Cargar los datos ya procesados"""
    
    print("="*70)
    print("ANÁLISIS DESCRIPTIVO DETALLADO - RCP TRANSTELEFÓNICA")
    print("="*70)
    print(f"Fecha de análisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Cargar datos procesados
    df_valid = pd.read_csv("datos_con_cpc_valido.csv")
    df_excluded = pd.read_csv("datos_excluidos.csv")
    
    print(f"Datos válidos cargados: {len(df_valid):,} registros")
    print(f"Datos excluidos cargados: {len(df_excluded):,} registros")
    
    return df_valid, df_excluded

def detailed_exclusion_analysis(df_excluded):
    """Análisis detallado de exclusiones"""
    
    print("\n" + "="*70)
    print("ANÁLISIS DETALLADO DE EXCLUSIONES")
    print("="*70)
    
    total_excluded = len(df_excluded)
    
    # Análisis por motivo de exclusión
    exclusion_reasons = df_excluded['Excluido'].value_counts()
    
    print("Motivos de exclusión:")
    print("-" * 40)
    for reason, count in exclusion_reasons.items():
        percentage = count / total_excluded * 100
        print(f"{reason:15s}: {count:4d} casos ({percentage:5.1f}%)")
    
    print(f"\nTotal excluidos: {total_excluded:,} casos")
    
    # Características de los excluidos
    print("\nCaracterísticas de casos excluidos:")
    print("-" * 40)
    
    if 'EDAD' in df_excluded.columns:
        edades_excluidos = df_excluded['EDAD'].dropna()
        if len(edades_excluidos) > 0:
            print(f"Edad promedio: {edades_excluidos.mean():.1f} años")
            print(f"Rango de edad: {edades_excluidos.min():.0f} - {edades_excluidos.max():.0f} años")
    
    if 'SEXO' in df_excluded.columns:
        sexo_excluidos = df_excluded['SEXO'].value_counts(dropna=False)
        print("Distribución por sexo:")
        for sexo, count in sexo_excluidos.items():
            pct = count / len(df_excluded) * 100
            print(f"  {sexo}: {count} ({pct:.1f}%)")

def detailed_valid_analysis(df_valid):
    """Análisis detallado de datos válidos"""
    
    print("\n" + "="*70)
    print("ANÁLISIS DETALLADO DE DATOS VÁLIDOS")
    print("="*70)
    
    total_valid = len(df_valid)
    print(f"Total de casos válidos para análisis: {total_valid:,}")
    
    # === ANÁLISIS POR GRUPOS DE RCP ===
    print("\n" + "="*50)
    print("ANÁLISIS POR GRUPOS DE RCP")
    print("="*50)
    
    # Crear categorías de RCP más claras
    def categorize_rcp(row):
        if row['RCP_TRANSTELEFONICA'] == 1:
            return 'RCP Transtelefónica'
        elif row['RCP_TESTIGOS'] == 'falso':
            return 'Sin RCP previa'
        elif row['RCP_TESTIGOS'] in ['lego', 'verdadero']:
            return 'RCP por testigos legos'
        elif row['RCP_TESTIGOS'] in ['sanitario', 'policia', 'bombero']:
            return 'RCP por primeros respondientes'
        else:
            return 'Otros'
    
    df_valid['Grupo_RCP'] = df_valid.apply(categorize_rcp, axis=1)
    
    grupos_rcp = df_valid['Grupo_RCP'].value_counts()
    print("Distribución por grupos de RCP:")
    print("-" * 40)
    for grupo, count in grupos_rcp.items():
        percentage = count / total_valid * 100
        print(f"{grupo:30s}: {count:4d} casos ({percentage:5.1f}%)")
    
    # === ANÁLISIS DE OUTCOMES PRINCIPALES ===
    print("\n" + "="*50)
    print("OUTCOMES PRINCIPALES POR GRUPO DE RCP")
    print("="*50)
    
    outcomes = ['ROSC', 'Supervivencia_7dias']
    
    for outcome in outcomes:
        if outcome in df_valid.columns:
            print(f"\n{outcome}:")
            print("-" * 30)
            outcome_by_group = df_valid.groupby('Grupo_RCP')[outcome].agg(['sum', 'count', 'mean'])
            outcome_by_group['percentage'] = outcome_by_group['mean'] * 100
            
            for grupo in outcome_by_group.index:
                positivos = int(outcome_by_group.loc[grupo, 'sum'])
                total = int(outcome_by_group.loc[grupo, 'count'])
                pct = outcome_by_group.loc[grupo, 'percentage']
                print(f"{grupo:30s}: {positivos:3d}/{total:3d} ({pct:5.1f}%)")
    
    # === ANÁLISIS DE CPC FAVORABLE ===
    print(f"\nCPC Favorable (1-2):")
    print("-" * 30)
    
    # Convertir CPC a favorable/no favorable
    def is_favorable_cpc(cpc_value):
        try:
            if pd.isna(cpc_value):
                return 0
            cpc = int(cpc_value)
            return 1 if cpc in [1, 2] else 0
        except (ValueError, TypeError):
            return 0
    
    df_valid['CPC_favorable_binary'] = df_valid['CPC'].apply(is_favorable_cpc)
    
    cpc_by_group = df_valid.groupby('Grupo_RCP')['CPC_favorable_binary'].agg(['sum', 'count', 'mean'])
    cpc_by_group['percentage'] = cpc_by_group['mean'] * 100
    
    for grupo in cpc_by_group.index:
        favorables = int(cpc_by_group.loc[grupo, 'sum'])
        total = int(cpc_by_group.loc[grupo, 'count'])
        pct = cpc_by_group.loc[grupo, 'percentage']
        print(f"{grupo:30s}: {favorables:3d}/{total:3d} ({pct:5.1f}%)")
    
    # === ESTRATIFICACIÓN POR EDAD ===
    print("\n" + "="*50)
    print("ESTRATIFICACIÓN POR EDAD")
    print("="*50)
    
    if 'EDAD' in df_valid.columns:
        # Crear grupos de edad
        df_valid['Grupo_edad'] = df_valid['EDAD'].apply(lambda x: '<65 años' if x < 65 else '≥65 años')
        
        edad_distribution = df_valid['Grupo_edad'].value_counts()
        print("Distribución por grupo de edad:")
        print("-" * 40)
        for grupo, count in edad_distribution.items():
            percentage = count / total_valid * 100
            print(f"{grupo:15s}: {count:4d} casos ({percentage:5.1f}%)")
        
        # Outcomes por edad
        print("\nOutcomes por grupo de edad:")
        print("-" * 40)
        
        for outcome in ['ROSC', 'Supervivencia_7dias', 'CPC_favorable_binary']:
            if outcome in df_valid.columns:
                print(f"\n{outcome}:")
                outcome_by_age = df_valid.groupby('Grupo_edad')[outcome].agg(['sum', 'count', 'mean'])
                outcome_by_age['percentage'] = outcome_by_age['mean'] * 100
                
                for grupo in outcome_by_age.index:
                    positivos = int(outcome_by_age.loc[grupo, 'sum'])
                    total = int(outcome_by_age.loc[grupo, 'count'])
                    pct = outcome_by_age.loc[grupo, 'percentage']
                    print(f"  {grupo:15s}: {positivos:3d}/{total:3d} ({pct:5.1f}%)")
    
    # === TIEMPOS DE RESPUESTA ===
    print("\n" + "="*50)
    print("ANÁLISIS DE TIEMPOS")
    print("="*50)
    
    if 'Tiempo_llegada' in df_valid.columns:
        tiempo_llegada = df_valid['Tiempo_llegada'].dropna()
        if len(tiempo_llegada) > 0:
            print("Tiempo de llegada (segundos):")
            print(f"  Media: {tiempo_llegada.mean():.0f}s ({tiempo_llegada.mean()/60:.1f} min)")
            print(f"  Mediana: {tiempo_llegada.median():.0f}s ({tiempo_llegada.median()/60:.1f} min)")
            print(f"  Rango: {tiempo_llegada.min():.0f}s - {tiempo_llegada.max():.0f}s")
            print(f"  Casos con datos: {len(tiempo_llegada):,}/{total_valid:,}")
    
    if 'Tiempo_Rcp' in df_valid.columns:
        tiempo_rcp = df_valid['Tiempo_Rcp'].dropna()
        tiempo_rcp = tiempo_rcp[tiempo_rcp > 0]  # Excluir valores 0
        if len(tiempo_rcp) > 0:
            print("\nTiempo de RCP (segundos, excluyendo 0s):")
            print(f"  Media: {tiempo_rcp.mean():.0f}s ({tiempo_rcp.mean()/60:.1f} min)")
            print(f"  Mediana: {tiempo_rcp.median():.0f}s ({tiempo_rcp.median()/60:.1f} min)")
            print(f"  Rango: {tiempo_rcp.min():.0f}s - {tiempo_rcp.max():.0f}s")
            print(f"  Casos con datos: {len(tiempo_rcp):,}/{total_valid:,}")
    
    return df_valid

def create_summary_table(df_valid, df_excluded):
    """Crear tabla resumen para LaTeX"""
    
    print("\n" + "="*70)
    print("GENERANDO TABLA RESUMEN")
    print("="*70)
    
    total_original = len(df_valid) + len(df_excluded)
    
    # Crear datos para tabla resumen
    summary_data = {
        'Variable': [
            'Total registros originales',
            'Registros excluidos',
            '  - TRAUMA',
            '  - SVB',
            '  - CADAVER',
            '  - Otros motivos',
            'Registros válidos para análisis',
            '',
            'CARACTERÍSTICAS POBLACIÓN VÁLIDA',
            'Edad, media ± DE (años)',
            'Sexo masculino',
            'RCP Transtelefónica',
            'RCP por testigos legos',
            'RCP por primeros respondientes',
            'Sin RCP previa',
            '',
            'OUTCOMES PRINCIPALES',
            'ROSC',
            'Supervivencia a 7 días',
            'CPC favorable (1-2)',
            'CPC 1 (función cerebral normal)',
            'CPC 2 (discapacidad leve)',
            'CPC 3 (discapacidad moderada)',
            'CPC 4 (discapacidad severa)',  
            'CPC 5 (estado vegetativo/muerte)',
        ],
        'n (%)': []
    }
    
    # Llenar los valores
    values = [
        f"{total_original:,}",
        f"{len(df_excluded):,} ({len(df_excluded)/total_original*100:.1f}%)",
    ]
    
    # Motivos de exclusión
    exclusion_counts = df_excluded['Excluido'].value_counts()
    trauma_count = exclusion_counts.get('TRAUMA', 0) + exclusion_counts.get('trauma', 0)
    svb_count = exclusion_counts.get('SVB', 0)
    cadaver_count = exclusion_counts.get('CADAVER', 0)
    otros_count = len(df_excluded) - trauma_count - svb_count - cadaver_count
    
    values.extend([
        f"{trauma_count:,} ({trauma_count/total_original*100:.1f}%)",
        f"{svb_count:,} ({svb_count/total_original*100:.1f}%)",
        f"{cadaver_count:,} ({cadaver_count/total_original*100:.1f}%)",
        f"{otros_count:,} ({otros_count/total_original*100:.1f}%)",
        f"{len(df_valid):,} ({len(df_valid)/total_original*100:.1f}%)",
        "",
        "",
    ])
    
    # Características población
    edad_mean = df_valid['EDAD'].mean()
    edad_std = df_valid['EDAD'].std()
    masculino_count = (df_valid['SEXO'] == 'Masculino').sum()
    
    values.extend([
        f"{edad_mean:.1f} ± {edad_std:.1f}",
        f"{masculino_count:,} ({masculino_count/len(df_valid)*100:.1f}%)",
    ])
    
    # Grupos RCP
    grupos_rcp = df_valid['Grupo_RCP'].value_counts()
    rcp_trans = grupos_rcp.get('RCP Transtelefónica', 0)
    rcp_legos = grupos_rcp.get('RCP por testigos legos', 0)
    rcp_primeros = grupos_rcp.get('RCP por primeros respondientes', 0)
    sin_rcp = grupos_rcp.get('Sin RCP previa', 0)
    
    values.extend([
        f"{rcp_trans:,} ({rcp_trans/len(df_valid)*100:.1f}%)",
        f"{rcp_legos:,} ({rcp_legos/len(df_valid)*100:.1f}%)",
        f"{rcp_primeros:,} ({rcp_primeros/len(df_valid)*100:.1f}%)",
        f"{sin_rcp:,} ({sin_rcp/len(df_valid)*100:.1f}%)",
        "",
        "",
    ])
    
    # Outcomes
    rosc_count = (df_valid['ROSC'] == 1).sum()
    supervivencia_count = (df_valid['Supervivencia_7dias'] == 1).sum()
    cpc_favorable_count = (df_valid['CPC_favorable_binary'] == 1).sum()
    
    # CPC por categorías
    cpc_counts = df_valid['CPC'].value_counts().sort_index()
    cpc_1 = cpc_counts.get(1.0, 0)
    cpc_2 = cpc_counts.get(2.0, 0)
    cpc_3 = cpc_counts.get(3.0, 0)
    cpc_4 = cpc_counts.get(4.0, 0)
    cpc_5 = cpc_counts.get(5.0, 0)
    
    values.extend([
        f"{rosc_count:,} ({rosc_count/len(df_valid)*100:.1f}%)",
        f"{supervivencia_count:,} ({supervivencia_count/len(df_valid)*100:.1f}%)",
        f"{cpc_favorable_count:,} ({cpc_favorable_count/len(df_valid)*100:.1f}%)",
        f"{cpc_1:,} ({cpc_1/len(df_valid)*100:.1f}%)",
        f"{cpc_2:,} ({cpc_2/len(df_valid)*100:.1f}%)",
        f"{cpc_3:,} ({cpc_3/len(df_valid)*100:.1f}%)",
        f"{cpc_4:,} ({cpc_4/len(df_valid)*100:.1f}%)",
        f"{cpc_5:,} ({cpc_5/len(df_valid)*100:.1f}%)",
    ])
    
    summary_data['n (%)'] = values
    
    # Crear DataFrame y guardar
    summary_df = pd.DataFrame(summary_data)
    
    # Guardar como CSV
    summary_df.to_csv("tabla_resumen_caracteristicas.csv", index=False)
    print("Tabla resumen guardada: tabla_resumen_caracteristicas.csv")
    
    # Mostrar tabla
    print("\nTABLA RESUMEN DE CARACTERÍSTICAS:")
    print("-" * 70)
    for i, row in summary_df.iterrows():
        if row['Variable'] == '':
            print()
        else:
            print(f"{row['Variable']:45s} {row['n (%)']:>20s}")

def main():
    """Función principal"""
    
    # Cambiar al directorio de datos limpios
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)
    
    try:
        # 1. Cargar datos procesados
        df_valid, df_excluded = load_processed_data()
        
        # 2. Análisis detallado de exclusiones
        detailed_exclusion_analysis(df_excluded)
        
        # 3. Análisis detallado de datos válidos
        df_valid = detailed_valid_analysis(df_valid)
        
        # 4. Crear tabla resumen
        create_summary_table(df_valid, df_excluded)
        
        print("\n" + "="*70)
        print("ANÁLISIS DESCRIPTIVO COMPLETADO")
        print("="*70)
        print("Archivo generado:")
        print("- tabla_resumen_caracteristicas.csv")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
