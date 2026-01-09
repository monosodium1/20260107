import psutil
import platform
import os
from datetime import datetime, timedelta
from app.models import CollectionData, CrawlerTask, CrawlerData, AIModelUsage
from app import db


class SystemMonitorService:
    """系统监控服务类"""

    @staticmethod
    def get_system_info():
        """
        获取系统基本信息

        Returns:
            系统信息字典
        """
        return {
            'system': platform.system(),
            'node_name': platform.node(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version()
        }

    @staticmethod
    def get_cpu_usage():
        """
        获取CPU使用率

        Returns:
            CPU使用率字典
        """
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'cpu_count': psutil.cpu_count(),
            'cpu_freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
        }

    @staticmethod
    def get_memory_usage():
        """
        获取内存使用情况

        Returns:
            内存使用情况字典
        """
        mem = psutil.virtual_memory()
        return {
            'total': mem.total,
            'available': mem.available,
            'used': mem.used,
            'percent': mem.percent
        }

    @staticmethod
    def get_disk_usage():
        """
        获取磁盘使用情况

        Returns:
            磁盘使用情况字典
        """
        disk = psutil.disk_usage('/')
        return {
            'total': disk.total,
            'used': disk.used,
            'free': disk.free,
            'percent': disk.percent
        }

    @staticmethod
    def get_network_status():
        """
        获取网络状态

        Returns:
            网络状态字典
        """
        try:
            import socket
            socket.setdefaulttimeout(2)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
            network_status = '正常'
        except:
            network_status = '异常'
        
        return {
            'status': network_status,
            'connections': len(psutil.net_connections())
        }

    @staticmethod
    def get_process_info():
        """
        获取进程信息

        Returns:
            进程信息字典
        """
        current_process = psutil.Process()
        return {
            'pid': current_process.pid,
            'name': current_process.name(),
            'cpu_percent': current_process.cpu_percent(),
            'memory_info': current_process.memory_info()._asdict(),
            'create_time': datetime.fromtimestamp(current_process.create_time())
        }

    @staticmethod
    def get_system_status():
        """
        获取系统综合状态

        Returns:
            系统状态字典
        """
        cpu_usage = SystemMonitorService.get_cpu_usage()
        memory_usage = SystemMonitorService.get_memory_usage()
        disk_usage = SystemMonitorService.get_disk_usage()
        network_status = SystemMonitorService.get_network_status()

        status = '正常'
        warning = None

        if cpu_usage['cpu_percent'] > 80:
            status = '警告'
            warning = 'CPU使用率过高'
        elif memory_usage['percent'] > 80:
            status = '警告'
            warning = '内存使用率过高'
        elif disk_usage['percent'] > 80:
            status = '警告'
            warning = '磁盘空间不足'
        elif network_status['status'] != '正常':
            status = '异常'
            warning = '网络连接异常'

        return {
            'status': status,
            'warning': warning,
            'cpu': cpu_usage,
            'memory': memory_usage,
            'disk': disk_usage,
            'network': network_status,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    @staticmethod
    def get_dashboard_stats():
        """
        获取后台主页统计数据

        Returns:
            统计数据字典
        """
        total_data = CollectionData.query.count()
        total_crawls = CrawlerTask.query.count()
        
        running_tasks = CrawlerTask.query.filter_by(status='running').count()
        completed_tasks = CrawlerTask.query.filter_by(status='completed').count()
        failed_tasks = CrawlerTask.query.filter_by(status='failed').count()
        
        crawler_data_count = CrawlerData.query.count()
        
        ai_engine_status = '运行中'
        ai_models_count = 0
        
        try:
            from app.models import AIModel
            ai_models_count = AIModel.query.filter_by(status='active').count()
            if ai_models_count == 0:
                ai_engine_status = '未配置'
        except:
            pass
        
        system_status = '正常'
        system_warning = None
        
        disk_usage = SystemMonitorService.get_disk_usage()
        if disk_usage['percent'] > 80:
            system_status = '警告'
            system_warning = '需关注存储'
        elif disk_usage['percent'] > 90:
            system_status = '严重'
            system_warning = '存储空间严重不足'
        
        cpu_usage = SystemMonitorService.get_cpu_usage()
        if cpu_usage['cpu_percent'] > 80:
            system_status = '警告'
            system_warning = 'CPU使用率过高'
        
        memory_usage = SystemMonitorService.get_memory_usage()
        if memory_usage['percent'] > 80:
            system_status = '警告'
            system_warning = '内存使用率过高'
        
        network_status = SystemMonitorService.get_network_status()
        if network_status['status'] != '正常':
            system_status = '异常'
            system_warning = '网络连接异常'
        
        return {
            'total_data': total_data,
            'total_crawls': total_crawls,
            'crawler_data_count': crawler_data_count,
            'ai_engine_status': ai_engine_status,
            'ai_models_count': ai_models_count,
            'system_status': system_status,
            'system_warning': system_warning,
            'network_status': network_status['status'],
            'running_tasks': running_tasks,
            'completed_tasks': completed_tasks,
            'failed_tasks': failed_tasks,
            'cpu_percent': cpu_usage['cpu_percent'],
            'memory_percent': memory_usage['percent'],
            'disk_percent': disk_usage['percent']
        }

    @staticmethod
    def get_data_trend(days=7):
        """
        获取数据采集趋势

        Args:
            days: 统计天数

        Returns:
            趋势数据字典
        """
        days_list = []
        crawls_data = []
        data_data = []
        
        for i in range(days):
            date = datetime.now() - timedelta(days=days-1-i)
            date_str = date.strftime('%Y-%m-%d')
            days_list.append(date.strftime('%m-%d'))
            
            start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            day_crawls = CrawlerTask.query.filter(
                CrawlerTask.created_at >= start_of_day,
                CrawlerTask.created_at <= end_of_day
            ).count()
            
            day_data = CollectionData.query.filter(
                CollectionData.saved_at >= start_of_day,
                CollectionData.saved_at <= end_of_day
            ).count()
            
            crawls_data.append(day_crawls)
            data_data.append(day_data)
        
        return {
            'days': days_list,
            'crawls': crawls_data,
            'data': data_data
        }

    @staticmethod
    def get_data_source_distribution():
        """
        获取数据来源分布

        Returns:
            数据来源分布字典
        """
        sources = db.session.query(
            CollectionData.source,
            db.func.count(CollectionData.id)
        ).group_by(CollectionData.source).all()
        
        distribution = []
        for source, count in sources:
            distribution.append({
                'value': count,
                'name': source if source else '未知来源'
            })
        
        return distribution

    @staticmethod
    def get_ai_distribution():
        """
        获取AI分析任务分布

        Returns:
            AI任务分布字典
        """
        try:
            from app.models import AIModelUsage
            distributions = db.session.query(
                AIModelUsage.request_type,
                db.func.count(AIModelUsage.id)
            ).group_by(AIModelUsage.request_type).all()
            
            result = []
            for request_type, count in distributions:
                type_names = {
                    'chat': '对话',
                    'test': '测试',
                    'deep_collect': '深度采集',
                    'analysis': '分析'
                }
                result.append({
                    'value': count,
                    'name': type_names.get(request_type, request_type)
                })
            
            return result if result else [
                {'value': 0, 'name': '对话'},
                {'value': 0, 'name': '测试'},
                {'value': 0, 'name': '深度采集'},
                {'value': 0, 'name': '分析'}
            ]
        except:
            return [
                {'value': 0, 'name': '对话'},
                {'value': 0, 'name': '测试'},
                {'value': 0, 'name': '深度采集'},
                {'value': 0, 'name': '分析'}
            ]

    @staticmethod
    def get_system_logs(limit=10):
        """
        获取系统操作日志

        Args:
            limit: 日志数量限制

        Returns:
            日志列表
        """
        try:
            from app.models import CrawlerTask
            tasks = CrawlerTask.query.order_by(CrawlerTask.created_at.desc()).limit(limit).all()
            
            logs = []
            for task in tasks:
                status_text = {
                    'pending': '待执行',
                    'running': '运行中',
                    'completed': '成功',
                    'failed': '失败'
                }.get(task.status, task.status)
                
                logs.append({
                    'time': task.created_at.strftime('%Y-%m-%d %H:%M:%S') if task.created_at else '',
                    'user': 'Admin',
                    'module': '爬虫管理',
                    'desc': f'任务: {task.task_name} - {task.keyword or "无关键词"}',
                    'status': status_text
                })
            
            return logs
        except:
            return []


system_monitor_service = SystemMonitorService()