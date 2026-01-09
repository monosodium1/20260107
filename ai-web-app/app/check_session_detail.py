import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'app.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 60)
print("检查会话标题的详细数据")
print("=" * 60)

cursor.execute("SELECT id, title, user_id, ai_model_id, created_at, updated_at FROM chat_session")
sessions = cursor.fetchall()

if sessions:
    print(f"\n共有 {len(sessions)} 个会话:\n")
    for session in sessions:
        session_id, title, user_id, ai_model_id, created_at, updated_at = session
        print(f"会话ID: {session_id}")
        print(f"  标题: '{title}' (长度: {len(title)})")
        print(f"  用户ID: {user_id}")
        print(f"  AI模型ID: {ai_model_id}")
        print(f"  创建时间: {created_at}")
        print(f"  更新时间: {updated_at}")
        print("-" * 60)
else:
    print("\n没有会话")

conn.close()
