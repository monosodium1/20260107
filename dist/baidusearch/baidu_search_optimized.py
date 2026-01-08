import requests
from bs4 import BeautifulSoup
import time
import random
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaiduSearchCrawlerOptimized:
    """优化后的百度搜索爬虫类"""

    def __init__(self):
        self.base_url = "https://www.baidu.com/s"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.baidu.com/'
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
                'ie': 'utf-8',
                'rsv_bp': '1',
                'rsv_idx': '1',
                'tn': 'baidu'
            }

            logger.info(f"正在搜索: {keyword}, 第{page}页")
            response = self.session.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()

            # 检查是否是验证码页面
            if '验证码' in response.text or 'captcha' in response.url.lower():
                logger.warning("遇到验证码页面，无法继续爬取")
                return []

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

        # 尝试多种选择器来查找搜索结果
        selectors = [
            'div.result',  # 原始选择器
            'div[class*="result"]',  # class包含result
            'div.c-container',  # 百度常用的class
            'div[class*="c-container"]',  # class包含c-container
            'div[data-tools]',  # 包含data-tools属性的div
            'div[class*="c-span"]',  # class包含c-span
        ]

        result_divs = []
        for selector in selectors:
            try:
                divs = soup.select(selector)
                if divs:
                    logger.info(f"使用选择器 '{selector}' 找到 {len(divs)} 个结果")
                    result_divs = divs
                    break
            except Exception as e:
                logger.warning(f"选择器 '{selector}' 失败: {str(e)}")
                continue

        # 如果没有找到，尝试查找所有包含h3的div
        if not result_divs:
            logger.info("尝试查找包含h3的div")
            all_divs = soup.find_all('div')
            result_divs = [div for div in all_divs if div.find('h3')]
            logger.info(f"找到 {len(result_divs)} 个包含h3的div")

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
            # 尝试多种方式查找标题
            title_tag = None
            title_selectors = ['h3', 'h3.t', 'h3[class*="t"]']
            
            for selector in title_selectors:
                title_tag = div.select_one(selector)
                if title_tag:
                    break

            if not title_tag:
                return None

            title = title_tag.get_text(strip=True)
            
            # 查找链接
            link_tag = title_tag.find('a')
            url = link_tag.get('href', '') if link_tag else ''

            # 尝试多种方式查找摘要
            summary_tag = None
            summary_selectors = [
                'div.c-abstract',
                'div[class*="c-abstract"]',
                'div.c-span-last',
                'div[class*="c-span"]',
                'div[class*="abstract"]'
            ]
            
            for selector in summary_selectors:
                summary_tag = div.select_one(selector)
                if summary_tag:
                    break
            
            summary = summary_tag.get_text(strip=True) if summary_tag else ''

            # 查找信息（时间、来源等）
            info_tag = None
            info_selectors = [
                'div.c-tools',
                'div[class*="c-tools"]',
                'span.c-color-gray',
                'span[class*="c-color"]'
            ]
            
            for selector in info_selectors:
                info_tag = div.select_one(selector)
                if info_tag:
                    break
            
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
                # 添加随机延迟避免被封
                delay = random.uniform(2, 5)
                logger.info(f"等待 {delay:.2f} 秒后继续...")
                time.sleep(delay)

        return all_results

    def close(self):
        """关闭会话"""
        self.session.close()


def main():
    """测试函数"""
    crawler = BaiduSearchCrawlerOptimized()
    
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
