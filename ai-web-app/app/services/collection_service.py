import sys
import os
import json
import threading
import queue
import time
from datetime import datetime

baidusearch_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../dist/baidusearch'))
if baidusearch_path not in sys.path:
    sys.path.insert(0, baidusearch_path)

try:
    from baidu_search import BaiduSearchCrawler
except ImportError:
    BaiduSearchCrawler = None

from app.models import CrawlerSource, CollectionData
from app.services.universal_crawler import create_crawler
from app import db
from app import create_app


class CollectionService:
    """采集管理服务类"""

    def __init__(self):
        self.active_collections = {}
        self.data_queues = {}
        self.crawler_pool = {}

    def get_available_sources(self):
        """
        获取可用的爬虫源列表

        Returns:
            源列表
        """
        sources = CrawlerSource.query.filter_by(status='active').all()
        return [s.to_dict() for s in sources]

    def start_collection(self, keyword, source_ids, page=1, pages=1, limit=10):
        """
        开始采集任务

        Args:
            keyword: 搜索关键词
            source_ids: 爬虫源ID列表
            page: 起始页
            pages: 总页数
            limit: 每页数量

        Returns:
            采集任务ID
        """
        collection_id = f"collection_{int(time.time() * 1000)}"
        
        self.data_queues[collection_id] = queue.Queue()
        
        thread = threading.Thread(
            target=self._execute_collection,
            args=(collection_id, keyword, source_ids, page, pages, limit)
        )
        thread.daemon = True
        thread.start()
        
        self.active_collections[collection_id] = {
            'thread': thread,
            'keyword': keyword,
            'source_ids': source_ids,
            'started_at': datetime.utcnow(),
            'status': 'running'
        }
        
        return collection_id

    def _execute_collection(self, collection_id, keyword, source_ids, page, pages, limit):
        """
        执行采集任务

        Args:
            collection_id: 采集任务ID
            keyword: 搜索关键词
            source_ids: 爬虫源ID列表
            page: 起始页
            pages: 总页数
            limit: 每页数量
        """
        app = create_app()
        with app.app_context():
            try:
                for source_id in source_ids:
                    source = CrawlerSource.query.get(source_id)
                    if not source or source.status != 'active':
                        continue

                    crawler = None
                    try:
                        # 尝试从池中获取已存在的爬虫实例
                        if source.id in self.crawler_pool:
                            crawler = self.crawler_pool[source.id]
                            print(f"✅ 从池中获取爬虫: {source.name}")
                        else:
                            source_config = {
                                'name': source.name,
                                'source_type': source.source_type,
                                'url': source.url,
                                'method': source.method,
                                'headers': source.headers,
                                'body_template': source.body_template,
                                'data_selector': source.data_selector,
                                'title_selector': source.title_selector,
                                'url_selector': source.url_selector,
                                'summary_selector': source.summary_selector,
                                'image_selector': source.image_selector,
                                'config': source.config
                            }

                            crawler = create_crawler(source_config)
                            self.crawler_pool[source.id] = crawler
                            print(f"✅ 创建新爬虫: {source.name} (类型: {type(crawler).__name__})")

                        for current_page in range(page, page + pages):
                            print(f"🔍 开始爬取第 {current_page} 页...")
                            page_results = crawler.crawl(keyword, current_page, limit)
                            print(f"📊 第 {current_page} 页获取到 {len(page_results)} 条结果")
                            
                            for result in page_results:
                                data_item = {
                                    'collection_id': collection_id,
                                    'title': result.get('title', ''),
                                    'url': result.get('url', ''),
                                    'summary': result.get('summary', ''),
                                    'source': result.get('source', ''),
                                    'image_url': self._extract_image(result),
                                    'keyword': keyword,
                                    'source_type': source.source_type,
                                    'source_name': source.name,
                                    'collected_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                                    'raw_data': json.dumps(result, ensure_ascii=False)
                                }
                                
                                self.data_queues[collection_id].put(data_item)
                                print(f"✅ 推送数据到队列: {data_item['title']}")

                    except Exception as e:
                        error_data = {
                            'collection_id': collection_id,
                            'error': str(e),
                            'source_name': source.name if source else 'Unknown'
                        }
                        self.data_queues[collection_id].put(error_data)
                    
                self.data_queues[collection_id].put({'type': 'completed', 'collection_id': collection_id})

            except Exception as e:
                self.data_queues[collection_id].put({
                    'type': 'error',
                    'collection_id': collection_id,
                    'error': str(e)
                })

            finally:
                if collection_id in self.active_collections:
                    self.active_collections[collection_id]['status'] = 'completed'

    def _extract_image(self, result):
        """
        从结果中提取图片URL

        Args:
            result: 搜索结果

        Returns:
            图片URL或默认图片
        """
        # 首先检查爬虫是否直接返回了图片URL
        image_url = result.get('image', '')
        if image_url:
            return image_url
        
        # 如果没有，尝试从摘要中提取图片URL
        summary = result.get('summary', '')
        if 'jpg' in summary or 'png' in summary or 'jpeg' in summary:
            import re
            img_urls = re.findall(r'https?://[^\s]+\.(?:jpg|png|jpeg|gif|webp)', summary)
            if img_urls:
                return img_urls[0]
        
        # 返回空字符串，让前端显示默认图标
        return ''

    def get_collection_data(self, collection_id):
        """
        获取采集数据（用于SSE推送）

        Args:
            collection_id: 采集任务ID

        Yields:
            数据项
        """
        if collection_id not in self.data_queues:
            yield f"data: {json.dumps({'error': 'Collection not found'})}\n\n"
            return

        data_queue = self.data_queues[collection_id]
        
        while True:
            try:
                data = data_queue.get(timeout=1)
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                
                if data.get('type') == 'completed' or data.get('type') == 'error':
                    break
                    
            except queue.Empty:
                continue

    def save_collection_data(self, data_items):
        """
        保存采集数据到数据库

        Args:
            data_items: 数据项列表

        Returns:
            保存的数量
        """
        saved_count = 0
        
        for item in data_items:
            try:
                collection_data = CollectionData(
                    title=item.get('title', ''),
                    url=item.get('url', ''),
                    summary=item.get('summary', ''),
                    source=item.get('source', ''),
                    image_url=item.get('image_url', ''),
                    keyword=item.get('keyword', ''),
                    source_type=item.get('source_type', ''),
                    raw_data=item.get('raw_data', ''),
                    collected_at=datetime.utcnow()
                )
                db.session.add(collection_data)
                saved_count += 1
            except Exception as e:
                print(f"Error saving data: {e}")
        
        if saved_count > 0:
            db.session.commit()
        
        return saved_count

    def get_saved_data(self, keyword=None, source_type=None, limit=50, offset=0):
        """
        获取已保存的数据

        Args:
            keyword: 关键词过滤
            source_type: 源类型过滤
            limit: 限制数量
            offset: 偏移量

        Returns:
            数据列表
        """
        query = CollectionData.query
        
        if keyword:
            query = query.filter(CollectionData.keyword.contains(keyword))
        if source_type:
            query = query.filter_by(source_type=source_type)
        
        query = query.order_by(CollectionData.saved_at.desc())
        
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        
        return query.all()

    def delete_saved_data(self, data_id):
        """
        删除已保存的数据

        Args:
            data_id: 数据ID

        Returns:
            是否成功
        """
        data = CollectionData.query.get(data_id)
        if data:
            db.session.delete(data)
            db.session.commit()
            return True
        return False

    def stop_collection(self, collection_id):
        """
        停止采集任务

        Args:
            collection_id: 采集任务ID

        Returns:
            是否成功
        """
        if collection_id in self.active_collections:
            self.active_collections[collection_id]['status'] = 'stopped'
            return True
        return False

    def get_collection_status(self, collection_id):
        """
        获取采集任务状态

        Args:
            collection_id: 采集任务ID

        Returns:
            状态信息
        """
        if collection_id not in self.active_collections:
            return {'status': 'not_found'}
        
        return {
            'status': self.active_collections[collection_id]['status'],
            'keyword': self.active_collections[collection_id]['keyword'],
            'started_at': self.active_collections[collection_id]['started_at'].strftime('%Y-%m-%d %H:%M:%S')
        }


collection_service = CollectionService()
