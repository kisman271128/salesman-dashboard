
import pandas as pd
import os
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Lokasi file Excel
EXCEL_FILE = r"C:\Dashboard\DbaseSalesmanWebApp.xlsb"

# Lokasi output
OUTPUT_ANDROID = r"C:\Users\kisman.pidu\AndroidStudioProjects\MAS\app\src\main\assets\data"
OUTPUT_DASHBOARD = r"C:\Dashboard\data"
os.makedirs(OUTPUT_ANDROID, exist_ok=True)
os.makedirs(OUTPUT_DASHBOARD, exist_ok=True)

def read_excel_sheets(file_path):
    """Ambil semua sheet Excel yang berawalan d."""
    xls = pd.ExcelFile(file_path, engine="pyxlsb")
    return {sheet: pd.read_excel(xls, sheet_name=sheet, engine="pyxlsb")
            for sheet in xls.sheet_names if sheet.startswith("d.")}

def save_json(data, filename, both_locations=True):
    """Simpan data ke JSON di folder Android + Dashboard"""
    path1 = os.path.join(OUTPUT_ANDROID, filename)
    path2 = os.path.join(OUTPUT_DASHBOARD, filename)

    data.to_json(path1, orient="records", lines=True, force_ascii=False)
    data.to_json(path2, orient="records", lines=True, force_ascii=False)

    logging.info(f"JSON disimpan: {filename} → Android & Dashboard")

def process_dashboard(df):
    """Proses khusus sheet d.dashboard → hitung gap/ach dsb."""
    records = []
    for _, row in df.iterrows():
        try:
            actual = float(row.get("ACTUAL", 0))
            target = float(row.get("TARGET", 0))
            gap = actual - target
            ach = (actual / target * 100) if target else 0
            record = {
                "lob": row.get("LOB"),
                "actual": actual,
                "target": target,
                "gap": gap,
                "ach": ach,
                "vs_bp": row.get("VS_BP"),
                "vs_ly": row.get("VS_LY"),
                "vs_lm": row.get("VS_LM"),
                "vs_3lm": row.get("VS_3LM")
            }
            records.append(record)
        except Exception as e:
            logging.warning(f"Gagal proses baris dashboard: {e}")
    return records

def main():
    logging.info("=== PEMBARUAN PAGI DIMULAI ===")

    sheets = read_excel_sheets(EXCEL_FILE)

    for sheet, df in sheets.items():
        # Simpan semua sheet mentah ke JSON di dua lokasi
        save_json(df, f"{sheet}.json")

        # Jika sheet d.dashboard → simpan versi terproses juga
        if sheet == "d.dashboard":
            dashboard = process_dashboard(df)
            out_file = os.path.join(OUTPUT_DASHBOARD, "dashboard_processed.json")
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(dashboard, f, ensure_ascii=False, indent=2)
            logging.info("Dashboard terproses disimpan → dashboard_processed.json")

    logging.info(f"Total {len(sheets)} sheet berhasil diekspor ke JSON.")
    logging.info("=== PEMBARUAN PAGI SELESAI ===")

if __name__ == "__main__":
    main()
