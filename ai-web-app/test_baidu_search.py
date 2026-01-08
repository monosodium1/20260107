#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试百度搜索爬虫并输出详细日志
"""
import sys
import os

# 添加baidusearch目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dist', 'baidusearch'))

from baidu_search import BaiduSearchCrawler
import logging

# 设置详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_baidu_search():
    """测试百度搜索爬虫"""
    print("=" * 80)
    print("百度搜索爬虫测试")
    print("=" * 80)
    
    crawler = BaiduSearchCrawler()
    
    try:
        print("\n1. 测试搜索 '人工智能'...")
        results = crawler.search("人工智能", page=1, limit=5)
        
        print(f"\n搜索结果共 {len(results)} 条:\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. 标题: {result['title']}")
            print(f"   URL: {result['url']}")
            print(f"   摘要: {result['summary'][:100]}...")
            print(f"   信息: {result['info']}")
            print()
        
        if len(results) == 0:
            print("\n⚠️ 未获取到搜索结果")
            print("可能的原因:")
            print("  1. 百度反爬虫机制（验证码）")
            print("  2. 网络连接问题")
            print("  3. HTML结构变化")
        else:
            print("\n✓ 搜索成功!")
            
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        crawler.close()
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    test_baidu_search()
