import requests
from bs4 import BeautifulSoup
import time
import random
from typing import List, Dict, Optional
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaiduSearchCrawler:
    """百度搜索爬虫类"""

    def __init__(self):
        self.base_url = "https://www.baidu.com/s"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def search(self, keyword: str, page: int = 1, limit: int = 10) -> List[Dict]:
        """
        执行百度搜索

        Args:
            keyword: 搜索关键词
            page: 页码（从1开始）
            limit: 每页结果数量

        Returns:
            搜索结果列表
        """
        try:
            pn = (page - 1) * 10
            params = {
                'wd': keyword,
                'pn': pn,
                'ie': 'utf-8'
            }

            logger.info(f"正在搜索: {keyword}, 第{page}页")
            response = self.session.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()

            results = self._parse_results(response.text)
            
            if limit and len(results) > limit:
                results = results[:limit]

            logger.info(f"搜索完成，共获取 {len(results)} 条结果")
            return results

        except Exception as e:
            logger.error(f"搜索失败: {str(e)}")
            return []

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

        result_divs = soup.find_all('div', class_='result')
        
        for div in result_divs:
            try:
                result = self._parse_single_result(div)
                if result:
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
            title_tag = div.find('h3', class_='t')
            if not title_tag:
                return None

            title = title_tag.get_text(strip=True)
            link_tag = title_tag.find('a')
            url = link_tag.get('href', '') if link_tag else ''

            summary_tag = div.find('div', class_='c-abstract')
            if not summary_tag:
                summary_tag = div.find('div', class_='c-span-last')
            
            summary = summary_tag.get_text(strip=True) if summary_tag else ''

            info_tag = div.find('div', class_='c-tools')
            info = info_tag.get_text(strip=True) if info_tag else ''

            return {
                'title': title,
                'url': url,
                'summary': summary,
                'info': info,
                'source': 'baidu'
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
                time.sleep(random.uniform(1, 3))

        return all_results

    def close(self):
        """关闭会话"""
        self.session.close()


def main():
    """测试函数"""
    crawler = BaiduSearchCrawler()
    
    try:
        results = crawler.search("林俊杰", page=1, limit=5)
        
        print(f"\n搜索结果共 {len(results)} 条:\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   URL: {result['url']}")
            print(f"   摘要: {result['summary'][:100]}...")
            print()

    finally:
        crawler.close()


if __name__ == '__main__':
    main()
