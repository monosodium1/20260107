import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from app import create_app, db
from app.models import AIModel

app = create_app()

with app.app_context():
    print("=" * 60)
    print("创建测试AI模型")
    print("=" * 60)

    print("\n检查现有AI模型...")
    models = AIModel.query.all()
    if models:
        print(f"   现有AI模型: {len(models)} 个")
        for model in models:
            print(f"     - {model.name} (ID: {model.id})")
        print("\n已有AI模型，跳过创建。")
        sys.exit(0)

    print("\n创建测试AI模型...")

    model = AIModel(
        name='测试AI模型',
        api_url='https://api.openai.com/v1/chat/completions',
        api_key='sk-test-key-placeholder',
        model_name='gpt-3.5-turbo',
        system_prompt='你是一个专业的数据分析助手，可以帮助用户查询和分析数据库中的数据。',
        status='active',
        is_default=True
    )

    db.session.add(model)
    db.session.commit()

    print("   ✓ 成功创建AI模型")
    print(f"   模型名称: {model.name}")
    print(f"   模型ID: {model.id}")
    print(f"   状态: {model.status}")
    print(f"   默认模型: {model.is_default}")

    print("\n" + "=" * 60)
    print("AI模型创建完成！")
    print("=" * 60)
    print("\n注意: 这是一个测试模型，API密钥是占位符。")
    print("如需使用真实的AI功能，请在AI模型管理中配置有效的API密钥。")