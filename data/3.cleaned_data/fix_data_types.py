#!/usr/bin/env python3
"""
Script para corregir tipos de datos a enteros naturales
"""

import pandas as pd
import numpy as np

def fix_data_types():
    """Corregir tipos de datos en los archivos finales"""
    
    print("CORRIGIENDO TIPOS DE DATOS A ENTEROS NATURALES")
    print("="*50)
    
    # Archivos a procesar
    files_to_fix = [
        'datos_con_cpc_valido.csv',
        'datos_excluidos.csv'
    ]
    
    # Columnas que deben ser enteros
    integer_columns = [
        'NUM INFORME', 'EDAD', 'RCP_TRANSTELEFONICA', 'DESA_EXTERNO',
        'Tiempo_llegada', 'Tiempo_Rcp', 'Desfibrilable_inicial',
        'ROSC', 'Supervivencia_7dias', 'CPC'
    ]
    
    for filename in files_to_fix:
        print(f"\nProcesando: {filename}")
        
        # Cargar archivo
        df = pd.read_csv(filename)
        print(f"Registros: {len(df):,}")
        
        # Convertir columnas a enteros
        for col in integer_columns:
            if col in df.columns:
                # Convertir a numérico, manteniendo NaN
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # Convertir a entero que permite NaN (Int64)
                df[col] = df[col].astype('Int64')
                print(f"  {col}: convertido a Int64")
        
        # Guardar archivo corregido
        df.to_csv(filename, index=False)
        print(f"✅ {filename} actualizado con tipos correctos")
    
    print("\n" + "="*50)
    print("CORRECCIÓN COMPLETADA")
    
    # Verificar resultado final
    print("\nVERIFICACIÓN FINAL:")
    df_final = pd.read_csv('datos_con_cpc_valido.csv')
    print("\nTipos de datos después de corrección:")
    for col in df_final.columns:
        print(f"  {col}: {df_final[col].dtype}")
    
    print(f"\nMuestra de valores enteros:")
    sample_cols = ['NUM INFORME', 'EDAD', 'RCP_TRANSTELEFONICA', 'ROSC', 'CPC']
    for col in sample_cols:
        if col in df_final.columns:
            sample_vals = df_final[col].dropna().head(3).tolist()
            print(f"  {col}: {sample_vals}")

if __name__ == "__main__":
    fix_data_types()
