import pandas as pd
import os

print("=" * 60)
print("I.N.D.C. DEBUG IMPORT TOOL")
print("=" * 60)

# Your Excel file path
excel_path = r"C:\Users\NDC\Desktop\Integrated Network for Disaster Coordination Project\02_Data\Impacts of Hydro-Meteorological Hazards in Mountain Province_1.xlsx"
print(f"Checking file: {excel_path}")

# Check if file exists
if os.path.exists(excel_path):
    print("✅ File found!")
else:
    print("❌ File not found!")
    exit()

# Look at raw data first
print("\n📊 RAW DATA VIEW (first 20 rows):")
print("-" * 40)
df_raw = pd.read_excel(excel_path, header=None)
print(df_raw.head(20))

# Try to find where the actual data starts
print("\n🔍 SEARCHING FOR HEADER ROW...")
print("-" * 40)

for i in range(10):
    row = df_raw.iloc[i].astype(str)
    row_text = ' | '.join(row.values)
    print(f"Row {i}: {row_text[:100]}...")
    
    # Check if this row contains 'YEAR'
    if 'YEAR' in row_text.upper():
        print(f"   ✅ Found 'YEAR' at row {i}!")
        header_row = i
        break

print("\n" + "=" * 60)
print("Now try reading with header =", header_row)
print("=" * 60)

try:
    df = pd.read_excel(excel_path, header=header_row)
    print(f"\n✅ Success! Shape: {df.shape}")
    print(f"\n📋 Column names found:")
    for col in df.columns:
        print(f"   • '{col}'")
    
    print(f"\n🔍 First 3 rows of data:")
    print(df.head(3))
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("Debug complete! Copy this output and paste it here.")
input("Press Enter to exit...")