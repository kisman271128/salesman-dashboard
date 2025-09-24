#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import logging
import json
import pandas as pd
from datetime import datetime
import subprocess

class SalesmanDashboardUpdater:
    def __init__(self, excel_file="DbaseSalesmanWebApp.xlsb"):
        self.excel_file = excel_file
        self.data_dir = "data"
        
        # Setup directories and logging
        os.makedirs(self.data_dir, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('morning_update.log', mode='w', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Morning Update Session Started - {datetime.now()}")

    def read_excel_sheets(self):
        """Read required sheets from Excel file"""
        try:
            self.logger.info("Reading Excel sheets...")
            required_sheets = ['d.dashboard', 'd.performance', 'd.salesmanlob', 
                             'd.salesmanproses', 'd.soharian']
            optional_sheets = ['d.insentif']
            
            # Try different engines for compatibility
            try:
                xl_file = pd.ExcelFile(self.excel_file, engine='openpyxl')
            except:
                xl_file = pd.ExcelFile(self.excel_file)
            
            sheets = {}
            available_sheets = xl_file.sheet_names
            
            for sheet_name in required_sheets + optional_sheets:
                if sheet_name in available_sheets:
                    sheets[sheet_name] = pd.read_excel(xl_file, sheet_name=sheet_name)
                    self.logger.info(f"Loaded {sheet_name}: {len(sheets[sheet_name])} rows")
                elif sheet_name in required_sheets:
                    raise Exception(f"Required sheet {sheet_name} not found")
            
            return sheets
            
        except Exception as e:
            self.logger.error(f"Error reading Excel: {e}")
            return None

    def safe_float(self, value):
        """Safely convert value to float"""
        try:
            if pd.isna(value):
                return 0.0
            if isinstance(value, str):
                value = value.replace('%', '').replace(',', '').replace('(', '-').replace(')', '')
            return float(value)
        except:
            return 0.0

    def format_currency_indonesia(self, value):
        """Format currency in Indonesian style (Rb/Jt/M)"""
        try:
            val = float(value)
            if val >= 1000000000:  # >= 1 Miliar
                return f"{val/1000000000:.1f}M"
            elif val >= 1000000:   # >= 1 Juta
                return f"{val/1000000:.1f}Jt"
            elif val >= 1000:      # >= 1 Ribu
                return f"{val/1000:.0f}Rb"
            else:
                return f"{val:.0f}"
        except:
            return "0"

    def parse_percentage(self, value):
        """Parse percentage values"""
        if pd.isna(value) or value == 0:
            return 0
        try:
            if isinstance(value, (int, float)):
                return int(round(value * 100 if -1 <= value <= 1 else value))
            if isinstance(value, str):
                clean_value = str(value).strip().replace('%', '').replace(',', '')
                if '(' in clean_value and ')' in clean_value:
                    clean_value = '-' + clean_value.replace('(', '').replace(')', '')
                return int(round(float(clean_value)))
            return int(round(float(value)))
        except:
            return 0

    def find_column_value(self, row, possible_names):
        """Find column value from multiple possible column names"""
        for name in possible_names:
            if name in row.index and pd.notna(row.get(name)) and row.get(name) != 0:
                return row.get(name)
        return 0

    def process_dashboard_data(self, sheets):
        """Process dashboard data"""
        try:
            self.logger.info("Processing dashboard data...")
            dashboard_df = sheets['d.dashboard']
            
            lob_cards = []
            total_data = None
            
            for _, row in dashboard_df.iterrows():
                if pd.notna(row.get('LOB', '')) and row.get('LOB', '').strip() != '':
                    lob_name = str(row['LOB']).strip()
                    
                    actual = self.safe_float(row.get('Actual', 0))
                    bp = self.safe_float(row.get('BP', 1))
                    gap = self.safe_float(row.get('Gap', 0))
                    achievement = (actual / bp * 100) if bp > 0 else 0
                    
                    # Get vs metrics
                    vs_bp = self.parse_percentage(self.find_column_value(row, ['vs BP', 'vs_BP', 'vsBP']))
                    vs_ly = self.parse_percentage(self.find_column_value(row, ['vs LY', 'vs_LY', 'vsLY']))
                    vs_3lm = self.parse_percentage(self.find_column_value(row, ['vs 3LM', 'vs_3LM', 'vs3LM']))
                    vs_lm = self.parse_percentage(self.find_column_value(row, ['vs LM', 'vs_LM', 'vsLM']))
                    
                    lob_data = {
                        'name': lob_name,
                        'achievement': f"{int(round(achievement))}%",
                        'actual': self.format_currency_indonesia(actual),
                        'target': self.format_currency_indonesia(bp),
                        'gap': self.format_currency_indonesia(abs(gap)),
                        'vs_bp': f"{'+' if vs_bp >= 0 else ''}{vs_bp}%",
                        'vs_ly': f"{'+' if vs_ly >= 0 else ''}{vs_ly}%",
                        'vs_3lm': f"{'+' if vs_3lm >= 0 else ''}{vs_3lm}%",
                        'vs_lm': f"{'+' if vs_lm >= 0 else ''}{vs_lm}%"
                    }
                    
                    if lob_name.upper() == 'TOTAL':
                        total_data = lob_data
                    else:
                        lob_cards.append(lob_data)
            
            result = {
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'depo_name': 'Depo Tanjung',
                'region_name': 'Region Kalimantan',
                'lob_cards': lob_cards
            }
            
            if total_data:
                result['total_data'] = total_data
            
            self.logger.info(f"Processed {len(lob_cards)} LOB cards + TOTAL data")
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing dashboard data: {e}")
            return None

    def process_salesman_data(self, sheets):
        """Process salesman list for ranking and login"""
        try:
            self.logger.info("Processing salesman data...")
            performance_df = sheets['d.performance']
            salesman_list = []
            
            for _, row in performance_df.iterrows():
                if pd.notna(row.get('szEmployeeId', '')) and pd.notna(row.get('szname', '')):
                    nik = str(int(float(row['szEmployeeId'])))
                    name = str(row['szname']).strip()
                    
                    actual = self.safe_float(row.get('Actual', 0))
                    target = self.safe_float(row.get('Target', 1))
                    achievement = (actual / target * 100) if target > 0 else 0
                    
                    # Determine status
                    if achievement >= 100:
                        status = 'Excellent'
                    elif achievement >= 90:
                        status = 'Very Good'
                    elif achievement >= 70:
                        status = 'Good'
                    else:
                        status = 'Extra Effort'
                    
                    salesman_list.append({
                        'id': nik,
                        'name': name,
                        'achievement': f"{int(round(achievement))}%",
                        'actual': self.format_currency_indonesia(actual),
                        'target': self.format_currency_indonesia(target),
                        'rank': int(row.get('Rank', 0)) if pd.notna(row.get('Rank')) else 0,
                        'type': str(row.get('Tipe Salesman', 'Sales')).strip(),
                        'status': status
                    })
            
            salesman_list.sort(key=lambda x: x['rank'] if x['rank'] > 0 else 999)
            self.logger.info(f"Processed {len(salesman_list)} salesman")
            return salesman_list
            
        except Exception as e:
            self.logger.error(f"Error processing salesman data: {e}")
            return []

    def process_salesman_details(self, sheets):
        """Process detailed salesman data"""
        try:
            self.logger.info("Processing salesman details...")
            lob_df = sheets['d.salesmanlob']
            process_df = sheets['d.salesmanproses']
            performance_df = sheets['d.performance']
            
            salesman_details = {}
            
            # Process LOB performance
            for _, row in lob_df.iterrows():
                if pd.notna(row.get('szEmployeeId', '')) and pd.notna(row.get('LOB', '')):
                    nik = str(int(float(row['szEmployeeId'])))
                    lob_name = str(row['LOB']).strip()
                    
                    if nik not in salesman_details:
                        salesman_details[nik] = {
                            'name': str(row.get('szname', '')).strip(),
                            'sac': str(row.get('Nama SAC', '')).strip(),
                            'type': str(row.get('Tipe Salesman', '')).strip(),
                            'performance': {},
                            'metrics': {}
                        }
                    
                    actual = self.safe_float(row.get('Actual', 0))
                    target = self.safe_float(row.get('Target', 1))
                    achievement = (actual / target * 100) if target > 0 else 0
                    gap = actual - target
                    
                    salesman_details[nik]['performance'][lob_name] = {
                        'actual': actual,
                        'target': target,
                        'percentage': int(round(achievement)),
                        'gap': gap
                    }
            
            # Process metrics
            for _, row in process_df.iterrows():
                if pd.notna(row.get('szEmployeeId', '')):
                    nik = str(int(float(row['szEmployeeId'])))
                    if nik in salesman_details:
                        ca = self.safe_float(row.get('Ach_CA', 0))
                        gp_food = self.safe_float(row.get('Ach_GPFood', 0))
                        gp_others = self.safe_float(row.get('Ach_GPOthers', 0))
                        avg_sku = self.safe_float(row.get('Ach_AvgSKU', 0))
                        
                        salesman_details[nik]['metrics'] = {
                            'CA': int(round(ca)),
                            'CAProd': int(round(self.safe_float(row.get('Ach_CAProdAll', 0)))),
                            'SKU': int(round(avg_sku)),
                            'GP': int(round((gp_food + gp_others) / 2)) if (gp_food + gp_others) > 0 else 0
                        }
            
            # Add TOTAL and Ranking
            total_salesman_count = len(salesman_details)
            for _, row in performance_df.iterrows():
                if pd.notna(row.get('szEmployeeId', '')):
                    nik = str(int(float(row['szEmployeeId'])))
                    if nik in salesman_details:
                        total_actual = self.safe_float(row.get('Actual', 0))
                        total_target = self.safe_float(row.get('Target', 1))
                        total_achievement = (total_actual / total_target * 100) if total_target > 0 else 0
                        
                        salesman_details[nik]['TOTAL'] = {
                            'actual': total_actual,
                            'target': total_target,
                            'percentage': int(round(total_achievement)),
                            'gap': total_actual - total_target
                        }
                        
                        salesman_details[nik]['Ranking'] = {
                            'Rank': int(row.get('Rank', 0)) if pd.notna(row.get('Rank')) else 0,
                            'total_salesman': total_salesman_count
                        }
            
            self.logger.info(f"Processed details for {len(salesman_details)} salesman")
            return salesman_details
            
        except Exception as e:
            self.logger.error(f"Error processing salesman details: {e}")
            return {}

    def process_incentive_data(self, sheets):
        """Process incentive data if available"""
        try:
            if 'd.insentif' not in sheets:
                self.logger.info("No incentive data available")
                return []
                
            self.logger.info("Processing incentive data...")
            insentif_df = sheets['d.insentif']
            incentive_records = []
            
            for _, row in insentif_df.iterrows():
                if pd.notna(row.get('szEmployeeId', '')):
                    incentive_record = {
                        'NIK SAC': int(self.safe_float(row.get('NIK SAC', 0))),
                        'Nama SAC': str(row.get('Nama SAC', '')).strip(),
                        'szEmployeeId': int(self.safe_float(row.get('szEmployeeId', 0))),
                        'szname': str(row.get('szname', '')).strip(),
                        'Dept': str(row.get('Dept', '')).strip(),
                        'Tipe Salesman': str(row.get('Tipe Salesman', '')).strip(),
                        'GPPJ & GEN': int(self.safe_float(row.get('GPPJ & GEN', 0))),
                        'GBS & OTHERS': int(self.safe_float(row.get('GBS & OTHERS', 0))),
                        'GPPJ': int(self.safe_float(row.get('GPPJ', 0))),
                        'GBS': int(self.safe_float(row.get('GBS', 0))),
                        'MBR': int(self.safe_float(row.get('MBR', 0))),
                        'HGJ': int(self.safe_float(row.get('HGJ', 0))),
                        'OTHERS': int(self.safe_float(row.get('OTHERS', 0))),
                        'Avg SKU': int(self.safe_float(row.get('Avg SKU', 0))),
                        'GP': int(self.safe_float(row.get('GP', 0))),
                        'POM': None if pd.isna(row.get('POM')) else int(self.safe_float(row.get('POM'))),
                        'AR Coll': int(self.safe_float(row.get('AR Coll', 0))),
                        'Insentif_sales': int(self.safe_float(row.get('Insentif_sales', 0))),
                        'Insentif_Proses': int(self.safe_float(row.get('Insentif_Proses', 0))),
                        'Total_Insentif': int(self.safe_float(row.get('Total_Insentif', 0)))
                    }
                    incentive_records.append(incentive_record)
            
            self.logger.info(f"Processed {len(incentive_records)} incentive records")
            return incentive_records
            
        except Exception as e:
            self.logger.error(f"Error processing incentive data: {e}")
            return []

    def generate_chart_data(self, sheets):
        """Generate chart data"""
        try:
            self.logger.info("Generating chart data...")
            so_df = sheets['d.soharian']
            
            # Process dates and numeric columns
            if 'Tgl' in so_df.columns:
                so_df['Tgl'] = pd.to_datetime(so_df['Tgl'], errors='coerce')
                so_df = so_df.dropna(subset=['Tgl']).sort_values('Tgl')
            
            for col in ['Target', 'SO', 'DO']:
                if col in so_df.columns:
                    so_df[col] = pd.to_numeric(so_df[col], errors='coerce').fillna(0)
            
            # Generate chart data
            so_data, do_data, target_data, labels = [], [], [], []
            
            for _, row in so_df.iterrows():
                if pd.notna(row.get('Tgl')):
                    so_data.append(int(self.safe_float(row.get('SO', 0))))
                    do_data.append(int(self.safe_float(row.get('DO', 0))))
                    target_data.append(int(self.safe_float(row.get('Target', 0))))
                    
                    date_val = row['Tgl']
                    day_label = date_val.strftime('%d') if hasattr(date_val, 'strftime') else str(date_val).split('-')[-1]
                    labels.append(day_label)
            
            # Calculate stats
            total_target = sum(target_data)
            total_so = sum(so_data)
            total_do = sum(do_data)
            
            # Get period
            current_date = datetime.now()
            month_id = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
                       'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'][current_date.month - 1]
            period = f"{month_id} {current_date.year}"
            
            # Get gap from dashboard
            gap_total = "0"
            try:
                dashboard_df = sheets.get('d.dashboard')
                if dashboard_df is not None:
                    for _, row in dashboard_df.iterrows():
                        if str(row.get('LOB', '')).strip().upper() == 'TOTAL':
                            gap_value = self.safe_float(row.get('Gap', 0))
                            if gap_value != 0:
                                gap_total = self.format_currency_indonesia(abs(gap_value))
                                break
            except:
                pass
            
            chart_data = {
                'period': period,
                'so_data': so_data,
                'do_data': do_data,
                'target_data': target_data,
                'labels': labels,
                'stats': {
                    'avg_target': self.format_currency_indonesia(total_target / len(target_data)) if target_data else "0",
                    'avg_so': self.format_currency_indonesia(total_so / len(so_data)) if so_data else "0",
                    'avg_do': self.format_currency_indonesia(total_do / len(do_data)) if do_data else "0",
                    'total_hk': len(so_data),
                    'sisa_hk_do': max(0, len([l for l in labels if int(l) > current_date.day]) if labels else 0),
                    'gap_total': gap_total
                }
            }
            
            self.logger.info(f"Generated chart with {len(chart_data['so_data'])} days")
            return chart_data
            
        except Exception as e:
            self.logger.error(f"Error generating chart data: {e}")
            return None

    def save_json_files(self, sheets):
        """Generate and save all JSON files"""
        try:
            self.logger.info("Generating JSON files...")
            
            # Process all data
            dashboard_data = self.process_dashboard_data(sheets)
            salesman_list = self.process_salesman_data(sheets)
            salesman_details = self.process_salesman_details(sheets)
            incentive_data = self.process_incentive_data(sheets)
            chart_data = self.generate_chart_data(sheets)
            
            if not dashboard_data or not salesman_list:
                self.logger.error("Failed to process required data")
                return False
            
            # Save files
            files_to_save = [
                ('dashboard.json', dashboard_data),
                ('salesman_list.json', salesman_list),
                ('salesman_details.json', salesman_details),
                ('chart_data.json', chart_data)
            ]
            
            for filename, data in files_to_save:
                if data:
                    filepath = os.path.join(self.data_dir, filename)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    self.logger.info(f"Saved {filename}")
            
            # Save incentive data in JSONL format
            if incentive_data:
                incentive_file = os.path.join(self.data_dir, 'd.insentif.json')
                with open(incentive_file, 'w', encoding='utf-8') as f:
                    for record in incentive_data:
                        json.dump(record, f, ensure_ascii=False)
                        f.write('\n')
                self.logger.info(f"Saved d.insentif.json with {len(incentive_data)} records")
            
            self.logger.info("All JSON files generated successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error generating JSON files: {e}")
            return False

    def git_push_changes(self):
        """Push changes to GitHub"""
        try:
            self.logger.info("Pushing to GitHub...")
            
            # Check git status
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.error(f"Git status failed: {result.stderr}")
                return False
            
            if not result.stdout.strip():
                self.logger.info("No changes to commit")
                return True
            
            # Add files
            files_to_add = ['data/', '*.html', 'morning_update.py', 'morning_update.log']
            for pattern in files_to_add:
                subprocess.run(['git', 'add', pattern], capture_output=True)
            
            # Commit
            commit_message = f"Morning update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            commit_result = subprocess.run(['git', 'commit', '-m', commit_message], 
                                         capture_output=True, text=True)
            
            if commit_result.returncode != 0 and "nothing to commit" not in commit_result.stdout:
                self.logger.error(f"Git commit failed: {commit_result.stderr}")
                return False
            
            # Push
            push_result = subprocess.run(['git', 'push', 'origin', 'main'], 
                                       capture_output=True, text=True)
            
            if push_result.returncode == 0:
                self.logger.info("Successfully pushed to GitHub!")
                self.logger.info("Dashboard URLs:")
                self.logger.info("- Main: https://kisman271128.github.io/salesman-dashboard/")
                self.logger.info("- Mobile: https://kisman271128.github.io/salesman-dashboard/dashboard.html")
                self.logger.info("- Desktop: https://kisman271128.github.io/salesman-dashboard/dashboard-desktop.html")
                return True
            else:
                self.logger.error(f"Git push failed: {push_result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error in git operations: {e}")
            return False

    def run(self):
        """Run the complete update process"""
        start_time = datetime.now()
        
        try:
            # Read Excel data
            sheets = self.read_excel_sheets()
            if not sheets:
                return False
            
            # Generate JSON files
            if not self.save_json_files(sheets):
                return False
            
            # Push to GitHub
            if not self.git_push_changes():
                return False
            
            # Success
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.info(f"Update completed successfully in {duration:.2f} seconds")
            return True
            
        except Exception as e:
            self.logger.error(f"Update failed: {e}")
            return False

def main():
    print("Salesman Dashboard Updater - Simplified Version")
    print("=" * 50)
    
    updater = SalesmanDashboardUpdater()
    success = updater.run()
    
    if success:
        print("\nUpdate successful!")
        print("Dashboard URLs:")
        print("- https://kisman271128.github.io/salesman-dashboard/")
        print("- https://kisman271128.github.io/salesman-dashboard/dashboard.html")
    else:
        print("\nUpdate failed! Check morning_update.log for details.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())