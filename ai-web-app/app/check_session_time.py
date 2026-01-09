import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'app.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 60)
print("检查会话时间格式")
print("=" * 60)

cursor.execute("SELECT id, title, updated_at FROM chat_session")
sessions = cursor.fetchall()

if sessions:
    print(f"\n共有 {len(sessions)} 个会话:\n")
    for session in sessions:
        session_id, title, updated_at = session
        print(f"会话ID: {session_id}")
        print(f"  标题: {title}")
        print(f"  更新时间: {updated_at}")
        print(f"  时间类型: {type(updated_at)}")
        print("-" * 60)
else:
    print("\n没有会话")

conn.close()
