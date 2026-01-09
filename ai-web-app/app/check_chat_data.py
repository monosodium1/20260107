import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'app.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 60)
print("检查对话会话和消息数据")
print("=" * 60)

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("\n数据库中的表:")
for table in tables:
    print(f"  - {table[0]}")

print("\n" + "=" * 60)
print("chat_session 表结构")
print("=" * 60)

cursor.execute("PRAGMA table_info(chat_session)")
columns = cursor.fetchall()

if columns:
    print("\n字段信息:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
else:
    print("\nchat_session 表不存在")

print("\n" + "=" * 60)
print("chat_message 表结构")
print("=" * 60)

cursor.execute("PRAGMA table_info(chat_message)")
columns = cursor.fetchall()

if columns:
    print("\n字段信息:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
else:
    print("\nchat_message 表不存在")

print("\n" + "=" * 60)
print("chat_session 表数据")
print("=" * 60)

cursor.execute("SELECT * FROM chat_session")
sessions = cursor.fetchall()

if sessions:
    print(f"\n共有 {len(sessions)} 个会话:\n")
    for session in sessions:
        print(f"ID: {session[0]}")
        print(f"标题: {session[1]}")
        print(f"用户ID: {session[2]}")
        print(f"AI模型ID: {session[3]}")
        print(f"创建时间: {session[4]}")
        print(f"更新时间: {session[5]}")
        print("-" * 60)
else:
    print("\n没有会话数据")

print("\n" + "=" * 60)
print("chat_message 表数据")
print("=" * 60)

cursor.execute("SELECT * FROM chat_message")
messages = cursor.fetchall()

if messages:
    print(f"\n共有 {len(messages)} 条消息:\n")
    for msg in messages:
        print(f"ID: {msg[0]}")
        print(f"会话ID: {msg[1]}")
        print(f"角色: {msg[2]}")
        print(f"内容: {msg[3][:50] if msg[3] else 'None'}...")
        print(f"消息类型: {msg[4]}")
        print(f"额外数据: {msg[5][:50] if msg[5] else 'None'}...")
        print(f"Token数量: {msg[6]}")
        print(f"创建时间: {msg[7]}")
        print("-" * 60)
else:
    print("\n没有消息数据")

print("\n" + "=" * 60)
print("检查完成")
print("=" * 60)

conn.close()
