import sqlite3
import os
import json

db_path = os.path.join(os.path.dirname(__file__), 'app.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 60)
print("检查AI消息内容")
print("=" * 60)

cursor.execute("SELECT id, role, content, message_type, extra_data FROM chat_message WHERE role = 'assistant'")
messages = cursor.fetchall()

if messages:
    print(f"\n共有 {len(messages)} 条AI消息:\n")
    for msg in messages:
        msg_id, role, content, message_type, extra_data = msg
        print(f"消息ID: {msg_id}")
        print(f"  角色: {role}")
        print(f"  类型: {message_type}")
        print(f"  内容长度: {len(content) if content else 0}")
        print(f"  内容: {content[:100] if content else 'None'}...")
        if extra_data:
            try:
                extra = json.loads(extra_data)
                print(f"  额外数据字段: {list(extra.keys())}")
                if 'text' in extra:
                    print(f"  额外数据中的text: {extra['text'][:100]}...")
            except:
                print(f"  额外数据解析失败")
        print("-" * 60)
else:
    print("\n没有AI消息")

conn.close()
