#!/usr/bin/env python3
"""
Debug script untuk inspect Excel data structure
Run: python debug_excel.py
"""

import pandas as pd
import sys

def debug_excel_structure():
    """Debug Excel file structure"""
    excel_file = "DbaseSalesmanWebApp.xlsm"
    
    print("🔍 DEBUGGING EXCEL FILE STRUCTURE")
    print("=" * 50)
    
    try:
        # Read Excel file
        xl_file = pd.ExcelFile(excel_file, engine='openpyxl')
        
        # Check dashboard sheet
        dashboard_df = pd.read_excel(xl_file, sheet_name='d.dashboard')
        
        print(f"📊 Dashboard sheet loaded: {len(dashboard_df)} rows")
        print(f"📋 Columns: {list(dashboard_df.columns)}")
        print()
        
        # Find GPPJ row
        gppj_rows = dashboard_df[dashboard_df['LOB'] == 'GPPJ']
        
        if len(gppj_rows) > 0:
            print("🎯 GPPJ ROW DATA:")
            print("-" * 30)
            
            gppj_row = gppj_rows.iloc[0]
            
            # Print all columns and values
            for col in dashboard_df.columns:
                value = gppj_row[col]
                value_type = type(value)
                print(f"  {col:<15}: {value} ({value_type})")
            
            print()
            print("🔍 VS METRICS ANALYSIS:")
            print("-" * 30)
            
            # Check all possible vs columns
            vs_columns = [col for col in dashboard_df.columns if 'vs' in str(col).lower()]
            print(f"Found vs columns: {vs_columns}")
            
            for col in vs_columns:
                value = gppj_row[col]
                print(f"  {col}: {value}")
            
            print()
            print("💰 NUMERIC VALUES:")
            print("-" * 30)
            
            numeric_cols = ['Actual', 'BP', 'Gap', 'LY', '3LM', 'LM']
            for col in numeric_cols:
                if col in dashboard_df.columns:
                    value = gppj_row[col]
                    print(f"  {col}: {value}")
            
            # Calculate achievement manually
            actual = float(gppj_row.get('Actual', 0))
            bp = float(gppj_row.get('BP', 1))
            achievement = (actual / bp * 100) if bp > 0 else 0
            
            print()
            print("🧮 MANUAL CALCULATIONS:")
            print("-" * 30)
            print(f"  Actual: {actual:,.0f}")
            print(f"  BP: {bp:,.0f}")
            print(f"  Achievement: {achievement:.1f}%")
            
        else:
            print("❌ GPPJ row not found!")
            print("Available LOBs:")
            print(dashboard_df['LOB'].unique())
    
    except Exception as e:
        print(f"❌ Error: {e}")
        
    print()
    print("=" * 50)
    print("✅ Debug completed")

if __name__ == "__main__":
    debug_excel_structure()