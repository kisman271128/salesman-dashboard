import pandas as pd
from morning_update import SalesmanDashboardUpdater

# Test the function directly
updater = SalesmanDashboardUpdater()

# Read Excel manually
sheets = updater.read_excel_sheets()
print("Sheets loaded:", list(sheets.keys()) if sheets else "None")

if sheets and 'soharian' in sheets:
    print("✅ d.soharian sheet found!")
    so_df = sheets['soharian']
    print(f"Rows: {len(so_df)}")
    print("First 3 rows:")
    print(so_df.head(3))
    
    # Test chart data generation
    chart_data = updater.generate_chart_data(sheets)
    print("\nChart data preview:")
    print("SO data length:", len(chart_data['so_data']))
    print("DO data length:", len(chart_data['do_data']))
    print("Labels sample:", chart_data['labels'][:5] if chart_data['labels'] else "Empty")
    print("Stats:", chart_data['stats'])
else:
    print("❌ d.soharian sheet NOT found in sheets!")