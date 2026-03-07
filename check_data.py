import pandas as pd
import os

print("=" * 60)
print("I.N.D.C. DATA CHECKER")
print("=" * 60)

# Your Excel file
excel_path = r"C:\Users\NDC\Desktop\Integrated Network for Disaster Coordination Project\02_Data\Impacts of Hydro-Meteorological Hazards in Mountain Province_1.xlsx"

# Read with header=3
df = pd.read_excel(excel_path, header=3)

print(f"\n📊 Total rows: {len(df)}")
print(f"📋 Total columns: {len(df.columns)}")

print("\n🔍 FIRST 5 ROWS (raw data):")
print("-" * 40)
print(df.head(5))

print("\n📑 COLUMN NAMES FOUND:")
print("-" * 40)
for i, col in enumerate(df.columns, 1):
    print(f"{i:2}. '{col}'")

print("\n🔍 CHECKING FIRST ROW FOR VALUES:")
print("-" * 40)
first_row = df.iloc[0]
for col in df.columns:
    val = first_row[col]
    if pd.notna(val):
        print(f"   {col}: {val} (type: {type(val).__name__})")

print("\n" + "=" * 60)
print("Run this and let me see the output!")
input("Press Enter to exit...")