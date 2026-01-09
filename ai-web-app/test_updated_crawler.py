from app import create_app, db
from app.models import CrawlerSource
from app.services.universal_crawler import create_crawler

def test_updated_crawler():
    """测试更新后的爬虫"""
    app = create_app()
    
    with app.app_context():
        baidu_source = CrawlerSource.query.filter_by(name='百度搜索').first()
        
        if not baidu_source:
            print("❌ 未找到百度搜索爬虫源")
            return
        
        print(f"✅ 找到百度搜索爬虫源 (ID: {baidu_source.id})")
        print(f"   名称: {baidu_source.name}")
        print(f"   类型: {baidu_source.source_type}")
        
        source_config = {
            'name': baidu_source.name,
            'source_type': baidu_source.source_type,
            'url': baidu_source.url,
            'method': baidu_source.method,
            'headers': baidu_source.headers,
            'body_template': baidu_source.body_template,
            'data_selector': baidu_source.data_selector,
            'title_selector': baidu_source.title_selector,
            'url_selector': baidu_source.url_selector,
            'summary_selector': baidu_source.summary_selector,
            'image_selector': baidu_source.image_selector,
            'config': baidu_source.config
        }
        
        print("\n🔍 开始测试爬虫...")
        print("=" * 60)
        
        try:
            crawler = create_crawler(source_config)
            print(f"✅ 成功创建爬虫实例: {type(crawler).__name__}")
            
            results = crawler.crawl('成都', 1, 10)
            
            print(f"✅ 爬取成功！共获取 {len(results)} 条结果")
            print("=" * 60)
            
            for i, result in enumerate(results[:5], 1):
                print(f"\n结果 {i}:")
                print(f"  标题: {result.get('title', 'N/A')}")
                print(f"  URL: {result.get('url', 'N/A')}")
                print(f"  摘要: {result.get('summary', 'N/A')[:100]}...")
            
            if len(results) > 5:
                print(f"\n... 还有 {len(results) - 5} 条结果")
            
            crawler.close()
            
        except Exception as e:
            print(f"❌ 爬取失败: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_updated_crawler()
