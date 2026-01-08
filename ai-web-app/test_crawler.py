#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
爬虫功能测试脚本
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import CrawlerSource, CrawlerTask, CollectionData
from app.services.universal_crawler import UniversalCrawler
import json

def test_crawler():
    """测试爬虫功能"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("爬虫功能测试")
        print("=" * 60)
        
        # 1. 检查现有爬虫源
        print("\n1. 检查现有爬虫源...")
        sources = CrawlerSource.query.all()
        if sources:
            print(f"   找到 {len(sources)} 个爬虫源:")
            for source in sources:
                print(f"   - ID: {source.id}, 名称: {source.name}, URL: {source.url}")
        else:
            print("   未找到爬虫源，正在创建测试爬虫源...")
            
            # 创建百度搜索爬虫源
            baidu_source = CrawlerSource(
                name="百度搜索",
                source_type="baidu",
                description="百度搜索引擎",
                url="https://www.baidu.com/s",
                method="GET",
                headers='{"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}',
                data_selector='{"title": ".result.c-container h3", "url": ".result.c-container h3 a", "summary": ".c-abstract"}',
                status="active"
            )
            db.session.add(baidu_source)
            db.session.commit()
            print(f"   已创建百度搜索爬虫源 (ID: {baidu_source.id})")
            sources = [baidu_source]
        
        # 2. 测试通用爬虫引擎
        print("\n2. 测试通用爬虫引擎...")
        
        for source in sources:
            print(f"\n   测试爬虫源: {source.name}")
            print(f"   URL: {source.url}")
            
            # 构建爬虫配置
            source_config = {
                'url': source.url,
                'method': source.method,
                'headers': source.headers,
                'data_selector': source.data_selector,
                'title_selector': source.title_selector,
                'url_selector': source.url_selector,
                'summary_selector': source.summary_selector,
                'image_selector': source.image_selector
            }
            
            crawler = UniversalCrawler(source_config)
            
            # 执行爬取
            try:
                print(f"   正在爬取关键词 '人工智能'...")
                result = crawler.crawl(keyword="人工智能", page=1, limit=5)
                
                print(f"   ✓ 爬取成功!")
                print(f"   采集到 {len(result)} 条数据")
                
                # 显示前3条数据
                for i, item in enumerate(result[:3]):
                    print(f"\n   数据 {i+1}:")
                    print(f"     标题: {item.get('title', 'N/A')[:50]}...")
                    print(f"     URL: {item.get('url', 'N/A')[:60]}...")
                    print(f"     摘要: {item.get('summary', 'N/A')[:80]}...")
                
                # 保存到数据库
                print(f"\n   正在保存数据到数据库...")
                saved_count = 0
                for item in result:
                    collection_data = CollectionData(
                        title=item.get('title', ''),
                        url=item.get('url', ''),
                        summary=item.get('summary', ''),
                        source=source.name,
                        keyword="人工智能",
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
        
        # 3. 检查数据库中的采集数据
        print("\n3. 检查数据库中的采集数据...")
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
        
        # 4. 统计信息
        print("\n4. 统计信息:")
        print(f"   爬虫源总数: {CrawlerSource.query.count()}")
        print(f"   爬虫任务总数: {CrawlerTask.query.count()}")
        print(f"   采集数据总数: {CollectionData.query.count()}")
        
        print("\n" + "=" * 60)
        print("测试完成!")
        print("=" * 60)

if __name__ == '__main__':
    test_crawler()
