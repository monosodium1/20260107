import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'app.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 60)
print("检查用户数据")
print("=" * 60)

cursor.execute("SELECT * FROM user")
users = cursor.fetchall()

if users:
    print(f"\n共有 {len(users)} 个用户:\n")
    for user in users:
        print(f"ID: {user[0]}")
        print(f"用户名: {user[1]}")
        print("-" * 60)
else:
    print("\n没有用户数据")

print("\n" + "=" * 60)
print("检查会话数据")
print("=" * 60)

cursor.execute("SELECT id, title, user_id FROM chat_session")
sessions = cursor.fetchall()

if sessions:
    print(f"\n共有 {len(sessions)} 个会话:\n")
    for session in sessions:
        print(f"会话ID: {session[0]}, 标题: {session[1]}, 用户ID: {session[2]}")
else:
    print("\n没有会话数据")

print("\n" + "=" * 60)
print("检查完成")
print("=" * 60)

conn.close()
