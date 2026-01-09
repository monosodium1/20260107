import sqlite3
import os
import json

db_path = os.path.join(os.path.dirname(__file__), 'app.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 60)
print("测试会话加载")
print("=" * 60)

cursor.execute("SELECT id, title, user_id, ai_model_id FROM chat_session")
sessions = cursor.fetchall()

for session in sessions:
    print(f"\n会话ID: {session[0]}, 标题: {session[1]}, 用户ID: {session[2]}, AI模型ID: {session[3]}")
    
    cursor.execute("SELECT id, role, content, message_type, extra_data FROM chat_message WHERE session_id = ?", (session[0],))
    messages = cursor.fetchall()
    
    print(f"  消息数量: {len(messages)}")
    
    for msg in messages:
        print(f"    消息ID: {msg[0]}, 角色: {msg[1]}, 类型: {msg[3]}")
        print(f"    内容: {msg[2][:50] if msg[2] else 'None'}")
        if msg[4]:
            try:
                extra = json.loads(msg[4])
                print(f"    额外数据: {list(extra.keys())}")
            except:
                print(f"    额外数据解析失败")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)

conn.close()
