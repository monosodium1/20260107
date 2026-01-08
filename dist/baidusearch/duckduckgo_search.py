import requests
from bs4 import BeautifulSoup
import time
import random
from typing import List, Dict, Optional
import logging
import urllib.parse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DuckDuckGoSearchCrawler:
    """DuckDuckGo搜索爬虫类（无反爬虫）"""

    def __init__(self):
        self.base_url = "https://html.duckduckgo.com/html/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'DNT': '1',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def search(self, keyword: str, page: int = 1, limit: int = 10) -> List[Dict]:
        """
        执行DuckDuckGo搜索

        Args:
            keyword: 搜索关键词
            page: 页码（从1开始）
            limit: 每页结果数量

        Returns:
            搜索结果列表
        """
        try:
            # DuckDuckGo使用vqd参数来跟踪搜索
            # 首先获取vqd
            vqd = self._get_vqd(keyword)
            
            params = {
                'q': keyword,
                'kl': 'cn-zh',
                'vqd': vqd,
                'b': ''
            }
            
            # 分页处理
            if page > 1:
                params['s'] = str((page - 1) * 30)

            logger.info(f"正在搜索: {keyword}, 第{page}页")
            response = self.session.post(self.base_url, data=params, timeout=10)
            response.raise_for_status()

            results = self._parse_results(response.text)
            
            if limit and len(results) > limit:
                results = results[:limit]

            logger.info(f"搜索完成，共获取 {len(results)} 条结果")
            return results

        except Exception as e:
            logger.error(f"搜索失败: {str(e)}")
            return []

    def _get_vqd(self, keyword: str) -> str:
        """
        获取vqd参数

        Args:
            keyword: 搜索关键词

        Returns:
            vqd字符串
        """
        try:
            url = f"https://duckduckgo.com/?q={urllib.parse.quote(keyword)}"
            response = self.session.get(url, timeout=10)
            
            # 从响应中提取vqd
            if 'vqd=' in response.text:
                import re
                match = re.search(r'vqd=["\']([^"\']+)["\']', response.text)
                if match:
                    return match.group(1)
            
            return ''
        except:
            return ''

    def _parse_results(self, html: str) -> List[Dict]:
        """
        解析搜索结果页面

        Args:
            html: HTML内容

        Returns:
            解析后的结果列表
        """
        soup = BeautifulSoup(html, 'html.parser')
        results = []

        # DuckDuckGo的结果容器
        result_divs = soup.find_all('div', class_='result')
        
        for div in result_divs:
            try:
                result = self._parse_single_result(div)
                if result and result.get('title'):
                    results.append(result)
            except Exception as e:
                logger.warning(f"解析单条结果失败: {str(e)}")
                continue

        return results

    def _parse_single_result(self, div) -> Optional[Dict]:
        """
        解析单条搜索结果

        Args:
            div: 结果div元素

        Returns:
            解析后的结果字典
        """
        try:
            # 查找标题和链接
            title_tag = div.find('a', class_='result__a')
            if not title_tag:
                return None

            title = title_tag.get_text(strip=True)
            url = title_tag.get('href', '')

            # 查找摘要
            snippet_tag = div.find('a', class_='result__snippet')
            if not snippet_tag:
                snippet_tag = div.find('div', class_='result__snippet')
            
            summary = snippet_tag.get_text(strip=True) if snippet_tag else ''

            # 查找URL显示
            url_display_tag = div.find('a', class_='result__url')
            url_display = url_display_tag.get_text(strip=True) if url_display_tag else ''

            return {
                'title': title,
                'url': url,
                'summary': summary,
                'info': url_display,
                'source': 'duckduckgo'
            }
        except Exception as e:
            logger.warning(f"解析结果失败: {str(e)}")
            return None

    def search_multiple_pages(self, keyword: str, pages: int = 3, limit_per_page: int = 10) -> List[Dict]:
        """
        搜索多页结果

        Args:
            keyword: 搜索关键词
            pages: 总页数
            limit_per_page: 每页结果数量

        Returns:
            所有搜索结果列表
        """
        all_results = []
        
        for page in range(1, pages + 1):
            results = self.search(keyword, page, limit_per_page)
            all_results.extend(results)
            
            if page < pages:
                # 添加随机延迟
                delay = random.uniform(1, 3)
                logger.info(f"等待 {delay:.2f} 秒后继续...")
                time.sleep(delay)

        return all_results

    def close(self):
        """关闭会话"""
        self.session.close()


def main():
    """测试函数"""
    crawler = DuckDuckGoSearchCrawler()
    
    try:
        results = crawler.search("人工智能", page=1, limit=5)
        
        print(f"\n搜索结果共 {len(results)} 条:\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   URL: {result['url']}")
            print(f"   摘要: {result['summary'][:100]}...")
            print(f"   信息: {result['info']}")
            print()

    finally:
        crawler.close()


if __name__ == '__main__':
    main()
