import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'app.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 60)
print("迁移数据库：添加 password_hash 和 created_at 字段")
print("=" * 60)

try:
    cursor.execute("PRAGMA table_info(user)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    print("\n当前 user 表字段:", column_names)
    
    if 'password_hash' not in column_names:
        print("\n添加 password_hash 字段...")
        cursor.execute("ALTER TABLE user ADD COLUMN password_hash VARCHAR(255) NOT NULL DEFAULT ''")
        print("✓ password_hash 字段添加成功")
    else:
        print("\npassword_hash 字段已存在")
    
    if 'created_at' not in column_names:
        print("\n添加 created_at 字段...")
        cursor.execute("ALTER TABLE user ADD COLUMN created_at DATETIME")
        print("✓ created_at 字段添加成功")
    else:
        print("\ncreated_at 字段已存在")
    
    conn.commit()
    
    cursor.execute("PRAGMA table_info(user)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    print("\n更新后的 user 表字段:", column_names)
    
    print("\n" + "=" * 60)
    print("数据库迁移完成！")
    print("=" * 60)
    
except Exception as e:
    print(f"\n错误: {e}")
    conn.rollback()
finally:
    conn.close()
