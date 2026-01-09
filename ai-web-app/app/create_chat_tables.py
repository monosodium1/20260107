import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from app import create_app, db
from app.models import ChatSession, ChatMessage

app = create_app()

with app.app_context():
    print("=" * 60)
    print("创建对话会话和消息表")
    print("=" * 60)

    print("\n创建数据库表...")
    
    db.create_all()
    
    print("   ✓ 数据库表创建成功")

    print("\n" + "=" * 60)
    print("表创建完成！")
    print("=" * 60)