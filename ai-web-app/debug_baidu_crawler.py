from app import create_app, db
from app.models import CrawlerSource
from app.services.universal_crawler import create_crawler
import requests
from bs4 import BeautifulSoup

def debug_baidu_crawler():
    """调试百度爬虫"""
    app = create_app()
    
    with app.app_context():
        baidu_source = CrawlerSource.query.filter_by(name='百度搜索').first()
        
        if not baidu_source:
            print("❌ 未找到百度搜索爬虫源")
            return
        
        url = 'https://www.baidu.com/s?wd=成都&pn=1&ie=utf-8'
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        print(f"正在访问: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"状态码: {response.status_code}")
        print(f"内容长度: {len(response.text)}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print("\n=== 测试选择器 ===")
        
        # 测试选择器
        results = soup.select('div.result')
        print(f"选择器 'div.result': 找到 {len(results)} 个元素")
        
        if results:
            print(f"\n第一个结果元素:")
            print(f"  class: {results[0].get('class', [])}")
            print(f"  id: {results[0].get('id', 'N/A')}")
            
            # 测试标题选择器
            title_elem = results[0].select_one('h3')
            print(f"\n标题元素 (h3):")
            if title_elem:
                print(f"  找到: {title_elem.get_text(strip=True)[:80]}")
            else:
                print(f"  未找到")
            
            # 测试URL选择器
            url_elem = results[0].select_one('h3 a')
            print(f"\nURL元素 (h3 a):")
            if url_elem:
                print(f"  找到: {url_elem.get('href', 'N/A')[:80]}")
            else:
                print(f"  未找到")
            
            # 测试摘要选择器
            summary_elem = results[0].select_one('div.c-abstract')
            print(f"\n摘要元素 (div.c-abstract):")
            if summary_elem:
                print(f"  找到: {summary_elem.get_text(strip=True)[:80]}")
            else:
                print(f"  未找到")
            
            # 测试其他摘要选择器
            summary_elem2 = results[0].select_one('div.c-span-last')
            print(f"\n摘要元素 (div.c-span-last):")
            if summary_elem2:
                print(f"  找到: {summary_elem2.get_text(strip=True)[:80]}")
            else:
                print(f"  未找到")

if __name__ == '__main__':
    debug_baidu_crawler()
