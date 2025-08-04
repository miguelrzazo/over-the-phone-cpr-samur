#!/usr/bin/env python3
"""
Script para procesar los datos de RCP Transtelefónica
Genera archivos separados para datos válidos y exclusiones
Crea reporte descriptivo en terminal y PDF
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
from datetime import datetime
import os

def load_and_analyze_data():
    """Cargar y analizar el dataset principal"""
    
    # Cargar datos
    input_file = "./Datos 2 años. En proceso de limpieza.xlsx - Sheet.csv"
    df = pd.read_csv(input_file)
    
    print("="*60)
    print("PROCESADOR DE DATOS RCP TRANSTELEFONICA")
    print("="*60)
    print(f"Fecha de procesamiento: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Archivo procesado: {input_file}")
    print(f"Total de registros cargados: {len(df):,}")
    
    # Columnas a eliminar según especificaciones
    columns_to_remove = [
        'Tipo de Unidad', 'CODIGO_INICIAL', 'CODIGO FINAL', 'CODIGO PATOLOGICO',
        'CONSULTA', 'ANTECEDENTES', 'TECNICAS', 'EVOLUCION', 'HOSPITAL',
        '6 HORAS', '24 HORAS', '7 DIAS', 'RITMO INICIAL', 'C0_C1', 'C1_C2',
        'C2_C3', 'C3_C4', 'C4_C5', 'C5_FIN'
    ]
    
    # Identificar columnas que realmente existen
    existing_columns_to_remove = [col for col in columns_to_remove if col in df.columns]
    missing_columns = [col for col in columns_to_remove if col not in df.columns]
    
    print(f"\nColumnas a eliminar: {len(existing_columns_to_remove)}")
    print(f"Columnas no encontradas: {len(missing_columns)}")
    if missing_columns:
        print(f"Columnas faltantes: {missing_columns}")
    
    # Eliminar columnas especificadas
    df_clean = df.drop(columns=existing_columns_to_remove)
    
    print(f"Columnas restantes después de limpieza: {len(df_clean.columns)}")
    print(f"Columnas finales: {list(df_clean.columns)}")
    
    return df_clean

def convert_numeric_columns(df):
    """Convertir columnas numéricas de float a int cuando sea posible"""
    
    df_converted = df.copy()
    
    # Columnas que deben ser enteros (permitiendo NaN)
    integer_columns = {
        'NUM INFORME': 'Int64',
        'EDAD': 'Int64', 
        'RCP_TRANSTELEFONICA': 'Int64',
        'DESA_EXTERNO': 'Int64',
        'Tiempo_llegada': 'Int64',
        'Tiempo_Rcp': 'Int64', 
        'Desfibrilable_inicial': 'Int64',
        'ROSC': 'Int64',
        'Supervivencia_7dias': 'Int64',
        'CPC': 'Int64'
    }
    
    for col, dtype in integer_columns.items():
        if col in df_converted.columns:
            # Convertir a numérico primero
            df_converted[col] = pd.to_numeric(df_converted[col], errors='coerce')
            # Luego convertir a entero que permite NaN
            df_converted[col] = df_converted[col].astype(dtype)
    
    return df_converted

def analyze_cpc_values(df):
    """Analizar los valores de CPC"""
    
    print("\n" + "="*60)
    print("ANÁLISIS DE VALORES CPC")
    print("="*60)
    
    # Analizar valores únicos de CPC
    cpc_counts = df['CPC'].value_counts(dropna=False)
    print("Distribución de valores CPC:")
    print(cpc_counts)
    
    # Identificar registros con CPC válido (numérico)
    def is_valid_cpc(value):
        if pd.isna(value) or value == '':
            return False
        try:
            # Intentar convertir a float para detectar valores numéricos
            float_val = float(str(value).strip())
            # CPC válido debe estar entre 1 y 5
            return 1 <= float_val <= 5
        except (ValueError, TypeError):
            return False
    
    df['CPC_valido'] = df['CPC'].apply(is_valid_cpc)
    
    valid_cpc_count = df['CPC_valido'].sum()
    invalid_cpc_count = len(df) - valid_cpc_count
    
    print(f"\nRegistros con CPC válido (1-5): {valid_cpc_count:,}")
    print(f"Registros sin CPC válido: {invalid_cpc_count:,}")
    print(f"Porcentaje con CPC válido: {valid_cpc_count/len(df)*100:.1f}%")
    
    return df

def analyze_exclusions(df):
    """Analizar las exclusiones"""
    
    print("\n" + "="*60)
    print("ANÁLISIS DE EXCLUSIONES")
    print("="*60)
    
    # Analizar columna Excluido
    if 'Excluido' in df.columns:
        excluido_counts = df['Excluido'].value_counts(dropna=False)
        print("Distribución de valores en columna 'Excluido':")
        print(excluido_counts)
        
        # Considerar como excluidos aquellos que tienen cualquier valor en Excluido (excepto NaN y vacío)
        df['Es_excluido'] = ~(df['Excluido'].isna() | (df['Excluido'] == ''))
    else:
        print("Columna 'Excluido' no encontrada")
        df['Es_excluido'] = False
    
    excluded_count = df['Es_excluido'].sum()
    included_count = len(df) - excluded_count
    
    print(f"\nTotal excluidos (con casilla Excluido rellenada): {excluded_count:,}")
    print(f"Total potencialmente incluibles: {included_count:,}")
    print(f"Porcentaje excluidos: {excluded_count/len(df)*100:.1f}%")
    
    # Verificar que no haya solapamiento: si Excluido está rellenado, no puede tener CPC válido
    solapamiento = df[(df['Es_excluido'] == True) & (df['CPC_valido'] == True)]
    if len(solapamiento) > 0:
        print(f"\n⚠️  ADVERTENCIA: {len(solapamiento)} registros tienen CPC válido pero casilla Excluido rellenada")
        print("Estos registros se incluirán SOLO en el archivo de exclusiones")
        # Corregir: si está excluido, no puede tener CPC válido para el dataset final
        df.loc[df['Es_excluido'] == True, 'CPC_valido'] = False
    
    return df

def create_datasets(df):
    """Crear los datasets separados"""
    
    print("\n" + "="*60)
    print("CREACIÓN DE DATASETS")
    print("="*60)
    
    # Dataset 1: Registros con CPC válido (sin casilla Excluido rellenada)
    df_with_cpc = df[(df['CPC_valido'] == True) & (df['Es_excluido'] == False)].copy()
    
    # Dataset 2: Registros excluidos (casilla Excluido rellenada)
    df_excluded = df[df['Es_excluido'] == True].copy()
    
    print(f"Dataset con CPC válido: {len(df_with_cpc):,} registros")
    print(f"Dataset de exclusiones: {len(df_excluded):,} registros")
    
    # Limpiar datasets - eliminar columnas auxiliares y convertir números
    columns_to_remove = ['CPC_valido', 'Es_excluido', 'Excluido']
    
    # Limpiar dataset CPC válido
    df_with_cpc_clean = df_with_cpc.drop(columns=columns_to_remove).copy()
    df_with_cpc_clean = convert_numeric_columns(df_with_cpc_clean)
    
    # Limpiar dataset excluidos (mantener columna Excluido para ver motivo)
    df_excluded_clean = df_excluded.drop(columns=['CPC_valido', 'Es_excluido']).copy()
    df_excluded_clean = convert_numeric_columns(df_excluded_clean)
    
    # Guardar datasets
    output_dir = "../3.cleaned_data/"
    os.makedirs(output_dir, exist_ok=True)
    
    # Guardar dataset con CPC
    cpc_file = os.path.join(output_dir, "datos_con_cpc_valido.csv")
    df_with_cpc_clean.to_csv(cpc_file, index=False)
    print(f"Archivo guardado: {cpc_file}")
    
    # Guardar dataset de exclusiones  
    excluded_file = os.path.join(output_dir, "datos_excluidos.csv")
    df_excluded_clean.to_csv(excluded_file, index=False)
    print(f"Archivo guardado: {excluded_file}")
    
    return df_with_cpc_clean, df_excluded_clean

def analyze_valid_data(df_valid):
    """Analizar datos válidos para el estudio"""
    
    print("\n" + "="*60)
    print("ANÁLISIS DE DATOS VÁLIDOS")
    print("="*60)
    
    # Estadísticas básicas
    total_valid = len(df_valid)
    print(f"Total de casos válidos: {total_valid:,}")
    
    # Análisis de RCP Transtelefónica
    if 'RCP_TRANSTELEFONICA' in df_valid.columns:
        rcp_trans_count = (df_valid['RCP_TRANSTELEFONICA'] == 1).sum()
        rcp_trans_pct = rcp_trans_count / total_valid * 100
        print(f"RCP Transtelefónica: {rcp_trans_count:,} ({rcp_trans_pct:.1f}%)")
    
    # Análisis de RCP por testigos
    if 'RCP_TESTIGOS' in df_valid.columns:
        # Contar diferentes tipos de testigos
        testigos_counts = df_valid['RCP_TESTIGOS'].value_counts(dropna=False)
        print(f"\nDistribución RCP por testigos:")
        for testigo, count in testigos_counts.items():
            pct = count / total_valid * 100
            print(f"  {testigo}: {count:,} ({pct:.1f}%)")
    
    # Análisis de ROSC
    if 'ROSC' in df_valid.columns:
        rosc_count = (df_valid['ROSC'] == 1).sum()
        rosc_pct = rosc_count / total_valid * 100
        print(f"\nROSC: {rosc_count:,} ({rosc_pct:.1f}%)")
    
    # Análisis de Supervivencia a 7 días
    if 'Supervivencia_7dias' in df_valid.columns:
        surv_count = (df_valid['Supervivencia_7dias'] == 1).sum()
        surv_pct = surv_count / total_valid * 100
        print(f"Supervivencia 7 días: {surv_count:,} ({surv_pct:.1f}%)")
    
    # Análisis de CPC favorable (1-2)
    def is_favorable_cpc(value):
        try:
            # Manejar tanto int como float
            if pd.isna(value):
                return False
            cpc_val = int(value)
            return cpc_val in [1, 2]
        except (ValueError, TypeError):
            return False
    
    df_valid_copy = df_valid.copy()
    df_valid_copy['CPC_favorable'] = df_valid_copy['CPC'].apply(is_favorable_cpc)
    cpc_fav_count = df_valid_copy['CPC_favorable'].sum()
    cpc_fav_pct = cpc_fav_count / total_valid * 100
    print(f"CPC favorable (1-2): {cpc_fav_count:,} ({cpc_fav_pct:.1f}%)")
    
    # Análisis por edad
    if 'EDAD' in df_valid.columns:
        edad_stats = df_valid['EDAD'].describe()
        print(f"\nEstadísticas de edad:")
        print(f"  Media: {edad_stats['mean']:.1f} años")
        print(f"  Mediana: {edad_stats['50%']:.1f} años")
        print(f"  Rango: {edad_stats['min']:.0f} - {edad_stats['max']:.0f} años")
        
        # Estratificación por edad <65 vs ≥65
        bajo_65 = (df_valid['EDAD'] < 65).sum()
        alto_65 = (df_valid['EDAD'] >= 65).sum()
        print(f"  <65 años: {bajo_65:,} ({bajo_65/total_valid*100:.1f}%)")
        print(f"  ≥65 años: {alto_65:,} ({alto_65/total_valid*100:.1f}%)")
    
    # Análisis por sexo
    if 'SEXO' in df_valid.columns:
        sexo_counts = df_valid['SEXO'].value_counts(dropna=False)
        print(f"\nDistribución por sexo:")
        for sexo, count in sexo_counts.items():
            pct = count / total_valid * 100
            print(f"  {sexo}: {count:,} ({pct:.1f}%)")
    
    return df_valid_copy

def create_pdf_report(df_original, df_valid, df_excluded):
    """Crear reporte en PDF"""
    
    print("\n" + "="*60)
    print("GENERANDO REPORTE PDF")
    print("="*60)
    
    output_file = "reporte_datos_rcp_transtelefonica.pdf"
    
    with PdfPages(output_file) as pdf:
        # Configurar estilo
        plt.style.use('default')
        fig_size = (12, 8)
        
        # Página 1: Resumen general
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=fig_size)
        fig.suptitle('Reporte de Datos RCP Transtelefónica', fontsize=16, fontweight='bold')
        
        # Gráfico 1: Distribución de registros
        labels = ['Datos válidos\n(con CPC)', 'Datos excluidos', 'Sin CPC válido']
        sizes = [len(df_valid), len(df_excluded), len(df_original) - len(df_valid) - len(df_excluded)]
        colors = ['#2E8B57', '#DC143C', '#FFD700']
        ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax1.set_title('Distribución de Registros')
        
        # Gráfico 2: CPC favorable
        if len(df_valid) > 0 and 'CPC' in df_valid.columns:
            def is_favorable_cpc_pdf(value):
                try:
                    if pd.isna(value):
                        return False
                    cpc_val = int(value)
                    return cpc_val in [1, 2]
                except (ValueError, TypeError):
                    return False
            
            cpc_favorable = df_valid['CPC'].apply(is_favorable_cpc_pdf).sum()
            cpc_no_favorable = len(df_valid) - cpc_favorable
            ax2.bar(['CPC Favorable\n(1-2)', 'CPC No Favorable\n(3-5)'], 
                   [cpc_favorable, cpc_no_favorable], 
                   color=['#228B22', '#B22222'])
            ax2.set_title('CPC Favorable vs No Favorable')
            ax2.set_ylabel('Número de casos')
            
            # Añadir valores en las barras
            for i, v in enumerate([cpc_favorable, cpc_no_favorable]):
                ax2.text(i, v + len(df_valid)*0.01, str(v), ha='center', va='bottom')
        
        # Gráfico 3: Distribución por edad
        if 'EDAD' in df_valid.columns and len(df_valid) > 0:
            edades = df_valid['EDAD'].dropna()
            ax3.hist(edades, bins=20, color='skyblue', alpha=0.7, edgecolor='black')
            ax3.axvline(edades.mean(), color='red', linestyle='--', label=f'Media: {edades.mean():.1f}')
            ax3.axvline(edades.median(), color='orange', linestyle='--', label=f'Mediana: {edades.median():.1f}')
            ax3.set_title('Distribución de Edades')
            ax3.set_xlabel('Edad (años)')
            ax3.set_ylabel('Frecuencia')
            ax3.legend()
        
        # Gráfico 4: Tipos de RCP
        if 'RCP_TESTIGOS' in df_valid.columns and len(df_valid) > 0:
            rcp_counts = df_valid['RCP_TESTIGOS'].value_counts().head(5)
            ax4.bar(range(len(rcp_counts)), rcp_counts.values, color='lightcoral')
            ax4.set_title('Tipos de RCP por Testigos (Top 5)')
            ax4.set_xlabel('Tipo de RCP')
            ax4.set_ylabel('Número de casos')
            ax4.set_xticks(range(len(rcp_counts)))
            ax4.set_xticklabels(rcp_counts.index, rotation=45, ha='right')
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # Página 2: Tablas resumen
        fig, ax = plt.subplots(figsize=fig_size)
        ax.axis('tight')
        ax.axis('off')
        
        # Crear tabla resumen
        summary_data = [
            ['Métrica', 'Valor', 'Porcentaje (%)'],
            ['Total registros originales', f'{len(df_original):,}', '100.0'],
            ['Registros con CPC válido', f'{len(df_valid):,}', f'{len(df_valid)/len(df_original)*100:.1f}'],
            ['Registros excluidos', f'{len(df_excluded):,}', f'{len(df_excluded)/len(df_original)*100:.1f}'],
        ]
        
        if len(df_valid) > 0:
            # Añadir estadísticas de datos válidos
            rcp_trans = (df_valid['RCP_TRANSTELEFONICA'] == 1).sum() if 'RCP_TRANSTELEFONICA' in df_valid.columns else 0
            rosc = (df_valid['ROSC'] == 1).sum() if 'ROSC' in df_valid.columns else 0
            supervivencia = (df_valid['Supervivencia_7dias'] == 1).sum() if 'Supervivencia_7dias' in df_valid.columns else 0
            
            # CPC favorable con manejo de enteros
            def is_favorable_cpc_table(value):
                try:
                    if pd.isna(value):
                        return False
                    cpc_val = int(value)
                    return cpc_val in [1, 2]
                except (ValueError, TypeError):
                    return False
            
            cpc_fav = df_valid['CPC'].apply(is_favorable_cpc_table).sum()
            
            summary_data.extend([
                ['', '', ''],
                ['--- DATOS VÁLIDOS ---', '', ''],
                ['RCP Transtelefónica', f'{rcp_trans:,}', f'{rcp_trans/len(df_valid)*100:.1f}'],
                ['ROSC', f'{rosc:,}', f'{rosc/len(df_valid)*100:.1f}'],
                ['Supervivencia 7 días', f'{supervivencia:,}', f'{supervivencia/len(df_valid)*100:.1f}'],
                ['CPC Favorable (1-2)', f'{cpc_fav:,}', f'{cpc_fav/len(df_valid)*100:.1f}'],
            ])
        
        table = ax.table(cellText=summary_data[1:], colLabels=summary_data[0], 
                        cellLoc='center', loc='center', bbox=[0, 0, 1, 1])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        
        # Colorear encabezados
        for i in range(len(summary_data[0])):
            table[(0, i)].set_facecolor('#4CAF50')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        ax.set_title('Resumen Estadístico - Datos RCP Transtelefónica', 
                    fontsize=14, fontweight='bold', pad=20)
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
    
    print(f"Reporte PDF guardado: {output_file}")

def main():
    """Función principal"""
    
    # Cambiar al directorio de trabajo
    os.chdir("/Users/miguelrosa/Desktop/RCP Transtelefonica/data/2.Data_cleaning")
    
    try:
        # 1. Cargar y limpiar datos
        df = load_and_analyze_data()
        
        # 2. Analizar CPC
        df = analyze_cpc_values(df)
        
        # 3. Analizar exclusiones
        df = analyze_exclusions(df)
        
        # 4. Crear datasets separados
        df_valid, df_excluded = create_datasets(df)
        
        # 5. Analizar datos válidos
        df_valid = analyze_valid_data(df_valid)
        
        # 6. Crear reporte PDF
        create_pdf_report(df, df_valid, df_excluded)
        
        print("\n" + "="*60)
        print("PROCESAMIENTO COMPLETADO EXITOSAMENTE")
        print("="*60)
        print("Archivos generados:")
        print("- datos_con_cpc_valido.csv (en ../3.cleaned_data/)")
        print("- datos_excluidos.csv (en ../3.cleaned_data/)")
        print("- reporte_datos_rcp_transtelefonica.pdf")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
