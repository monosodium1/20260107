import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'app.db')

if os.path.exists(db_path):
    print(f"数据库文件: {db_path}")
    print(f"文件大小: {os.path.getsize(db_path)} 字节")
    print()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    print("数据库表:")
    for table in tables:
        print(f"  - {table[0]}")

    print()

    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"{table_name}: {count} 条记录")

    conn.close()
else:
    print(f"数据库文件不存在: {db_path}")