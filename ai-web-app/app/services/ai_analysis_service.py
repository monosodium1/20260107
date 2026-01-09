from app.models import CollectionData, DeepCollectionData, AIModel
from app import db
from app.services.ai_model_service import AIModelService
import json
import re
from datetime import datetime, timedelta
from sqlalchemy import func, desc


class AIAnalysisService:
    """AI分析服务"""

    @staticmethod
    def get_available_tools():
        """
        获取可用的工具列表

        Returns:
            list: 工具列表
        """
        return [
            {
                "name": "query_collection_data",
                "description": "查询采集数据表(collection_data)中的数据",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keyword": {
                            "type": "string",
                            "description": "关键词过滤"
                        },
                        "source": {
                            "type": "string",
                            "description": "数据源过滤"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "返回数量限制，默认100"
                        },
                        "days": {
                            "type": "integer",
                            "description": "最近多少天的数据，默认7天"
                        }
                    }
                }
            },
            {
                "name": "query_deep_collection_data",
                "description": "查询深度采集数据表(deep_collection_data)中的数据",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "collection_status": {
                            "type": "string",
                            "description": "采集状态过滤"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "返回数量限制，默认100"
                        },
                        "days": {
                            "type": "integer",
                            "description": "最近多少天的数据，默认7天"
                        }
                    }
                }
            },
            {
                "name": "get_collection_stats",
                "description": "获取采集数据的统计信息",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "days": {
                            "type": "integer",
                            "description": "统计最近多少天的数据，默认7天"
                        }
                    }
                }
            },
            {
                "name": "get_source_distribution",
                "description": "获取数据源分布统计",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "days": {
                            "type": "integer",
                            "description": "统计最近多少天的数据，默认7天"
                        }
                    }
                }
            },
            {
                "name": "get_deep_collection_stats",
                "description": "获取深度采集统计信息",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "days": {
                            "type": "integer",
                            "description": "统计最近多少天的数据，默认7天"
                        }
                    }
                }
            },
            {
                "name": "get_keyword_trends",
                "description": "获取关键词趋势统计",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "days": {
                            "type": "integer",
                            "description": "统计最近多少天的数据，默认7天"
                        },
                        "top_n": {
                            "type": "integer",
                            "description": "返回前N个关键词，默认10"
                        }
                    }
                }
            }
        ]

    @staticmethod
    def query_collection_data(keyword=None, source=None, limit=100, days=7):
        """
        查询采集数据

        Args:
            keyword: 关键词
            source: 数据源
            limit: 返回数量限制
            days: 最近多少天的数据

        Returns:
            list: 数据列表
        """
        query = CollectionData.query

        if keyword:
            query = query.filter(CollectionData.keyword.like(f'%{keyword}%'))

        if source:
            query = query.filter(CollectionData.source == source)

        if days:
            start_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(CollectionData.collected_at >= start_date)

        results = query.order_by(desc(CollectionData.collected_at)).limit(limit).all()

        return [item.to_dict() for item in results]

    @staticmethod
    def query_deep_collection_data(collection_status=None, limit=100, days=7):
        """
        查询深度采集数据

        Args:
            collection_status: 采集状态
            limit: 返回数量限制
            days: 最近多少天的数据

        Returns:
            list: 数据列表
        """
        query = DeepCollectionData.query

        if collection_status:
            query = query.filter(DeepCollectionData.collection_status == collection_status)

        if days:
            start_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(DeepCollectionData.created_at >= start_date)

        results = query.order_by(desc(DeepCollectionData.created_at)).limit(limit).all()

        return [item.to_dict() for item in results]

    @staticmethod
    def get_collection_stats(days=7):
        """
        获取采集数据统计

        Args:
            days: 统计最近多少天的数据

        Returns:
            dict: 统计信息
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        total_count = CollectionData.query.filter(
            CollectionData.collected_at >= start_date
        ).count()

        daily_stats = db.session.query(
            func.date(CollectionData.collected_at).label('date'),
            func.count(CollectionData.id).label('count')
        ).filter(
            CollectionData.collected_at >= start_date
        ).group_by(
            func.date(CollectionData.collected_at)
        ).order_by(
            func.date(CollectionData.collected_at)
        ).all()

        return {
            'total_count': total_count,
            'daily_stats': [{'date': str(stat.date), 'count': stat.count} for stat in daily_stats]
        }

    @staticmethod
    def get_source_distribution(days=7):
        """
        获取数据源分布

        Args:
            days: 统计最近多少天的数据

        Returns:
            list: 数据源分布列表
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        distribution = db.session.query(
            CollectionData.source,
            func.count(CollectionData.id).label('count')
        ).filter(
            CollectionData.collected_at >= start_date
        ).group_by(
            CollectionData.source
        ).order_by(
            desc(func.count(CollectionData.id))
        ).all()

        return [{'source': item.source, 'count': item.count} for item in distribution]

    @staticmethod
    def get_deep_collection_stats(days=7):
        """
        获取深度采集统计

        Args:
            days: 统计最近多少天的数据

        Returns:
            dict: 统计信息
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        total_count = DeepCollectionData.query.filter(
            DeepCollectionData.created_at >= start_date
        ).count()

        success_count = DeepCollectionData.query.filter(
            DeepCollectionData.created_at >= start_date,
            DeepCollectionData.collection_status == 'success'
        ).count()

        failed_count = DeepCollectionData.query.filter(
            DeepCollectionData.created_at >= start_date,
            DeepCollectionData.collection_status == 'failed'
        ).count()

        return {
            'total_count': total_count,
            'success_count': success_count,
            'failed_count': failed_count,
            'success_rate': round(success_count / total_count * 100, 2) if total_count > 0 else 0
        }

    @staticmethod
    def get_keyword_trends(days=7, top_n=10):
        """
        获取关键词趋势

        Args:
            days: 统计最近多少天的数据
            top_n: 返回前N个关键词

        Returns:
            list: 关键词趋势列表
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        keywords = db.session.query(
            CollectionData.keyword,
            func.count(CollectionData.id).label('count')
        ).filter(
            CollectionData.collected_at >= start_date,
            CollectionData.keyword.isnot(None),
            CollectionData.keyword != ''
        ).group_by(
            CollectionData.keyword
        ).order_by(
            desc(func.count(CollectionData.id))
        ).limit(top_n).all()

        return [{'keyword': item.keyword, 'count': item.count} for item in keywords]

    @staticmethod
    def execute_tool(tool_name, parameters):
        """
        执行工具

        Args:
            tool_name: 工具名称
            parameters: 工具参数

        Returns:
            dict: 执行结果
        """
        try:
            if tool_name == 'query_collection_data':
                result = AIAnalysisService.query_collection_data(
                    keyword=parameters.get('keyword'),
                    source=parameters.get('source'),
                    limit=parameters.get('limit', 100),
                    days=parameters.get('days', 7)
                )
                return {'success': True, 'data': result}

            elif tool_name == 'query_deep_collection_data':
                result = AIAnalysisService.query_deep_collection_data(
                    collection_status=parameters.get('collection_status'),
                    limit=parameters.get('limit', 100),
                    days=parameters.get('days', 7)
                )
                return {'success': True, 'data': result}

            elif tool_name == 'get_collection_stats':
                result = AIAnalysisService.get_collection_stats(
                    days=parameters.get('days', 7)
                )
                return {'success': True, 'data': result}

            elif tool_name == 'get_source_distribution':
                result = AIAnalysisService.get_source_distribution(
                    days=parameters.get('days', 7)
                )
                return {'success': True, 'data': result}

            elif tool_name == 'get_deep_collection_stats':
                result = AIAnalysisService.get_deep_collection_stats(
                    days=parameters.get('days', 7)
                )
                return {'success': True, 'data': result}

            elif tool_name == 'get_keyword_trends':
                result = AIAnalysisService.get_keyword_trends(
                    days=parameters.get('days', 7),
                    top_n=parameters.get('top_n', 10)
                )
                return {'success': True, 'data': result}

            else:
                return {'success': False, 'error': f'未知的工具: {tool_name}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def generate_chart_config(chart_type, data, title):
        """
        生成图表配置

        Args:
            chart_type: 图表类型 (bar, line, pie)
            data: 图表数据
            title: 图表标题

        Returns:
            dict: ECharts配置
        """
        config = {
            'title': {
                'text': title,
                'textStyle': {
                    'color': '#e0f7fa'
                }
            },
            'tooltip': {
                'trigger': 'axis' if chart_type in ['bar', 'line'] else 'item',
                'backgroundColor': 'rgba(10, 30, 55, 0.9)',
                'borderColor': '#3b82f6',
                'textStyle': {
                    'color': '#e0f7fa'
                }
            },
            'legend': {
                'textStyle': {
                    'color': '#e0f7fa'
                }
            },
            'xAxis': {
                'type': 'category',
                'axisLine': {
                    'lineStyle': {
                        'color': '#3b82f6'
                    }
                },
                'axisLabel': {
                    'color': '#e0f7fa'
                }
            },
            'yAxis': {
                'type': 'value',
                'axisLine': {
                    'lineStyle': {
                        'color': '#3b82f6'
                    }
                },
                'axisLabel': {
                    'color': '#e0f7fa'
                },
                'splitLine': {
                    'lineStyle': {
                        'color': 'rgba(59, 130, 246, 0.2)'
                    }
                }
            }
        }

        if chart_type == 'bar':
            config['series'] = [{
                'type': 'bar',
                'data': data.get('values', []),
                'itemStyle': {
                    'color': '#3b82f6'
                }
            }]
            config['xAxis']['data'] = data.get('labels', [])

        elif chart_type == 'line':
            config['series'] = [{
                'type': 'line',
                'data': data.get('values', []),
                'itemStyle': {
                    'color': '#10b981'
                },
                'areaStyle': {
                    'color': 'rgba(16, 185, 129, 0.3)'
                }
            }]
            config['xAxis']['data'] = data.get('labels', [])

        elif chart_type == 'pie':
            config.pop('xAxis', None)
            config.pop('yAxis', None)
            config['series'] = [{
                'type': 'pie',
                'radius': ['40%', '70%'],
                'data': data.get('values', []),
                'itemStyle': {
                    'borderColor': '#0a192f',
                    'borderWidth': 2
                },
                'label': {
                    'show': False
                },
                'emphasis': {
                    'label': {
                        'show': True,
                        'fontSize': '16',
                        'fontWeight': 'bold'
                    }
                },
                'color': ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
            }]

        return config

    @staticmethod
    def generate_table_data(data, columns):
        """
        生成表格数据

        Args:
            data: 数据列表
            columns: 列名列表

        Returns:
            dict: 表格数据
        """
        rows = []
        for item in data:
            row = []
            for col in columns:
                if col == 'ID':
                    row.append(str(item.get('id', '')))
                elif col == '标题':
                    row.append(str(item.get('title', '')))
                elif col == '来源':
                    row.append(str(item.get('source', '')))
                elif col == '关键词':
                    row.append(str(item.get('keyword', '')))
                elif col == '采集时间':
                    row.append(str(item.get('collected_at', '')))
                elif col == '采集状态':
                    row.append(str(item.get('collection_status', '')))
                elif col == 'Token使用':
                    row.append(str(item.get('tokens_used', '')))
                elif col == '创建时间':
                    row.append(str(item.get('created_at', '')))
                else:
                    row.append(str(item.get(col, '')))
            rows.append(row)

        return {
            'headers': columns,
            'rows': rows
        }

    @staticmethod
    def analyze_user_message(message):
        """
        分析用户消息，判断需要使用的工具和响应类型

        Args:
            message: 用户消息

        Returns:
            dict: 分析结果
        """
        message_lower = message.lower()

        tool_name = None
        parameters = {}
        response_type = 'text'
        chart_type = None

        if '趋势' in message or 'trend' in message_lower:
            tool_name = 'get_collection_stats'
            response_type = 'chart'
            chart_type = 'line'

        elif '分布' in message or 'distribution' in message_lower:
            if '数据源' in message or 'source' in message_lower:
                tool_name = 'get_source_distribution'
                response_type = 'chart'
                chart_type = 'pie'
            else:
                tool_name = 'get_source_distribution'
                response_type = 'chart'
                chart_type = 'pie'

        elif '关键词' in message or 'keyword' in message_lower:
            tool_name = 'get_keyword_trends'
            response_type = 'chart'
            chart_type = 'bar'

        elif '深采' in message or '深度采集' in message or 'deep' in message_lower:
            if '成功率' in message or 'success' in message_lower:
                tool_name = 'get_deep_collection_stats'
                response_type = 'text'
            else:
                tool_name = 'query_deep_collection_data'
                response_type = 'table'

        elif '查询' in message or 'query' in message_lower or '搜索' in message or 'search' in message_lower:
            tool_name = 'query_collection_data'
            response_type = 'table'

            if '最近' in message:
                match = re.search(r'最近(\d+)天', message)
                if match:
                    parameters['days'] = int(match.group(1))

        else:
            return {
                'tool_name': None,
                'parameters': {},
                'response_type': 'text',
                'chart_type': None
            }

        return {
            'tool_name': tool_name,
            'parameters': parameters,
            'response_type': response_type,
            'chart_type': chart_type
        }

    @staticmethod
    def process_message(message, model_id):
        """
        处理用户消息

        Args:
            message: 用户消息
            model_id: AI模型ID

        Returns:
            dict: 处理结果
        """
        model = AIModelService.get_model_by_id(model_id)
        if not model:
            return {
                'success': False,
                'error': 'AI模型不存在'
            }

        analysis = AIAnalysisService.analyze_user_message(message)

        if not analysis['tool_name']:
            return {
                'success': True,
                'type': 'text',
                'content': '我理解您的问题，但需要更具体的信息。您可以询问关于数据采集趋势、数据源分布、关键词统计或深度采集成功率等问题。'
            }

        tool_result = AIAnalysisService.execute_tool(
            analysis['tool_name'],
            analysis['parameters']
        )

        if not tool_result['success']:
            return {
                'success': False,
                'error': tool_result['error']
            }

        data = tool_result['data']

        if analysis['response_type'] == 'chart':
            chart_data = AIAnalysisService.prepare_chart_data(
                analysis['tool_name'],
                data
            )
            chart_config = AIAnalysisService.generate_chart_config(
                analysis['chart_type'],
                chart_data,
                AIAnalysisService.get_chart_title(analysis['tool_name'])
            )

            return {
                'success': True,
                'type': 'chart',
                'chart_config': chart_config,
                'message': AIAnalysisService.get_chart_message(analysis['tool_name'], data)
            }

        elif analysis['response_type'] == 'table':
            columns = AIAnalysisService.get_table_columns(analysis['tool_name'])
            table_data = AIAnalysisService.generate_table_data(data, columns)

            return {
                'success': True,
                'type': 'table',
                'table_data': table_data,
                'message': AIAnalysisService.get_table_message(analysis['tool_name'], data)
            }

        else:
            return {
                'success': True,
                'type': 'text',
                'content': AIAnalysisService.format_text_response(analysis['tool_name'], data)
            }

    @staticmethod
    def prepare_chart_data(tool_name, data):
        """
        准备图表数据

        Args:
            tool_name: 工具名称
            data: 原始数据

        Returns:
            dict: 图表数据
        """
        if tool_name == 'get_collection_stats':
            return {
                'labels': [item['date'] for item in data['daily_stats']],
                'values': [item['count'] for item in data['daily_stats']]
            }

        elif tool_name == 'get_source_distribution':
            return {
                'labels': [item['source'] for item in data],
                'values': [{'name': item['source'], 'value': item['count']} for item in data]
            }

        elif tool_name == 'get_keyword_trends':
            return {
                'labels': [item['keyword'] for item in data],
                'values': [item['count'] for item in data]
            }

        return {'labels': [], 'values': []}

    @staticmethod
    def get_chart_title(tool_name):
        """
        获取图表标题

        Args:
            tool_name: 工具名称

        Returns:
            str: 图表标题
        """
        titles = {
            'get_collection_stats': '数据采集趋势',
            'get_source_distribution': '数据源分布',
            'get_keyword_trends': '关键词统计'
        }
        return titles.get(tool_name, '数据统计')

    @staticmethod
    def get_chart_message(tool_name, data):
        """
        获取图表说明文字

        Args:
            tool_name: 工具名称
            data: 数据

        Returns:
            str: 说明文字
        """
        if tool_name == 'get_collection_stats':
            return f'最近7天共采集数据 {data["total_count"]} 条'

        elif tool_name == 'get_source_distribution':
            return f'共有 {len(data)} 个数据源'

        elif tool_name == 'get_keyword_trends':
            return f'Top {len(data)} 热门关键词'

        return '数据统计如下'

    @staticmethod
    def get_table_columns(tool_name):
        """
        获取表格列名

        Args:
            tool_name: 工具名称

        Returns:
            list: 列名列表
        """
        columns = {
            'query_collection_data': ['ID', '标题', '来源', '关键词', '采集时间'],
            'query_deep_collection_data': ['ID', '标题', '来源', '采集状态', 'Token使用', '创建时间']
        }
        return columns.get(tool_name, [])

    @staticmethod
    def get_table_message(tool_name, data):
        """
        获取表格说明文字

        Args:
            tool_name: 工具名称
            data: 数据

        Returns:
            str: 说明文字
        """
        if tool_name == 'query_collection_data':
            return f'查询到 {len(data)} 条采集数据'

        elif tool_name == 'query_deep_collection_data':
            return f'查询到 {len(data)} 条深度采集数据'

        return f'查询到 {len(data)} 条数据'

    @staticmethod
    def format_text_response(tool_name, data):
        """
        格式化文本响应

        Args:
            tool_name: 工具名称
            data: 数据

        Returns:
            str: 格式化的文本
        """
        if tool_name == 'get_deep_collection_stats':
            return f'''深度采集统计：
- 总采集数：{data['total_count']} 条
- 成功数：{data['success_count']} 条
- 失败数：{data['failed_count']} 条
- 成功率：{data['success_rate']}%'''

        return str(data)