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
        """Read Excel file and return xl_file object"""
        try:
            self.logger.info("Reading Excel file...")
            
            # Try different engines for compatibility
            try:
                xl_file = pd.ExcelFile(self.excel_file, engine='pyxlsb')
            except:
                try:
                    xl_file = pd.ExcelFile(self.excel_file, engine='openpyxl')
                except:
                    xl_file = pd.ExcelFile(self.excel_file)
            
            self.logger.info(f"Excel file loaded with {len(xl_file.sheet_names)} sheets")
            return xl_file
            
        except Exception as e:
            self.logger.error(f"Error reading Excel: {e}")
            return None

    def export_raw_sheets_for_android(self, xl_file):
        """Export raw sheets for Android app"""
        try:
            self.logger.info("Exporting raw JSONL sheets for Android app...")
            
            # Get all sheet names that start with "d."
            all_sheet_names = xl_file.sheet_names
            filtered_sheets = [sheet for sheet in all_sheet_names if sheet.startswith('d.')]
            
            # Define output folders
            android_folder = r'C:\Users\kisman.pidu\AndroidStudioProjects\MAS\app\src\main\assets\data'
            dashboard_folder = r'C:\Dashboard\data'
            
            # Create folders if they don't exist
            os.makedirs(android_folder, exist_ok=True)
            os.makedirs(dashboard_folder, exist_ok=True)
            
            # Export each filtered sheet to both locations
            for sheet in filtered_sheets:
                try:
                    df = pd.read_excel(xl_file, sheet_name=sheet)
                    
                    # Save to Android Studio location (JSONL format)
                    android_file = os.path.join(android_folder, f"{sheet}.json")
                    df.to_json(android_file, orient='records', lines=True)
                    
                    # Save to Dashboard location (JSONL format) 
                    dashboard_file = os.path.join(dashboard_folder, f"{sheet}.json")
                    df.to_json(dashboard_file, orient='records', lines=True)
                    
                    self.logger.info(f"Exported raw {sheet} to both locations ({len(df)} rows)")
                    
                except Exception as e:
                    self.logger.warning(f"Could not export {sheet}: {e}")
            
            self.logger.info(f"Raw export completed: {len(filtered_sheets)} sheets processed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting raw sheets: {e}")
            return False

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

    def generate_chart_data_only(self, xl_file):
        """Generate only chart_data.json for web dashboard"""
        try:
            self.logger.info("Generating chart_data.json...")
            
            # Read only the required sheet for chart
            try:
                so_df = pd.read_excel(xl_file, sheet_name='d.soharian')
            except Exception as e:
                self.logger.error(f"Could not read d.soharian sheet: {e}")
                return None
            
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
            
            # 🔧 FIXED: Filter untuk menghitung avg hanya dari nilai > 0
            so_data_positive = [x for x in so_data if x > 0]
            do_data_positive = [x for x in do_data if x > 0]

            # Get period
            current_date = datetime.now()
            month_id = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
                       'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'][current_date.month - 1]
            period = f"{month_id} {current_date.year}"
            
            # Get gap from dashboard sheet
            gap_total = "0"
            try:
                dashboard_df = pd.read_excel(xl_file, sheet_name='d.dashboard')
                for _, row in dashboard_df.iterrows():
                    if str(row.get('LOB', '')).strip().upper() == 'TOTAL':
                        gap_value = self.safe_float(row.get('Gap', 0))
                        if gap_value != 0:
                            gap_total = self.format_currency_indonesia(abs(gap_value))
                            break
            except Exception as e:
                self.logger.warning(f"Could not get gap total from dashboard: {e}")
            
            # Calculate sisa_hk_do: total days minus days with DO > 0
            closed_days = sum(1 for d in do_data if d > 0)
            sisa_hk_do = len(do_data) - closed_days
            
            chart_data = {
                'period': period,
                'so_data': so_data,
                'do_data': do_data,
                'target_data': target_data,
                'labels': labels,
                'stats': {
                    'avg_target': self.format_currency_indonesia(total_target / len(target_data)) if target_data else "0",
                    'avg_so': self.format_currency_indonesia(sum(so_data_positive) / len(so_data_positive)) if so_data_positive else "0",
                    'avg_do': self.format_currency_indonesia(sum(do_data_positive) / len(do_data_positive)) if do_data_positive else "0",
                    'total_hk': len(so_data),
                    'sisa_hk_do': sisa_hk_do,
                    'gap_total': gap_total
                }
            }
            
            self.logger.info(f"Generated chart with {len(chart_data['so_data'])} days")
            return chart_data
            
        except Exception as e:
            self.logger.error(f"Error generating chart data: {e}")
            return None

    def save_chart_data_json(self, chart_data):
        """Save only chart_data.json"""
        try:
            if not chart_data:
                self.logger.error("No chart data to save")
                return False
            
            # Save chart_data.json
            chart_file = os.path.join(self.data_dir, 'chart_data.json')
            with open(chart_file, 'w', encoding='utf-8') as f:
                json.dump(chart_data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Saved chart_data.json")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving chart data: {e}")
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
            files_to_add = [
                'data/', 
                '*.html', 
                'morning_update.py', 
                'morning_update.log',
                # PWA files
                'manifest.json',
                'service-worker.js',
                'device-auth.js',
                'icon-*.png',
                'device-admin.html'
            ]
            for pattern in files_to_add:
                subprocess.run(['git', 'add', pattern], capture_output=True)
            
            # Commit
            commit_message = f"Morning update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Simplified: Raw JSONL + Chart Data Only"
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
        """Run the super simplified update process"""
        start_time = datetime.now()
        
        try:
            # Read Excel file
            xl_file = self.read_excel_sheets()
            if not xl_file:
                return False
            
            # Export raw JSONL sheets for Android app
            # This creates d.dashboard.json, d.performance.json, etc. in JSONL format
            if not self.export_raw_sheets_for_android(xl_file):
                self.logger.warning("Raw sheets export failed, continuing...")
            
            # Generate only chart_data.json for web dashboard
            chart_data = self.generate_chart_data_only(xl_file)
            if not self.save_chart_data_json(chart_data):
                return False
            
            # Push to GitHub
            if not self.git_push_changes():
                return False
            
            # Success
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.info(f"Super simplified update finished successfully in {duration:.2f} seconds")
            return True
            
        except Exception as e:
            self.logger.error(f"Update failed: {e}")
            return False

def main():
    print("Salesman Dashboard Updater - Super Simplified Version")
    print("=" * 55)
    print("Features:")
    print("- Raw JSONL export for Android app (all d.* sheets)")
    print("- Only chart_data.json for web dashboard")
    print("- No processed JSON files (dashboard.json, salesman_list.json, etc.)")
    print("- Dual location export (Android Studio + Dashboard folder)")
    print()
    print("Files Generated:")
    print("1. data/d.dashboard.json (JSONL) - For dashboard.html")
    print("2. data/d.performance.json (JSONL) - For dashboard.html") 
    print("3. data/chart_data.json (JSON) - For dashboard.html")
    print("4. All other d.* sheets (JSONL) - For Android app")
    
    updater = SalesmanDashboardUpdater()
    success = updater.run()
    
    if success:
        print("\nSuper simplified update successful!")
        print("\nWeb Dashboard (uses 3 files only):")
        print("- https://kisman271128.github.io/salesman-dashboard/")
        print("- https://kisman271128.github.io/salesman-dashboard/dashboard.html")
        print("\nAndroid App Data:")
        print("- All d.* sheets exported as JSONL to Android Studio assets")
    else:
        print("\nUpdate failed! Check morning_update.log for details.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())