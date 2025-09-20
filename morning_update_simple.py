import pandas as pd
import json
import os
import logging
import subprocess

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

EXCEL_FILE = r"C:\Dashboard\DbaseSalesmanWebApp.xlsb"
OUTPUT_ANDROID = r"C:\Users\kisman.pidu\AndroidStudioProjects\MAS\app\src\main\assets\data"
OUTPUT_DASHBOARD = r"C:\Dashboard\data"

os.makedirs(OUTPUT_ANDROID, exist_ok=True)
os.makedirs(OUTPUT_DASHBOARD, exist_ok=True)

# === 1. Ekspor semua sheet mentah ===
def export_all_raw_sheets(file_path):
    xls = pd.ExcelFile(file_path, engine="pyxlsb")
    for sheet in xls.sheet_names:
        if sheet.startswith("d."):
            try:
                df = pd.read_excel(xls, sheet_name=sheet, engine="pyxlsb")

                # Lokasi Android
                out_android = os.path.join(OUTPUT_ANDROID, f"{sheet}.json")
                df.to_json(out_android, orient="records", lines=True, force_ascii=False)

                # Lokasi Dashboard
                out_dash = os.path.join(OUTPUT_DASHBOARD, f"{sheet}.json")
                df.to_json(out_dash, orient="records", lines=True, force_ascii=False)

                logging.info(f"Sheet mentah diekspor: {sheet}")
            except Exception as e:
                logging.warning(f"Gagal ekspor sheet {sheet}: {e}")

# === 2. Proses sheet dashboard ===
def process_dashboard(df):
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

# === 3. Simpan JSON hasil olahan ===
def save_processed_json(data, filename):
    path = os.path.join(OUTPUT_DASHBOARD, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logging.info(f"Data terproses disimpan → {path}")

# === 4. Validasi sheet ===
def validate_sheets(file_path, required_sheets):
    xls = pd.ExcelFile(file_path, engine="pyxlsb")
    available = xls.sheet_names
    for sheet in required_sheets:
        if sheet not in available:
            logging.error(f"Sheet wajib tidak ada: {sheet}")
            return False
    return True

# === 5. Git commit & push ===
def git_commit_push(message="Pembaruan otomatis pagi"):
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", message], check=True)
        subprocess.run(["git", "push"], check=True)
        logging.info("Perubahan berhasil dikirim ke GitHub")
    except subprocess.CalledProcessError as e:
        logging.warning(f"Git operation failed: {e}")

# === MAIN ===
def main():
    logging.info("=== PEMBARUAN PAGI DIMULAI ===")

    if not validate_sheets(EXCEL_FILE, ["d.dashboard", "d.insentif"]):
        logging.error("Validasi gagal. Pembaruan dihentikan.")
        return

    # Ekspor semua sheet mentah
    export_all_raw_sheets(EXCEL_FILE)

    # Proses dashboard
    try:
        df_dash = pd.read_excel(EXCEL_FILE, sheet_name="d.dashboard", engine="pyxlsb")
        dashboard = process_dashboard(df_dash)
        save_processed_json(dashboard, "dashboard_processed.json")
    except Exception as e:
        logging.warning(f"Gagal proses dashboard: {e}")

    # Proses insentif (mentah → JSON terstruktur)
    try:
        df_ins = pd.read_excel(EXCEL_FILE, sheet_name="d.insentif", engine="pyxlsb")
        insentif = df_ins.to_dict(orient="records")
        save_processed_json(insentif, "insentif.json")
    except Exception as e:
        logging.warning(f"Gagal proses insentif: {e}")

    # Git push
    git_commit_push(f"Pembaruan otomatis pagi")

    logging.info("=== PEMBARUAN PAGI SELESAI ===")

if __name__ == "__main__":
    main()
