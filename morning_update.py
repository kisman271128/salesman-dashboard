# Fix untuk masalah encoding di Windows
import sys
import os
import logging
import json
import pandas as pd
from datetime import datetime, timedelta
import subprocess

# Fix encoding untuk Windows console
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# Menggunakan path absolut untuk file Excel
file_path = r'C:\Dashboard\DbaseSalesmanWebApp.xlsx'

# Mengambil semua nama sheet
xls = pd.ExcelFile(file_path)
sheet_names = xls.sheet_names

# Memfilter sheet yang berawalan "d."
filtered_sheets = [sheet for sheet in sheet_names if sheet.startswith('d.')]

# Menentukan folder output (dua lokasi)
output_folder_1 = r'C:\Users\kisman.pidu\AndroidStudioProjects\DailySalesBoard\app\src\main\assets\data'
output_folder_2 = r'C:\Dashboard\data'

# Memastikan kedua folder output ada
os.makedirs(output_folder_1, exist_ok=True)
os.makedirs(output_folder_2, exist_ok=True)

# Mengonversi setiap sheet ke JSON
for sheet in filtered_sheets:
    df = pd.read_excel(xls, sheet_name=sheet)
    
    # Menyimpan ke lokasi pertama (Android Studio)
    json_file_name_1 = os.path.join(output_folder_1, f"{sheet}.json")
    df.to_json(json_file_name_1, orient='records', lines=True)
    print(f"File JSON '{json_file_name_1}' telah dibuat.")
    
    # Menyimpan ke lokasi kedua (Dashboard)
    json_file_name_2 = os.path.join(output_folder_2, f"{sheet}.json")
    df.to_json(json_file_name_2, orient='records', lines=True)
    print(f"File JSON '{json_file_name_2}' telah dibuat.")

print(f"\nProses selesai. Total {len(filtered_sheets)} sheet telah dikonversi ke JSON dan disimpan di kedua lokasi.")

class SalesmanDashboardUpdater:
    def __init__(self, excel_file="DbaseSalesmanWebApp.xlsx"):
        self.excel_file = excel_file
        self.data_dir = "data"
        self.log_file = 'morning_update.log'
        
        # Setup directories
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        # 🆕 NEW: Clear previous log file for fresh start
        self.clear_previous_log()
        
        # Setup logging dengan encoding yang aman
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        
        # Setup file handler dengan UTF-8 dan mode 'w' untuk overwrite
        file_handler = logging.FileHandler(self.log_file, mode='w', encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(log_format))
        
        # Setup console handler dengan fallback untuk emoji
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(log_format))
        
        # Configure logger
        logging.basicConfig(
            level=logging.INFO,
            handlers=[file_handler, console_handler],
            format=log_format,
            force=True  # Force reconfiguration if logger already exists
        )
        
        self.logger = logging.getLogger(__name__)
        
        # Log session start
        self.safe_log('info', "=" * 80, "=" * 50)
        self.safe_log('info', f"🚀 MORNING UPDATE SESSION STARTED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", f"[LAUNCH] MORNING UPDATE SESSION STARTED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.safe_log('info', "=" * 80, "=" * 50)

    def clear_previous_log(self):
        """🆕 NEW: Clear previous log file untuk fresh start"""
        try:
            if os.path.exists(self.log_file):
                # Get file info before deletion
                file_size = os.path.getsize(self.log_file)
                mod_time = datetime.fromtimestamp(os.path.getmtime(self.log_file))
                
                # Delete the old log file
                os.remove(self.log_file)
                
                print(f"🗑️  Cleared previous log file: {self.log_file}")
                print(f"   Previous size: {file_size:,} bytes")
                print(f"   Last modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   Starting fresh log session...")
            else:
                print(f"📝 Creating new log file: {self.log_file}")
        except Exception as e:
            print(f"⚠️  Warning: Could not clear previous log: {str(e)}")

    def safe_log(self, level, message, fallback_message=None):
        """Logging yang aman dengan fallback untuk emoji"""
        try:
            getattr(self.logger, level)(message)
        except UnicodeEncodeError:
            # Fallback tanpa emoji
            safe_message = fallback_message or self.remove_emoji(message)
            getattr(self.logger, level)(safe_message)
    
    def remove_emoji(self, text):
        """Hapus emoji dari text untuk kompatibilitas"""
        # Simple emoji removal - replace common ones
        emoji_map = {
            '📊': '[CHART]',
            '✅': '[OK]',
            '🔍': '[SEARCH]', 
            '🔄': '[PROCESS]',
            '📅': '[DATE]',
            '💰': '[MONEY]',
            '📈': '[TREND]',
            '🎉': '[SUCCESS]',
            '📋': '[LIST]',
            '🚀': '[LAUNCH]',
            '⚠️': '[WARNING]',
            '❌': '[ERROR]',
            '📱': '[MOBILE]',
            '🐍': '[PYTHON]',
            '📁': '[FOLDER]',
            '📦': '[PACKAGE]',
            '🔐': '[LOGIN]',
            '🎯': '[TARGET]',
            '🔗': '[LINK]',
            '🧭': '[NAV]',
            '🔑': '[KEY]',
            '🌐': '[WEB]',
            '⏰': '[TIME]',
            '⏱️': '[TIMER]',
            '🖥️': '[DESKTOP]',
            '💻': '[LAPTOP]',
            '💸': '[INCENTIVE]',
            '🗑️': '[DELETE]',
            '📝': '[NOTE]'
        }
        
        for emoji, replacement in emoji_map.items():
            text = text.replace(emoji, replacement)
        
        return text

    def read_excel_sheets(self):
        """Read all required sheets from Excel file"""
        try:
            self.safe_log('info', "📊 Reading Excel sheets...", "Reading Excel sheets...")
            
            # 🆕 UPDATED: Added d.insentif to required sheets
            required_sheets = ['d.dashboard', 'd.performance', 'd.salesmanlob', 'd.salesmanproses', 'd.soharian', 'd.insentif']
            
            sheets = {}
            
            # Read with multiple engines for compatibility
            try:
                # Try openpyxl first (best for .xlsx)
                xl_file = pd.ExcelFile(self.excel_file, engine='openpyxl')
            except:
                try:
                    # Fallback to xlrd for .xls
                    xl_file = pd.ExcelFile(self.excel_file, engine='xlrd')
                except:
                    # Last resort - default engine
                    xl_file = pd.ExcelFile(self.excel_file)
            
            available_sheets = xl_file.sheet_names
            self.safe_log('info', f"Available sheets: {available_sheets}")
            
            # Read each required sheet
            for sheet_name in required_sheets:
                if sheet_name in available_sheets:
                    try:
                        df = pd.read_excel(xl_file, sheet_name=sheet_name)
                        sheets[sheet_name] = df
                        self.safe_log('info', f"✅ Loaded sheet: {sheet_name}", f"[OK] Loaded sheet: {sheet_name}")
                        self.safe_log('info', f"   Rows: {len(df)}, Columns: {list(df.columns)}")
                    except Exception as e:
                        self.safe_log('error', f"Failed to read sheet {sheet_name}: {str(e)}")
                else:
                    # 🆕 SPECIAL: d.insentif is optional for backward compatibility
                    if sheet_name == 'd.insentif':
                        self.safe_log('warning', f"Sheet {sheet_name} not found - will be skipped (optional)")
                    else:
                        self.safe_log('warning', f"Sheet {sheet_name} not found in Excel file")
            
            if not sheets:
                raise Exception("No required sheets found in Excel file")
                
            return sheets
            
        except Exception as e:
            self.safe_log('error', f"Error reading Excel file: {str(e)}")
            return None

    # 🆕 NEW: Process incentive data from d.insentif sheet
    def process_insentif_data(self, sheets):
        """Process incentive data from d.insentif sheet"""
        try:
            self.safe_log('info', "💸 Processing incentive data...", "[INCENTIVE] Processing incentive data...")
            
            # Check if d.insentif sheet exists
            if 'd.insentif' not in sheets:
                self.safe_log('warning', "d.insentif sheet not found - skipping incentive data processing")
                return []
            
            insentif_df = sheets['d.insentif']
            self.safe_log('info', f"Incentive columns: {list(insentif_df.columns)}")
            
            incentive_records = []
            
            for _, row in insentif_df.iterrows():
                # Check if this row has valid data (at least szEmployeeId should exist)
                if pd.notna(row.get('szEmployeeId', '')):
                    
                    # Build incentive record following the exact structure from your sample
                    incentive_record = {}
                    
                    # 🔧 MAIN FIELDS - Handle common fields with proper type conversion
                    incentive_record['NIK SAC'] = self.safe_int(row.get('NIK SAC', 0))
                    incentive_record['Nama SAC'] = str(row.get('Nama SAC', '')).strip()
                    incentive_record['szEmployeeId'] = self.safe_int(row.get('szEmployeeId', 0))
                    incentive_record['szname'] = str(row.get('szname', '')).strip()
                    incentive_record['Dept'] = str(row.get('Dept', '')).strip()
                    incentive_record['Tipe Salesman'] = str(row.get('Tipe Salesman', '')).strip()
                    
                    # 🔧 PERFORMANCE METRICS - Handle numeric fields
                    incentive_record['GPPJ & GEN'] = self.safe_int(row.get('GPPJ & GEN', 0))
                    incentive_record['GBS & OTHERS'] = self.safe_int(row.get('GBS & OTHERS', 0))
                    incentive_record['GPPJ'] = self.safe_int(row.get('GPPJ', 0))
                    incentive_record['GBS'] = self.safe_int(row.get('GBS', 0))
                    incentive_record['MBR'] = self.safe_int(row.get('MBR', 0))
                    incentive_record['HGJ'] = self.safe_int(row.get('HGJ', 0))
                    incentive_record['OTHERS'] = self.safe_int(row.get('OTHERS', 0))
                    incentive_record['Avg SKU'] = self.safe_int(row.get('Avg SKU', 0))
                    incentive_record['GP'] = self.safe_int(row.get('GP', 0))
                    
                    # 🔧 SPECIAL FIELDS - Handle null values properly
                    pom_value = row.get('POM')
                    incentive_record['POM'] = None if pd.isna(pom_value) else self.safe_int(pom_value)
                    
                    incentive_record['AR Coll'] = self.safe_int(row.get('AR Coll', 0))
                    
                    # 🔧 INCENTIVE CALCULATIONS
                    incentive_record['Insentif_sales'] = self.safe_int(row.get('Insentif_sales', 0))
                    incentive_record['Insentif_Proses'] = self.safe_int(row.get('Insentif_Proses', 0))
                    incentive_record['Total_Insentif'] = self.safe_int(row.get('Total_Insentif', 0))
                    
                    incentive_records.append(incentive_record)
                    
                    self.safe_log('info', f"✅ Added incentive for szEmployeeId {incentive_record['szEmployeeId']}: {incentive_record['szname']} - Sales:{incentive_record['Insentif_sales']}, Proses:{incentive_record['Insentif_Proses']}", 
                                f"[OK] Added incentive for szEmployeeId {incentive_record['szEmployeeId']}: {incentive_record['szname']}")
            
            self.safe_log('info', f"✅ Processed {len(incentive_records)} incentive records", f"[OK] Processed {len(incentive_records)} incentive records")
            
            return incentive_records
            
        except Exception as e:
            self.safe_log('error', f"Error processing incentive data: {str(e)}")
            return []
    
    # 🆕 NEW: Helper method for safe integer conversion
    def safe_int(self, value):
        """Safely convert value to integer"""
        try:
            if pd.isna(value):
                return 0
            if isinstance(value, str):
                # Handle empty strings
                if value.strip() == '':
                    return 0
                # Handle currency strings with commas
                value = value.replace(',', '').replace('(', '-').replace(')', '')
            return int(float(value))
        except:
            return 0

    def debug_dashboard_data(self, dashboard_df):
        """🔧 ENHANCED: Debug function to inspect dashboard data structure"""
        self.safe_log('info', "🔍 DEBUG: Inspecting dashboard data structure...")
        
        # Print column names with spaces/special chars
        self.safe_log('info', f"Column names: {list(dashboard_df.columns)}")
        
        # Print first few rows to understand the data
        self.safe_log('info', "First 3 rows of dashboard data:")
        for i in range(min(3, len(dashboard_df))):
            row = dashboard_df.iloc[i]
            lob_name = row.get('LOB', 'Unknown')
            self.safe_log('info', f"Row {i}: LOB={lob_name}")
            
            # Print key values for this row
            for col in ['Actual', 'BP', 'vs BP', 'vs LY', 'vs 3LM', 'vs LM']:
                if col in dashboard_df.columns:
                    value = row.get(col)
                    self.safe_log('info', f"  {col}: {value} (type: {type(value)})")
        
        # Check for column name variations
        all_columns = list(dashboard_df.columns)
        vs_columns = [col for col in all_columns if 'vs' in str(col).lower() or 'v' in str(col).lower()]
        self.safe_log('info', f"Potential vs columns: {vs_columns}")
        
        return True

    def process_dashboard_data(self, sheets):
        """🔧 SUPER FIXED: Process dashboard data with ALL metrics properly + TOTAL card"""
        try:
            self.safe_log('info', "🔄 Processing dashboard data with all metrics + Total...", "Processing dashboard data with all metrics + Total...")
            
            dashboard_df = sheets['d.dashboard']
            self.safe_log('info', f"Dashboard columns: {list(dashboard_df.columns)}")
            
            # 🔍 DEBUG: Inspect data structure
            self.debug_dashboard_data(dashboard_df)
            
            # Process LOB cards with all vs metrics
            lob_cards = []
            total_data = None  # ✅ NEW: Store TOTAL data separately
            
            for index, row in dashboard_df.iterrows():
                if pd.notna(row.get('LOB', '')) and row.get('LOB', '').strip() != '':
                    lob_name = str(row['LOB']).strip()
                    
                    self.safe_log('info', f"🎯 Processing LOB: {lob_name}")
                    
                    # 🔧 SUPER FIXED: Get raw values properly
                    actual_raw = row.get('Actual', 0)
                    bp_raw = row.get('BP', 1)
                    gap_raw = row.get('Gap', 0)
                    
                    # Convert to numbers
                    actual = self.safe_float(actual_raw)
                    bp = self.safe_float(bp_raw)
                    gap = self.safe_float(gap_raw)
                    
                    # Achievement calculation
                    achievement = (actual / bp * 100) if bp > 0 else 0
                    
                    # 🔧 SUPER FIXED: Get vs metrics with comprehensive column checking
                    vs_bp_raw = self.get_comprehensive_vs_metric(row, dashboard_df.columns, ['vs BP', 'vs_BP', 'vsBP', 'VS BP', 'vs bp'])
                    vs_ly_raw = self.get_comprehensive_vs_metric(row, dashboard_df.columns, ['vs LY', 'vs_LY', 'vsLY', 'VS LY', 'vs ly'])
                    vs_3lm_raw = self.get_comprehensive_vs_metric(row, dashboard_df.columns, ['vs 3LM', 'vs_3LM', 'vs3LM', 'VS 3LM', 'vs 3lm'])
                    vs_lm_raw = self.get_comprehensive_vs_metric(row, dashboard_df.columns, ['vs LM', 'vs_LM', 'vsLM', 'VS LM', 'vs lm'])
                    
                    # 🔧 SUPER FIXED: Parse percentage values properly
                    vs_bp = self.parse_percentage_value(vs_bp_raw)
                    vs_ly = self.parse_percentage_value(vs_ly_raw) 
                    vs_3lm = self.parse_percentage_value(vs_3lm_raw)
                    vs_lm = self.parse_percentage_value(vs_lm_raw)
                    
                    # ✅ NEW: Handle TOTAL row separately
                    if lob_name.upper() == 'TOTAL':
                        total_data = {
                            'name': 'TOTAL',
                            'achievement': f"{self.safe_percentage(achievement)}%",
                            'actual': self.format_currency_indonesia(actual),
                            'target': self.format_currency_indonesia(bp),
                            'gap': self.format_currency_indonesia(abs(gap)),
                            'vs_bp': f"{'+' if vs_bp >= 0 else ''}{vs_bp}%",
                            'vs_ly': f"{'+' if vs_ly >= 0 else ''}{vs_ly}%", 
                            'vs_3lm': f"{'+' if vs_3lm >= 0 else ''}{vs_3lm}%",
                            'vs_lm': f"{'+' if vs_lm >= 0 else ''}{vs_lm}%"
                        }
                        self.safe_log('info', f"✅ Stored TOTAL data: {total_data['achievement']}, Actual: {total_data['actual']}, Target: {total_data['target']}, Gap: {total_data['gap']}", 
                                    f"[OK] Stored TOTAL data: {total_data['achievement']}, Actual: {total_data['actual']}")
                        continue  # Skip adding TOTAL to individual LOB cards
                    
                    # 🔧 DEBUGGING: Log found values
                    self.safe_log('info', f"DEBUG {lob_name}:")
                    self.safe_log('info', f"  Actual: {actual_raw} -> {actual}")
                    self.safe_log('info', f"  BP: {bp_raw} -> {bp}")
                    self.safe_log('info', f"  Achievement: {achievement:.1f}%")
                    self.safe_log('info', f"  vs_BP: {vs_bp_raw} -> {vs_bp}%")
                    self.safe_log('info', f"  vs_LY: {vs_ly_raw} -> {vs_ly}%")
                    self.safe_log('info', f"  vs_3LM: {vs_3lm_raw} -> {vs_3lm}%")
                    self.safe_log('info', f"  vs_LM: {vs_lm_raw} -> {vs_lm}%")
                    
                    lob_card = {
                        'name': lob_name,
                        'achievement': f"{self.safe_percentage(achievement)}%",
                        'actual': self.format_currency_indonesia(actual),
                        'target': self.format_currency_indonesia(bp),
                        'gap': self.format_currency_indonesia(abs(gap)),
                        'vs_bp': f"{'+' if vs_bp >= 0 else ''}{vs_bp}%",
                        'vs_ly': f"{'+' if vs_ly >= 0 else ''}{vs_ly}%", 
                        'vs_3lm': f"{'+' if vs_3lm >= 0 else ''}{vs_3lm}%",
                        'vs_lm': f"{'+' if vs_lm >= 0 else ''}{vs_lm}%"
                    }
                    
                    lob_cards.append(lob_card)
                    self.safe_log('info', f"✅ Added LOB: {lob_card['name']} - Ach:{lob_card['achievement']}, vs LM:{lob_card['vs_lm']}, vs 3LM:{lob_card['vs_3lm']}, vs LY:{lob_card['vs_ly']}", 
                                f"[OK] Added LOB: {lob_card['name']} - Ach:{lob_card['achievement']}, vs LM:{lob_card['vs_lm']}, vs 3LM:{lob_card['vs_3lm']}, vs LY:{lob_card['vs_ly']}")
            
            self.safe_log('info', f"✅ Processed {len(lob_cards)} LOB cards + TOTAL data with all metrics", f"[OK] Processed {len(lob_cards)} LOB cards + TOTAL data with all metrics")
            
            # ✅ NEW: Include total_data in return
            result = {
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'depo_name': 'Depo Tanjung',
                'region_name': 'Region Kalimantan',
                'lob_cards': lob_cards
            }
            
            # ✅ NEW: Add total_data if available
            if total_data:
                result['total_data'] = total_data
                self.safe_log('info', f"✅ Added TOTAL data to result: {total_data['name']} - {total_data['achievement']}", 
                            f"[OK] Added TOTAL data to result: {total_data['name']} - {total_data['achievement']}")
            else:
                self.safe_log('warning', "⚠️ No TOTAL data found in dashboard")
            
            return result
            
        except Exception as e:
            self.safe_log('error', f"Error processing dashboard data: {str(e)}")
            return None

    def get_comprehensive_vs_metric(self, row, all_columns, possible_names):
        """🔧 SUPER FIXED: Comprehensive column name matching"""
        # First try exact matches
        for col_name in possible_names:
            if col_name in all_columns:
                value = row.get(col_name)
                if pd.notna(value) and value != 0:
                    self.safe_log('info', f"Found exact match: {col_name} = {value}")
                    return value
        
        # Then try partial matches (case insensitive)
        for target in possible_names:
            for actual_col in all_columns:
                if target.lower().replace(' ', '').replace('_', '') == str(actual_col).lower().replace(' ', '').replace('_', ''):
                    value = row.get(actual_col)
                    if pd.notna(value) and value != 0:
                        self.safe_log('info', f"Found partial match: {actual_col} = {value}")
                        return value
        
        # If still not found, log all column names for debugging
        self.safe_log('warning', f"Could not find vs metric from options: {possible_names}")
        self.safe_log('warning', f"Available columns: {all_columns}")
        return 0

    def parse_percentage_value(self, value):
        """🔧 SUPER FIXED: Parse percentage values properly"""
        if pd.isna(value) or value == 0:
            return 0
            
        try:
            # If it's already a number, use it directly
            if isinstance(value, (int, float)):
                # Check if it's already a percentage (between -100 and 100) or decimal (between -1 and 1)
                if -1 <= value <= 1:
                    return int(round(value * 100))  # Convert decimal to percentage
                else:
                    return int(round(value))  # Already a percentage
            
            # If it's a string, parse it
            if isinstance(value, str):
                # Remove percentage sign and whitespace
                clean_value = str(value).strip().replace('%', '').replace(',', '')
                
                # Handle negative values
                if '(' in clean_value and ')' in clean_value:
                    clean_value = '-' + clean_value.replace('(', '').replace(')', '')
                
                return int(round(float(clean_value)))
            
            return int(round(float(value)))
            
        except (ValueError, TypeError):
            self.safe_log('warning', f"Could not parse percentage value: {value}")
            return 0

    def format_currency_indonesia(self, value):
        """🔧 FIXED: Format currency dengan format Indonesia yang benar (Rb/Jt/M)"""
        try:
            val = float(value)
            
            # Format sesuai standar Indonesia
            if val >= 1000000000:  # >= 1 Miliar
                return f"{val/1000000000:.1f}M"
            elif val >= 1000000:  # >= 1 Juta, < 1 Miliar  
                return f"{val/1000000:.1f}Jt"
            elif val >= 1000:  # >= 1 Ribu, < 1 Juta
                return f"{val/1000:.0f}Rb"
            else:  # < 1 Ribu
                return f"{val:.0f}"
        except:
            return "0"

    def process_salesman_data(self, sheets):
        """Process salesman data for ranking and login"""
        try:
            self.safe_log('info', "🔄 Processing salesman data for ranking and login...", "Processing salesman data for ranking and login...")
            
            performance_df = sheets['d.performance']
            self.safe_log('info', f"Performance columns: {list(performance_df.columns)}")
            
            salesman_list = []
            
            for _, row in performance_df.iterrows():
                if pd.notna(row.get('szEmployeeId', '')) and pd.notna(row.get('szname', '')):
                    nik = str(int(float(row['szEmployeeId']))) if pd.notna(row['szEmployeeId']) else ''
                    name = str(row['szname']).strip()
                    
                    if nik and name:
                        # Calculate achievement
                        actual = self.safe_float(row.get('Actual', 0))
                        target = self.safe_float(row.get('Target', 1))
                        achievement = (actual / target * 100) if target > 0 else 0
                        
                        # Determine status
                        status = self.determine_status(achievement)
                        
                        salesman_data = {
                            'id': nik,  # szEmployeeId as login ID
                            'name': name,
                            'achievement': f"{self.safe_percentage(achievement)}%",
                            'actual': self.format_currency_indonesia(actual),
                            'target': self.format_currency_indonesia(target),
                            'rank': int(row.get('Rank', 0)) if pd.notna(row.get('Rank')) else 0,
                            'type': str(row.get('Tipe Salesman', 'Sales')).strip(),
                            'status': status
                        }
                        
                        salesman_list.append(salesman_data)
                        self.safe_log('info', f"✅ Added salesman: szEmployeeId {salesman_data['id']} - {salesman_data['name']} - {salesman_data['achievement']}", 
                                    f"[OK] Added salesman: szEmployeeId {salesman_data['id']} - {salesman_data['name']} - {salesman_data['achievement']}")
            
            # Sort by rank
            salesman_list.sort(key=lambda x: x['rank'] if x['rank'] > 0 else 999)
            
            self.safe_log('info', f"✅ Processed {len(salesman_list)} salesman with szEmployeeId authentication", f"[OK] Processed {len(salesman_list)} salesman with szEmployeeId authentication")
            
            return salesman_list
            
        except Exception as e:
            self.safe_log('error', f"Error processing salesman data: {str(e)}")
            return []

    def determine_status(self, achievement):
        """Determine performance status based on achievement"""
        if achievement >= 100:
            return 'Excellent'
        elif achievement >= 90:
            return 'Very Good'
        elif achievement >= 70:
            return 'Good'
        else:
            return 'Extra Effort'

    def process_salesman_detail(self, sheets):
        """Process detailed salesman data with szEmployeeId mapping + TOTAL & Ranking"""
        try:
            self.safe_log('info', "🔄 Processing salesman details with szEmployeeId mapping + TOTAL & Ranking...", "Processing salesman details with szEmployeeId mapping + TOTAL & Ranking...")
            
            lob_df = sheets['d.salesmanlob']
            process_df = sheets['d.salesmanproses'] 
            performance_df = sheets['d.performance']  # Add performance sheet for TOTAL & Ranking
            
            self.safe_log('info', f"LOB columns: {list(lob_df.columns)}")
            self.safe_log('info', f"Performance columns: {list(performance_df.columns)}")
            
            salesman_details = {}
            
            # Process LOB performance by szEmployeeId
            for _, row in lob_df.iterrows():
                if pd.notna(row.get('szEmployeeId', '')) and pd.notna(row.get('LOB', '')):
                    nik = str(int(float(row['szEmployeeId']))) if pd.notna(row['szEmployeeId']) else ''
                    lob_name = str(row['LOB']).strip()
                    
                    if nik and lob_name:
                        if nik not in salesman_details:
                            salesman_details[nik] = {
                                'name': str(row.get('szname', '')).strip(),
                                'sac': str(row.get('Nama SAC', '')).strip(),
                                'type': str(row.get('Tipe Salesman', '')).strip(),
                                'performance': {},
                                'metrics': {}
                            }
                        
                        # Calculate LOB achievement
                        actual = self.safe_float(row.get('Actual', 0))
                        target = self.safe_float(row.get('Target', 1))
                        achievement = (actual / target * 100) if target > 0 else 0
                        
                        # Calculate gap (Actual - Target)
                        gap = actual - target
                        
                        # Store data in format expected by HTML
                        salesman_details[nik]['performance'][lob_name] = {
                            'actual': actual,
                            'target': target,
                            'percentage': int(round(achievement)),
                            'gap': gap
                        }
                        
                        self.safe_log('info', f"✅ Added performance for szEmployeeId {nik}, LOB {lob_name}: {self.safe_percentage(achievement)}%, Gap: {self.format_currency_indonesia(gap)}", 
                                    f"[OK] Added performance for szEmployeeId {nik}, LOB {lob_name}: {self.safe_percentage(achievement)}%, Gap: {self.format_currency_indonesia(gap)}")
            
            # Process additional metrics
            self.safe_log('info', f"Process columns: {list(process_df.columns)}")
            
            for _, row in process_df.iterrows():
                if pd.notna(row.get('szEmployeeId', '')):
                    nik = str(int(float(row['szEmployeeId']))) if pd.notna(row['szEmployeeId']) else ''
                    
                    if nik and nik in salesman_details:
                        # Calculate key process metrics
                        ca = self.safe_float(row.get('Ach_CA', 0))
                        gp_food = self.safe_float(row.get('Ach_GPFood', 0))
                        gp_others = self.safe_float(row.get('Ach_GPOthers', 0))
                        
                        # Calculate averages and combined metrics
                        ca_prod_w = self.safe_float(row.get('Ach_CAProdW', 0))
                        ca_prod_r = self.safe_float(row.get('Ach_CAProdR', 0))
                        ca_prod_m = self.safe_float(row.get('Ach_CAProdM', 0))
                        ca_prod_all = self.safe_float(row.get('Ach_CAProdAll', 0))
                        
                        avg_sku = self.safe_float(row.get('Ach_AvgSKU', 0))
                        
                        # Store metrics in expected format
                        salesman_details[nik]['metrics'] = {
                            'CA': int(round(ca)),
                            'CAProd': int(round(ca_prod_all)) if ca_prod_all > 0 else int(round((ca_prod_w + ca_prod_r + ca_prod_m) / 3)) if (ca_prod_w + ca_prod_r + ca_prod_m) > 0 else 0,
                            'SKU': int(round(avg_sku)),
                            'GP': int(round((gp_food + gp_others) / 2)) if (gp_food + gp_others) > 0 else 0
                        }
                        
                        self.safe_log('info', f"✅ Added metrics for szEmployeeId {nik}: CA:{ca}%, GP:{(gp_food + gp_others) / 2:.1f}%", 
                                    f"[OK] Added metrics for szEmployeeId {nik}: CA:{ca}%, GP:{(gp_food + gp_others) / 2:.1f}%")
            
            # 🆕 NEW: Add TOTAL and Ranking from d.performance sheet
            self.safe_log('info', "🎯 Adding TOTAL and Ranking data from d.performance...", "[TARGET] Adding TOTAL and Ranking data from d.performance...")
            
            # Get total salesman count for ranking context
            total_salesman_count = len([nik for nik in salesman_details.keys() if nik])
            
            for _, row in performance_df.iterrows():
                if pd.notna(row.get('szEmployeeId', '')):
                    nik = str(int(float(row['szEmployeeId']))) if pd.notna(row['szEmployeeId']) else ''
                    
                    if nik and nik in salesman_details:
                        # Get TOTAL performance data from d.performance
                        total_actual = self.safe_float(row.get('Actual', 0))
                        total_target = self.safe_float(row.get('Target', 1))
                        total_achievement = (total_actual / total_target * 100) if total_target > 0 else 0
                        total_gap = total_actual - total_target
                        
                        # Add TOTAL section
                        salesman_details[nik]['TOTAL'] = {
                            'actual': total_actual,
                            'target': total_target,
                            'percentage': int(round(total_achievement)),
                            'gap': total_gap
                        }
                        
                        # Get ranking information
                        rank = int(row.get('Rank', 0)) if pd.notna(row.get('Rank')) else 0
                        
                        # Add Ranking section
                        salesman_details[nik]['Ranking'] = {
                            'Rank': rank,
                            'total_salesman': total_salesman_count
                        }
                        
                        self.safe_log('info', f"✅ Added TOTAL for szEmployeeId {nik}: Actual={self.format_currency_indonesia(total_actual)}, Target={self.format_currency_indonesia(total_target)}, Achievement={total_achievement:.1f}%, Gap={self.format_currency_indonesia(total_gap)}", 
                                    f"[OK] Added TOTAL for szEmployeeId {nik}: Achievement={total_achievement:.1f}%, Rank={rank}/{total_salesman_count}")
                        
                        self.safe_log('info', f"✅ Added Ranking for szEmployeeId {nik}: Rank {rank} of {total_salesman_count} salesman", 
                                    f"[OK] Added Ranking for szEmployeeId {nik}: Rank {rank} of {total_salesman_count}")
            
            self.safe_log('info', f"✅ Processed details for {len(salesman_details)} salesman with szEmployeeId keys + Gap field + TOTAL + Ranking", f"[OK] Processed details for {len(salesman_details)} salesman with szEmployeeId keys + Gap field + TOTAL + Ranking")
            
            return salesman_details
            
        except Exception as e:
            self.safe_log('error', f"Error processing salesman details: {str(e)}")
            return {}
            
    def generate_chart_data(self, sheets):
        """🔧 FIXED: Generate chart data dengan format Indonesia Rb/Jt/M"""
        try:
            # Get period info
            data_period = self.get_period_from_data(sheets)
            self.safe_log('info', f"📅 Period from data: {data_period}", f"[DATE] Period from data: {data_period}")
            
            # Process SO data
            so_df = sheets['d.soharian']
            
            # Convert date column and ensure numeric columns
            if 'Tgl' in so_df.columns:
                so_df['Tgl'] = pd.to_datetime(so_df['Tgl'], errors='coerce')
                so_df = so_df.dropna(subset=['Tgl'])
                so_df = so_df.sort_values('Tgl')
            
            # Ensure numeric columns
            for col in ['Target', 'SO', 'DO']:
                if col in so_df.columns:
                    so_df[col] = pd.to_numeric(so_df[col], errors='coerce').fillna(0)
            
            self.safe_log('info', f"📊 Processing {len(so_df)} rows for modern chart", f"[CHART] Processing {len(so_df)} rows for modern chart")
            self.safe_log('info', f"📊 Columns in soharian: {list(so_df.columns)}", f"[CHART] Columns in soharian: {list(so_df.columns)}")
            
            # Generate chart data in format expected by HTML
            so_data = []
            do_data = []
            target_data = []
            labels = []
            
            for _, row in so_df.iterrows():
                if pd.notna(row.get('Tgl')):
                    date_val = row['Tgl']
                    
                    # Format data for chart
                    so_value = int(self.safe_float(row.get('SO', 0)))
                    do_value = int(self.safe_float(row.get('DO', 0)))
                    target_value = int(self.safe_float(row.get('Target', 0)))
                    
                    so_data.append(so_value)
                    do_data.append(do_value)
                    target_data.append(target_value)
                    
                    # Format label
                    day_label = date_val.strftime('%d') if hasattr(date_val, 'strftime') else str(date_val).split('-')[-1]
                    labels.append(day_label)
            
            # Calculate statistics
            total_target = sum(target_data)
            total_so = sum(so_data)
            total_do = sum(do_data)
            
            # 🔧 FIXED: Format stats dengan format Indonesia yang benar
            avg_target_formatted = self.format_currency_indonesia(total_target / len(target_data)) if target_data else "0"
            avg_so_formatted = self.format_currency_indonesia(total_so / len(so_data)) if so_data else "0"
            avg_do_formatted = self.format_currency_indonesia(total_do / len(do_data)) if do_data else "0"
            
            # Count working days
            total_hk = len(so_data)
            current_date = datetime.now()
            remaining_days = 0
            
            for i, label in enumerate(labels):
                try:
                    # Reconstruct date to check if it's in the future
                    day = int(label)
                    current_month = current_date.month
                    current_year = current_date.year
                    check_date = datetime(current_year, current_month, day)
                    
                    if check_date > current_date:
                        remaining_days += 1
                except:
                    pass
            
            sisa_hk_do = max(0, remaining_days)
            
            # Format chart data correctly
            chart_data = {
                'period': data_period,
                'so_data': so_data,
                'do_data': do_data,
                'target_data': target_data,
                'labels': labels,
                'stats': {
                    'avg_target': avg_target_formatted,  # 🔧 FIXED: Format Indonesia
                    'avg_so': avg_so_formatted,         # 🔧 FIXED: Format Indonesia
                    'avg_do': avg_do_formatted,         # 🔧 FIXED: Format Indonesia
                    'total_hk': total_hk,
                    'sisa_hk_do': sisa_hk_do
                }
            }
            
            # Add gap total from dashboard
            chart_data['stats']['gap_total'] = self.get_gap_total_from_dashboard(sheets)
            
            self.safe_log('info', f"✅ Modern chart data processed: {len(chart_data['so_data'])} days", f"[OK] Modern chart data processed: {len(chart_data['so_data'])} days")
            self.safe_log('info', f"📊 Period: {data_period}", f"[CHART] Period: {data_period}")
            self.safe_log('info', f"📈 Stats: SO={chart_data['stats']['avg_so']}, DO={chart_data['stats']['avg_do']}, Target={chart_data['stats']['avg_target']}", 
                        f"[TREND] Stats: SO={chart_data['stats']['avg_so']}, DO={chart_data['stats']['avg_do']}, Target={chart_data['stats']['avg_target']}")
            self.safe_log('info', f"📅 HK: Total={chart_data['stats']['total_hk']}, Sisa DO={chart_data['stats']['sisa_hk_do']}", 
                        f"[DATE] HK: Total={chart_data['stats']['total_hk']}, Sisa DO={chart_data['stats']['sisa_hk_do']}")
            self.safe_log('info', f"💰 Gap Total: {chart_data['stats']['gap_total']}", f"[MONEY] Gap Total: {chart_data['stats']['gap_total']}")
            
            return chart_data
            
        except Exception as e:
            self.safe_log('error', f"Error generating chart data: {str(e)}")
            return None

    # Helper methods
    def safe_float(self, value):
        """Safely convert value to float"""
        try:
            if pd.isna(value):
                return 0.0
            if isinstance(value, str):
                # Handle percentage strings
                if '%' in value:
                    return float(value.replace('%', ''))
                # Handle currency strings with commas
                value = value.replace(',', '').replace('(', '-').replace(')', '')
            return float(value)
        except:
            return 0.0
    
    def safe_percentage(self, value):
        """Safely format percentage"""
        try:
            return int(round(float(value)))
        except:
            return 0
    
    def format_currency(self, value):
        """🔧 LEGACY: Keep for backward compatibility"""
        return self.format_currency_indonesia(value)

    def get_period_from_data(self, sheets):
        """Extract period information from data"""
        try:
            # Try to get from soharian sheet dates
            so_df = sheets.get('d.soharian')
            if so_df is not None and 'Tgl' in so_df.columns:
                dates = pd.to_datetime(so_df['Tgl'], errors='coerce').dropna()
                if len(dates) > 0:
                    latest_date = dates.max()
                    month_name = latest_date.strftime('%B') if hasattr(latest_date, 'strftime') else 'Juni'
                    year = latest_date.year if hasattr(latest_date, 'year') else 2025
                    
                    # Translate month to Indonesian
                    month_id = {
                        'January': 'Januari', 'February': 'Februari', 'March': 'Maret',
                        'April': 'April', 'May': 'Mei', 'June': 'Juni',
                        'July': 'Juli', 'August': 'Agustus', 'September': 'September', 
                        'October': 'Oktober', 'November': 'November', 'December': 'Desember'
                    }.get(month_name, month_name)
                    
                    period = f"{month_id} {year}"
                    self.safe_log('info', f"📅 Period from data: {period}", f"[DATE] Period from data: {period}")
                    return period
        except Exception as e:
            self.safe_log('warning', f"Could not extract period from data: {str(e)}")
        
        # Fallback to current date
        current_date = datetime.now()
        month_id = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
                   'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'][current_date.month - 1]
        return f"{month_id} {current_date.year}"

    def get_gap_total_from_dashboard(self, sheets):
        """Get Gap Total from dashboard data dengan format Indonesia"""
        try:
            dashboard_df = sheets.get('d.dashboard')
            if dashboard_df is not None:
                self.safe_log('info', f"🔍 Looking for Gap Total in dashboard with {len(dashboard_df)} rows", f"[SEARCH] Looking for Gap Total in dashboard with {len(dashboard_df)} rows")
                
                # Look for TOTAL row
                for _, row in dashboard_df.iterrows():
                    lob_name = str(row.get('LOB', '')).strip().upper()
                    if lob_name == 'TOTAL':
                        gap_value = self.safe_float(row.get('Gap', 0))
                        
                        # Format gap value using Indonesian format
                        if gap_value != 0:
                            gap_formatted = self.format_currency_indonesia(abs(gap_value))
                            self.safe_log('info', f"✅ Found Gap Total: {gap_formatted} for LOB: {lob_name}", f"[OK] Found Gap Total: {gap_formatted} for LOB: {lob_name}")
                            return gap_formatted
                
                self.safe_log('warning', "Gap Total not found in dashboard")
                return "0"
        except Exception as e:
            self.safe_log('error', f"Error getting gap total: {str(e)}")
        
        return "0"

    def validate_data(self, sheets):
        """Validate that all required data is present"""
        try:
            self.safe_log('info', "🔍 Validating data...", "Validating data...")
            
            # 🆕 UPDATED: d.insentif is optional
            required_sheets = ['d.dashboard', 'd.performance', 'd.salesmanlob', 'd.salesmanproses', 'd.soharian']
            optional_sheets = ['d.insentif']
            
            for sheet_name in required_sheets:
                if sheet_name not in sheets:
                    self.safe_log('error', f"Required sheet missing: {sheet_name}")
                    return False
                    
                if sheets[sheet_name].empty:
                    self.safe_log('error', f"Sheet is empty: {sheet_name}")
                    return False
            
            # Check optional sheets
            for sheet_name in optional_sheets:
                if sheet_name in sheets:
                    self.safe_log('info', f"✅ Optional sheet found: {sheet_name}", f"[OK] Optional sheet found: {sheet_name}")
                else:
                    self.safe_log('info', f"ℹ️ Optional sheet not found: {sheet_name} (will be skipped)", f"[INFO] Optional sheet not found: {sheet_name}")
            
            self.safe_log('info', "✅ Data validation passed", "[OK] Data validation passed")
            return True
            
        except Exception as e:
            self.safe_log('error', f"Validation error: {str(e)}")
            return False

    def check_html_files(self):
        """🆕 NEW: Check if HTML files exist and are ready for deployment"""
        try:
            self.safe_log('info', "🔍 Checking HTML dashboard files...", "[SEARCH] Checking HTML dashboard files...")
            
            # List of HTML files to check
            html_files = [
                'index.html',
                'dashboard.html',
                'dashboard-desktop.html'
            ]
            
            existing_files = []
            missing_files = []
            
            for file in html_files:
                if os.path.exists(file):
                    file_size = os.path.getsize(file)
                    mod_time = datetime.fromtimestamp(os.path.getmtime(file))
                    existing_files.append(file)
                    self.safe_log('info', f"✅ Found: {file} ({file_size:,} bytes, modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')})", f"[OK] Found: {file}")
                else:
                    missing_files.append(file)
                    self.safe_log('warning', f"⚠️  Missing: {file}")
            
            if missing_files:
                self.safe_log('warning', f"Missing HTML files: {missing_files}")
            
            self.safe_log('info', f"📱 Found {len(existing_files)} HTML files for deployment", f"[MOBILE] Found {len(existing_files)} HTML files for deployment")
            return existing_files
            
        except Exception as e:
            self.safe_log('error', f"Error checking HTML files: {str(e)}")
            return []

    def generate_json_files(self, sheets):
        """🆕 UPDATED: Generate all JSON files with complete data + incentive data"""
        try:
            self.safe_log('info', "🔄 Processing Excel data to JSON with format Indonesia Rb/Jt/M + Gap field + Incentive...", "Processing Excel data to JSON with format Indonesia + Gap field + Incentive...")
            
            # Process all data
            dashboard_data = self.process_dashboard_data(sheets)
            salesman_list = self.process_salesman_data(sheets)
            salesman_details = self.process_salesman_detail(sheets)
            incentive_data = self.process_insentif_data(sheets)  # 🆕 NEW: Process incentive data
            
            if not dashboard_data or not salesman_list:
                self.safe_log('error', "Failed to process required data")
                return False
            
            # Save dashboard data
            dashboard_file = os.path.join(self.data_dir, 'dashboard.json')
            with open(dashboard_file, 'w', encoding='utf-8') as f:
                json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
            self.safe_log('info', f"✅ Saved: {dashboard_file} with format Indonesia", f"[OK] Saved: {dashboard_file} with format Indonesia")
            
            # Save salesman list
            list_file = os.path.join(self.data_dir, 'salesman_list.json')
            with open(list_file, 'w', encoding='utf-8') as f:
                json.dump(salesman_list, f, indent=2, ensure_ascii=False)
            self.safe_log('info', f"✅ Saved: {list_file} with format Indonesia", f"[OK] Saved: {list_file} with format Indonesia")
            
            # Save salesman details 
            details_file = os.path.join(self.data_dir, 'salesman_details.json')
            with open(details_file, 'w', encoding='utf-8') as f:
                json.dump(salesman_details, f, indent=2, ensure_ascii=False)
            self.safe_log('info', f"✅ Saved: {details_file} with format Indonesia + Gap field", f"[OK] Saved: {details_file} with format Indonesia + Gap field")
            
            # Generate and save chart data
            chart_data = self.generate_chart_data(sheets)
            if chart_data:
                chart_file = os.path.join(self.data_dir, 'chart_data.json')
                with open(chart_file, 'w', encoding='utf-8') as f:
                    json.dump(chart_data, f, indent=2, ensure_ascii=False)
                self.safe_log('info', f"✅ Saved: {chart_file} with format Indonesia", f"[OK] Saved: {chart_file} with format Indonesia")
            
            # 🆕 NEW: Save incentive data in JSONL format (matching your sample structure)
            if incentive_data:
                incentive_file = os.path.join(self.data_dir, 'd.insentif.json')
                with open(incentive_file, 'w', encoding='utf-8') as f:
                    for record in incentive_data:
                        # Write each record as a single line JSON (JSONL format)
                        json.dump(record, f, ensure_ascii=False)
                        f.write('\n')
                self.safe_log('info', f"✅ Saved: {incentive_file} in JSONL format with {len(incentive_data)} records", f"[OK] Saved: {incentive_file} in JSONL format with {len(incentive_data)} records")
            else:
                self.safe_log('warning', "No incentive data to save - d.insentif.json will not be created")
            
            # 🆕 UPDATED: Count files generated
            total_files = 4 + (1 if incentive_data else 0)
            self.safe_log('info', f"🎉 Generated {total_files} JSON files with Indonesia format (Rb/Jt/M) + Gap field + Incentive!", f"[SUCCESS] Generated {total_files} JSON files with Indonesia format + Gap field + Incentive!")
            self.safe_log('info', "📋 Files updated with Rb/Jt/M format + Gap field + Incentive:", "[LIST] Files updated with Rb/Jt/M format + Gap field + Incentive:")
            
            files = ['dashboard.json', 'salesman_list.json', 'salesman_details.json', 'chart_data.json']
            if incentive_data:
                files.append('d.insentif.json')
            
            for file in files:
                self.safe_log('info', f"   - {file}")
            
            return True
            
        except Exception as e:
            self.safe_log('error', f"Error generating JSON files: {str(e)}")
            return False

    def git_push_changes(self):
        """🔧 ENHANCED: FIXED Push changes to GitHub with proper error handling"""
        try:
            self.safe_log('info', "🚀 Pushing to GitHub with improved error handling...", "Pushing to GitHub with improved error handling...")
            
            # Check HTML files first
            html_files = self.check_html_files()
            
            # 🔧 FIXED: Check git status first
            try:
                status_result = subprocess.run(['git', 'status', '--porcelain'], 
                                              capture_output=True, text=True, cwd='.')
                if status_result.returncode != 0:
                    self.safe_log('error', f"Git status failed: {status_result.stderr}")
                    return False
                
                # Check if there are any changes
                if not status_result.stdout.strip():
                    self.safe_log('info', "No changes detected in git repository")
                    return True
                
                self.safe_log('info', f"Git status output:\n{status_result.stdout}")
                
            except Exception as e:
                self.safe_log('error', f"Error checking git status: {str(e)}")
                return False
            
            # 🔧 FIXED: Add files with better error handling
            files_to_add = [
                'data/',
                'index.html',
                'dashboard.html',
                'dashboard-desktop.html',
                'salesman-desktop.html',
                'salesman-detail.html',
                'profile.html',
                'dashboard_insentif_sales_desktop.html',
                'morning_update.py',
                'morning_update.log'
            ]
            
            # Add files one by one with detailed logging
            for file_pattern in files_to_add:
                try:
                    if os.path.exists(file_pattern.rstrip('/')):
                        add_result = subprocess.run(['git', 'add', file_pattern], 
                                                  capture_output=True, text=True, cwd='.')
                        if add_result.returncode == 0:
                            self.safe_log('info', f"✅ Added: {file_pattern}", f"[OK] Added: {file_pattern}")
                        else:
                            self.safe_log('warning', f"⚠️ Failed to add {file_pattern}: {add_result.stderr}")
                    else:
                        self.safe_log('warning', f"⚠️ File not found: {file_pattern}")
                except Exception as e:
                    self.safe_log('error', f"Error adding {file_pattern}: {str(e)}")
            
            # 🔧 FIXED: Check git status after adding
            try:
                status_after_add = subprocess.run(['git', 'status', '--porcelain'], 
                                                 capture_output=True, text=True, cwd='.')
                if status_after_add.returncode == 0:
                    self.safe_log('info', f"Git status after add:\n{status_after_add.stdout}")
                else:
                    self.safe_log('warning', f"Could not check git status after add: {status_after_add.stderr}")
            except Exception as e:
                self.safe_log('warning', f"Error checking git status after add: {str(e)}")
            
            # 🔧 FIXED: Commit with better error handling
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            commit_message = f"""Morning update: {current_time} - ENHANCED Dashboard System + Incentive Support

📱 Mobile Dashboard (dashboard.html) - Optimized for smartphones
💻 Desktop Dashboard (dashboard-desktop.html) - Optimized for laptops/PC
🔧 Updated Features:
   - Indonesian number format (Rb/Jt/M)
   - vs metrics display (vs LM/3LM/LY)
   - Gap field calculation (Actual - Target)
   - Device-specific dashboard selection
   - Enhanced user experience
💸 NEW: Incentive Data Support (d.insentif.json)
   - JSONL format for application compatibility
   - Complete incentive calculations
   - Sales and Process incentives

🔐 Login: admin/admin123 or szEmployeeId/sales123"""

            try:
                commit_result = subprocess.run(['git', 'commit', '-m', commit_message], 
                                              capture_output=True, text=True, cwd='.')
                
                if commit_result.returncode == 0:
                    self.safe_log('info', "✅ Git commit successful", "[OK] Git commit successful")
                    self.safe_log('info', f"Commit output: {commit_result.stdout}")
                else:
                    if "nothing to commit" in commit_result.stdout:
                        self.safe_log('info', "No changes to commit - repository is up to date")
                        return True
                    else:
                        self.safe_log('error', f"Git commit failed: {commit_result.stderr}")
                        self.safe_log('error', f"Git commit stdout: {commit_result.stdout}")
                        return False
                        
            except Exception as e:
                self.safe_log('error', f"Error during git commit: {str(e)}")
                return False
            
            # 🔧 FIXED: Push with better error handling
            try:
                push_result = subprocess.run(['git', 'push', 'origin', 'main'], 
                                           capture_output=True, text=True, cwd='.')
                
                if push_result.returncode == 0:
                    self.safe_log('info', "✅ Successfully pushed to GitHub!", "[OK] Successfully pushed to GitHub!")
                    self.safe_log('info', f"Push output: {push_result.stdout}")
                    
                    # Show deployment URLs
                    self.safe_log('info', "🌐 Deployment URLs:", "[WEB] Deployment URLs:")
                    self.safe_log('info', "   🏠 Main Login: https://kisman271128.github.io/salesman-dashboard/")
                    self.safe_log('info', "   📱 Mobile: https://kisman271128.github.io/salesman-dashboard/dashboard.html")
                    self.safe_log('info', "   💻 Desktop: https://kisman271128.github.io/salesman-dashboard/dashboard-desktop.html")
                    
                    return True
                else:
                    self.safe_log('error', f"Git push failed: {push_result.stderr}")
                    self.safe_log('error', f"Git push stdout: {push_result.stdout}")
                    
                    # Try to provide more helpful error messages
                    if "rejected" in push_result.stderr:
                        self.safe_log('error', "Push was rejected. This might be due to authentication issues or conflicting changes.")
                    elif "Could not resolve host" in push_result.stderr:
                        self.safe_log('error', "Network connectivity issue. Please check your internet connection.")
                    elif "Permission denied" in push_result.stderr:
                        self.safe_log('error', "Permission denied. Please check your GitHub authentication.")
                    
                    return False
                    
            except Exception as e:
                self.safe_log('error', f"Error during git push: {str(e)}")
                return False
                
        except Exception as e:
            self.safe_log('error', f"Error in git operations: {str(e)}")
            return False

    def run_morning_update(self):
        """Run the complete morning update process"""
        start_time = datetime.now()
        
        try:
            # Read Excel data
            sheets = self.read_excel_sheets()
            if not sheets:
                return False
            
            # Validate data
            if not self.validate_data(sheets):
                return False
            
            # Generate JSON files
            if not self.generate_json_files(sheets):
                return False
            
            # Push to GitHub
            if not self.git_push_changes():
                return False
            
            # Success message
            duration = (datetime.now() - start_time).total_seconds()
            
            # 🆕 NEW: Log session summary
            self.safe_log('info', "=" * 80, "=" * 50)
            self.safe_log('info', f"🎉 MORNING UPDATE COMPLETED SUCCESSFULLY!", f"[SUCCESS] MORNING UPDATE COMPLETED SUCCESSFULLY!")
            self.safe_log('info', f"⏱️  Processing time: {duration:.2f} seconds", f"[TIMER] Processing time: {duration:.2f} seconds")
            self.safe_log('info', f"📅 Session completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", f"[DATE] Session completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self.safe_log('info', "=" * 80, "=" * 50)
            
            success_message = f"""
=======================================================
🎉 MORNING UPDATE COMPLETED SUCCESSFULLY!
⏱️  Processing time: {duration:.2f} seconds

🌐 DEPLOYMENT URLS:
   🏠 Main Login: https://kisman271128.github.io/salesman-dashboard/
   📱 Mobile Dashboard: https://kisman271128.github.io/salesman-dashboard/dashboard.html
   💻 Desktop Dashboard: https://kisman271128.github.io/salesman-dashboard/dashboard-desktop.html

📊 ENHANCED FEATURES:
   💰 Indonesian Number Format - FIXED Rb/Jt/M display
   📈 vs Metrics Display - FIXED vs LM/3LM/LY showing
   🎯 Chart Stats Format - FIXED proper Rb/Jt/M format
   📊 Gap Field Added - FIXED Gap calculation (Actual - Target) for each LOB
   💸 Incentive Data Support - NEW d.insentif.json in JSONL format
   🔐 szEmployeeId Login - All salesman + admin access
   📱💻 Dual Dashboard - Mobile & Desktop optimized versions
   🎨 Device Selection - Auto-detect with manual override

🔑 LOGIN CREDENTIALS:
   Admin: admin / admin123
   Salesman: [szEmployeeId] / sales123

💡 DASHBOARD FEATURES:
   📱 Mobile Version:
      • Compact layout optimized for smartphones
      • Bottom navigation for easy thumb access
      • Touch-friendly interface elements
      
   💻 Desktop Version:
      • Sidebar navigation for larger screens
      • Multi-column layout utilizing screen space
      • Enhanced charts and tables for detailed viewing
      • Keyboard shortcuts support

🎯 AUTO DEVICE SELECTION:
   • < 768px width → Mobile Dashboard
   • ≥ 1024px width → Desktop Dashboard
   • 768-1024px → User choice (tablets)
   • Manual override always available

💸 INCENTIVE DATA:
   • d.insentif.json in JSONL format
   • Complete incentive calculations
   • Sales and Process incentives
   • Application-ready structure

💡 Format Indonesia + Data Enhancement:
   • < 1K = angka langsung (500)
   • 1K-999K = Rb (500Rb) 
   • 1Jt-999Jt = Jt (50.5Jt)
   • ≥1M = M (1.5M)
   • Gap = Actual - Target (untuk analisis performance)

📝 LOG INFO:
   • Fresh log file created for this session
   • Previous log cleared for clarity
   • All operations logged with timestamps
=======================================================
"""
            
            # Print without emoji for compatibility
            safe_message = self.remove_emoji(success_message)
            print(safe_message)
            
            return True
            
        except Exception as e:
            self.safe_log('error', f"Morning update failed: {str(e)}")
            return False

def main():
    """🆕 UPDATED: Main function - Enhanced with Desktop Dashboard + Incentive Support + Fresh Log"""
    print("🚀 SALESMAN DASHBOARD UPDATER v2.8 - ENHANCED WITH FRESH LOG SESSION")
    print("=" * 85)
    print("Running with ENHANCED FEATURES:")
    print("✅ NEW: Fresh log session (previous log cleared)")
    print("✅ FIXED git status checking before operations")
    print("✅ FIXED git add with detailed logging")
    print("✅ FIXED git commit with proper error handling")
    print("✅ FIXED git push with comprehensive error messages")
    print("✅ FIXED format Rb/Jt/M sesuai standar Indonesia")
    print("✅ FIXED vs metrics display (vs LM/3LM/LY)")
    print("✅ FIXED chart stats dengan format yang benar")
    print("✅ ADDED Gap field (Actual - Target) untuk setiap LOB") 
    print("✅ Enhanced number formatting untuk semua section")
    print("✅ ADDED Desktop dashboard untuk laptop/PC")
    print("✅ ADDED Device auto-detection & selection")
    print("✅ NEW: Incentive Data Support (d.insentif.json)")
    print("✅ NEW: Clear previous log for fresh session")
    print("=" * 80)
    
    print("\n🌅 MORNING BATCH UPDATE v2.8 - FRESH LOG SESSION")
    print("=" * 70)
    print("🚀 Version 2.8 - FRESH LOG + ENHANCED ERROR HANDLING & INCENTIVE SUPPORT:")
    print("   🗑️  NEW: Clear previous log file untuk fresh start")
    print("   📝 NEW: Session start/end logging dengan timestamps")
    print("   🔧 FIXED git status checking before operations")
    print("   🔧 FIXED git add with individual file logging")
    print("   🔧 FIXED git commit with detailed error messages")
    print("   🔧 FIXED git push with network/auth error detection")
    print("   📱 Mobile Dashboard - Optimized untuk smartphone")
    print("   💻 Desktop Dashboard - Optimized untuk laptop/PC")
    print("   🎨 Device Selection - Auto-detect dengan manual override")
    print("   ✅ FIXED Rb untuk < 1 juta (contoh: 500Rb)")
    print("   ✅ FIXED Jt untuk 1-999 juta (contoh: 50.5Jt)")
    print("   ✅ FIXED M untuk ≥ 1 miliar (contoh: 1.5M)")
    print("   ✅ FIXED vs metrics yang tidak muncul")
    print("   ✅ FIXED chart stats format Indonesia")
    print("   ✅ ADDED Gap field untuk setiap LOB performance")
    print("   💸 NEW: d.insentif.json dalam format JSONL")
    print("   💸 NEW: Complete incentive calculations")
    print("   💸 NEW: Application-ready incentive structure")
    print("=" * 65)
    
    # Create updater and run
    updater = SalesmanDashboardUpdater()
    success = updater.run_morning_update()
    
    if success:
        print("\n✅ ENHANCED DASHBOARD SYSTEM UPDATE SUCCESSFUL!")
        print("🌐 Multi-platform dashboard dengan format Rb/Jt/M yang benar")
        print("💸 Incentive data support untuk aplikasi mobile")
        print("📝 Fresh log session untuk troubleshooting yang lebih mudah")
        print("📱 Mobile: https://kisman271128.github.io/salesman-dashboard/dashboard.html")
        print("💻 Desktop: https://kisman271128.github.io/salesman-dashboard/dashboard-desktop.html")
        print("🏠 Login: https://kisman271128.github.io/salesman-dashboard/")
        sys.exit(0)
    else:
        print("\n❌ UPDATE FAILED!")
        print("❗ Check morning_update.log for details (fresh session)")
        sys.exit(1)

if __name__ == "__main__":
    main()