from app import create_app, db
from app.models import CrawlerSource
import json

def create_baidu_source():
    """创建百度搜索爬虫源"""
    app = create_app()
    
    with app.app_context():
        baidu_source = CrawlerSource(
            name='百度搜索',
            source_type='baidu',
            description='百度搜索引擎，用于搜索关键词并获取相关结果',
            url='https://www.baidu.com/s?wd={keyword}&pn={page}&ie=utf-8',
            method='GET',
            headers=json.dumps({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }),
            data_selector=json.dumps({
                'type': 'css',
                'selector': 'div.result'
            }),
            title_selector='h3.t',
            url_selector='h3.t a',
            summary_selector='div.c-abstract, div.c-span-last',
            image_selector='img',
            config=json.dumps({
                'page_size': 10,
                'delay_range': [1, 3]
            }),
            status='active'
        )
        
        db.session.add(baidu_source)
        db.session.commit()
        
        print(f"✅ 成功创建百度搜索爬虫源！")
        print(f"   ID: {baidu_source.id}")
        print(f"   名称: {baidu_source.name}")
        print(f"   类型: {baidu_source.source_type}")
        print(f"   状态: {baidu_source.status}")

if __name__ == '__main__':
    create_baidu_source()
