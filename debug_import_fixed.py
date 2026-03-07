import pandas as pd
import os

print("=" * 60)
print("I.N.D.C. DEBUG IMPORT TOOL - FIXED")
print("=" * 60)

# Your Excel file path
excel_path = r"C:\Users\NDC\Desktop\Integrated Network for Disaster Coordination Project\02_Data\Impacts of Hydro-Meteorological Hazards in Mountain Province_1.xlsx"
print(f"Checking file: {excel_path}")

if os.path.exists(excel_path):
    print("✅ File found!")
else:
    print("❌ File not found!")
    exit()

# Look at raw data first
print("\n📊 RAW DATA VIEW (first 15 rows):")
print("-" * 60)

df_raw = pd.read_excel(excel_path, header=None)
for i in range(min(15, len(df_raw))):
    row_values = []
    for val in df_raw.iloc[i].values:
        if pd.isna(val):
            row_values.append("NaN")
        else:
            row_values.append(str(val))
    print(f"Row {i:2}: {' | '.join(row_values[:5])}...")

# Find header row
print("\n🔍 SEARCHING FOR HEADER ROW...")
print("-" * 60)

header_row = None
for i in range(10):
    row_values = []
    for val in df_raw.iloc[i].values:
        if pd.isna(val):
            row_values.append("")
        else:
            row_values.append(str(val).upper())
    
    row_text = " ".join(row_values)
    print(f"Row {i}: {row_text[:100]}")
    
    if 'YEAR' in row_text and 'LOCAL NAME' in row_text:
        header_row = i
        print(f"   ✅ Found header at row {i}!")
        break

if header_row is None:
    print("❌ Could not find header row. Using row 2 as default.")
    header_row = 2

# Read with found header
print(f"\n📖 Reading Excel with header row {header_row}...")
df = pd.read_excel(excel_path, header=header_row)

print(f"\n✅ Success! Loaded {len(df)} rows and {len(df.columns)} columns")

print("\n📋 COLUMN NAMES:")
for i, col in enumerate(df.columns):
    print(f"   {i:2}. '{col}'")

print("\n🔍 FIRST 3 ROWS OF DATA:")
print(df.head(3))

print("\n" + "=" * 60)
print("✅ Debug complete! Copy this output and paste it here.")
input("\nPress Enter to exit...")