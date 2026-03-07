import pandas as pd

# Your Excel file path
excel_file = r"C:\Users\NDC\Desktop\Integrated Network for Disaster Coordination Project\02_Data\Impacts of Hydro-Meteorological Hazards in Mountain Province_1.xlsx"

print("=" * 50)
print("I.N.D.C. DIAGNOSTIC TOOL")
print("=" * 50)

# Read the Excel file
df = pd.read_excel(excel_file)

print(f"\n📊 Total rows: {len(df)}")
print(f"📋 Total columns: {len(df.columns)}")

print("\n🔍 FIRST 3 ROWS:")
print("-" * 40)
print(df.head(3))

print("\n📑 COLUMN NAMES:")
print("-" * 40)
for i, col in enumerate(df.columns, 1):
    print(f"{i:2}. '{col}'")

print("\n📈 DATA TYPES:")
print("-" * 40)
print(df.dtypes)

print("\n✅ Diagnostic complete!")