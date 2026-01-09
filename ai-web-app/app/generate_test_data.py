import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from app import create_app, db
from app.models import CollectionData, DeepCollectionData, AIModel
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    print("=" * 60)
    print("生成AI分析报告测试数据")
    print("=" * 60)

    print("\n检查现有数据...")
    collection_count = CollectionData.query.count()
    deep_collection_count = DeepCollectionData.query.count()
    print(f"   现有采集数据: {collection_count} 条")
    print(f"   现有深度采集数据: {deep_collection_count} 条")

    if collection_count > 0:
        print("\n已有测试数据，跳过生成。")
        print("如需重新生成，请先删除现有数据。")
        sys.exit(0)

    print("\n开始生成测试数据...")

    sources = ['百度', '谷歌', '必应', '搜狗', '360搜索']
    keywords = ['人工智能', '机器学习', '深度学习', '大数据', '云计算', '区块链', '物联网', '5G', '自动驾驶', '智能制造']

    for i in range(50):
        days_ago = i // 7
        collected_at = datetime.utcnow() - timedelta(days=days_ago)

        collection_data = CollectionData(
            title=f'测试数据标题 {i+1} - {keywords[i % len(keywords)]}',
            url=f'https://example.com/article/{i+1}',
            summary=f'这是第{i+1}条测试数据的摘要内容，关于{keywords[i % len(keywords)]}的相关信息。',
            source=sources[i % len(sources)],
            image_url=f'https://example.com/images/{i+1}.jpg',
            keyword=keywords[i % len(keywords)],
            source_type='search',
            raw_data='{}',
            collected_at=collected_at,
            saved_at=collected_at,
            has_deep_collected=(i % 5 == 0)
        )
        db.session.add(collection_data)

        if i % 5 == 0:
            deep_collection = DeepCollectionData(
                collection_data_id=i+1,
                deep_content=f'这是第{i+1}条数据的深度采集内容，包含更详细的分析和解读。',
                analysis_result=f'AI分析结果：该数据关于{keywords[i % len(keywords)]}，具有较高的参考价值。',
                ai_model_id=1,
                collection_status='success',
                error_message=None,
                tokens_used=150 + i,
                created_at=collected_at,
                updated_at=collected_at
            )
            db.session.add(deep_collection)

    db.session.commit()

    print("   ✓ 成功生成 50 条采集数据")
    print("   ✓ 成功生成 10 条深度采集数据")

    print("\n数据统计:")
    print(f"   总采集数据: {CollectionData.query.count()} 条")
    print(f"   总深度采集数据: {DeepCollectionData.query.count()} 条")
    print(f"   数据源数量: {len(set([d.source for d in CollectionData.query.all()]))} 个")
    print(f"   关键词数量: {len(set([d.keyword for d in CollectionData.query.all()]))} 个")

    print("\n" + "=" * 60)
    print("测试数据生成完成！")
    print("=" * 60)