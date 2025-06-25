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

class SalesmanDashboardUpdater:
    def __init__(self, excel_file="DbaseSalesmanWebApp.xlsx"):
        self.excel_file = excel_file
        self.data_dir = "data"
        
        # Setup directories
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        # Setup logging dengan encoding yang aman
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        
        # Setup file handler dengan UTF-8
        file_handler = logging.FileHandler('morning_update.log', encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(log_format))
        
        # Setup console handler dengan fallback untuk emoji
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(log_format))
        
        # Configure logger
        logging.basicConfig(
            level=logging.INFO,
            handlers=[file_handler, console_handler],
            format=log_format
        )
        
        self.logger = logging.getLogger(__name__)

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
            '⏱️': '[TIMER]'
        }
        
        for emoji, replacement in emoji_map.items():
            text = text.replace(emoji, replacement)
        
        return text

    def read_excel_sheets(self):
        """Read all required sheets from Excel file"""
        try:
            self.safe_log('info', "📊 Reading Excel sheets...", "Reading Excel sheets...")
            
            # Required sheets
            required_sheets = ['d.dashboard', 'd.performance', 'd.salesmanlob', 'd.salesmanproses', 'd.soharian']
            
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
                    self.safe_log('warning', f"Sheet {sheet_name} not found in Excel file")
            
            if not sheets:
                raise Exception("No required sheets found in Excel file")
                
            return sheets
            
        except Exception as e:
            self.safe_log('error', f"Error reading Excel file: {str(e)}")
            return None

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
        """🔧 SUPER FIXED: Process dashboard data with ALL metrics properly"""
        try:
            self.safe_log('info', "🔄 Processing dashboard data with all metrics...", "Processing dashboard data with all metrics...")
            
            dashboard_df = sheets['d.dashboard']
            self.safe_log('info', f"Dashboard columns: {list(dashboard_df.columns)}")
            
            # 🔍 DEBUG: Inspect data structure
            self.debug_dashboard_data(dashboard_df)
            
            # Process LOB cards with all vs metrics
            lob_cards = []
            
            for index, row in dashboard_df.iterrows():
                if pd.notna(row.get('LOB', '')) and row.get('LOB', '').strip() != '':
                    lob_name = str(row['LOB']).strip()
                    
                    # Skip TOTAL row for individual LOB cards
                    if lob_name.upper() == 'TOTAL':
                        continue
                    
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
            
            self.safe_log('info', f"✅ Processed {len(lob_cards)} LOB cards with all metrics", f"[OK] Processed {len(lob_cards)} LOB cards with all metrics")
            
            return {
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'depo_name': 'Depo Tanjung',
                'region_name': 'Region Kalimantan',
                'lob_cards': lob_cards
            }
            
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
                if pd.notna(row.get('NIK', '')) and pd.notna(row.get('Nama Salesman', '')):
                    nik = str(int(float(row['NIK']))) if pd.notna(row['NIK']) else ''
                    name = str(row['Nama Salesman']).strip()
                    
                    if nik and name:
                        # Calculate achievement
                        actual = self.safe_float(row.get('Actual', 0))
                        target = self.safe_float(row.get('Target', 1))
                        achievement = (actual / target * 100) if target > 0 else 0
                        
                        # Determine status
                        status = self.determine_status(achievement)
                        
                        salesman_data = {
                            'id': nik,  # NIK as login ID
                            'name': name,
                            'achievement': f"{self.safe_percentage(achievement)}%",
                            'actual': self.format_currency_indonesia(actual),
                            'target': self.format_currency_indonesia(target),
                            'rank': int(row.get('Rank', 0)) if pd.notna(row.get('Rank')) else 0,
                            'type': str(row.get('Tipe Salesman', 'Sales')).strip(),
                            'status': status
                        }
                        
                        salesman_list.append(salesman_data)
                        self.safe_log('info', f"✅ Added salesman: NIK {salesman_data['id']} - {salesman_data['name']} - {salesman_data['achievement']}", 
                                    f"[OK] Added salesman: NIK {salesman_data['id']} - {salesman_data['name']} - {salesman_data['achievement']}")
            
            # Sort by rank
            salesman_list.sort(key=lambda x: x['rank'] if x['rank'] > 0 else 999)
            
            self.safe_log('info', f"✅ Processed {len(salesman_list)} salesman with NIK authentication", f"[OK] Processed {len(salesman_list)} salesman with NIK authentication")
            
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
        """Process detailed salesman data with NIK mapping"""
        try:
            self.safe_log('info', "🔄 Processing salesman details with NIK mapping...", "Processing salesman details with NIK mapping...")
            
            lob_df = sheets['d.salesmanlob']
            process_df = sheets['d.salesmanproses'] 
            
            self.safe_log('info', f"LOB columns: {list(lob_df.columns)}")
            
            salesman_details = {}
            
            # Process LOB performance by NIK
            for _, row in lob_df.iterrows():
                if pd.notna(row.get('NIK', '')) and pd.notna(row.get('LOB', '')):
                    nik = str(int(float(row['NIK']))) if pd.notna(row['NIK']) else ''
                    lob_name = str(row['LOB']).strip()
                    
                    if nik and lob_name:
                        if nik not in salesman_details:
                            salesman_details[nik] = {
                                'name': str(row.get('Nama Salesman', '')).strip(),
                                'sac': str(row.get('Nama SAC', '')).strip(),
                                'type': str(row.get('Tipe Salesman', '')).strip(),
                                'performance': {},
                                'metrics': {}
                            }
                        
                        # Calculate LOB achievement
                        actual = self.safe_float(row.get('Actual', 0))
                        target = self.safe_float(row.get('Target', 1))
                        achievement = (actual / target * 100) if target > 0 else 0
                        
                        # Store data in format expected by HTML
                        salesman_details[nik]['performance'][lob_name] = {
                            'actual': actual,
                            'target': target,
                            'percentage': int(round(achievement))
                        }
                        
                        self.safe_log('info', f"✅ Added performance for NIK {nik}, LOB {lob_name}: {self.safe_percentage(achievement)}%", 
                                    f"[OK] Added performance for NIK {nik}, LOB {lob_name}: {self.safe_percentage(achievement)}%")
            
            # Process additional metrics
            self.safe_log('info', f"Process columns: {list(process_df.columns)}")
            
            for _, row in process_df.iterrows():
                if pd.notna(row.get('NIK', '')):
                    nik = str(int(float(row['NIK']))) if pd.notna(row['NIK']) else ''
                    
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
                        
                        self.safe_log('info', f"✅ Added metrics for NIK {nik}: CA:{ca}%, GP:{(gp_food + gp_others) / 2:.1f}%", 
                                    f"[OK] Added metrics for NIK {nik}: CA:{ca}%, GP:{(gp_food + gp_others) / 2:.1f}%")
            
            self.safe_log('info', f"✅ Processed details for {len(salesman_details)} salesman with NIK keys", f"[OK] Processed details for {len(salesman_details)} salesman with NIK keys")
            
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
            
            required_sheets = ['d.dashboard', 'd.performance', 'd.salesmanlob', 'd.salesmanproses', 'd.soharian']
            
            for sheet_name in required_sheets:
                if sheet_name not in sheets:
                    self.safe_log('error', f"Required sheet missing: {sheet_name}")
                    return False
                    
                if sheets[sheet_name].empty:
                    self.safe_log('error', f"Sheet is empty: {sheet_name}")
                    return False
            
            self.safe_log('info', "✅ Data validation passed", "[OK] Data validation passed")
            return True
            
        except Exception as e:
            self.safe_log('error', f"Validation error: {str(e)}")
            return False

    def generate_json_files(self, sheets):
        """Generate all JSON files with complete data"""
        try:
            self.safe_log('info', "🔄 Processing Excel data to JSON with format Indonesia Rb/Jt/M...", "Processing Excel data to JSON with format Indonesia...")
            
            # Process all data
            dashboard_data = self.process_dashboard_data(sheets)
            salesman_list = self.process_salesman_data(sheets)
            salesman_details = self.process_salesman_detail(sheets)
            
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
            self.safe_log('info', f"✅ Saved: {details_file} with format Indonesia", f"[OK] Saved: {details_file} with format Indonesia")
            
            # Generate and save chart data
            chart_data = self.generate_chart_data(sheets)
            if chart_data:
                chart_file = os.path.join(self.data_dir, 'chart_data.json')
                with open(chart_file, 'w', encoding='utf-8') as f:
                    json.dump(chart_data, f, indent=2, ensure_ascii=False)
                self.safe_log('info', f"✅ Saved: {chart_file} with format Indonesia", f"[OK] Saved: {chart_file} with format Indonesia")
            
            self.safe_log('info', f"🎉 Generated 4 JSON files with Indonesia format (Rb/Jt/M)!", f"[SUCCESS] Generated 4 JSON files with Indonesia format!")
            self.safe_log('info', "📋 Files updated with Rb/Jt/M format:", "[LIST] Files updated with Rb/Jt/M format:")
            
            files = ['dashboard.json', 'salesman_list.json', 'salesman_details.json', 'chart_data.json']
            for file in files:
                self.safe_log('info', f"   - {file}")
            
            return True
            
        except Exception as e:
            self.safe_log('error', f"Error generating JSON files: {str(e)}")
            return False

    def git_push_changes(self):
        """Push changes to GitHub"""
        try:
            self.safe_log('info', "🚀 Pushing to GitHub...", "Pushing to GitHub...")
            
            # Git add
            result = subprocess.run(['git', 'add', '.'], 
                                  capture_output=True, text=True, cwd='.')
            
            if result.returncode != 0:
                self.safe_log('error', f"Git add failed: {result.stderr}")
                return False
            
            # Git commit
            commit_message = f"Morning update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - FIXED format Indonesia Rb/Jt/M & vs metrics display"
            result = subprocess.run(['git', 'commit', '-m', commit_message], 
                                  capture_output=True, text=True, cwd='.')
            
            if result.returncode != 0:
                if "nothing to commit" in result.stdout:
                    self.safe_log('info', "No changes to commit")
                    return True
                else:
                    self.safe_log('error', f"Git commit failed: {result.stderr}")
                    return False
            
            # Git push
            result = subprocess.run(['git', 'push', 'origin', 'main'], 
                                  capture_output=True, text=True, cwd='.')
            
            if result.returncode == 0:
                self.safe_log('info', "✅ Successfully pushed to GitHub!", "[OK] Successfully pushed to GitHub!")
                return True
            else:
                self.safe_log('error', f"Git push failed: {result.stderr}")
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
            
            success_message = f"""
=======================================================
🎉 MORNING UPDATE COMPLETED SUCCESSFULLY!
⏱️  Processing time: {duration:.2f} seconds
📱 Dashboard URL: https://kisman271128.github.io/salesman-dashboard

📊 FIXED Features:
   💰 Indonesian Number Format - FIXED Rb/Jt/M display
   📈 vs Metrics Display - FIXED vs LM/3LM/LY showing
   🎯 Chart Stats Format - FIXED proper Rb/Jt/M format
   🔐 NIK Login - All salesman + admin access
   🧭 Modern Navigation - Updated 4 & 5 icon menus

🔑 Login Credentials:
   Admin: admin / admin123
   Salesman: [NIK] / sales123

💡 Format Indonesia:
   • < 1K = angka langsung (500)
   • 1K-999K = Rb (500Rb) 
   • 1Jt-999Jt = Jt (50.5Jt)
   • ≥1M = M (1.5M)
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
    """Main function - Fixed Indonesia Format"""
    print("🚀 SALESMAN DASHBOARD UPDATER v2.3 - INDONESIA FORMAT FIXED")
    print("=" * 70)
    print("Running with INDONESIA FORMAT FIXES:")
    print("✅ FIXED format Rb/Jt/M sesuai standar Indonesia")
    print("✅ FIXED vs metrics display (vs LM/3LM/LY)")
    print("✅ FIXED chart stats dengan format yang benar") 
    print("✅ Enhanced number formatting untuk semua section")
    print("=" * 70)
    
    print("\n🌅 MORNING BATCH UPDATE - INDONESIA FORMAT")
    print("=" * 55)
    print("🚀 Version 2.3 - INDONESIA FORMAT FIXES:")
    print("   ✅ FIXED Rb untuk < 1 juta (contoh: 500Rb)")
    print("   ✅ FIXED Jt untuk 1-999 juta (contoh: 50.5Jt)")
    print("   ✅ FIXED M untuk ≥ 1 miliar (contoh: 1.5M)")
    print("   ✅ FIXED vs metrics yang tidak muncul")
    print("   ✅ FIXED chart stats format Indonesia")
    print("=" * 55)
    
    # Create updater and run
    updater = SalesmanDashboardUpdater()
    success = updater.run_morning_update()
    
    if success:
        print("\n✅ INDONESIA FORMAT UPDATE SUCCESSFUL!")
        print("🌐 Dashboard dengan format Rb/Jt/M yang benar")
        print("📱 URL: https://kisman271128.github.io/salesman-dashboard")
        sys.exit(0)
    else:
        print("\n❌ UPDATE FAILED!")
        print("❗ Check logs for details")
        sys.exit(1)

if __name__ == "__main__":
    main()