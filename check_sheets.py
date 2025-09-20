import pandas as pd

xl = pd.ExcelFile('DbaseSalesmanWebApp.xlsm')
print('Available sheets:')
for sheet in xl.sheet_names:
    print(f'  - {sheet}')
print()
print('Is d.soharian present?', 'd.soharian' in xl.sheet_names)

# If sheet exists, check content
if 'd.soharian' in xl.sheet_names:
    df = pd.read_excel('DbaseSalesmanWebApp.xlsm', sheet_name='d.soharian')
    print('Sheet content:')
    print('Columns:', list(df.columns))
    print('Rows:', len(df))
    print('First 3 rows:')
    print(df.head(3))
else:
    print('❌ Sheet d.soharian NOT FOUND!')