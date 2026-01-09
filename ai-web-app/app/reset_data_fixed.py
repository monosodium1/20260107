import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from app import create_app, db
from app.models import User, CrawlerSource, CollectionData

app = create_app()

with app.app_context():
    print("=" * 60)
    print("重置数据库数据")
    print("=" * 60)

    print("\n删除所有现有数据...")
    
    # 删除所有表的数据（不删除表结构）
    db.session.query(CollectionData).delete()
    db.session.query(CrawlerSource).delete()
    db.session.query(User).delete()
    
    db.session.commit()
    print("   ✓ 所有数据已删除")
    
    print("\n" + "=" * 60)
    print("创建测试数据")
    print("=" * 60)
    
    print("\n1. 创建管理员用户...")
    admin = User(username='admin')
    db.session.add(admin)
    db.session.commit()
    print("   ✓ 管理员用户创建成功")
    
    print("\n2. 创建爬虫源...")
    
    # 百度搜索源
    baidu_source = CrawlerSource()
    baidu_source.name = '百度搜索'
    baidu_source.source_type = 'baidu'
    baidu_source.description = '百度搜索引擎'
    baidu_source.url = 'https://www.baidu.com/s'
    baidu_source.method = 'GET'
    baidu_source.headers = '{"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}'
    baidu_source.data_selector = '{"type": "css", "selector": "div.result"}'
    baidu_source.title_selector = 'h3 a'
    baidu_source.url_selector = 'h3 a'
    baidu_source.summary_selector = 'div.c-abstract'
    baidu_source.status = 'active'
    db.session.add(baidu_source)
    print("   ✓ 百度搜索源创建成功")
    
    # DuckDuckGo搜索源
    duckduckgo_source = CrawlerSource()
    duckduckgo_source.name = 'DuckDuckGo搜索'
    duckduckgo_source.source_type = 'duckduckgo'
    duckduckgo_source.description = 'DuckDuckGo搜索引擎（无反爬虫）'
    duckduckgo_source.url = 'https://html.duckduckgo.com/html/'
    duckduckgo_source.method = 'POST'
    duckduckgo_source.headers = '{"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}'
    duckduckgo_source.body_template = '{"q": "{keyword}", "kl": "cn-zh"}'
    duckduckgo_source.data_selector = '{"type": "css", "selector": "div.result"}'
    duckduckgo_source.title_selector = 'a.result__a'
    duckduckgo_source.url_selector = 'a.result__a'
    duckduckgo_source.summary_selector = 'a.result__snippet'
    duckduckgo_source.status = 'active'
    db.session.add(duckduckgo_source)
    print("   ✓ DuckDuckGo搜索源创建成功")
    
    # 自定义测试源
    custom_source = CrawlerSource()
    custom_source.name = '测试网站'
    custom_source.source_type = 'custom'
    custom_source.description = '用于测试的HTTP请求网站'
    custom_source.url = 'https://httpbin.org/html'
    custom_source.method = 'GET'
    custom_source.headers = '{"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}'
    custom_source.data_selector = '{"type": "css", "selector": "body"}'
    custom_source.title_selector = 'h1'
    custom_source.url_selector = 'a'
    custom_source.summary_selector = 'p'
    custom_source.status = 'active'
    db.session.add(custom_source)
    print("   ✓ 测试网站源创建成功")
    
    db.session.commit()
    
    print("\n3. 创建采集数据...")
    
    mock_data = [
        {
            'title': '人工智能在医疗领域的应用',
            'url': 'https://example.com/ai-medical',
            'summary': '人工智能技术在医疗诊断、药物研发等方面的应用越来越广泛...',
            'image_url': 'https://example.com/images/ai-medical.jpg',
            'source': '模拟数据',
            'keyword': '人工智能'
        },
        {
            'title': '机器学习算法的最新进展',
            'url': 'https://example.com/ml-algorithms',
            'summary': '深度学习、强化学习等机器学习算法在各个领域的应用案例...',
            'image_url': 'https://example.com/images/ml-algorithms.jpg',
            'source': '模拟数据',
            'keyword': '机器学习'
        },
        {
            'title': '自然语言处理技术突破',
            'url': 'https://example.com/nlp-breakthrough',
            'summary': '大语言模型在文本生成、翻译、问答等任务中表现出色...',
            'image_url': 'https://example.com/images/nlp.jpg',
            'source': '模拟数据',
            'keyword': '自然语言处理'
        },
        {
            'title': '计算机视觉在工业质检中的应用',
            'url': 'https://example.com/cv-quality',
            'summary': '基于深度学习的计算机视觉技术在工业质检中大幅提高了效率...',
            'image_url': 'https://example.com/images/cv-quality.jpg',
            'source': '模拟数据',
            'keyword': '计算机视觉'
        },
        {
            'title': 'AI驱动的智能客服系统',
            'url': 'https://example.com/ai-customer-service',
            'summary': '智能客服系统通过自然语言处理技术为客户提供24小时服务...',
            'image_url': 'https://example.com/images/ai-cs.jpg',
            'source': '模拟数据',
            'keyword': '智能客服'
        }
    ]
    
    for item in mock_data:
        collection_data = CollectionData()
        collection_data.title = item['title']
        collection_data.url = item['url']
        collection_data.summary = item['summary']
        collection_data.image_url = item['image_url']
        collection_data.source = item['source']
        collection_data.keyword = item['keyword']
        collection_data.source_type = 'mock'
        db.session.add(collection_data)
    
    db.session.commit()
    print(f"   ✓ 创建了 {len(mock_data)} 条采集数据")
    
    print("\n" + "=" * 60)
    print("数据库重置完成!")
    print("=" * 60)
    print("\n默认登录信息:")
    print("  用户名: admin")
    print("  密码: 123456")
    print()