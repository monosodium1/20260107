import requests
import json
import time
import re
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UniversalCrawler:
    """通用爬虫引擎类"""

    def __init__(self, source_config: Dict):
        """
        初始化爬虫引擎

        Args:
            source_config: 爬虫源配置字典
        """
        self.config = source_config
        self.session = requests.Session()
        
        headers = source_config.get('headers', {})
        if isinstance(headers, str):
            headers = json.loads(headers)
        
        default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        default_headers.update(headers)
        self.session.headers.update(default_headers)

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
            url = self._build_url(keyword, page)
            logger.info(f"正在爬取: {url}")
            
            if self.config.get('method', 'GET').upper() == 'POST':
                body = self._build_body(keyword, page)
                response = self.session.post(url, data=body, timeout=10)
            else:
                response = self.session.get(url, timeout=10)
            
            response.raise_for_status()
            
            results = self._parse_response(response.text)
            
            if limit and len(results) > limit:
                results = results[:limit]
            
            logger.info(f"爬取完成，共获取 {len(results)} 条结果")
            return results

        except Exception as e:
            logger.error(f"爬取失败: {str(e)}")
            raise

    def _build_url(self, keyword: str, page: int) -> str:
        """
        构建请求URL

        Args:
            keyword: 关键词
            page: 页码

        Returns:
            完整的URL
        """
        url_template = self.config.get('url', '')
        
        url = url_template.replace('{keyword}', str(keyword))
        url = url.replace('{page}', str(page))
        url = url.replace('{limit}', str(self.config.get('limit', 10)))
        
        return url

    def _build_body(self, keyword: str, page: int) -> Optional[Dict]:
        """
        构建请求体（POST方法使用）

        Args:
            keyword: 关键词
            page: 页码

        Returns:
            请求体字典
        """
        body_template = self.config.get('body_template')
        
        if not body_template:
            return None
        
        if isinstance(body_template, str):
            body_template = json.loads(body_template)
        
        body = {}
        for key, value in body_template.items():
            body[key] = str(value).replace('{keyword}', str(keyword))
            body[key] = body[key].replace('{page}', str(page))
        
        return body

    def _parse_response(self, html: str) -> List[Dict]:
        """
        解析响应内容

        Args:
            html: HTML内容

        Returns:
            解析后的结果列表
        """
        data_selector = self.config.get('data_selector')
        
        if data_selector:
            return self._parse_with_selector(html)
        else:
            return self._parse_with_selectors(html)

    def _parse_with_selector(self, html: str) -> List[Dict]:
        """
        使用JSON选择器解析

        Args:
            html: HTML内容

        Returns:
            结果列表
        """
        try:
            data_selector = self.config.get('data_selector')
            
            if isinstance(data_selector, str):
                data_selector = json.loads(data_selector)
            
            selector_type = data_selector.get('type', 'css')
            selector = data_selector.get('selector', '')
            
            soup = BeautifulSoup(html, 'html.parser')
            
            if selector_type == 'css':
                elements = soup.select(selector)
            elif selector_type == 'xpath':
                elements = soup.select(selector)
            else:
                elements = []
            
            results = []
            for elem in elements:
                result = {
                    'title': self._extract_text(elem, self.config.get('title_selector')),
                    'url': self._extract_text(elem, self.config.get('url_selector')),
                    'summary': self._extract_text(elem, self.config.get('summary_selector')),
                    'image': self._extract_attr(elem, self.config.get('image_selector'), 'src'),
                    'source': self.config.get('name', 'unknown')
                }
                
                if result['title']:
                    results.append(result)
            
            return results

        except Exception as e:
            logger.error(f"使用选择器解析失败: {str(e)}")
            return []

    def _parse_with_selectors(self, html: str) -> List[Dict]:
        """
        使用单独的选择器解析

        Args:
            html: HTML内容

        Returns:
            结果列表
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            title_selector = self.config.get('title_selector', '')
            url_selector = self.config.get('url_selector', '')
            summary_selector = self.config.get('summary_selector', '')
            image_selector = self.config.get('image_selector', '')
            
            title_elements = soup.select(title_selector) if title_selector else []
            url_elements = soup.select(url_selector) if url_selector else []
            summary_elements = soup.select(summary_selector) if summary_selector else []
            image_elements = soup.select(image_selector) if image_selector else []
            
            max_len = max(len(title_elements), len(url_elements), len(summary_elements), len(image_elements))
            
            results = []
            for i in range(max_len):
                result = {
                    'title': self._get_element_text(title_elements, i),
                    'url': self._get_element_text(url_elements, i),
                    'summary': self._get_element_text(summary_elements, i),
                    'image': self._get_element_attr(image_elements, i, 'src'),
                    'source': self.config.get('name', 'unknown')
                }
                
                if result['title']:
                    results.append(result)
            
            return results

        except Exception as e:
            logger.error(f"解析失败: {str(e)}")
            return []

    def _extract_text(self, element, selector: Optional[str]) -> str:
        """
        从元素中提取文本

        Args:
            element: BeautifulSoup元素
            selector: 选择器

        Returns:
            提取的文本
        """
        if not selector:
            return ''
        
        try:
            elem = element.select_one(selector)
            return elem.get_text(strip=True) if elem else ''
        except:
            return ''

    def _extract_attr(self, element, selector: Optional[str], attr: str) -> str:
        """
        从元素中提取属性

        Args:
            element: BeautifulSoup元素
            selector: 选择器
            attr: 属性名

        Returns:
            提取的属性值
        """
        if not selector:
            return ''
        
        try:
            elem = element.select_one(selector)
            return elem.get(attr, '') if elem else ''
        except:
            return ''

    def _get_element_text(self, elements, index: int) -> str:
        """
        从元素列表中获取指定索引的文本

        Args:
            elements: 元素列表
            index: 索引

        Returns:
            文本内容
        """
        if index < len(elements):
            return elements[index].get_text(strip=True)
        return ''

    def _get_element_attr(self, elements, index: int, attr: str) -> str:
        """
        从元素列表中获取指定索引的属性

        Args:
            elements: 元素列表
            index: 索引
            attr: 属性名

        Returns:
            属性值
        """
        if index < len(elements):
            return elements[index].get(attr, '')
        return ''

    def close(self):
        """关闭会话"""
        self.session.close()


class BaiduCrawler(UniversalCrawler):
    """百度搜索爬虫（继承通用爬虫）"""

    def __init__(self):
        config = {
            'name': '百度搜索',
            'source_type': 'baidu',
            'url': 'https://www.baidu.com/s?wd={keyword}&pn={page}&ie=utf-8',
            'method': 'GET',
            'data_selector': {
                'type': 'css',
                'selector': 'div.result'
            },
            'title_selector': 'h3.t a',
            'url_selector': 'h3.t a',
            'summary_selector': 'div.c-abstract, div.c-span-last',
            'image_selector': None
        }
        super().__init__(config)

    def _parse_response(self, html: str) -> List[Dict]:
        """
        百度特殊解析逻辑
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            results = []
            
            result_divs = soup.find_all('div', class_='result')
            
            for div in result_divs:
                try:
                    title_tag = div.find('h3', class_='t')
                    if not title_tag:
                        continue
                    
                    link_tag = title_tag.find('a')
                    title = title_tag.get_text(strip=True)
                    url = link_tag.get('href', '') if link_tag else ''
                    
                    summary_tag = div.find('div', class_='c-abstract')
                    if not summary_tag:
                        summary_tag = div.find('div', class_='c-span-last')
                    
                    summary = summary_tag.get_text(strip=True) if summary_tag else ''
                    
                    results.append({
                        'title': title,
                        'url': url,
                        'summary': summary,
                        'image': '',
                        'source': 'baidu'
                    })
                except Exception as e:
                    logger.warning(f"解析单条结果失败: {str(e)}")
                    continue
            
            return results

        except Exception as e:
            logger.error(f"百度解析失败: {str(e)}")
            return []


def create_crawler(source_config: Dict) -> UniversalCrawler:
    """
    工厂方法：根据配置创建爬虫实例

    Args:
        source_config: 爬虫源配置

    Returns:
        爬虫实例
    """
    source_type = source_config.get('source_type', 'custom')
    
    if source_type == 'baidu':
        return BaiduCrawler()
    else:
        return UniversalCrawler(source_config)
