import psycopg2

# Your correct database configuration
DB_CONFIG = {
    "host": "db.bdzbweytmejqiajnvuea.supabase.co",
    "database": "postgres",
    "user": "postgres",
    "password": "3GlkHj5WkjMSUeSq",
    "port": 5432
}

print("Testing connection to Supabase...")
print(f"Host: {DB_CONFIG['host']}")

try:
    conn = psycopg2.connect(**DB_CONFIG)
    print("✅ SUCCESS! Connected to database!")
    conn.close()
except Exception as e:
    print(f"❌ FAILED: {e}")