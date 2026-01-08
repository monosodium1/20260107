import sys
import os

baidusearch_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../dist/baidusearch'))
if baidusearch_path not in sys.path:
    sys.path.insert(0, baidusearch_path)

try:
    from baidu_search import BaiduSearchCrawler
except ImportError:
    BaiduSearchCrawler = None

import json
import threading
from datetime import datetime
from app.models import CrawlerSource, CrawlerTask, CrawlerData
from app.services.universal_crawler import create_crawler
from app import db


class CrawlerService:
    """爬虫服务类"""

    def __init__(self):
        self.active_tasks = {}

    def create_source(self, name, source_type, url=None, description=None, method='GET', 
                   headers=None, body_template=None, data_selector=None,
                   title_selector=None, url_selector=None, summary_selector=None, 
                   image_selector=None, config=None):
        """
        创建爬虫源

        Args:
            name: 源名称
            source_type: 源类型
            url: 目标URL
            description: 描述
            method: 请求方法
            headers: 请求头
            body_template: 请求体模板
            data_selector: 数据选择器
            title_selector: 标题选择器
            url_selector: URL选择器
            summary_selector: 摘要选择器
            image_selector: 图片选择器
            config: 其他配置

        Returns:
            CrawlerSource对象
        """
        source = CrawlerSource(
            name=name,
            source_type=source_type,
            url=url,
            description=description,
            method=method,
            headers=json.dumps(headers) if headers else None,
            body_template=body_template,
            data_selector=json.dumps(data_selector) if data_selector else None,
            title_selector=title_selector,
            url_selector=url_selector,
            summary_selector=summary_selector,
            image_selector=image_selector,
            config=json.dumps(config) if config else None
        )
        db.session.add(source)
        db.session.commit()
        return source

    def get_sources(self, status=None):
        """
        获取爬虫源列表

        Args:
            status: 状态过滤

        Returns:
            源列表
        """
        query = CrawlerSource.query
        if status:
            query = query.filter_by(status=status)
        return query.all()

    def get_source(self, source_id):
        """获取单个爬虫源"""
        return CrawlerSource.query.get(source_id)

    def update_source(self, source_id, **kwargs):
        """更新爬虫源"""
        source = CrawlerSource.query.get(source_id)
        if source:
            for key, value in kwargs.items():
                if key == 'config' and value:
                    value = json.dumps(value)
                setattr(source, key, value)
            source.updated_at = datetime.utcnow()
            db.session.commit()
        return source

    def delete_source(self, source_id):
        """删除爬虫源"""
        source = CrawlerSource.query.get(source_id)
        if source:
            db.session.delete(source)
            db.session.commit()
            return True
        return False

    def create_task(self, source_id, task_name, keyword=None, page=1, limit=10, pages=1):
        """
        创建爬虫任务

        Args:
            source_id: 源ID
            task_name: 任务名称
            keyword: 搜索关键词
            page: 起始页
            limit: 每页数量
            pages: 总页数

        Returns:
            CrawlerTask对象
        """
        task = CrawlerTask(
            source_id=source_id,
            task_name=task_name,
            keyword=keyword,
            page=page,
            limit=limit,
            pages=pages,
            status='pending'
        )
        db.session.add(task)
        db.session.commit()
        return task

    def get_tasks(self, source_id=None, status=None):
        """
        获取任务列表

        Args:
            source_id: 源ID过滤
            status: 状态过滤

        Returns:
            任务列表
        """
        query = CrawlerTask.query
        if source_id:
            query = query.filter_by(source_id=source_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(CrawlerTask.created_at.desc()).all()

    def get_task(self, task_id):
        """获取单个任务"""
        return CrawlerTask.query.get(task_id)

    def run_task(self, task_id):
        """
        执行爬虫任务

        Args:
            task_id: 任务ID

        Returns:
            是否成功启动
        """
        task = CrawlerTask.query.get(task_id)
        if not task:
            return False

        if task.status == 'running':
            return False

        task.status = 'running'
        task.started_at = datetime.utcnow()
        task.progress = 0
        db.session.commit()

        thread = threading.Thread(target=self._execute_task, args=(task,))
        thread.daemon = True
        thread.start()

        self.active_tasks[task_id] = thread
        return True

    def _execute_task(self, task):
        """
        执行任务的具体逻辑

        Args:
            task: 任务对象
        """
        try:
            source = task.source
            crawler = None

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

            results = []
            total_pages = task.pages

            for page in range(1, total_pages + 1):
                page_results = crawler.crawl(task.keyword, page, task.limit)
                results.extend(page_results)

                progress = int((page / total_pages) * 100)
                task.progress = progress
                task.result_count = len(results)
                db.session.commit()

            for result in results:
                data = CrawlerData(
                    task_id=task.id,
                    title=result.get('title', ''),
                    url=result.get('url', ''),
                    summary=result.get('summary', ''),
                    info=result.get('image', ''),
                    source=result.get('source', ''),
                    raw_data=json.dumps(result, ensure_ascii=False)
                )
                db.session.add(data)

            task.status = 'completed'
            task.completed_at = datetime.utcnow()
            task.progress = 100
            db.session.commit()

            if crawler:
                crawler.close()

        except Exception as e:
            task.status = 'failed'
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
            db.session.commit()

        finally:
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]

    def stop_task(self, task_id):
        """
        停止任务

        Args:
            task_id: 任务ID

        Returns:
            是否成功停止
        """
        task = CrawlerTask.query.get(task_id)
        if not task or task.status != 'running':
            return False

        task.status = 'failed'
        task.error_message = '任务被用户停止'
        task.completed_at = datetime.utcnow()
        db.session.commit()

        return True

    def get_task_data(self, task_id, limit=None, offset=0):
        """
        获取任务数据

        Args:
            task_id: 任务ID
            limit: 限制数量
            offset: 偏移量

        Returns:
            数据列表
        """
        query = CrawlerData.query.filter_by(task_id=task_id)
        query = query.order_by(CrawlerData.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        
        return query.all()

    def delete_task(self, task_id):
        """删除任务"""
        task = CrawlerTask.query.get(task_id)
        if task:
            db.session.delete(task)
            db.session.commit()
            return True
        return False

    def get_stats(self):
        """
        获取统计信息

        Returns:
            统计数据字典
        """
        total_sources = CrawlerSource.query.count()
        active_sources = CrawlerSource.query.filter_by(status='active').count()
        total_tasks = CrawlerTask.query.count()
        running_tasks = CrawlerTask.query.filter_by(status='running').count()
        completed_tasks = CrawlerTask.query.filter_by(status='completed').count()
        total_data = CrawlerData.query.count()

        return {
            'total_sources': total_sources,
            'active_sources': active_sources,
            'total_tasks': total_tasks,
            'running_tasks': running_tasks,
            'completed_tasks': completed_tasks,
            'total_data': total_data
        }


crawler_service = CrawlerService()
