import pandas as pd
import psycopg2
import uuid
from datetime import datetime
import re
import os
import glob

print("=" * 60)
print("  I.N.D.C. PROJECT - FINAL WORKING IMPORT TOOL")
print("  Integrated Network for Disaster Coordination")
print("=" * 60)

# ============================================
# CONFIGURATION
# ============================================

DB_CONFIG = {
    "host": "db.bdzbweytmejqiajnvuea.supabase.co",
    "database": "postgres",
    "user": "postgres",
    "password": "3GlkHj5WkjMSUeSq",
    "port": 5432
}

# Find paths
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
PROJECT_PATH = os.path.dirname(SCRIPT_PATH)
DATA_FOLDER = os.path.join(PROJECT_PATH, "02_Data")

print(f"\n📁 Project path: {PROJECT_PATH}")
print(f"📁 Data folder: {DATA_FOLDER}")

# ============================================
# STEP 1: FIND EXCEL FILE
# ============================================
print("\n🔍 STEP 1: Looking for Excel files...")
print("-" * 40)

excel_files = glob.glob(os.path.join(DATA_FOLDER, "*.xlsx"))
if not excel_files:
    print(f"❌ No Excel files found")
    exit(1)

EXCEL_FILE = excel_files[0]
print(f"✅ Found: {os.path.basename(EXCEL_FILE)}")

# ============================================
# STEP 2: READ EXCEL WITH CORRECT HEADERS
# ============================================
print("\n📋 STEP 2: Reading Excel file...")
print("-" * 40)

# Read with headers at row 2 (index 2)
df = pd.read_excel(EXCEL_FILE, header=2)

# Skip the first 3 rows of data (they're empty/title rows)
df = df.iloc[3:].reset_index(drop=True)

print(f"✅ Loaded {len(df)} rows of data")
print(f"✅ Found {len(df.columns)} columns")

# ============================================
# STEP 3: CLEAN COLUMN NAMES
# ============================================
print("\n🧹 STEP 3: Identifying columns...")

# Create a mapping dictionary
col_map = {
    'year': 'YEAR',
    'local_name': 'LOCAL NAME',
    'intl_name': 'INTERNATIONAL NAME',
    'tcws': 'TCWS',
    'affected': 'NO. OF AFFECTED BARANGAYS',
    'injured': None,  # Will find from multi-level headers
    'dead': None,
    'missing': None,
    'partial': None,
    'total': None,
    'agriculture': 'AGRICULTURE',
    'infrastructure': 'INFRASTRUCTURE',
    'source': 'SOURCE / REFERENCE',
    'remarks1': 'REMARKS 1',
    'remarks2': 'REMARKS 2'
}

# Print what we found
print("\n📊 Columns available:")
for i, col in enumerate(df.columns):
    print(f"   {i:2}. '{col}'")

# ============================================
# STEP 4: CONNECT TO DATABASE
# ============================================
print("\n🔌 STEP 4: Connecting to database...")
print("-" * 40)

try:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    print("✅ Database connected!")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    exit(1)

# ============================================
# STEP 5: CLEANING FUNCTIONS
# ============================================
print("\n🧹 STEP 5: Preparing data...")

def clean_number(value):
    if pd.isna(value) or value == '':
        return None
    if isinstance(value, (int, float)):
        return float(value) if value != 0 else None
    if isinstance(value, str):
        # Remove non-numeric characters
        value = re.sub(r'[^\d.-]', '', value)
        try:
            return float(value) if float(value) != 0 else None
        except:
            return None
    return None

def clean_integer(value):
    num = clean_number(value)
    return int(num) if num is not None else None

def clean_text(value):
    if pd.isna(value):
        return None
    return str(value).strip()

# ============================================
# STEP 6: INSERT DATA
# ============================================
print("\n💾 STEP 6: Inserting data into database...")
print("-" * 40)

inserted = 0
errors = 0

for index, row in df.iterrows():
    try:
        # Get year - if no year, skip
        year_val = row['YEAR']
        if pd.isna(year_val):
            continue
            
        year = clean_integer(year_val)
        
        # Get basic info
        local_name = clean_text(row['LOCAL NAME'])
        intl_name = clean_text(row['INTERNATIONAL NAME'])
        tcws = clean_integer(row['TCWS'])
        affected = clean_integer(row['NO. OF AFFECTED BARANGAYS'])
        
        # Get casualties (these are in columns 7, 8, 9)
        injured = clean_integer(row.iloc[7])  # NUMBER OF CASUALTIES column
        dead = clean_integer(row.iloc[8])     # Unnamed: 8
        missing = clean_integer(row.iloc[9])  # Unnamed: 9
        
        # Get damaged houses (columns 10, 11)
        partial = clean_integer(row.iloc[10])  # NUMBER OF DAMAGED HOUSES
        total = clean_integer(row.iloc[11])    # Unnamed: 11
        
        # Get damage costs (columns 12, 13)
        agri = clean_number(row.iloc[12])      # COST OF DAMAGE
        infra = clean_number(row.iloc[13])     # Unnamed: 13
        
        # Get source and remarks
        source = clean_text(row['SOURCE / REFERENCE'])
        remarks1 = clean_text(row['REMARKS 1'])
        remarks2 = clean_text(row['REMARKS 2'])
        
        # Combine remarks
        remarks_parts = []
        if remarks1:
            remarks_parts.append(remarks1)
        if remarks2:
            remarks_parts.append(remarks2)
        full_remarks = " | ".join(remarks_parts) if remarks_parts else None
        
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
            year,
            local_name,
            intl_name,
            tcws,
            affected,
            injured,
            dead,
            missing,
            partial,
            total,
            agri,
            infra,
            source,
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
            print(f"   ⚠️ Error on row {index}: {e}")

conn.commit()

# ============================================
# STEP 7: SUMMARY
# ============================================
print("\n" + "=" * 60)
print("📊 IMPORT SUMMARY")
print("=" * 60)
print(f"   ✅ Successfully inserted: {inserted} records")
print(f"   ⚠️ Errors: {errors}")

# Show sample
print("\n🔍 Sample of imported data:")
cur.execute("""
    SELECT year, local_name, casualties_dead 
    FROM hazard_events 
    WHERE year IS NOT NULL 
    ORDER BY year DESC 
    LIMIT 5
""")
samples = cur.fetchall()
for year, name, dead in samples:
    print(f"   • {int(year) if year else 'Unknown'}: {name or 'Unnamed'}")

cur.close()
conn.close()

print("\n" + "=" * 60)
print("✅ IMPORT COMPLETE!")
print("=" * 60)