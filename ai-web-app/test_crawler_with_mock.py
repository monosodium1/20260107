#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
爬虫功能测试脚本 - 使用测试网站
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import CrawlerSource, CrawlerTask, CollectionData
from app.services.universal_crawler import UniversalCrawler
import json

def test_crawler_with_test_site():
    """使用测试网站测试爬虫功能"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("爬虫功能测试 - 使用测试网站")
        print("=" * 60)
        
        # 1. 创建测试爬虫源
        print("\n1. 创建测试爬虫源...")
        
        # 使用httpbin.org作为测试网站
        test_source = CrawlerSource(
            name="测试网站",
            source_type="test",
            description="用于测试的HTTP请求网站",
            url="https://httpbin.org/html",
            method="GET",
            headers='{"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}',
            data_selector='{"title": "h1", "content": "p"}',
            status="active"
        )
        
        # 检查是否已存在
        existing = CrawlerSource.query.filter_by(name="测试网站").first()
        if existing:
            db.session.delete(existing)
            db.session.commit()
        
        db.session.add(test_source)
        db.session.commit()
        print(f"   已创建测试爬虫源 (ID: {test_source.id})")
        
        # 2. 测试通用爬虫引擎
        print("\n2. 测试通用爬虫引擎...")
        
        # 构建爬虫配置
        source_config = {
            'url': test_source.url,
            'method': test_source.method,
            'headers': test_source.headers,
            'data_selector': test_source.data_selector,
            'title_selector': test_source.title_selector,
            'url_selector': test_source.url_selector,
            'summary_selector': test_source.summary_selector,
            'image_selector': test_source.image_selector
        }
        
        crawler = UniversalCrawler(source_config)
        
        # 执行爬取
        try:
            print(f"   正在爬取测试网站...")
            result = crawler.crawl(keyword="test", page=1, limit=5)
            
            print(f"   ✓ 爬取成功!")
            print(f"   采集到 {len(result)} 条数据")
            
            # 显示结果
            for i, item in enumerate(result[:3]):
                print(f"\n   数据 {i+1}:")
                print(f"     标题: {item.get('title', 'N/A')[:100]}...")
                print(f"     URL: {item.get('url', 'N/A')[:100]}...")
                print(f"     摘要: {item.get('summary', 'N/A')[:100]}...")
            
            # 保存到数据库
            print(f"\n   正在保存数据到数据库...")
            saved_count = 0
            for item in result:
                collection_data = CollectionData(
                    title=item.get('title', ''),
                    url=item.get('url', ''),
                    summary=item.get('summary', ''),
                    source=test_source.name,
                    keyword="test",
                    image_url=item.get('image_url', '')
                )
                db.session.add(collection_data)
                saved_count += 1
            
            db.session.commit()
            print(f"   ✓ 已保存 {saved_count} 条数据到数据库")
                
        except Exception as e:
            print(f"   ✗ 测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # 3. 创建模拟数据
        print("\n3. 创建模拟数据用于测试...")
        
        mock_data = [
            {
                'title': '人工智能在医疗领域的应用',
                'url': 'https://example.com/ai-medical',
                'summary': '人工智能技术在医疗诊断、药物研发等方面的应用越来越广泛...',
                'image_url': 'https://example.com/images/ai-medical.jpg'
            },
            {
                'title': '机器学习算法的最新进展',
                'url': 'https://example.com/ml-algorithms',
                'summary': '深度学习、强化学习等机器学习算法在各个领域的应用案例...',
                'image_url': 'https://example.com/images/ml-algorithms.jpg'
            },
            {
                'title': '自然语言处理技术突破',
                'url': 'https://example.com/nlp-breakthrough',
                'summary': '大语言模型在文本生成、翻译、问答等任务中表现出色...',
                'image_url': 'https://example.com/images/nlp.jpg'
            },
            {
                'title': '计算机视觉在工业质检中的应用',
                'url': 'https://example.com/cv-quality',
                'summary': '基于深度学习的计算机视觉技术在工业质检中大幅提高了效率...',
                'image_url': 'https://example.com/images/cv-quality.jpg'
            },
            {
                'title': 'AI驱动的智能客服系统',
                'url': 'https://example.com/ai-customer-service',
                'summary': '智能客服系统通过自然语言处理技术为客户提供24小时服务...',
                'image_url': 'https://example.com/images/ai-cs.jpg'
            }
        ]
        
        saved_count = 0
        for item in mock_data:
            collection_data = CollectionData(
                title=item['title'],
                url=item['url'],
                summary=item['summary'],
                source='模拟数据',
                keyword='人工智能',
                image_url=item['image_url']
            )
            db.session.add(collection_data)
            saved_count += 1
        
        db.session.commit()
        print(f"   ✓ 已创建 {saved_count} 条模拟数据")
        
        # 4. 检查数据库中的采集数据
        print("\n4. 检查数据库中的采集数据...")
        collection_data = CollectionData.query.all()
        print(f"   数据库中共有 {len(collection_data)} 条采集数据")
        
        if collection_data:
            print(f"\n   最新采集的5条数据:")
            for item in collection_data[-5:]:
                print(f"   - 标题: {item.title[:50]}...")
                print(f"     来源: {item.source}")
                print(f"     关键词: {item.keyword}")
                print(f"     采集时间: {item.collected_at}")
                print()
        
        # 5. 统计信息
        print("\n5. 统计信息:")
        print(f"   爬虫源总数: {CrawlerSource.query.count()}")
        print(f"   爬虫任务总数: {CrawlerTask.query.count()}")
        print(f"   采集数据总数: {CollectionData.query.count()}")
        
        print("\n" + "=" * 60)
        print("测试完成!")
        print("=" * 60)
        print("\n说明:")
        print("- 由于百度等搜索引擎有反爬虫机制，直接爬取可能会失败")
        print("- 实际使用时，需要配置合适的请求头、代理或使用其他策略")
        print("- 本测试创建了模拟数据以验证系统功能")
        print("- 您可以在Web界面中查看这些数据")

if __name__ == '__main__':
    test_crawler_with_test_site()
