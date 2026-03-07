import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import uuid
from datetime import datetime
import os

print("=" * 60)
print("  I.N.D.C. - FINAL IMPORT SCRIPT (FIXED)")
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

# Read the Excel file with headers
df = pd.read_excel(excel_path, header=2)  # Headers are at row 3

# Remove any completely empty rows
df = df.dropna(how='all')

# Skip the first row if it's empty
if pd.isna(df.iloc[0, 0]):
    df = df.iloc[1:].reset_index(drop=True)

print(f"\n📊 Found {len(df)} rows of data")
print(f"📋 Columns: {list(df.columns)}")

# Show first few rows to verify
print("\n🔍 First 3 rows of data:")
print(df.head(3))

# Connect to database
print("\n🔌 Connecting to database...")
conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

# Import data
print("\n💾 Importing data...")
inserted = 0
errors = 0

for index, row in df.iterrows():
    try:
        # Skip if year is missing
        year_val = row.get('YEAR')
        if pd.isna(year_val):
            continue
            
        # Convert year to integer
        try:
            year = int(float(year_val))
        except:
            continue
        
        # Generate UUID as string
        record_id = str(uuid.uuid4())
        
        # Get other values
        local_name = str(row.get('LOCAL NAME')) if not pd.isna(row.get('LOCAL NAME')) else None
        intl_name = str(row.get('INTERNATIONAL NAME')) if not pd.isna(row.get('INTERNATIONAL NAME')) else None
        
        # Create remarks from all data
        remarks = []
        for col in df.columns:
            val = row.get(col)
            if not pd.isna(val):
                remarks.append(f"{col}: {val}")
        
        full_remarks = "\n".join(remarks) if remarks else None
        
        # Insert into database
        cur.execute("""
            INSERT INTO hazard_events (
                id, year, local_name, international_name, raw_remarks,
                created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            record_id,  # This is now a string, not UUID object
            year,
            local_name,
            intl_name,
            full_remarks,
            datetime.now(),
            datetime.now()
        ))
        
        inserted += 1
        if inserted % 10 == 0:
            print(f"   ✅ Inserted {inserted} records...")
            
    except Exception as e:
        errors += 1
        if errors <= 5:
            print(f"   ⚠️ Error on row {index}: {type(e).__name__} - {e}")

conn.commit()
cur.close()
conn.close()

print("\n" + "=" * 60)
print("📊 IMPORT SUMMARY")
print("=" * 60)
print(f"   ✅ Successfully inserted: {inserted} records")
print(f"   ⚠️ Errors: {errors}")

if inserted > 0:
    print("\n🎉 SUCCESS! Your database now has data!")
    print("\n🔍 To verify, run this in Supabase SQL Editor:")
    print("   SELECT COUNT(*) FROM hazard_events;")
    print("   SELECT year, local_name FROM hazard_events LIMIT 5;")
else:
    print("\n❌ No records were inserted. Let me know what errors you see.")

print("=" * 60)