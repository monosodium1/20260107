import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from app import create_app, db
from app.models import CollectionData, DeepCollectionData

app = create_app()

with app.app_context():
    print("=" * 60)
    print("删除所有测试数据")
    print("=" * 60)

    print("\n删除所有采集数据和深度采集数据...")

    db.session.query(DeepCollectionData).delete()
    db.session.query(CollectionData).delete()
    db.session.commit()

    print("   ✓ 所有数据已删除")

    print("\n" + "=" * 60)
    print("数据删除完成！")
    print("=" * 60)