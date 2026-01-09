import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'app.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 60)
print("数据库表结构")
print("=" * 60)

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

for table in tables:
    table_name = table[0]
    print(f"\n表名: {table_name}")
    print("-" * 60)
    
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    for col in columns:
        print(f"  {col[1]} ({col[2]})")

conn.close()