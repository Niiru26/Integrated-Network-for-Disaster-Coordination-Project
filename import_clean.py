import pandas as pd
import psycopg2
import uuid
from datetime import datetime
import os

print("=" * 60)
print("  I.N.D.C. - CLEAN DATA IMPORT")
print("  Integrated Network for Disaster Coordination")
print("=" * 60)

# Database connection
DB_CONFIG = {
    "host": "db.bdzbweytmejqiajnvuea.supabase.co",
    "database": "postgres",
    "user": "postgres",
    "password": "3GlkHj5WkjMSUeSq",
    "port": 5432
}

# Your cleaned Excel file
excel_path = r"C:\Users\NDC\Desktop\Integrated Network for Disaster Coordination Project\02_Data\I.N.D.C_Impacts of Typhoon.xlsx"

print(f"\n📂 Reading file: {os.path.basename(excel_path)}")

# Read the Excel file (headers are in row 1)
df = pd.read_excel(excel_path)
print(f"📊 Found {len(df)} rows of data")
print(f"📋 Found {len(df.columns)} columns")

# Show first few rows to verify
print("\n🔍 Preview of first 3 rows:")
print(df.head(3))

# Connect to database
print("\n🔌 Connecting to database...")
conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

# Optional: Clear existing data if you want fresh start
# cur.execute("DELETE FROM hazard_events")
# print("🧹 Cleared existing data")

# Import data
print("\n💾 Importing data...")
inserted = 0
errors = 0

for index, row in df.iterrows():
    try:
        # Skip if year is missing
        if pd.isna(row.get('YEAR')):
            continue
            
        # Insert into database
        cur.execute("""
            INSERT INTO hazard_events (
                id, year, local_name, international_name, tcws_signal,
                affected_barangays_count,
                casualties_injured, casualties_dead, casualties_missing,
                houses_partial, houses_total,
                damage_agriculture, damage_infrastructure,
                source_reference, raw_remarks,
                created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            uuid.uuid4(),
            row.get('YEAR') if not pd.isna(row.get('YEAR')) else None,
            row.get('LOCAL NAME') if not pd.isna(row.get('LOCAL NAME')) else None,
            row.get('INTERNATIONAL NAME') if not pd.isna(row.get('INTERNATIONAL NAME')) else None,
            row.get('TCWS') if not pd.isna(row.get('TCWS')) else None,
            row.get('NO. OF AFFECTED BARANGAYS') if not pd.isna(row.get('NO. OF AFFECTED BARANGAYS')) else None,
            row.get('Injured') if not pd.isna(row.get('Injured')) else None,
            row.get('Dead') if not pd.isna(row.get('Dead')) else None,
            row.get('Missing') if not pd.isna(row.get('Missing')) else None,
            row.get('Partial') if not pd.isna(row.get('Partial')) else None,
            row.get('Total') if not pd.isna(row.get('Total')) else None,
            row.get('AGRICULTURE') if not pd.isna(row.get('AGRICULTURE')) else None,
            row.get('INFRASTRUCTURE') if not pd.isna(row.get('INFRASTRUCTURE')) else None,
            row.get('SOURCE / REFERENCE') if not pd.isna(row.get('SOURCE / REFERENCE')) else None,
            f"Remarks 1: {row.get('REMARKS 1')} | Remarks 2: {row.get('REMARKS 2')}",
            datetime.now(),
            datetime.now()
        ))
        
        inserted += 1
        if inserted % 10 == 0:
            print(f"   ✅ Inserted {inserted} records...")
            
    except Exception as e:
        errors += 1
        if errors <= 5:
            print(f"   ⚠️ Error on row {index}: {e}")

conn.commit()
cur.close()
conn.close()

print("\n" + "=" * 60)
print("📊 IMPORT SUMMARY")
print("=" * 60)
print(f"   ✅ Successfully inserted: {inserted} records")
print(f"   ⚠️ Errors: {errors}")
print("=" * 60)