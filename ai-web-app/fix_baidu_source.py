from app import create_app, db
from app.models import CrawlerSource
import json

def fix_baidu_source():
    """修复百度搜索爬虫源的URL配置"""
    app = create_app()
    
    with app.app_context():
        baidu_source = CrawlerSource.query.filter_by(name='百度搜索').first()
        
        if not baidu_source:
            print("❌ 未找到百度搜索爬虫源")
            return
        
        print(f"✅ 找到百度搜索爬虫源 (ID: {baidu_source.id})")
        print(f"   当前URL: {baidu_source.url}")
        
        # 更新URL
        baidu_source.url = 'https://www.baidu.com/s?wd={keyword}&pn={page}&ie=utf-8'
        
        # 更新配置
        baidu_source.config = json.dumps({
            'page_size': 10,
            'delay_range': [1, 3]
        })
        
        db.session.commit()
        
        print(f"✅ 成功修复百度搜索爬虫源！")
        print(f"   新URL: {baidu_source.url}")
        print(f"   配置: {baidu_source.config}")

if __name__ == '__main__':
    fix_baidu_source()
