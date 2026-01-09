import sqlite3
import os
from werkzeug.security import generate_password_hash

db_path = os.path.join(os.path.dirname(__file__), 'app.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 60)
print("为现有用户设置密码")
print("=" * 60)

cursor.execute("SELECT id, username FROM user")
users = cursor.fetchall()

if users:
    print(f"\n找到 {len(users)} 个用户:\n")
    
    for user in users:
        user_id, username = user[0], user[1]
        print(f"用户ID: {user_id}, 用户名: {username}")
        
        cursor.execute("SELECT password_hash FROM user WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        
        if result and result[0]:
            print(f"  密码已设置，跳过")
        else:
            password_hash = generate_password_hash('123456')
            cursor.execute("UPDATE user SET password_hash = ? WHERE id = ?", (password_hash, user_id))
            print(f"  ✓ 已设置默认密码: 123456")
    
    conn.commit()
    print("\n" + "=" * 60)
    print("密码设置完成！")
    print("=" * 60)
else:
    print("\n没有找到用户")

conn.close()
