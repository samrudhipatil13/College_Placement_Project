from database.db_connection import get_connection

conn = get_connection()

if conn:
    print("✅ Connected to MySQL successfully!")
    conn.close()
else:
    print("❌ Failed to connect.")