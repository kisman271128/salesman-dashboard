import pandas as pd
import os

# Menggunakan path absolut untuk file Excel
file_path = r'C:\Dashboard\DbaseSalesmanWebApp.xlsb'

# Mengambil semua nama sheet
xls = pd.ExcelFile(file_path, engine='pyxlsb')
sheet_names = xls.sheet_names

# Memfilter sheet yang berawalan "d."
filtered_sheets = [sheet for sheet in sheet_names if sheet.startswith('d.')]

# Menentukan folder output (dua lokasi)
output_folder_1 = r'C:\Users\kisman.pidu\AndroidStudioProjects\MAS\app\src\main\assets\data'
output_folder_2 = r'C:\Dashboard\data'

# Memastikan kedua folder output ada
os.makedirs(output_folder_1, exist_ok=True)
os.makedirs(output_folder_2, exist_ok=True)

# Mengonversi setiap sheet ke JSON
for sheet in filtered_sheets:
    df = pd.read_excel(xls, sheet_name=sheet, engine='pyxlsb')
    
    # Menyimpan ke lokasi pertama (Android Studio)
    json_file_name_1 = os.path.join(output_folder_1, f"{sheet}.json")
    df.to_json(json_file_name_1, orient='records', lines=True)
    print(f"File JSON '{json_file_name_1}' telah dibuat.")
    
    # Menyimpan ke lokasi kedua (Dashboard)
    json_file_name_2 = os.path.join(output_folder_2, f"{sheet}.json")
    df.to_json(json_file_name_2, orient='records', lines=True)
    print(f"File JSON '{json_file_name_2}' telah dibuat.")

print(f"\nProses selesai. Total {len(filtered_sheets)} sheet telah dikonversi ke JSON dan disimpan di kedua lokasi.")