from app import create_app, db
from app.models import CrawlerSource
import json

def update_baidu_source():
    """更新百度搜索爬虫源的选择器配置"""
    app = create_app()
    
    with app.app_context():
        baidu_source = CrawlerSource.query.filter_by(name='百度搜索').first()
        
        if not baidu_source:
            print("❌ 未找到百度搜索爬虫源")
            return
        
        print(f"✅ 找到百度搜索爬虫源 (ID: {baidu_source.id})")
        print(f"   当前选择器: {baidu_source.data_selector}")
        
        # 更新选择器配置
        baidu_source.data_selector = json.dumps({
            'type': 'css',
            'selector': 'div.result'
        })
        
        baidu_source.title_selector = 'h3'
        baidu_source.url_selector = 'h3 a'
        baidu_source.summary_selector = 'div.c-abstract, div.c-span-last, div[class*="abstract"]'
        baidu_source.image_selector = 'img'
        
        db.session.commit()
        
        print(f"✅ 成功更新百度搜索爬虫源！")
        print(f"   新选择器: {baidu_source.data_selector}")
        print(f"   标题选择器: {baidu_source.title_selector}")
        print(f"   URL选择器: {baidu_source.url_selector}")
        print(f"   摘要选择器: {baidu_source.summary_selector}")

if __name__ == '__main__':
    update_baidu_source()
