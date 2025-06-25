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
    def __init__(self, excel_file="DbaseSalesmanWebApp.xlsm"):
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

    def process_dashboard_data(self, sheets):
        """Process dashboard data with all metrics"""
        try:
            self.safe_log('info', "🔄 Processing dashboard data with all metrics...", "Processing dashboard data with all metrics...")
            
            dashboard_df = sheets['d.dashboard']
            self.safe_log('info', f"Dashboard columns: {list(dashboard_df.columns)}")
            
            # Process LOB cards with all vs metrics
            lob_cards = []
            
            for _, row in dashboard_df.iterrows():
                if pd.notna(row.get('LOB', '')) and row.get('LOB', '').strip() != '':
                    lob_name = str(row['LOB']).strip()
                    
                    # Skip TOTAL row for individual LOB cards
                    if lob_name.upper() == 'TOTAL':
                        continue
                    
                    # Calculate metrics
                    actual = self.safe_float(row.get('Actual', 0))
                    bp = self.safe_float(row.get('BP', 1))
                    achievement = (actual / bp * 100) if bp > 0 else 0
                    
                    # VS metrics
                    vs_bp = self.safe_float(row.get('vs BP', 0))
                    vs_ly = self.safe_float(row.get('vs LY', 0)) 
                    vs_3lm = self.safe_float(row.get('vs 3LM', 0))
                    vs_lm = self.safe_float(row.get('vs LM', 0))
                    
                    lob_card = {
                        'name': lob_name,
                        'achievement': f"{self.safe_percentage(achievement)}%",
                        'actual': self.format_currency(actual),
                        'target': self.format_currency(bp),
                        'vs_bp': f"{'+' if vs_bp >= 0 else ''}{self.safe_percentage(vs_bp)}%",
                        'vs_ly': f"{'+' if vs_ly >= 0 else ''}{self.safe_percentage(vs_ly)}%", 
                        'vs_3lm': f"{'+' if vs_3lm >= 0 else ''}{self.safe_percentage(vs_3lm)}%",
                        'vs_lm': f"{'+' if vs_lm >= 0 else ''}{self.safe_percentage(vs_lm)}%"
                    }
                    
                    lob_cards.append(lob_card)
                    self.safe_log('info', f"✅ Added LOB: {lob_card['name']} - Ach:{lob_card['achievement']}, vs LM:{lob_card['vs_lm']}, vs 3LM:{lob_card['vs_3lm']}, vs LY:{lob_card['vs_ly']}", 
                                f"[OK] Added LOB: {lob_card['name']} - Ach:{lob_card['achievement']}, vs LM:{lob_card['vs_lm']}, vs 3LM:{lob_card['vs_3lm']}, vs LY:{lob_card['vs_ly']}")
            
            self.safe_log('info', f"✅ Processed {len(lob_cards)} LOB cards with all metrics", f"[OK] Processed {len(lob_cards)} LOB cards with all metrics")
            
            return {
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'depo': 'Depo Tanjung - Region Kalimantan', 
                'lob_cards': lob_cards
            }
            
        except Exception as e:
            self.safe_log('error', f"Error processing dashboard data: {str(e)}")
            return None

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
                        
                        salesman_data = {
                            'id': nik,  # NIK as login ID
                            'name': name,
                            'achievement': f"{self.safe_percentage(achievement)}%",
                            'actual': self.format_currency(actual),
                            'target': self.format_currency(target),
                            'rank': int(row.get('Rank', 0)) if pd.notna(row.get('Rank')) else 0,
                            'type': str(row.get('Tipe Salesman', 'Sales')).strip()
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
                                'lob_performance': {},
                                'process_metrics': {}
                            }
                        
                        # Calculate LOB achievement
                        actual = self.safe_float(row.get('Actual', 0))
                        target = self.safe_float(row.get('Target', 1))
                        achievement = (actual / target * 100) if target > 0 else 0
                        
                        salesman_details[nik]['lob_performance'][lob_name] = {
                            'actual': self.format_currency(actual),
                            'target': self.format_currency(target), 
                            'achievement': f"{self.safe_percentage(achievement)}%",
                            'vs_3lm': f"{'+' if self.safe_float(row.get('vs 3LM', 0)) >= 0 else ''}{self.safe_percentage(self.safe_float(row.get('vs 3LM', 0)))}%"
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
                        gp = (gp_food + gp_others) / 2 if gp_food > 0 or gp_others > 0 else 0
                        
                        salesman_details[nik]['process_metrics'] = {
                            'ca_achievement': f"{self.safe_percentage(ca)}%",
                            'gp_achievement': f"{self.safe_percentage(gp)}%",
                            'cr_achievement': f"{self.safe_percentage(self.safe_float(row.get('Ach_CR', 0)))}%",
                            'pc_achievement': f"{self.safe_percentage(self.safe_float(row.get('Ach_PC', 0)))}%"
                        }
                        
                        self.safe_log('info', f"✅ Added metrics for NIK {nik}: CA:{self.safe_percentage(ca)}%, GP:{self.safe_percentage(gp)}%", 
                                    f"[OK] Added metrics for NIK {nik}: CA:{self.safe_percentage(ca)}%, GP:{self.safe_percentage(gp)}%")
            
            self.safe_log('info', f"✅ Processed details for {len(salesman_details)} salesman with NIK keys", f"[OK] Processed details for {len(salesman_details)} salesman with NIK keys")
            
            return salesman_details
            
        except Exception as e:
            self.safe_log('error', f"Error processing salesman details: {str(e)}")
            return {}

    def generate_chart_data(self, sheets):
        """Generate modern chart data with real statistics"""
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
            
            # Generate chart data points
            chart_points = []
            
            for _, row in so_df.iterrows():
                if pd.notna(row.get('Tgl')):
                    date_val = row['Tgl']
                    
                    point = {
                        'date': date_val.strftime('%Y-%m-%d') if hasattr(date_val, 'strftime') else str(date_val),
                        'day': date_val.strftime('%d') if hasattr(date_val, 'strftime') else str(date_val).split('-')[-1],
                        'target': int(self.safe_float(row.get('Target', 0))),
                        'so': int(self.safe_float(row.get('SO', 0))),
                        'do': int(self.safe_float(row.get('DO', 0)))
                    }
                    
                    chart_points.append(point)
            
            # Calculate statistics
            total_target = sum(p['target'] for p in chart_points)
            total_so = sum(p['so'] for p in chart_points)
            total_do = sum(p['do'] for p in chart_points)
            
            avg_target = int(total_target / len(chart_points)) if chart_points else 0
            avg_so = int(total_so / len(chart_points)) if chart_points else 0
            avg_do = int(total_do / len(chart_points)) if chart_points else 0
            
            # Count working days
            total_hk = len(chart_points)
            current_date = datetime.now()
            remaining_days = 0
            
            for point in chart_points:
                try:
                    point_date = datetime.strptime(point['date'], '%Y-%m-%d')
                    if point_date > current_date:
                        remaining_days += 1
                except:
                    pass
            
            sisa_hk_do = max(0, remaining_days)
            
            chart_data = {
                'period': data_period,
                'so_data': chart_points,
                'stats': {
                    'avg_target': avg_target,
                    'avg_so': avg_so, 
                    'avg_do': avg_do,
                    'total_hk': total_hk,
                    'sisa_hk_do': sisa_hk_do
                }
            }
            
            # Add gap total from dashboard
            chart_data['stats']['gap_total'] = self.get_gap_total_from_dashboard(sheets)
            
            self.safe_log('info', f"✅ Modern chart data processed: {len(chart_data['so_data'])} days", f"[OK] Modern chart data processed: {len(chart_data['so_data'])} days")
            self.safe_log('info', f"📊 Period: {data_period}", f"[CHART] Period: {data_period}")
            self.safe_log('info', f"📈 Stats: SO={chart_data['stats']['avg_so']}M, DO={chart_data['stats']['avg_do']}M, Target={chart_data['stats']['avg_target']}M", 
                        f"[TREND] Stats: SO={chart_data['stats']['avg_so']}M, DO={chart_data['stats']['avg_do']}M, Target={chart_data['stats']['avg_target']}M")
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
        """Format currency in millions"""
        try:
            val = float(value) / 1000000  # Convert to millions
            if val >= 1000:
                return f"{val/1000:.1f}T"
            elif val >= 1:
                return f"{val:.0f}M"
            else:
                return f"{val*1000:.0f}K"
        except:
            return "0M"

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
        """Get Gap Total from dashboard data"""
        try:
            dashboard_df = sheets.get('d.dashboard')
            if dashboard_df is not None:
                self.safe_log('info', f"🔍 Looking for Gap Total in dashboard with {len(dashboard_df)} rows", f"[SEARCH] Looking for Gap Total in dashboard with {len(dashboard_df)} rows")
                
                # Look for TOTAL row
                for _, row in dashboard_df.iterrows():
                    lob_name = str(row.get('LOB', '')).strip().upper()
                    if lob_name == 'TOTAL':
                        gap_value = self.safe_float(row.get('Gap', 0))
                        
                        # Format gap value
                        if gap_value != 0:
                            gap_formatted = self.format_currency(gap_value)
                            self.safe_log('info', f"✅ Found Gap Total: {gap_formatted} for LOB: {lob_name}", f"[OK] Found Gap Total: {gap_formatted} for LOB: {lob_name}")
                            return gap_formatted
                
                self.safe_log('warning', "Gap Total not found in dashboard")
                return "0M"
        except Exception as e:
            self.safe_log('error', f"Error getting gap total: {str(e)}")
        
        return "0M"

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
            self.safe_log('info', "🔄 Processing Excel data to JSON with all improvements...", "Processing Excel data to JSON with all improvements...")
            
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
            self.safe_log('info', f"✅ Saved: {dashboard_file} with all vs metrics", f"[OK] Saved: {dashboard_file} with all vs metrics")
            
            # Save salesman list
            list_file = os.path.join(self.data_dir, 'salesman_list.json')
            with open(list_file, 'w', encoding='utf-8') as f:
                json.dump(salesman_list, f, indent=2, ensure_ascii=False)
            self.safe_log('info', f"✅ Saved: {list_file} with NIK authentication", f"[OK] Saved: {list_file} with NIK authentication")
            
            # Save salesman details 
            details_file = os.path.join(self.data_dir, 'salesman_details.json')
            with open(details_file, 'w', encoding='utf-8') as f:
                json.dump(salesman_details, f, indent=2, ensure_ascii=False)
            self.safe_log('info', f"✅ Saved: {details_file} with NIK mapping", f"[OK] Saved: {details_file} with NIK mapping")
            
            # Generate and save chart data
            chart_data = self.generate_chart_data(sheets)
            if chart_data:
                chart_file = os.path.join(self.data_dir, 'chart_data.json')
                with open(chart_file, 'w', encoding='utf-8') as f:
                    json.dump(chart_data, f, indent=2, ensure_ascii=False)
                self.safe_log('info', f"✅ Saved: {chart_file} with modern chart data", f"[OK] Saved: {chart_file} with modern chart data")
            
            self.safe_log('info', f"🎉 Generated 4 JSON files with all improvements!", f"[SUCCESS] Generated 4 JSON files with all improvements!")
            self.safe_log('info', "📋 Files updated:", "[LIST] Files updated:")
            
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
            commit_message = f"Morning update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Updated with all improvements"
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
⏰ Next update: Tomorrow morning at 07:00

📊 Features Updated:
   🎯 Modern Chart - Real trend SO/DO vs Target
   🔐 NIK Login - All salesman + admin access
   📈 Complete Metrics - vs LM/3LM/LY displayed
   🔗 Data Integration - Real JSON connections
   🧭 Updated Navigation - 4 & 5 icon menus

🔑 Login Credentials:
   Admin: admin / admin123
   Salesman: [NIK] / sales123
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
    """Main function - Fully Automated"""
    print("🚀 SALESMAN DASHBOARD UPDATER v2.0 - AUTOMATED MODE")
    print("=" * 60)
    print("Running in fully automated mode...")
    print("✅ Modern chart visualization")
    print("✅ NIK-based authentication") 
    print("✅ Complete metrics display")
    print("✅ Real-time data integration")
    print("=" * 60)
    
    print("\n🌅 MORNING BATCH UPDATE - AUTOMATED")
    print("=" * 55)
    print("🚀 Version 2.0 - All Improvements:")
    print("   ✅ Modern SVG Chart with real data")
    print("   ✅ NIK-based Login System")
    print("   ✅ All VS Metrics in LOB Cards") 
    print("   ✅ Real Data Integration")
    print("   ✅ Updated Navigation")
    print("=" * 55)
    
    # Create updater and run
    updater = SalesmanDashboardUpdater()
    success = updater.run_morning_update()
    
    if success:
        print("\n✅ AUTOMATED UPDATE SUCCESSFUL!")
        print("🌐 Dashboard ready with all improvements")
        print("📱 URL: https://kisman271128.github.io/salesman-dashboard")
        # No input() for automation
        sys.exit(0)
    else:
        print("\n❌ AUTOMATED UPDATE FAILED!")
        print("❗ Check logs for details")
        # No input() for automation  
        sys.exit(1)

if __name__ == "__main__":
    main()