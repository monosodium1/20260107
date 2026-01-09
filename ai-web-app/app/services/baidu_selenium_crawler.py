"""
百度搜索爬虫 - 使用Selenium绕过反爬机制
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import json
from typing import List, Dict

class BaiduSeleniumCrawler:
    """百度搜索爬虫 - Selenium版本"""
    
    def __init__(self):
        """初始化爬虫"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
    
    def crawl(self, keyword: str, page: int = 1, limit: int = 10) -> List[Dict]:
        """
        执行爬取
        
        Args:
            keyword: 搜索关键词
            page: 页码
            limit: 每页数量
            
        Returns:
            爬取结果列表
        """
        try:
            # 构建URL
            pn = (page - 1) * 10
            url = f'https://www.baidu.com/s?wd={keyword}&pn={pn}&ie=utf-8'
            
            print(f"正在访问: {url}")
            self.driver.get(url)
            
            # 使用智能等待而不是固定sleep
            try:
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.result')))
            except:
                pass
            
            # 检查是否有验证码
            if 'wappass.baidu.com' in self.driver.current_url:
                print("⚠️  检测到验证码页面，需要人工处理")
                return []
            
            # 获取页面源码
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # 提取搜索结果
            results = []
            result_elements = soup.select('div.result')
            
            print(f"找到 {len(result_elements)} 个搜索结果")
            
            for idx, elem in enumerate(result_elements[:limit]):
                print(f"\n=== 处理第 {idx+1} 个结果 ===")
                print(f"HTML片段: {str(elem)[:500]}...")
                
                result = {
                    'title': self._extract_title(elem),
                    'url': self._extract_url(elem),
                    'summary': self._extract_summary(elem),
                    'image': self._extract_image(elem),
                    'source': '百度搜索'
                }
                
                print(f"提取结果: title={result['title']}, summary={result['summary'][:50] if result['summary'] else '空'}...")
                
                if result['title']:
                    results.append(result)
            
            return results
            
        except Exception as e:
            print(f"爬取失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def _extract_title(self, elem) -> str:
        """提取标题"""
        try:
            title_elem = elem.select_one('h3')
            return title_elem.get_text(strip=True) if title_elem else ''
        except:
            return ''
    
    def _extract_url(self, elem) -> str:
        """提取URL"""
        try:
            url_elem = elem.select_one('h3 a')
            return url_elem.get('href', '') if url_elem else ''
        except:
            return ''
    
    def _extract_summary(self, elem) -> str:
        """提取摘要"""
        try:
            # 尝试多种选择器
            selectors = [
                'div.c-abstract',
                'div.c-span-last',
                'div[class*="abstract"]',
                'div[class*="content"]',
                'div[class*="desc"]',
                'span.content-right_8Zs40'
            ]
            
            for selector in selectors:
                summary_elem = elem.select_one(selector)
                if summary_elem:
                    text = summary_elem.get_text(strip=True)
                    if text:
                        return text
            
            # 如果上述选择器都失败，尝试获取整个元素的内容（排除标题）
            all_text = elem.get_text(strip=True)
            title = self._extract_title(elem)
            if all_text and all_text != title:
                # 移除标题部分
                if title in all_text:
                    summary = all_text.replace(title, '').strip()
                    return summary
                return all_text
            
            return ''
        except Exception as e:
            print(f"摘要提取失败: {str(e)}")
            return ''
    
    def _extract_image(self, elem) -> str:
        """提取图片"""
        try:
            # 尝试多种选择器查找图片
            selectors = [
                'img',
                'div.c-img img',
                'div[class*="img"] img',
                'a img',
                'img[data-src]'
            ]
            
            for selector in selectors:
                img_elem = elem.select_one(selector)
                if img_elem:
                    # 优先使用data-src属性（懒加载）
                    img_url = img_elem.get('data-src', '')
                    if not img_url:
                        img_url = img_elem.get('src', '')
                    
                    # 过滤掉小图标和占位图
                    if img_url and not any(x in img_url for x in ['icon', 'logo', 'avatar', 'placeholder']):
                        # 如果是相对路径，转换为绝对路径
                        if img_url.startswith('//'):
                            img_url = 'https:' + img_url
                        elif img_url.startswith('/'):
                            img_url = 'https://www.baidu.com' + img_url
                        
                        return img_url
            
            return ''
        except Exception as e:
            print(f"图片提取失败: {str(e)}")
            return ''
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()

def test_crawler():
    """测试爬虫"""
    crawler = BaiduSeleniumCrawler()
    
    try:
        results = crawler.crawl('成都', 1, 10)
        
        print(f"\n✅ 爬取成功！共获取 {len(results)} 条结果")
        print("=" * 60)
        
        for i, result in enumerate(results[:5], 1):
            print(f"\n结果 {i}:")
            print(f"  标题: {result.get('title', 'N/A')}")
            print(f"  URL: {result.get('url', 'N/A')}")
            print(f"  摘要: {result.get('summary', 'N/A')[:100]}...")
        
    finally:
        crawler.close()

if __name__ == '__main__':
    test_crawler()
