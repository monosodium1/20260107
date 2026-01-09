from app import create_app, db
from app.models import CrawlerSource

def check_baidu_source():
    """检查百度搜索爬虫源配置"""
    app = create_app()
    
    with app.app_context():
        baidu_source = CrawlerSource.query.filter_by(name='百度搜索').first()
        
        if not baidu_source:
            print("❌ 未找到百度搜索爬虫源")
            return
        
        print(f"✅ 找到百度搜索爬虫源 (ID: {baidu_source.id})")
        print(f"   名称: {baidu_source.name}")
        print(f"   URL: {baidu_source.url}")
        print(f"   方法: {baidu_source.method}")
        print(f"   状态: {baidu_source.status}")
        print(f"   选择器: {baidu_source.data_selector}")
        print(f"   标题选择器: {baidu_source.title_selector}")
        print(f"   URL选择器: {baidu_source.url_selector}")
        print(f"   摘要选择器: {baidu_source.summary_selector}")
        print(f"   配置: {baidu_source.config}")

if __name__ == '__main__':
    check_baidu_source()
