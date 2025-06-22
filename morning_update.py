import pandas as pd
import json
import os
import subprocess
from datetime import datetime
import logging
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('morning_update.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class SalesmanDashboardUpdater:
    def __init__(self):
        self.excel_file = "DbaseSalesmanWebApp.xlsm"
        self.data_folder = "data"
        self.photos_folder = "photos"
        self.ensure_folders()
        
        # Excel sheet mapping sesuai dengan file Anda
        self.sheet_mapping = {
            'dashboard': 'd.dashboard',
            'performance': 'd.performance', 
            'salesmanlob': 'd.salesmanlob',
            'salesmanproses': 'd.salesmanproses',
            'soharian': 'd.soharian'  # ← ADD THIS
        }
    
    def ensure_folders(self):
        """Buat folder yang diperlukan"""
        for folder in [self.data_folder, self.photos_folder]:
            if not os.path.exists(folder):
                os.makedirs(folder)
                logging.info(f"Created folder: {folder}")
    
    def read_excel_sheets(self):
        """Baca semua sheet dari Excel dengan error handling"""
        try:
            logging.info("📊 Reading Excel sheets...")
            
            if not os.path.exists(self.excel_file):
                logging.error(f"❌ Excel file not found: {self.excel_file}")
                return None
            
            sheets = {}
            
            # Check available sheets
            xl_file = pd.ExcelFile(self.excel_file)
            available_sheets = xl_file.sheet_names
            logging.info(f"Available sheets: {available_sheets}")
            
            # Read each required sheet
            for key, sheet_name in self.sheet_mapping.items():
                if sheet_name in available_sheets:
                    try:
                        sheets[key] = pd.read_excel(self.excel_file, sheet_name=sheet_name)
                        logging.info(f"✅ Loaded sheet: {sheet_name}")
                        
                        # Log basic info about the sheet
                        df = sheets[key]
                        logging.info(f"   Rows: {len(df)}, Columns: {list(df.columns)}")
                        
                    except Exception as e:
                        logging.error(f"❌ Error reading sheet {sheet_name}: {e}")
                        return None
                else:
                    logging.warning(f"⚠️ Sheet not found: {sheet_name}")
            
            return sheets
            
        except Exception as e:
            logging.error(f"❌ Error reading Excel file: {e}")
            return None
    
    def process_dashboard_data(self, sheets):
        """Process data untuk dashboard utama dengan mapping yang fleksibel"""
        try:
            dashboard_df = sheets['dashboard']
            logging.info("🔄 Processing dashboard data...")
            
            # Print columns untuk debugging
            logging.info(f"Dashboard columns: {list(dashboard_df.columns)}")
            
            # Flexible column mapping - adjust sesuai struktur Excel Anda
            lob_cards = []
            
            for index, row in dashboard_df.iterrows():
                # Skip empty rows
                if pd.isna(row.iloc[0]):
                    continue
                    
                # Map columns fleksibel - sesuaikan dengan nama kolom Excel Anda
                lob_name = self.get_cell_value(row, ['LOB'])
                achievement = self.get_cell_value(row, ['vs BP'])
                gap = self.get_cell_value(row, ['Gap'])
                vs_lm = self.get_cell_value(row, ['vs LM'])
                vs_3lm = self.get_cell_value(row, ['vs 3LM'])
                vs_ly = self.get_cell_value(row, ['vs LY'])
                
                if lob_name:  # Only add if LOB name exists
                    lob_card = {
                        'name': str(lob_name).upper(),
                        'achievement': f"{self.safe_percentage(achievement)}%",
                        'gap': self.format_currency(gap),
                        'vs_lm': self.format_growth(vs_lm),
                        'vs_3lm': self.format_growth(vs_3lm),
                        'vs_ly': self.format_growth(vs_ly)
                    }
                    lob_cards.append(lob_card)
                    logging.info(f"Added LOB: {lob_card['name']} - {lob_card['achievement']}")
            
            dashboard_data = {
                'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'depo_name': 'Depo Tanjung',
                'region_name': 'Region Kalimantan',
                'lob_cards': lob_cards,
                'total_lobs': len(lob_cards)
            }
            
            logging.info(f"✅ Processed {len(lob_cards)} LOB cards")
            return dashboard_data
            
        except Exception as e:
            logging.error(f"❌ Error processing dashboard data: {e}")
            return None
    
    def process_salesman_data(self, sheets):
        """Process data salesman untuk ranking"""
        try:
            performance_df = sheets['performance']
            logging.info("🔄 Processing salesman data...")
            
            # Print columns untuk debugging
            logging.info(f"Performance columns: {list(performance_df.columns)}")
            
            salesman_list = []
            
            for index, row in performance_df.iterrows():
                # Skip empty rows
                if pd.isna(row.iloc[0]):
                    continue
                
                # Flexible column mapping
                salesman_id = self.get_cell_value(row, ['NIK'])
                name = self.get_cell_value(row, ['Nama Salesman'])
                tipe = self.get_cell_value(row, ['Tipe Salesman'])
                achievement = self.get_cell_value(row, ['Ach'])
                
                if name and achievement is not None:  # Only add if essential data exists
                    achievement_num = self.safe_percentage(achievement)
                    
                    # Determine status
                    if achievement_num < 85:
                        status = 'Extra Effort'
                    elif achievement_num < 95:
                        status = 'Good'
                    elif achievement_num < 110:
                        status = 'Very Good'
                    else:
                        status = 'Excellent'
                    
                    salesman_data = {
                        'id': str(salesman_id) if salesman_id else f"S{index+1}",
                        'name': str(name),
                        'tipe': str(zone) if Tipe else 'Zone Unknown',
                        'achievement': f"{achievement_num}%",
                        'achievement_num': achievement_num,  # For sorting
                        'status': status
                    }
                    salesman_list.append(salesman_data)
                    logging.info(f"Added salesman: {salesman_data['name']} - {salesman_data['achievement']}")
            
            # Sort by achievement (lowest to highest for ranking display)
            salesman_list.sort(key=lambda x: x['achievement_num'])
            
            # Add rank
            for i, salesman in enumerate(salesman_list):
                salesman['rank'] = len(salesman_list) - i  # Reverse ranking
                del salesman['achievement_num']  # Remove helper field
            
            logging.info(f"✅ Processed {len(salesman_list)} salesman")
            return salesman_list
            
        except Exception as e:
            logging.error(f"❌ Error processing salesman data: {e}")
            return []
    
    def process_salesman_detail(self, sheets):
        """Process detailed performance untuk setiap salesman"""
        try:
            salesmanlob_df = sheets.get('salesmanlob')
            salesmanproses_df = sheets.get('salesmanproses')
            
            logging.info("🔄 Processing salesman details...")
            
            salesman_details = {}
            
            # Process LOB performance
            if salesmanlob_df is not None:
                logging.info(f"LOB columns: {list(salesmanlob_df.columns)}")
                
                for index, row in salesmanlob_df.iterrows():
                    if pd.isna(row.iloc[0]):
                        continue
                    
                    salesman_id = self.get_cell_value(row, ['NIK'])
                    lob_name = self.get_cell_value(row, ['LOB'])
                    achievement = self.get_cell_value(row, ['Ach'])
                    target = self.get_cell_value(row, ['Target'])
                    actual = self.get_cell_value(row, ['Actual'])
                    
                    if salesman_id and lob_name:
                        if salesman_id not in salesman_details:
                            salesman_details[salesman_id] = {
                                'performance': {},
                                'metrics': {}
                            }
                        
                        salesman_details[salesman_id]['performance'][str(lob_name).upper()] = {
                            'percentage': self.safe_percentage(achievement),
                            'target': self.safe_number(target),
                            'actual': self.safe_number(actual)
                        }
            
            # Process metrics (CA, CA Prod, SKU, GP)
            if salesmanproses_df is not None:
                logging.info(f"Process columns: {list(salesmanproses_df.columns)}")
                
                for index, row in salesmanproses_df.iterrows():
                    if pd.isna(row.iloc[0]):
                        continue
                    
                    salesman_id = self.get_cell_value(row, ['NIK'])
                    
                    if salesman_id and salesman_id in salesman_details:
                        ca = self.get_cell_value(row, ['Ach_CA'])
                        ca_prod = self.get_cell_value(row, ['Ach_CAProdAll'])
                        sku = self.get_cell_value(row, ['Ach_AvgSKU'])
                        gp = self.get_cell_value(row, ['Ach_GPFood'])
                        
                        salesman_details[salesman_id]['metrics'] = {
                            'CA': self.safe_percentage(ca),
                            'CAProd': self.safe_percentage(ca_prod),
                            'SKU': self.safe_percentage(sku),
                            'GP': self.safe_percentage(gp)
                        }
            
            logging.info(f"✅ Processed details for {len(salesman_details)} salesman")
            return salesman_details
            
        except Exception as e:
            logging.error(f"❌ Error processing salesman details: {e}")
            return {}
    
    def get_cell_value(self, row, possible_columns):
        """Ambil nilai dari row dengan berbagai kemungkinan nama kolom"""
        for col in possible_columns:
            if col in row.index:
                value = row[col]
                if pd.notna(value):
                    return value
        return None
    
    def safe_percentage(self, value):
        """Konversi ke percentage dengan handling error - Preserve sign"""
        if pd.isna(value):
            return 0
        try:
            percentage = float(value)
            
            # If value is 0-1 range (like 0.59), multiply by 100
            if 0 <= abs(percentage) <= 1:
                percentage = percentage * 100
            
            # Return integer but preserve sign
            return int(round(percentage))
        except:
            return 0
    
    def safe_number(self, value):
        """Konversi ke number dengan handling error"""
        if pd.isna(value):
            return 0
        try:
            return int(float(value))
        except:
            return 0
            
    def format_currency(self, value):
        """Format currency untuk display ringkas"""
        if pd.isna(value):
            return "0"
        try:
            num = float(value)
            
            # Handle negative numbers
            sign = "+" if num >= 0 else ""
            abs_num = abs(num)
            
            if abs_num >= 1_000_000_000:
                # Miliar - format: 1.26 M
                formatted = f"{abs_num / 1_000_000_000:.2f} M".rstrip('0').rstrip('.')
            elif abs_num >= 1_000_000:
                # Juta - format: 742 jt
                formatted = f"{int(abs_num / 1_000_000)} jt"
            elif abs_num >= 1_000:
                # Ribu - format: 250 rb
                formatted = f"{int(abs_num / 1_000)} rb"
            else:
                # Kurang dari ribu
                formatted = f"{int(abs_num)}"
            
            return f"{sign}{formatted}"
        except:
            return "0"
            
    def format_growth(self, value):
        """Format growth percentage dengan tanda + atau -"""
        if pd.isna(value):
            return "+0%"
        try:
            percentage = float(value)
            
            # If value is 0-1 range, multiply by 100
            if 0 <= abs(percentage) <= 1:
                percentage = percentage * 100
            
            # Round to integer
            rounded_pct = int(round(percentage))
            
            # Add explicit + or - sign
            if rounded_pct > 0:
                return f"+{rounded_pct}%"
            elif rounded_pct < 0:
                return f"{rounded_pct}%"  # Negative sign already included
            else:
                return "+0%"
        except:
            return "+0%"
        
    def generate_json_files(self, sheets):
        """Generate JSON files dari Excel data"""
        try:
            logging.info("🔄 Processing Excel data to JSON...")
            
            # Process all data
            dashboard_data = self.process_dashboard_data(sheets)
            salesman_list = self.process_salesman_data(sheets)
            salesman_details = self.process_salesman_detail(sheets)
            
            if not dashboard_data:
                logging.error("❌ Failed to process dashboard data")
                return False
            
            # Save JSON files
            files_saved = []
            
            # Dashboard data
            dashboard_file = f'{self.data_folder}/dashboard.json'
            with open(dashboard_file, 'w', encoding='utf-8') as f:
                json.dump(dashboard_data, f, ensure_ascii=False, indent=2)
            files_saved.append('dashboard.json')
            logging.info(f"✅ Saved: {dashboard_file}")
            
            # Salesman list
            list_file = f'{self.data_folder}/salesman_list.json'
            with open(list_file, 'w', encoding='utf-8') as f:
                json.dump(salesman_list, f, ensure_ascii=False, indent=2)
            files_saved.append('salesman_list.json')
            logging.info(f"✅ Saved: {list_file}")
            
            # Salesman details
            details_file = f'{self.data_folder}/salesman_details.json'
            with open(details_file, 'w', encoding='utf-8') as f:
                json.dump(salesman_details, f, ensure_ascii=False, indent=2)
            files_saved.append('salesman_details.json')
            logging.info(f"✅ Saved: {details_file}")
            
            # Generate sample chart data
            chart_data = self.generate_chart_data()
            chart_file = f'{self.data_folder}/chart_data.json'
            with open(chart_file, 'w', encoding='utf-8') as f:
                json.dump(chart_data, f, ensure_ascii=False, indent=2)
            files_saved.append('chart_data.json')
            logging.info(f"✅ Saved: {chart_file}")
            
            logging.info(f"🎉 Generated {len(files_saved)} JSON files successfully!")
            return True
            
        except Exception as e:
            logging.error(f"❌ Error generating JSON files: {e}")
            return False
    
        def generate_chart_data(self, sheets=None):
            """Generate modern chart data dari Excel sheet d.soharian"""
            from datetime import datetime
            
            chart_data = {
                'so_data': [],
                'do_data': [],
                'target_data': [],
                'labels': [],
                'period': '30 Hari Terakhir',
                'stats': {
                    'avg_so': 0,
                    'avg_do': 0,
                    'avg_target': 160,
                    'achievement_so': 0,
                    'achievement_do': 0,
                    'total_days': 0
                }
            }
            
            try:
                if sheets and 'soharian' in sheets:
                    so_df = sheets['soharian']
                    logging.info("📊 Reading SO Harian data from d.soharian sheet...")
                    
                    # Read data dari Excel
                    for index, row in so_df.iterrows():
                        if pd.isna(row.iloc[0]):  # Skip empty rows
                            continue
                        
                        # Get values dengan column mapping
                        tanggal = self.get_cell_value(row, ['Tgl'])
                        target = self.get_cell_value(row, ['Target'])
                        so = self.get_cell_value(row, ['SO'])
                        do = self.get_cell_value(row, ['DO'])
                        
                        if tanggal is not None:
                            # Format tanggal untuk label
                            try:
                                if isinstance(tanggal, str):
                                    date_obj = datetime.strptime(tanggal, '%Y-%m-%d')
                                else:
                                    date_obj = pd.to_datetime(tanggal)
                                label = date_obj.strftime('%d/%m')
                            except:
                                label = str(tanggal)[:5] if tanggal else f"Day {len(chart_data['labels'])+1}"
                            
                            # Add data points
                            chart_data['labels'].append(label)
                            chart_data['so_data'].append(self.safe_number(so))
                            chart_data['do_data'].append(self.safe_number(do))
                            chart_data['target_data'].append(self.safe_number(target) if target else 160)
                    
                    # Limit to last 30 days
                    if len(chart_data['so_data']) > 30:
                        chart_data['so_data'] = chart_data['so_data'][-30:]
                        chart_data['do_data'] = chart_data['do_data'][-30:]
                        chart_data['target_data'] = chart_data['target_data'][-30:]
                        chart_data['labels'] = chart_data['labels'][-30:]
                    
                    # Calculate statistics
                    if chart_data['so_data']:
                        chart_data['stats']['avg_so'] = int(sum(chart_data['so_data']) / len(chart_data['so_data']))
                        chart_data['stats']['avg_do'] = int(sum(chart_data['do_data']) / len(chart_data['do_data']))
                        chart_data['stats']['avg_target'] = int(sum(chart_data['target_data']) / len(chart_data['target_data']))
                        chart_data['stats']['total_days'] = len(chart_data['so_data'])
                        
                        # Achievement percentages
                        if chart_data['stats']['avg_target'] > 0:
                            chart_data['stats']['achievement_so'] = round((chart_data['stats']['avg_so'] / chart_data['stats']['avg_target']) * 100, 1)
                            chart_data['stats']['achievement_do'] = round((chart_data['stats']['avg_do'] / chart_data['stats']['avg_target']) * 100, 1)
                    
                    logging.info(f"✅ Loaded {len(chart_data['so_data'])} days of SO/DO data")
                    logging.info(f"📈 Avg SO: {chart_data['stats']['avg_so']}, Avg DO: {chart_data['stats']['avg_do']}")
                    
                else:
                    logging.info("📊 Sheet d.soharian not found, using sample data")
                    self.generate_sample_chart_data(chart_data)
                    
            except Exception as e:
                logging.error(f"❌ Error reading SO harian data: {e}")
                self.generate_sample_chart_data(chart_data)
            
            return chart_data

        def generate_sample_chart_data(self, chart_data):
            """Generate sample data untuk testing"""
            import random
            from datetime import datetime, timedelta
            
            base_date = datetime.now() - timedelta(days=30)
            
            for i in range(30):
                # Realistic sample data
                target_val = 160
                so_val = random.randint(120, 180)
                do_val = int(so_val * random.uniform(0.7, 0.95))  # DO usually lower than SO
                
                chart_data['so_data'].append(so_val)
                chart_data['do_data'].append(do_val)
                chart_data['target_data'].append(target_val)
                
                current_date = base_date + timedelta(days=i)
                chart_data['labels'].append(current_date.strftime('%d/%m'))
            
            # Calculate sample stats
            chart_data['stats']['avg_so'] = int(sum(chart_data['so_data']) / len(chart_data['so_data']))
            chart_data['stats']['avg_do'] = int(sum(chart_data['do_data']) / len(chart_data['do_data']))
            chart_data['stats']['avg_target'] = 160
            chart_data['stats']['total_days'] = 30
            chart_data['stats']['achievement_so'] = round((chart_data['stats']['avg_so'] / 160) * 100, 1)
            chart_data['stats']['achievement_do'] = round((chart_data['stats']['avg_do'] / 160) * 100, 1)
    
    def git_push_changes(self):
        """Push changes ke GitHub dengan error handling"""
        try:
            logging.info("🚀 Pushing to GitHub...")
            
            # Check if git is initialized
            if not os.path.exists('.git'):
                logging.info("Initializing git repository...")
                subprocess.run(['git', 'init'], check=True)
                subprocess.run(['git', 'branch', '-M', 'main'], check=True)
            
            # Git commands
            subprocess.run(['git', 'add', '.'], check=True)
            
            # Check if there are changes to commit
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True)
            
            if not result.stdout.strip():
                logging.info("📝 No changes to commit")
                return True
            
            commit_message = f"Morning update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            
            # Push to remote (will fail on first run, user needs to set remote)
            try:
                subprocess.run(['git', 'push'], check=True)
                logging.info("✅ Successfully pushed to GitHub!")
            except subprocess.CalledProcessError:
                logging.warning("⚠️ Push failed - might need to set remote repository")
                logging.info("Run: git remote add origin https://github.com/kisman271128/salesman-dashboard.git")
                logging.info("Then: git push -u origin main")
            
            return True
            
        except subprocess.CalledProcessError as e:
            logging.error(f"❌ Git error: {e}")
            return False
    
    def validate_data(self, sheets):
        """Validasi data sebelum processing"""
        logging.info("🔍 Validating data...")
        
        required_sheets = ['dashboard', 'performance']
        missing_sheets = []
        
        for sheet in required_sheets:
            if sheet not in sheets or sheets[sheet].empty:
                missing_sheets.append(sheet)
        
        if missing_sheets:
            logging.error(f"❌ Missing or empty sheets: {missing_sheets}")
            return False
        
        logging.info("✅ Data validation passed")
        return True
    
    def run_morning_update(self):
        """Main function untuk morning update"""
        print("🌅 MORNING BATCH UPDATE - SALESMAN DASHBOARD")
        print("=" * 55)
        
        start_time = datetime.now()
        
        try:
            # Step 1: Read Excel
            sheets = self.read_excel_sheets()
            if not sheets:
                logging.error("❌ Failed to read Excel sheets")
                return False
            
            # Step 2: Validate data
            if not self.validate_data(sheets):
                return False
            
            # Step 3: Generate JSON
            if not self.generate_json_files(sheets):
                logging.error("❌ Failed to generate JSON files")
                return False
            
            # Step 4: Push to GitHub
            if not self.git_push_changes():
                logging.warning("⚠️ Git push failed, but files are ready")
            
            # Calculate processing time
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print("=" * 55)
            print("🎉 MORNING UPDATE COMPLETED SUCCESSFULLY!")
            print(f"⏱️  Processing time: {duration:.2f} seconds")
            print("📱 Dashboard URL: https://kisman271128.github.io/salesman-dashboard")
            print("⏰ Next update: Tomorrow morning at 07:00")
            print("📊 Files updated:")
            print("   - dashboard.json")
            print("   - salesman_list.json") 
            print("   - salesman_details.json")
            print("   - chart_data.json")
            print("=" * 55)
            
            return True
            
        except Exception as e:
            logging.error(f"❌ Unexpected error: {e}")
            return False

def main():
    """Main entry point"""
    updater = SalesmanDashboardUpdater()
    success = updater.run_morning_update()
    
    if not success:
        print("\n❌ Update failed! Check morning_update.log for details")
        input("Press Enter to continue...")
        return False
    
    print("\n✅ Update successful! Team can now see latest data")
    input("Press Enter to continue...")
    return True

if __name__ == "__main__":
    main()